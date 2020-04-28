from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from data import db_session, users, login_class, registration, redefine_roles, news, \
    translater, forum_db, answer_on_question, ask_question, settings, settings_db, \
    edit_profile_form, api_func
from random import choice
import sys
from flask_restful import abort, Api
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, send
import feedparser, json, os, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'matesearch_secretkey'  # Секретный ключ
socketio = SocketIO(app)
login_manager = LoginManager()
api = Api(app)
login_manager.init_app(app)
sys.stdout.encoding  # 'UTF-8'


@login_manager.user_loader
def load_user(user_id):
    sessions = db_session.create_session()
    return sessions.query(users.User).get(user_id)


@app.errorhandler(404)  # функция ошибки
def not_found(error):
    try:
        sessions = db_session.create_session()
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    colors = choice(["primary", "success", "danger", "info"])
    return render_template("not_found.html", colors=colors, main_color=main_color,
                           main_lang=main_lang)


@app.route("/")  # Главная страница
def index():
    news_theft()
    check_last_page()
    counter_1 = 6
    counter_2 = 0
    next_page = 2
    back_page = 1
    sessions = db_session.create_session()
    news_on_page = sessions.query(news.News).order_by(news.News.created_date.desc())
    colors = choice(["primary", "success", "danger", "info"])
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    return render_template("index.html", colors=colors, news=news_on_page, counter_1=counter_1,
                           counter_2=counter_2, next_page=next_page, back_page=back_page,
                           main_color=main_color, main_lang=main_lang)


@app.route("/page/<int:num>")  # Страницы новостей
def new_page(num):
    news_theft()
    check_last_page()
    counter_1 = num * 5 + 1
    counter_2 = counter_1 - 6
    next_page = num + 1
    back_page = num - 1
    if num == 1:
        back_page = 1
    if num == 6:
        next_page = 6
    sessions = db_session.create_session()
    news_on_page = sessions.query(news.News).order_by(news.News.created_date.desc())
    colors = choice(["primary", "success", "danger", "info"])
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    return render_template("index.html", colors=colors, news=news_on_page, counter_1=counter_1,
                           counter_2=counter_2, next_page=next_page, back_page=back_page,
                           main_color=main_color, main_lang=main_lang)


@app.route('/logout', methods=["GET", "POST"])  # Выйти из аккаунта
def logout():
    with open("static/json/chaty.json") as file:
        data = json.load(file)
    for key in data["chats"].keys():
        if str(current_user.id) in key:
            count = 0
            chats = data["chats"]
            for i in range(1, len(data["chats"][key])):
                time1 = (chats[key][i - count][0][0] * 365 + chats[key][i - count][0][1] * 30 +
                         chats[key][i - count][0][2]) * 3600 * 24 + chats[key][i - count][0][3] * \
                        3600 + chats[key][i - count][0][4] * 60 + chats[key][i - count][0][5]
                time = datetime.datetime.now()
                time2 = (time.year * 365 + time.month * 30 + time.day) * 3600 * 24 + time.hour * \
                        3600 + time.minute * 60 + time.second
                if time2 - time1 > 3600 * 24:
                    del data["chats"][key][i - count]
                    count += 1
    with open("static/json/chaty.json", "w") as file:
        json.dump(data, file)
    logout_user()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])  # Войти в аккаунт
def login():
    check_last_page()
    form = login_class.LoginForm()
    sessions = db_session.create_session()
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    colors = choice(["primary", "success", "danger", "info"])
    if form.validate_on_submit():
        user = sessions.query(users.User).filter(users.User.email == form.email.data).first()
        password = generate_password_hash(form.password.data)
        if user and check_password_hash(password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Invalid username or password', colors=colors,
                               form=form, main_color=main_color, main_lang=main_lang)
    return render_template('login.html', title='Авторизация', colors=colors, form=form,
                           main_color=main_color, main_lang=main_lang)


@app.route('/register', methods=['GET', 'POST'])  # Страница регистрации
def reqister():
    check_last_page()
    form = registration.RegisterForm()
    sessions = db_session.create_session()
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, main_color=main_color,
                                   message="Passwords don't match", main_lang=main_lang)
        if sessions.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form, main_color=main_color,
                                   message="This user already exists", main_lang=main_lang)
        if len(form.name.data) > 16 or len(form.name.data) < 3:
            return render_template('register.html', title='Регистрация',
                                   form=form, main_color=main_color,
                                   message="This login too long", main_lang=main_lang)
        user = users.User(name=form.name.data,
                          email=form.email.data,
                          password=form.password.data,
                          role="user")
        user.set_password(form.password.data)
        sessions.add(user)
        sessions.commit()
        settings = settings_db.Settings_db(user_id=user.id,
                                           language='en',
                                           theme='light')
        sessions.add(settings)
        sessions.commit()
        return redirect('/login')
    colors = choice(["primary", "success", "danger", "info"])
    return render_template('register.html', colors=colors, title='Registration', form=form,
                           main_color=main_color, main_lang=main_lang)


@app.route("/searchmates/<string:game>/<string:types>")  # Страница поиска тиммейтов
@login_required
def add_to_search(game, types):
    check_last_page()
    if not "/searchmates" in current_user.last_page:
        session = db_session.create_session()
        current_user.last_page = f"/searchmates/{game}/{types}"
        session.merge(current_user)
        session.commit()
        with open("static/json/searching_mates.json") as file:
            data = json.load(file)
        if current_user.id not in data[game][types]:
            data[game][types] += [current_user.id]
        with open("static/json/searching_mates.json", "w") as file:
            json.dump(data, file)
    elif ("/searchmates" in current_user.last_page and
          (game != current_user.last_page.split("/")[1] or
           types != current_user.last_page.split("/")[2])):
        with open("static/json/searching_mates.json") as file:
            data = json.load(file)
        games, typess = current_user.last_page.split("/")[2], current_user.last_page.split("/")[3]
        if current_user.id in data[games][typess]:
            del data[games][typess][data[games][typess].index(current_user.id)]
        with open("static/json/searching_mates.json", "w") as file:
            json.dump(data, file)
        session = db_session.create_session()
        current_user.last_page = f"/searchmates/{game}/{types}"
        session.merge(current_user)
        session.commit()
        with open("static/json/searching_mates.json") as file:
            data = json.load(file)
        if current_user.id not in data[game][types]:
            data[game][types] += [current_user.id]
        with open("static/json/searching_mates.json", "w") as file:
            json.dump(data, file)
    mates_id = data[game][types]
    mates = []
    session = db_session.create_session()
    for mate_id in mates_id:
        mate = session.query(users.User).get(mate_id)
        mates.append([mate.name, mate.reputation, mate.avatar, mate.id, 0])
    colors = choice(["primary", "success", "danger", "info"])
    sessions = db_session.create_session()
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    return render_template("search_table.html", colors=colors, mates=mates,
                           main_color=main_color, main_lang=main_lang, name_game=game,
                           type_game=types)


@socketio.on("message")  # Сообщения
def Message(message):
    with open("static/json/chaty.json") as file:
        data = json.load(file)
    time = datetime.datetime.now()
    message, url = map(str, message.split("4a96a813f286fb923b0b4ead19e0052c3ddc1c36"))
    data["chats"][url] += [[(time.year, time.month, time.day, time.hour, time.minute,
                             time.second), current_user.name, message]]
    with open("static/json/chaty.json", "w") as file:
        json.dump(data, file)
    send(message + "_<}]:;,.!$?$228?!.,;:[{>_" + current_user.name, broadcast=True)


@app.route("/chats/<int:first_id>/<int:second_id>", methods=["GET", "POST"])  # Чат
@login_required
def chats(first_id, second_id):
    check_last_page()
    # chats: {
    #   url:
    #       [
    #           ["data", "user", "text"]
    #       ]
    # }
    sessions = db_session.create_session()
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    if current_user.id != first_id and current_user.id != second_id:
        if main_lang == "en":
            mess = "You cann't wathing this chat"
        else:
            mess = "Вы не можете следить за этим чатом"
        return mess
    first_url = str(first_id) + "_" + str(second_id)
    second_url = str(second_id) + "_" + str(first_id)
    url = ""
    with open("static/json/chaty.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    if first_url in data["chats"].keys():
        url = first_url
    elif second_url in data["chats"].keys():
        url = second_url
    else:
        url = first_url
    if not url in data["chats"].keys():
        time = datetime.datetime.now()
        data["chats"].update([(url, [[time.year, time.month, time.day, time.hour, time.minute,
                                      time.second, {first_id: 0, second_id: 0}]])])
        with open("static/json/chaty.json", "w", encoding='utf-8') as file:
            json.dump(data, file)
        with open("static/json/chaty.json") as file:
            data = json.load(file)
    chat = data["chats"][url][1:]
    for i in range(len(chat)):
        chat[i][2] = chat[i][2].encode('l1').decode()
    colors = choice(["primary", "success", "danger", "info"])
    return render_template("chats.html", colors=colors, chat=chat, url=url, main_color=main_color,
                           main_lang=main_lang)


# Чаты во время поиска
@app.route("/chats_in_search/<string:game>/<string:type>", methods=["GET", "POST"])
def chats_in_search(game, type):
    sessions = db_session.create_session()
    with open("static/json/chaty.json") as file:
        data = json.load(file)
    chat_list = []
    for key in data["chats"].keys():
        if str(current_user.id) in key:
            id_list = key.split("_")
            del id_list[id_list.index(str(current_user.id))]
            user = sessions.query(users.User).get(id_list[0])
            chat_list += [user]
    colors = choice(["primary", "success", "danger", "info"])
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    return render_template("chat_in_search.html", colors=colors, main_color=main_color,
                           chat_list=chat_list, main_lang=main_lang, name_game=game, type_game=type)


@app.route("/chat")  # Все чаты
@login_required
def chat():
    sessions = db_session.create_session()
    with open("static/json/chaty.json") as file:
        data = json.load(file)
    chat_list = []
    for key in data["chats"].keys():
        if str(current_user.id) in key:
            id_list = key.split("_")
            del id_list[id_list.index(str(current_user.id))]
            user = sessions.query(users.User).get(id_list[0])
            chat_list += [user]
    colors = choice(["primary", "success", "danger", "info"])
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    return render_template("chat_list.html", colors=colors, main_color=main_color,
                           chat_list=chat_list, main_lang=main_lang)


def check_last_page():  # Проверка, что вы ушли со страницы поиска, для остановки поиска игроков
    if current_user.is_authenticated and "/searchmates" in current_user.last_page:
        with open("static/json/searching_mates.json") as file:
            data = json.load(file)
        game, types = current_user.last_page.split("/")[2], current_user.last_page.split("/")[3]
        if current_user.id in data[game][types]:
            del data[game][types][data[game][types].index(current_user.id)]
        with open("static/json/searching_mates.json", "w") as file:
            json.dump(data, file)
        session = db_session.create_session()
        current_user.last_page = "/"
        session.merge(current_user)
        session.commit()


def news_theft():  # Обновление новостей
    session = db_session.create_session()
    NewsFeed = feedparser.parse("https://news.yandex.ru/games.rss")
    nowosty = NewsFeed["entries"]
    for new in nowosty:
        title = new["title"]
        content = new["summary"]
        old_news = session.query(news.News)
        coincidence = False
        for old_new in old_news:
            if old_new.rus_content == content:
                coincidence = True
        if not coincidence:
            new_new = news.News(
                title=translater.translate(title),
                rus_title=title,
                rus_content=content,
                content=translater.translate(content)
            )
            session.add(new_new)
    session.commit()
    nowosty = session.query(news.News).order_by(news.News.created_date.desc())
    count = 0
    for new in nowosty:
        if count > 50:
            session.delete(new)
        count += 1
    session.commit()


@app.route("/searchmates/<string:game>")  # Страница для выбора типа игры
def searchmates(game):
    check_last_page()
    colors = choice(["primary", "success", "danger", "info"])
    sessions = db_session.create_session()
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    return render_template('search.html', colors=colors, game=game, main_color=main_color,
                           main_lang=main_lang)


@app.route("/profile/<int:id>")  # Профиль
@login_required
def user_info(id):
    check_last_page()
    sessions = db_session.create_session()
    user = sessions.query(users.User).get(id)
    if user:
        user_id_str = str(user.id)
        colors = choice(["primary", "success", "danger", "info"])
        ocenka_reputacii = False
        dobavlenie_v_druzya = False
        with open("static/json/chaty.json") as file:
            data = json.load(file)
        chats = data["chats"]
        url1 = str(current_user.id) + "_" + str(id)
        url2 = str(id) + "_" + str(current_user.id)
        url = ""
        if url1 in chats.keys():
            url = url1
        elif url2 in chats.keys():
            url = url2
        if (url != "" and str(current_user.id) not in user.appraisers and
                str(current_user.id) + ";1" not in user.notifications):
            time1 = (chats[url][0][0] * 365 + chats[url][0][1] * 30 + chats[url][0][2]) * \
                    3600 * 24 + chats[url][0][3] * 3600 + chats[url][0][4] * 60 + chats[url][0][5]
            time = datetime.datetime.now()
            time2 = (time.year * 365 + time.month * 30 + time.day) * 3600 * 24 + time.hour * \
                    3600 + time.minute * 60 + time.second
            if time2 - time1 > 3600:
                ocenka_reputacii = True
        if (str(current_user.id) + ";0;" + str(user.id) not in user.notifications and
                str(current_user.id) not in user.friends):
            dobavlenie_v_druzya = True
        try:
            settings_info = sessions.query(settings_db.Settings_db).filter(
                settings_db.Settings_db.user_id == current_user.id).first()
            main_color = settings_info.theme
            main_lang = settings_info.language
        except AttributeError:
            main_color = "white"
            main_lang = "en"
        return render_template("profile.html", colors=colors, user=user, main_color=main_color,
                               userid=user_id_str, ocenka_reputacii=ocenka_reputacii,
                               dobavlenie_v_druzya=dobavlenie_v_druzya, main_lang=main_lang)


@app.route("/edit_reputation/<int:id>/<int:znach>/<int:second_id>")  # Редактирование репутации
@login_required
def edit_reputation(id, znach, second_id):
    sessions = db_session.create_session()
    user = sessions.query(users.User).get(id)
    if current_user.id != id:
        if (str(current_user.id) not in user.appraisers and
                f"_[{second_id};1;{znach}]" not in user.notifications):
            user.notifications = user.notifications + f"_[{second_id};1;{znach}]"
            sessions.merge(user)
            sessions.commit()
            return redirect(f"/profile/{id}")
    else:
        if znach == 0:
            user.reputation = min(100, int(user.reputation * 10.5) * 0.1)
        else:
            user.reputation = max(1, int(user.reputation * 9.5) * 0.1)
        user.appraisers += "_" + str(second_id)
        sessions.merge(user)
        sessions.commit()
        return redirect(f"/clean_notifications/{id}/{second_id}/1/{znach}")


@app.route("/add_to_friend/<int:first_id>/<int:second_id>")  # Добавление в друзья
@login_required
def add_to_friend(first_id, second_id):
    sessions = db_session.create_session()
    if first_id != current_user.id:
        user = sessions.query(users.User).get(first_id)
        if (str(current_user.id) not in user.friends.split("_") and
                f"_[{second_id};0;{first_id}]" not in user.notifications):
            user.notifications = user.notifications + f"_[{second_id};0;{first_id}]"
            sessions.merge(user)
            sessions.commit()
        return redirect(f"/profile/{first_id}")
    else:
        if str(second_id) not in current_user.friends.split("_"):
            current_user.friends = current_user.friends + f"_{second_id}"
            user_2 = sessions.query(users.User).get(second_id)
            user_2.friends = user_2.friends + f"_{first_id}"
            sessions.merge(user_2)
            sessions.merge(current_user)
            sessions.commit()
        return redirect(f"/clean_notifications/{current_user.id}/{second_id}/0/{first_id}")


@app.route("/edit_profile", methods=["GET", "POST"])  # Редактирование профиля
@login_required
def edit_profile():
    check_last_page()
    colors = choice(["primary", "success", "danger", "info"])
    form = edit_profile_form.EditProfileForm()
    try:
        sessions = db_session.create_session()
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    if main_lang == "en":
        message = "If you want to change your password, enter your old password"
    else:
        message = "Если вы хотите изменить свой пароль, введите свой старый пароль"
    if request.method == "POST":
        session = db_session.create_session()
        if form.old_password.data != "" and form.new_password.data != "":
            if not current_user.check_password(form.old_password.data):
                if main_lang == "en":
                    message = "Invalid old password"
                else:
                    message = "Неверный старый пароль"
                return render_template("edit_profile.html", colors=colors, form=form,
                                       message=message)
            elif form.new_password.data != form.new_password_again:
                if main_lang == "en":
                    message = "The new password is incorrectly repeated"
                else:
                    message = "Новый пароль повторен неправильно"
                return render_template("edit_profile.html", colors=colors, form=form,
                                       message=message)
            elif form.old_password.data == form.new_password.data:
                if main_lang == "en":
                    message = "The new password matches the old one"
                else:
                    message = "Новый пароль совпадает со старым"
                return render_template("edit_profile.html", colors=colors, form=form,
                                       message=message)
            else:
                current_user.set_password(form.new_password.data)
        if str(request.files["file"]) != "<FileStorage: '' ('application/octet-stream')>":
            file = request.files["file"]
            name = "static/img/avatar_img/avatar_" + \
                   str(1 + len(os.listdir("static/img/avatar_img"))) + ".jpg"
            file.save(name)
            current_user.avatar = "/" + name
        current_user.favorite_games = form.favorite_games.data
        if form.name.data != "":
            if len(form.name.data) > 16 or len(form.name.data) < 3:
                if main_lang == "en":
                    message = "This login too long"
                else:
                    message = "Этот логин слишком длинный"
                return render_template("edit_profile.html", colors=colors, form=form,
                                       message=message)
            current_user.name = form.name.data
        session.merge(current_user)
        session.commit()
        return redirect(f'/profile/{current_user.id}')
    form.avatar.data = current_user.avatar
    form.favorite_games.data = current_user.favorite_games
    form.name.data = current_user.name
    return render_template("edit_profile.html", colors=colors, form=form, message=message)


@app.route("/notifications", methods=["GET", "POST"])  # Уведомления
@login_required
def notifications():
    # _[id - от кого;0 - запрос дружбы, 1 - отзыв; id - если запрос, ocenka - если отзыв]
    session = db_session.create_session()
    notifications = current_user.notifications.split("_")[1:]
    new_notifications = []
    message = ""
    sessions = db_session.create_session()
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    if notifications == [""]:
        if main_lang == "en":
            message = "You don't have any new requests"
        else:
            message = "У вас нет новых запрсов"
    else:
        for i in notifications[1:]:
            print(i[1:-1])
            items = list(map(int, i[1:-1].split(";")))
            user = session.query(users.User).get(items[0])
            new_notifications += [[user, items[1], items[2]]]
    colors = choice(["primary", "success", "danger", "info"])
    return render_template("notifications.html", notifications=new_notifications, colors=colors,
                           message=message, main_color=main_color, main_lang=main_lang)


@app.route(
    "/clean_notifications/<int:user_id>/<int:first_item>/<int:second_item>/<int:third_item>")
@login_required
def clean_notifications(user_id, first_item, second_item, third_item):
    sessions = db_session.create_session()
    user = sessions.query(users.User).get(user_id)
    notification = f"_[{first_item};{second_item};{third_item}]"
    user.notifications = "".join(user.notifications.split(notification))
    sessions.merge(user)
    sessions.commit()
    return redirect("/notifications")


@app.route("/redefine_role", methods=["GET", "POST"])  # Страница переопределения ролей
def redefine_role():
    check_last_page()
    form = redefine_roles.Redefine_role()
    colors = choice(["primary", "success", "danger", "info"])
    sessions = db_session.create_session()
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    if form.validate_on_submit():
        if 'submit' in request.form or 'submit_rus' in request.form:
            try:
                sessions = db_session.create_session()
                user_info = sessions.query(users.User).filter(
                    users.User.id == form.user_id.data).first()
                return render_template('redefine_role.html', colors=colors, form=form,
                                       user_name=user_info.name,
                                       user_role=user_info.role,
                                       main_color=main_color,
                                       main_lang=main_lang)
            except AttributeError:
                return render_template('redefine_role.html', colors=colors, form=form,
                                       message="Данного id не существует!",
                                       user_name="",
                                       user_role="",
                                       main_color=main_color,
                                       main_lang=main_lang)
        elif 'save' in request.form or 'save_rus' in request.form:
            sessions = db_session.create_session()
            new_user_role = form.input_user_role.data
            user_info = sessions.query(users.User).filter(
                users.User.id == form.user_id.data).first()
            user_info.role = new_user_role
            sessions.commit()
            return render_template('redefine_role.html', colors=colors, form=form,
                                   user_name="",
                                   user_role="",
                                   main_color=main_color,
                                   main_lang=main_lang)
    return render_template('redefine_role.html', colors=colors, form=form,
                           user_name="",
                           user_role="",
                           main_color=main_color,
                           main_lang=main_lang)


@app.route("/forum", methods=["GET", "POST"])  # Главная страница форума
def forum_func():
    colors = choice(["primary", "success", "danger", "info"])
    sessions = db_session.create_session()
    forum_questions = sessions.query(forum_db.Forum).filter(forum_db.Forum.date).all()
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    return render_template("forum.html", colors=colors, forum_questions=forum_questions,
                           main_color=main_color, main_lang=main_lang)


# Полная страница вопроса (форум)
@app.route("/forum/question/<int:num_id>", methods=["GET", "POST"])
def forum_full_question(num_id):
    colors = choice(["primary", "success", "danger", "info"])
    sessions = db_session.create_session()
    forum_question = sessions.query(forum_db.Forum).filter(
        forum_db.Forum.id == num_id).first()
    name_users = []
    answers = []
    try:
        for i in forum_question.user_id.split("/end/new_author/"):
            if i != "None":
                name_users.append(sessions.query(users.User).filter(
                    users.User.id == i).first().name)
        for i in forum_question.answers.split("/end/new_answer/"):
            if i != "None":
                answers.append(i)
    except AttributeError:
        pass
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    return render_template("forum_full_question.html", colors=colors, num_id=num_id,
                           title=forum_question.title, question=forum_question.question,
                           answers=answers, user_name=name_users, count=len(answers),
                           main_color=main_color, main_lang=main_lang)


# Страница ответа на вопрос (форум)
@app.route("/forum/answere_on_question/<int:num_id>", methods=["GET", "POST"])
def answer_on_question_func(num_id):
    form = answer_on_question.Answer_on_question()
    if request.method == 'GET':
        colors = choice(["primary", "success", "danger", "info"])
        sessions = db_session.create_session()
        try:
            settings_info = sessions.query(settings_db.Settings_db).filter(
                settings_db.Settings_db.user_id == current_user.id).first()
            main_color = settings_info.theme
            main_lang = settings_info.language
        except AttributeError:
            main_color = "white"
            main_lang = "en"
        return render_template("answer_on_question.html", colors=colors, num_id=num_id, form=form,
                               main_color=main_color, main_lang=main_lang)
    elif request.method == 'POST':
        sessions = db_session.create_session()
        answer = form.answer.data
        if "/end/new_answer/" in answer:
            correct_answer = answer.split('/end/new_answer/')
            answer = ''.join(correct_answer)
        answer_db = sessions.query(forum_db.Forum).filter(
            forum_db.Forum.id == num_id).first()
        first_answer = str(answer_db.answers) + "/end/new_answer/"
        first_author = str(answer_db.user_id) + "/end/new_author/"
        user_id_db = sessions.query(forum_db.Forum).filter(
            forum_db.Forum.id == num_id).first()
        id_user = current_user.id
        user_id_db.user_id = str(first_author) + str(id_user)
        answer_db.answers = str(first_answer) + str(answer)
        sessions.commit()
        return redirect("/forum")


@app.route("/forum/ask_question", methods=["GET", "POST"])  # Страница для задавания вопроса (форум)
def ask_a_question():
    form = ask_question.Ask_question()
    colors = choice(["primary", "success", "danger", "info"])
    if form.validate_on_submit():
        sessions = db_session.create_session()
        forum_ask_question = forum_db.Forum(
            title=str(form.title.data),
            question=str(form.question.data),
            theme=str(form.theme.data)
        )
        sessions.add(forum_ask_question)
        sessions.commit()
        return redirect("/forum")
    sessions = db_session.create_session()
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    return render_template("ask_question.html", colors=colors, form=form,
                           main_color=main_color, main_lang=main_lang)


@app.route("/settings", methods=["GET", "POST"])  # Настройки
def site_settings():
    colors = choice(["primary", "success", "danger", "info"])
    form = settings.Settings_form()
    sessions = db_session.create_session()
    user_info = sessions.query(settings_db.Settings_db).filter(
        settings_db.Settings_db.user_id == current_user.id).first()
    if form.validate_on_submit():
        if 'white_theme' in request.form or 'white_theme_rus' in request.form:
            user_info.theme = "white"
        elif 'dusty_cheese_theme' in request.form or 'dusty_cheese_theme_rus' in request.form:
            user_info.theme = "beige"
        elif 'sneezing_fairy_theme' in request.form or 'sneezing_fairy_theme_rus' in request.form:
            user_info.theme = "#e3f3ff"
        elif 'lilac_cloud_theme' in request.form or 'lilac_cloud_theme_rus' in request.form:
            user_info.theme = "#f9e8fa"
        elif 'en_language' in request.form:
            user_info.language = "en"
        elif 'ru_language' in request.form:
            user_info.language = "ru"
        sessions.commit()
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    return render_template("settings.html", colors=colors, form=form, main_color=main_color,
                           main_lang=main_lang)


@app.route('/question_delete/<int:id>', methods=['GET', 'POST'])  # Удаление вопроса на форуме
@login_required
def news_delete(id):
    sessions = db_session.create_session()
    new = sessions.query(forum_db.Forum).filter(forum_db.Forum.id == id).first()
    if new:
        sessions.delete(new)
        sessions.commit()
    else:
        abort(404)
    return redirect('/forum')


@app.route("/api")  # API
def api_page():
    colors = choice(["primary", "success", "danger", "info"])
    sessions = db_session.create_session()
    try:
        settings_info = sessions.query(settings_db.Settings_db).filter(
            settings_db.Settings_db.user_id == current_user.id).first()
        main_color = settings_info.theme
        main_lang = settings_info.language
    except AttributeError:
        main_color = "white"
        main_lang = "en"
    return render_template("api_page.html", colors=colors, main_color=main_color,
                           main_lang=main_lang)


def main():
    db_session.global_init("db/news.db")
    api.add_resource(api_func.NewsListResource, '/api/forum')
    api.add_resource(api_func.NewsResource, '/api/forum/<int:news_id>')
    socketio.run(app)


if __name__ == '__main__':
    main()

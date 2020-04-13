from flask import Flask, render_template, redirect, request, make_response, session, abort
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, logout_user, current_user, login_manager, \
    login_required
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from data import db_session, users, login_class, registration, redefine_roles, news, \
    translater, forum_db, forum, answer_on_question, ask_question
from random import choice
from werkzeug.security import generate_password_hash, check_password_hash
import feedparser, pprint, json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'matesearch_secretkey'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    sessions = db_session.create_session()
    return sessions.query(users.User).get(user_id)


@app.route("/")
def index():
    news_theft()
    check_last_page()
    counter_1 = 6
    counter_2 = 0
    next_page = 2
    back_page = 2
    sessions = db_session.create_session()
    news_on_page = sessions.query(news.News).order_by(news.News.created_date.desc())
    colors = choice(["primary", "success", "danger", "info"])
    return render_template("index.html", colors=colors, news=news_on_page, counter_1=counter_1,
                           counter_2=counter_2, next_page=next_page, back_page=back_page)


@app.route("/page/<int:num>")
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
    return render_template("index.html", colors=colors, news=news_on_page, counter_1=counter_1,
                           counter_2=counter_2, next_page=next_page, back_page=back_page)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    check_last_page()
    form = login_class.LoginForm()
    colors = choice(["primary", "success", "danger", "info"])
    if form.validate_on_submit():
        sessions = db_session.create_session()
        user = sessions.query(users.User).filter(users.User.email == form.email.data).first()
        password = generate_password_hash(form.password.data)
        if user and check_password_hash(password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Invalid username or password', colors=colors,
                               form=form)
    return render_template('login.html', title='Авторизация', colors=colors, form=form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    check_last_page()
    form = registration.RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Passwords don't match")
        sessions = db_session.create_session()
        if sessions.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="This user already exists")
        user = users.User(name=form.name.data,
                          email=form.email.data,
                          password=form.password.data,
                          role="user")
        user.set_password(form.password.data)
        sessions.add(user)
        sessions.commit()
        return redirect('/login')
    colors = choice(["primary", "success", "danger", "info"])
    return render_template('register.html', colors=colors, title='Registration', form=form)


@app.route("/searchmates/<string:game>/<string:types>")
@login_required
def add_to_search(game, types):
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
        mates.append([mate.name, mate.reputation, mate.avatar])
    colors = choice(["primary", "success", "danger", "info"])
    return render_template("search_table.html", colors=colors, mates=mates)


def check_last_page():
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


def news_theft():
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


@app.route("/searchmates/<string:game>")
@login_required
def searchmates(game):
    check_last_page()
    colors = choice(["primary", "success", "danger", "info"])
    return render_template('search.html', colors=colors, game=game)


@app.route("/cyberclubs")
def cyberclubs():
    check_last_page()
    colors = choice(["primary", "success", "danger", "info"])
    return render_template('cyberclubs.html', colors=colors)


@app.route("/profile/<int:id>")
@login_required
def user_info(id):
    session = db_session.create_session()
    user = session.query(users.User).get(id)
    if user:
        colors = choice(["primary", "success", "danger", "info"])
        return render_template("profile.html", colors=colors, user=user)


@app.route("/redefine_role", methods=["GET", "POST"])
def redefine_role():
    check_last_page()
    form = redefine_roles.Redefine_role()
    colors = choice(["primary", "success", "danger", "info"])
    if form.validate_on_submit():
        if 'submit' in request.form:
            try:
                sessions = db_session.create_session()
                user_info = sessions.query(users.User).filter(
                    users.User.id == form.user_id.data).first()
                return render_template('redefine_role.html', colors=colors, form=form,
                                       user_name=user_info.name,
                                       user_role=user_info.role)
            except AttributeError:
                return render_template('redefine_role.html', colors=colors, form=form,
                                       message="Данного id не существует!",
                                       user_name="",
                                       user_role="")
        elif 'save' in request.form:
            sessions = db_session.create_session()
            new_user_role = form.input_user_role.data
            user_info = sessions.query(users.User).filter(
                users.User.id == form.user_id.data).first()
            user_info.role = new_user_role
            sessions.commit()
            return render_template('redefine_role.html', colors=colors, form=form,
                                   user_name="",
                                   user_role="")
    return render_template('redefine_role.html', colors=colors, form=form,
                           user_name="",
                           user_role="")


@app.route("/forum", methods=["GET", "POST"])
def forum_func():
    form = forum.Forum()
    colors = choice(["primary", "success", "danger", "info"])
    sessions = db_session.create_session()
    forum_questions = sessions.query(forum_db.Forum).filter(forum_db.Forum.date).all()
    return render_template("forum.html", colors=colors, form=form, forum_questions=forum_questions)


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
    return render_template("forum_full_question.html", colors=colors, num_id=num_id,
                           title=forum_question.title, question=forum_question.question,
                           answers=answers, user_name=name_users, count=len(answers))


@app.route("/forum/answere_on_question/<int:num_id>", methods=["GET", "POST"])
def answer_on_question_func(num_id):
    if request.method == 'GET':
        form = answer_on_question.Answer_on_question()
        colors = choice(["primary", "success", "danger", "info"])
        if form.validate_on_submit():
            sessions = db_session.create_session()
            answer = form.answer.data
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
        return render_template("answer_on_question.html", colors=colors, num_id=num_id, form=form)
    elif request.method == 'POST':
        return redirect("/forum/question/1")


@app.route("/forum/ask_question", methods=["GET", "POST"])
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
    return render_template("ask_question.html", colors=colors, form=form)


def main():
    db_session.global_init("db/news.db")
    sessions = db_session.create_session()
    app.run()


if __name__ == '__main__':
    main()

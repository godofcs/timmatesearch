from flask import Flask, render_template, redirect, request, make_response, session, abort
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_user, logout_user, current_user, login_manager, login_required
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from data import db_session, users, login, registration
from random import choice
from werkzeug.security import generate_password_hash, check_password_hash

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
    colors = choice(["primary", "success", "danger", "info"])
    return render_template("index.html", colors=colors)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = login.LoginForm()
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
                          about=form.about.data)
        user.set_password(form.password.data)
        sessions.add(user)
        sessions.commit()
        return redirect('/login')
    colors = choice(["primary", "success", "danger", "info"])
    return render_template('register.html', colors=colors, title='Registration', form=form)


@app.route("/searchmates/<string:game>/<string:types>")
@login_required
def add_to_search(game, types):
    pass


@app.route("/searchmates/<string:game>")
@login_required
def searchmates(game):
    colors = choice(["primary", "success", "danger", "info"])
    return render_template('search.html', colors=colors, game=game)


def main():
    db_session.global_init("db/news.db")
    sessions = db_session.create_session()
    app.run()


if __name__ == '__main__':
    main()

import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    role = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    reputation = sqlalchemy.Column(sqlalchemy.Integer, default=50)
    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=True,
                               default="/static/img/avatar_img/0.jpg")
    favorite_games = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    last_page = sqlalchemy.Column(sqlalchemy.String, nullable=True, default="/")
    news = orm.relation('News', back_populates='user')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f'{self.id}, {self.name}, {self.role}, {self.email}'

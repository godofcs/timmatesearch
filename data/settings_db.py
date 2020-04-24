import datetime
import sqlalchemy
from data import db_session
from .db_session import SqlAlchemyBase


class Settings_db(SqlAlchemyBase):
    __tablename__ = 'settings'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    language = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)
    theme = sqlalchemy.Column(sqlalchemy.VARCHAR, nullable=True)

import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Post(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    creater_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    text = sqlalchemy.Column(sqlalchemy.String)
    create_data = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    user = orm.relation('User')
import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Comment(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    main_post = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('posts.id'))
    creater_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    text = sqlalchemy.Column(sqlalchemy.String)
    create_data = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    post = orm.relation('Post')
    user = orm.relation('User')
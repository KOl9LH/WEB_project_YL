from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta
import pytz

Base = declarative_base()

mskdelta = timedelta(hours=3)
mskzone = timezone(mskdelta, name='МСК')  # создаю таймзону Москвы при помощи библиотеки pytz, чтобы пользоваться потом

msktime = datetime.now(mskzone)

time_atm = msktime.strftime('%H:%M')


class User(Base, UserMixin):  # класс отвечающий за аккаунты в базе данных
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    nickname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)


class Post(Base):  # класс отвечающий за посты в базе данных
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(pytz.timezone('Europe/Moscow')), nullable=False)
    is_edited = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='posts')


User.posts = relationship('Post', order_by=Post.id, back_populates='user')


def init_db():  # функция отвечающая за создание базы данных с созданными ранее колоннами
    engine = create_engine('sqlite:///YumRecipe.db')
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    init_db()

'''Necessary SQLAlchemy modules'''
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    '''User Table'''
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    surname = Column(String)
    password = Column(String)

    posts = relationship("Post", back_populates="author")
    reactions = relationship("Reaction", back_populates="user")
    comments = relationship("Comment", back_populates="user")

class Post(Base):
    '''Post Table'''
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    created_at = Column(Date, default=datetime.utcnow)
    updated_at = Column(Date, default=datetime.utcnow, onupdate=datetime.utcnow)
    author_id = Column(Integer, ForeignKey("users.id"))

    author = relationship("User", back_populates="posts")
    reactions = relationship("Reaction", back_populates="post")
    comments = relationship("Comment", back_populates="post")

class Reaction(Base):
    '''Reaction Table to store likes and dislikes'''
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    reaction = Column(String)

    post = relationship("Post", back_populates="reactions")
    user = relationship("User", back_populates="reactions")

class Comment(Base):
    '''Comment table to store them'''
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

class Subscription(Base):
    '''Table to store all subscriptions'''
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscriber_id = Column(Integer, ForeignKey('users.id'))
    subscribed_to_id = Column(Integer, ForeignKey('users.id'))

    subscriber = relationship("User", foreign_keys=[subscriber_id])
    subscribed_to = relationship("User", foreign_keys=[subscribed_to_id])

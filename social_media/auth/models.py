'''Necessary SQLAlchemy modules'''
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    '''User Table'''
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    posts = relationship("Post", back_populates="author")
    reactions = relationship("Reaction", back_populates="user")

class Post(Base):
    '''Post Table'''
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    author_id = Column(Integer, ForeignKey("users.id"))

    author = relationship("User", back_populates="posts")
    reactions = relationship("Reaction", back_populates="post")

class Reaction(Base):
    '''Reaction Table to store likes and dislikes'''
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    reaction = Column(String)

    post = relationship("Post", back_populates="reactions")
    user = relationship("User", back_populates="reactions")

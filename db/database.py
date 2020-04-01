import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, create_engine, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    chat_id = Column(Integer, primary_key=True)
    projects = relationship("Project", back_populates="user")

    def __init__(self, chat_id, projects=[]):
        self.chat_id = chat_id
        self.projects = projects


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    token = Column(String, unique=True, nullable=False)
    user_id = Column(ForeignKey("users.chat_id"), nullable=True)
    user = relationship("User", back_populates="projects")

    def __init__(self, token, name, user_id):
        self.token = token
        self.name = name
        self.user_id = user_id


engine = create_engine(os.environ.get("DATABASE_URL"), echo=False)
Session = sessionmaker(bind=engine)

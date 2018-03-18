from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class NavigationUrl(Base):
    __tablename__ = 'navigation_urls'
    id = Column(Integer, primary_key=True)
    url = Column(Text)
    hash = Column(String(32), nullable=False, unique=True)
    status = Column(String(20), nullable=False)
    # __table_args__ = (UniqueConstraint('hash', name='_hash_uc'),)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(25), nullable=False, unique=True)
    status = Column(String(20), nullable=False)


class UserDetails(Base):
    __tablename__ = 'user_details'
    id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)
    gender = Column(String(10))
    age = Column(String(10))
    religion = Column(String(100))
    marital_status = Column(String(50))
    occupation = Column(Text)
    education = Column(Text)
    uid = Column(Integer, ForeignKey(User.id), unique=True, nullable=False)

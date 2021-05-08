import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Image(Base):

    __tablename__ = "images"
    id =Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)

class Video(Base):

    __tablename__ = "videos"
    id =Column(Integer, primary_key=True)
    name = Column(String)
    path = Column(String)

class Mask(Base):
    __tablename__="masking"
    id=Column(Integer, primary_key=True)
    filename=Column(String(50),nullable=False)
    mask_filename=Column(String(50),nullable=False)
    mask_values=Column(String(30),nullable=False)
    created=Column(String(20),nullable=False)

if __name__ == "__main__":
    engine = create_engine('sqlite:///db.sqlite3')
    Base.metadata.create_all(engine)
    
    


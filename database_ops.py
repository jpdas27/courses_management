from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base


DATABASE_URL = "sqlite:///./courses.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(Integer)
    description = Column(Text)
    domain = Column(String)
    total_rating = Column(Integer, default=0)
    rating_count = Column(Integer, default=0)

    chapters = relationship("Chapter", back_populates="course")


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    chapter_name = Column(String, index=True)
    chapter_text = Column(Text)

    course = relationship("Course", back_populates="chapters")
    ratings = relationship("Rating", back_populates="chapter")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    value = Column(Integer)

    chapter = relationship("Chapter", back_populates="ratings")


Base.metadata.create_all(bind=engine)

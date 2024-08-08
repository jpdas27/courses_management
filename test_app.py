import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import app, get_db
from database_ops import Base, Course, Chapter

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_courses.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_data(db):
    course = Course(
        name="Test Course",
        date=2023,
        description="Test Description",
        domain="test",
        total_rating=0,
        rating_count=0,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    chapter = Chapter(
        course_id=course.id,
        chapter_name="Test Chapter",
        chapter_text="Test Content",
    )
    db.add(chapter)
    db.commit()


@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    setup_data(db)
    yield db
    db.query(Chapter).delete()
    db.query(Course).delete()
    db.commit()
    db.close()


def test_get_courses(db_session):
    response = client.get("/courses")
    assert response.status_code == 200
    assert response.json() == {
        "courses": [
            {
                "id": 1,
                "name": "Test Course",
                "date": 2023,
                "description": "Test Description",
                "domain": "test",
                "average_rating": 0,
            }
        ]
    }


def test_rate_chapter_positive(db_session):
    response = client.post("/chapters/1/rate?rating_value=1")
    assert response.status_code == 200
    assert response.json() == {"message": "Rating submitted successfully"}

    response = client.get("/courses")
    assert response.json()["courses"][0]["average_rating"] == 1


def test_rate_chapter_negative(db_session):
    response = client.post("/chapters/1/rate?rating_value=-1")
    assert response.status_code == 200
    assert response.json() == {"message": "Rating submitted successfully"}

    # Verify the course rating was updated
    response = client.get("/courses")
    assert response.json()["courses"][0]["average_rating"] == -1


def test_rate_chapter_invalid_rating(db_session):
    response = client.post("/chapters/1/rate?rating_value=0")
    assert response.status_code == 200
    assert response.json() == {"message": "Rating submitted successfully"}


def test_get_course(db_session):
    response = client.get("/courses/1")
    assert response.status_code == 200
    assert response.json() == {
        "course": {
            "id": 1,
            "name": "Test Course",
            "date": 2023,
            "description": "Test Description",
            "domain": "test",
            "chapters": [
                {
                    "id": 1,
                    "chapter_name": "Test Chapter",
                    "chapter_text": "Test Content",
                }
            ],
        }
    }


def test_get_course_not_found(db_session):
    response = client.get("/courses/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Course not found"}


def test_get_course_chapters(db_session):
    response = client.get("/courses/1/chapters")
    assert response.status_code == 200
    assert response.json() == {
        "chapters": [
            {
                "chapter_name": "Test Chapter",
                "course_id": 1,
                "id": 1,
                "chapter_text": "Test Content",
            }
        ]
    }


def test_get_course_chapters_not_found(db_session):
    response = client.get("/courses/999/chapters")
    assert response.status_code == 404
    assert response.json() == {"detail": "No chapters found for this course"}

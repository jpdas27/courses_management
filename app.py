from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import json

from database_ops import SessionLocal, Course, Chapter, Rating

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def import_data_from_json(db: Session):
    # Load JSON data
    with open("courses.json", "r") as file:
        courses = json.load(file)

    for course_data in courses:
        course = Course(
            name=course_data["name"],
            date=course_data["date"],
            description=course_data["description"],
            domain=",".join(course_data["domain"]),
            total_rating=0,
            rating_count=0,
        )
        db.add(course)
        db.commit()
        db.refresh(course)

        for chapter_data in course_data["chapters"]:
            chapter = Chapter(
                course_id=course.id,
                chapter_name=chapter_data["name"],
                chapter_text=chapter_data["text"],
            )
            db.add(chapter)
        db.commit()


with SessionLocal() as db:
    import_data_from_json(db)


@app.get("/courses")
def get_courses(
    sort_by: str = "name", domain: str = None, db: Session = Depends(get_db)
):
    query = db.query(Course)

    if domain:
        query = query.filter(Course.domain.like(f"%{domain}%"))

    if sort_by == "name":
        query = query.order_by(Course.name.asc())
    elif sort_by == "date":
        query = query.order_by(Course.date.desc())
    elif sort_by == "rating":
        query = query.order_by(
            desc(func.ifnull(Course.total_rating / Course.rating_count, 0))
        )

    courses = query.all()
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found")

    course_list = [
        {
            "id": course.id,
            "name": course.name,
            "date": course.date,
            "description": course.description,
            "domain": course.domain,
            "average_rating": (
                (course.total_rating / course.rating_count)
                if course.rating_count > 0
                else 0
            ),
        }
        for course in courses
    ]

    return {"courses": course_list}


@app.get("/courses/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    chapters = db.query(Chapter).filter(Chapter.course_id == course_id).all()
    course_data = {
        "id": course.id,
        "name": course.name,
        "date": course.date,
        "description": course.description,
        "domain": course.domain,
        "chapters": [
            {
                "id": chapter.id,
                "chapter_name": chapter.chapter_name,
                "chapter_text": chapter.chapter_text,
            }
            for chapter in chapters
        ],
    }
    return {"course": course_data}


@app.get("/courses/{course_id}/chapters")
def get_course_chapters(course_id: int, db: Session = Depends(get_db)):
    chapters = db.query(Chapter).filter(Chapter.course_id == course_id).all()
    if not chapters:
        raise HTTPException(
            status_code=404, detail="No chapters found for this course"
        )
    return {"chapters": chapters}


@app.post("/chapters/{chapter_id}/rate")
def rate_chapter(
    chapter_id: int, rating_value: int, db: Session = Depends(get_db)
):
    if rating_value not in [1, 2, 3, 4, 5, -1, -2, -3, -4, -5, 0]:
        raise HTTPException(
            status_code=400, detail="Rating must be between -5 to 5"
        )

    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()

    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    rating = Rating(chapter_id=chapter.id, value=rating_value)
    db.add(rating)
    db.commit()
    course = chapter.course
    course.total_rating += rating_value
    course.rating_count += 1
    db.commit()

    return {"message": "Rating submitted successfully"}

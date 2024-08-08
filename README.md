# FastAPI Courses API

This project is a FastAPI-based web application that provides an API for managing courses and chapters. Users can retrieve courses, rate chapters, and perform filtering and sorting operations on the courses.

## Features

- Retrieve a list of courses with optional filtering by domain and sorting by name, date, or average rating.
- Retrieve detailed information about a specific course, including its chapters.
- Rate chapters with positive or negative feedback, which is aggregated into the course's overall rating.

## Project Structure

```bash
.
├── app.py    
├── database_ops.py    
├── test_app.py   
├── courses.json    
├── requirements.txt  
├── pyproject.toml  
└── README.md    
```

## Installation

To set up the project locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone git@github.com:jpdas27/courses_management.git
   cd courses_management
    ```
2. **Create a virtual environment:**
    ```bash 
   python3 -m venv venv
   source venv/bin/activate 
    ```
3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4. **Run the application:**
    ```bash
   uvicorn app:app --reload
    ```
The application will be available at http://localhost:8000.

## API Endpoints
# Courses
#Get all courses:

### Endpoint: /courses  
Method: GET  
Query Parameters:  
*    sort_by: name (default), date, or rating  
*    domain: Filter by domain (optional)

**Response:**
```bash
{
  "courses": [
    {
      "id": 1,
      "name": "Course Name",
      "date": 2023,
      "description": "Course Description",
      "domain": "Domain",
      "average_rating": 4.5
    }
  ]
}
```


# Student Data Management System (OOP Based)

A console-based student record manager built with Python and Object-Oriented
Programming. Originally based on a beginner brief (store student name, roll
number, marks), extended into a fuller mini-project with grade tracking,
GPA calculation, search/sort/filter, class statistics, and persistent storage.

## Features

- **`Student` class** — holds personal info (roll number, name, age, email)
  plus a per-course grade book
- **Grades & GPA** — add/update marks per course, automatic average,
  4.0-scale GPA, letter grades (A+ down to F), pass/fail status
- **Printable report cards** per student
- **`StudentManager` class** — full CRUD:
  - `add_student`, `update_student`, `remove_student`, `get_student`
- **Search & filter**:
  - search by name (partial match)
  - filter by percentage range
  - top performers, failing students
- **Sorting** — by GPA, by name, or by roll number
- **Class-wide statistics** — class average, highest/lowest score,
  passing/failing counts
- **Custom exceptions** for clean error handling:
  `StudentNotFoundError`, `DuplicateStudentError`, `InvalidDataError`
- **JSON persistence** (`student_data.json`) — data is saved between runs
- **Interactive CLI menu** for trying everything out

## Requirements

- Python 3.8+
- No third-party packages — standard library only

## Getting Started

```bash
git clone <your-repo-url>
cd <your-repo-folder>
python3 student_system.py
```

You'll see a menu:

```
1.  Add student
2.  Update student
3.  Remove student
4.  Add/update a grade for a student
5.  View report card
6.  Search by name
7.  Filter by grade range
8.  Top performers
9.  Failing students
10. List all students (sorted)
11. Class statistics
0.  Save & Exit
```

Data is stored in `student_data.json` in the same folder, created
automatically the first time you save.

## Project Structure

```
.
├── student_system.py  # main application (classes + CLI)
├── README.md          # this file
├── LICENSE            # MIT license
└── .gitignore         # ignores generated data files, caches, etc.
```

## Example: Using the classes directly

```python
from student_system import StudentManager

manager = StudentManager()
alice = manager.add_student("R001", "Alice", 20, "alice@example.com")
alice.add_or_update_grade("Math", 95)
alice.add_or_update_grade("Science", 82)

print(alice.report_card())
print(manager.class_statistics())

manager.save()  # persists everything to student_data.json
```

## Possible Extensions

- Attendance tracking per student
- Export report cards to PDF
- Multi-semester / multi-term grade history
- REST API wrapper (FastAPI/Flask) around `StudentManager`
- Unit tests with `pytest` for CRUD and grading logic


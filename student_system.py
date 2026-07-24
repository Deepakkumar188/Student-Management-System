"""
Advanced Student Data Management System (OOP Based)
=====================================================

Project brief (from shared spec):
    Create a Student Data Management System using Object-Oriented Programming
    in Python, allowing users to store and manage student information such as
    student name, roll number, and marks.

This implementation extends the brief into a more advanced project with:
    - A `Student` class holding personal info + a per-course grade book
    - GPA / percentage calculation and letter-grade assignment
    - A `StudentManager` class providing full CRUD (add / update / remove / find)
    - Search & filter (by name, by roll number, by grade range, top performers)
    - Sorting (by GPA, by name, by roll number)
    - Class-wide statistics (average, highest, lowest, pass/fail counts)
    - Custom exceptions for clean error handling
    - JSON-based persistence so data survives between runs
    - A simple interactive command-line menu (run this file directly)

Run:
    python3 student_system.py
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


DATA_FILE = "student_data.json"


# ----------------------------------------------------------------------
# Custom Exceptions
# ----------------------------------------------------------------------
class StudentSystemError(Exception):
    """Base class for all student-system-related errors."""
    pass


class StudentNotFoundError(StudentSystemError):
    """Raised when a roll number does not exist in the system."""
    pass


class DuplicateStudentError(StudentSystemError):
    """Raised when trying to add a student with a roll number already in use."""
    pass


class InvalidDataError(StudentSystemError):
    """Raised when supplied student/grade data is invalid."""
    pass


# ----------------------------------------------------------------------
# Grade helper
# ----------------------------------------------------------------------
def marks_to_letter(marks: float) -> str:
    if marks >= 90:
        return "A+"
    if marks >= 80:
        return "A"
    if marks >= 70:
        return "B"
    if marks >= 60:
        return "C"
    if marks >= 50:
        return "D"
    return "F"


# ----------------------------------------------------------------------
# Student class
# ----------------------------------------------------------------------
class Student:
    def __init__(self, roll_number: str, name: str, age: int, email: str = "",
                 courses: Optional[Dict[str, float]] = None,
                 created_at: Optional[str] = None):
        self.roll_number = roll_number
        self.name = name
        self.age = age
        self.email = email
        self.courses: Dict[str, float] = courses or {}   # course_name -> marks (0-100)
        self.created_at = created_at or datetime.now().isoformat(timespec="seconds")

    # ---- grade operations ----
    def add_or_update_grade(self, course: str, marks: float):
        if not course.strip():
            raise InvalidDataError("Course name cannot be empty.")
        if not (0 <= marks <= 100):
            raise InvalidDataError("Marks must be between 0 and 100.")
        self.courses[course] = marks

    def remove_course(self, course: str):
        if course not in self.courses:
            raise InvalidDataError(f"Student has no record for course '{course}'.")
        del self.courses[course]

    def average_marks(self) -> float:
        if not self.courses:
            return 0.0
        return round(sum(self.courses.values()) / len(self.courses), 2)

    def gpa(self) -> float:
        """4.0-scale GPA derived from average percentage."""
        avg = self.average_marks()
        return round(avg / 25, 2)  # 100% -> 4.0

    def overall_letter_grade(self) -> str:
        return marks_to_letter(self.average_marks())

    def is_passing(self, pass_mark: float = 50.0) -> bool:
        if not self.courses:
            return False
        return all(m >= pass_mark for m in self.courses.values())

    def report_card(self) -> str:
        lines = [f"Report Card — {self.name} (Roll No: {self.roll_number})",
                 f"Age: {self.age}   Email: {self.email or 'N/A'}",
                 "-" * 50]
        if not self.courses:
            lines.append("  No courses recorded yet.")
        else:
            for course, marks in self.courses.items():
                lines.append(f"  {course:<20} {marks:>6.2f}  ({marks_to_letter(marks)})")
        lines.append("-" * 50)
        lines.append(f"  Average: {self.average_marks():.2f}%   "
                     f"GPA: {self.gpa():.2f}   "
                     f"Overall Grade: {self.overall_letter_grade()}   "
                     f"Status: {'PASS' if self.is_passing() else 'FAIL'}")
        return "\n".join(lines)

    # ---- persistence ----
    def to_dict(self) -> Dict:
        return {
            "roll_number": self.roll_number,
            "name": self.name,
            "age": self.age,
            "email": self.email,
            "courses": self.courses,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(d: Dict) -> "Student":
        return Student(d["roll_number"], d["name"], d["age"], d.get("email", ""),
                        d.get("courses", {}), d.get("created_at"))

    def __str__(self):
        return (f"{self.roll_number} | {self.name:<20} | Age: {self.age:<3} | "
                f"Avg: {self.average_marks():>6.2f}% | GPA: {self.gpa():.2f} | "
                f"Grade: {self.overall_letter_grade()}")


# ----------------------------------------------------------------------
# StudentManager: manages the whole collection of students
# ----------------------------------------------------------------------
class StudentManager:
    def __init__(self):
        self.students: Dict[str, Student] = {}

    # ---- CRUD ----
    def add_student(self, roll_number: str, name: str, age: int, email: str = "") -> Student:
        if not roll_number.strip() or not name.strip():
            raise InvalidDataError("Roll number and name are required.")
        if roll_number in self.students:
            raise DuplicateStudentError(f"Roll number '{roll_number}' already exists.")
        if age <= 0:
            raise InvalidDataError("Age must be a positive number.")
        student = Student(roll_number, name, age, email)
        self.students[roll_number] = student
        return student

    def get_student(self, roll_number: str) -> Student:
        student = self.students.get(roll_number)
        if student is None:
            raise StudentNotFoundError(f"No student with roll number '{roll_number}'.")
        return student

    def update_student(self, roll_number: str, name: Optional[str] = None,
                        age: Optional[int] = None, email: Optional[str] = None) -> Student:
        student = self.get_student(roll_number)
        if name is not None and name.strip():
            student.name = name
        if age is not None:
            if age <= 0:
                raise InvalidDataError("Age must be a positive number.")
            student.age = age
        if email is not None:
            student.email = email
        return student

    def remove_student(self, roll_number: str):
        self.get_student(roll_number)  # raises if not found
        del self.students[roll_number]

    # ---- search & filter ----
    def search_by_name(self, keyword: str) -> List[Student]:
        keyword = keyword.lower()
        return [s for s in self.students.values() if keyword in s.name.lower()]

    def filter_by_grade_range(self, min_pct: float, max_pct: float) -> List[Student]:
        return [s for s in self.students.values() if min_pct <= s.average_marks() <= max_pct]

    def top_performers(self, n: int = 3) -> List[Student]:
        return self.sorted_by_gpa(descending=True)[:n]

    def failing_students(self, pass_mark: float = 50.0) -> List[Student]:
        return [s for s in self.students.values() if not s.is_passing(pass_mark)]

    # ---- sorting ----
    def sorted_by_gpa(self, descending: bool = True) -> List[Student]:
        return sorted(self.students.values(), key=lambda s: s.gpa(), reverse=descending)

    def sorted_by_name(self) -> List[Student]:
        return sorted(self.students.values(), key=lambda s: s.name.lower())

    def sorted_by_roll_number(self) -> List[Student]:
        return sorted(self.students.values(), key=lambda s: s.roll_number)

    # ---- class-wide statistics ----
    def class_statistics(self) -> Dict:
        if not self.students:
            return {"count": 0}
        averages = [s.average_marks() for s in self.students.values()]
        passing = sum(1 for s in self.students.values() if s.is_passing())
        return {
            "count": len(self.students),
            "class_average": round(sum(averages) / len(averages), 2),
            "highest": max(averages),
            "lowest": min(averages),
            "passing_count": passing,
            "failing_count": len(self.students) - passing,
        }

    def list_all(self) -> List[Student]:
        return list(self.students.values())

    # ---- persistence ----
    def save(self, path: str = DATA_FILE):
        data = {"students": [s.to_dict() for s in self.students.values()]}
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path: str = DATA_FILE) -> "StudentManager":
        manager = cls()
        if not os.path.exists(path):
            return manager
        with open(path, "r") as f:
            data = json.load(f)
        for d in data.get("students", []):
            student = Student.from_dict(d)
            manager.students[student.roll_number] = student
        return manager


# ----------------------------------------------------------------------
# Command-line interface
# ----------------------------------------------------------------------
def prompt_int(msg: str) -> int:
    while True:
        try:
            return int(input(msg))
        except ValueError:
            print("  Please enter a valid whole number.")


def prompt_float(msg: str) -> float:
    while True:
        try:
            return float(input(msg))
        except ValueError:
            print("  Please enter a valid number.")


def main():
    manager = StudentManager.load()
    print("=== Student Data Management System ===")

    menu = """
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
"""
    while True:
        print(menu)
        choice = input("Choose an option: ").strip()
        try:
            if choice == "1":
                roll = input("Roll number: ").strip()
                name = input("Name: ").strip()
                age = prompt_int("Age: ")
                email = input("Email (optional): ").strip()
                manager.add_student(roll, name, age, email)
                print("  Student added.")

            elif choice == "2":
                roll = input("Roll number to update: ").strip()
                name = input("New name (blank to keep): ").strip() or None
                age_raw = input("New age (blank to keep): ").strip()
                age = int(age_raw) if age_raw else None
                email = input("New email (blank to keep): ").strip() or None
                manager.update_student(roll, name, age, email)
                print("  Student updated.")

            elif choice == "3":
                roll = input("Roll number to remove: ").strip()
                manager.remove_student(roll)
                print("  Student removed.")

            elif choice == "4":
                roll = input("Roll number: ").strip()
                course = input("Course name: ").strip()
                marks = prompt_float("Marks (0-100): ")
                manager.get_student(roll).add_or_update_grade(course, marks)
                print("  Grade recorded.")

            elif choice == "5":
                roll = input("Roll number: ").strip()
                print()
                print(manager.get_student(roll).report_card())

            elif choice == "6":
                kw = input("Name contains: ").strip()
                results = manager.search_by_name(kw)
                for s in results:
                    print("  " + str(s))
                if not results:
                    print("  No matches.")

            elif choice == "7":
                lo = prompt_float("Min %: ")
                hi = prompt_float("Max %: ")
                for s in manager.filter_by_grade_range(lo, hi):
                    print("  " + str(s))

            elif choice == "8":
                n = prompt_int("How many top performers? ")
                for s in manager.top_performers(n):
                    print("  " + str(s))

            elif choice == "9":
                for s in manager.failing_students():
                    print("  " + str(s))

            elif choice == "10":
                sort_choice = input("Sort by (gpa/name/roll): ").strip().lower() or "roll"
                if sort_choice == "gpa":
                    students = manager.sorted_by_gpa()
                elif sort_choice == "name":
                    students = manager.sorted_by_name()
                else:
                    students = manager.sorted_by_roll_number()
                for s in students:
                    print("  " + str(s))

            elif choice == "11":
                stats = manager.class_statistics()
                if stats["count"] == 0:
                    print("  No students yet.")
                else:
                    print(f"  Total students : {stats['count']}")
                    print(f"  Class average  : {stats['class_average']}%")
                    print(f"  Highest average: {stats['highest']}%")
                    print(f"  Lowest average : {stats['lowest']}%")
                    print(f"  Passing        : {stats['passing_count']}")
                    print(f"  Failing        : {stats['failing_count']}")

            elif choice == "0":
                manager.save()
                print("  Data saved. Goodbye!")
                break

            else:
                print("  Invalid option, try again.")

        except StudentSystemError as e:
            print(f"  Error: {e}")
        except Exception as e:
            print(f"  Unexpected error: {e}")


if __name__ == "__main__":
    main()

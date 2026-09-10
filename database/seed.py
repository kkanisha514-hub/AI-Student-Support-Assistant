"""
Seeds the database with DEMO data so the application is usable out of the box.

IMPORTANT: This is clearly demo/sample data for a fictional college
("Greenfield Institute of Technology"). Replace with your real
college data before using this in production.
"""
from datetime import date
from database.database import SessionLocal, init_db
from database.models import Department, Subject, Notice, ExamSchedule, AcademicCalendar
from logging_config import get_logger

logger = get_logger(__name__)


def seed_departments(db):
    if db.query(Department).count() > 0:
        return
    departments = [
        Department(code="CSE", name="Computer Science and Engineering"),
        Department(code="ECE", name="Electronics and Communication Engineering"),
        Department(code="MECH", name="Mechanical Engineering"),
        Department(code="CIVIL", name="Civil Engineering"),
    ]
    db.add_all(departments)
    db.commit()
    logger.info("Seeded departments (demo data).")


def seed_subjects(db):
    if db.query(Subject).count() > 0:
        return
    cse = db.query(Department).filter_by(code="CSE").first()
    subjects = [
        Subject(department_id=cse.id, name="Data Structures", code="CS201", year=2, semester=3),
        Subject(department_id=cse.id, name="Database Management Systems", code="CS301", year=3, semester=5),
        Subject(department_id=cse.id, name="Operating Systems", code="CS302", year=3, semester=5),
        Subject(department_id=cse.id, name="Computer Networks", code="CS303", year=3, semester=5),
        Subject(department_id=cse.id, name="Machine Learning", code="CS401", year=3, semester=6),
    ]
    db.add_all(subjects)
    db.commit()
    logger.info("Seeded subjects (demo data).")


def seed_notices(db):
    if db.query(Notice).count() > 0:
        return
    notices = [
        Notice(
            title="Mid-Semester Exam Timetable Released (DEMO)",
            content="The mid-semester examination timetable for all departments "
                    "has been published on the notice board. Students must carry "
                    "their ID cards to the exam hall.",
            department_code=None,
            posted_on=date(2026, 8, 20),
        ),
        Notice(
            title="CSE Workshop on AI Tools (DEMO)",
            content="The CSE department is organizing a workshop on practical AI "
                    "tools for 3rd year students on the last Friday of this month.",
            department_code="CSE",
            posted_on=date(2026, 8, 25),
        ),
    ]
    db.add_all(notices)
    db.commit()
    logger.info("Seeded notices (demo data).")


def seed_exam_schedule(db):
    if db.query(ExamSchedule).count() > 0:
        return
    exams = [
        ExamSchedule(department_code="CSE", year=3, semester=5, subject_name="Database Management Systems",
                     exam_date=date(2026, 11, 10), exam_time="10:00 AM - 1:00 PM", room="Block A - 204"),
        ExamSchedule(department_code="CSE", year=3, semester=5, subject_name="Operating Systems",
                     exam_date=date(2026, 11, 12), exam_time="10:00 AM - 1:00 PM", room="Block A - 204"),
        ExamSchedule(department_code="CSE", year=3, semester=5, subject_name="Computer Networks",
                     exam_date=date(2026, 11, 14), exam_time="10:00 AM - 1:00 PM", room="Block A - 205"),
    ]
    db.add_all(exams)
    db.commit()
    logger.info("Seeded exam schedule (demo data).")


def seed_academic_calendar(db):
    if db.query(AcademicCalendar).count() > 0:
        return
    events = [
        AcademicCalendar(event_name="Odd Semester Begins", start_date=date(2026, 8, 1),
                          description="Classes commence for the odd semester (DEMO)."),
        AcademicCalendar(event_name="Mid-Semester Exams", start_date=date(2026, 10, 5),
                          end_date=date(2026, 10, 12), description="Mid-semester examinations (DEMO)."),
        AcademicCalendar(event_name="End-Semester Exams", start_date=date(2026, 11, 10),
                          end_date=date(2026, 11, 20), description="End-semester examinations (DEMO)."),
        AcademicCalendar(event_name="Winter Break", start_date=date(2026, 12, 20),
                          end_date=date(2027, 1, 2), description="Winter vacation (DEMO)."),
    ]
    db.add_all(events)
    db.commit()
    logger.info("Seeded academic calendar (demo data).")


def run_seed():
    init_db()
    db = SessionLocal()
    try:
        seed_departments(db)
        seed_subjects(db)
        seed_notices(db)
        seed_exam_schedule(db)
        seed_academic_calendar(db)
    finally:
        db.close()
    logger.info("Seeding complete.")


if __name__ == "__main__":
    run_seed()

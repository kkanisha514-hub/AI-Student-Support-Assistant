"""
Real LangChain tools backed by SQLite queries (via SQLAlchemy).
These are bound to the LLM and invoked automatically by the LangGraph agent
through a ToolNode.
"""
from typing import Optional
from langchain_core.tools import tool

from database.database import get_db_context
from database.models import Notice, ExamSchedule, Subject, Department, AcademicCalendar
from logging_config import get_logger

logger = get_logger(__name__)


@tool
def search_notice(keyword: str) -> str:
    """Search college notices by a keyword found in the title or content.
    Use this when the student asks about announcements, events, or notices."""
    with get_db_context() as db:
        results = (
            db.query(Notice)
            .filter(Notice.title.ilike(f"%{keyword}%") | Notice.content.ilike(f"%{keyword}%"))
            .order_by(Notice.posted_on.desc())
            .limit(5)
            .all()
        )
        if not results:
            return "NO_RESULTS"
        lines = []
        for n in results:
            lines.append(f"- [{n.posted_on}] {n.title}: {n.content}")
        return "\n".join(lines)


@tool
def get_exam_schedule(department_code: str, year: Optional[int] = None, semester: Optional[int] = None) -> str:
    """Get the examination schedule for a department, optionally filtered by year and semester.
    department_code examples: CSE, ECE, MECH, CIVIL."""
    with get_db_context() as db:
        query = db.query(ExamSchedule).filter(ExamSchedule.department_code == department_code.upper())
        if year:
            query = query.filter(ExamSchedule.year == year)
        if semester:
            query = query.filter(ExamSchedule.semester == semester)
        results = query.order_by(ExamSchedule.exam_date).all()
        if not results:
            return "NO_RESULTS"
        lines = []
        for e in results:
            lines.append(
                f"- {e.subject_name}: {e.exam_date} {e.exam_time or ''} (Room: {e.room or 'TBA'})"
            )
        return "\n".join(lines)


@tool
def get_syllabus(department_code: str, year: int, semester: Optional[int] = None) -> str:
    """Get the list of subjects (syllabus overview) for a department and year, optionally filtered by semester."""
    with get_db_context() as db:
        dept = db.query(Department).filter(Department.code == department_code.upper()).first()
        if not dept:
            return "NO_RESULTS"
        query = db.query(Subject).filter(Subject.department_id == dept.id, Subject.year == year)
        if semester:
            query = query.filter(Subject.semester == semester)
        results = query.all()
        if not results:
            return "NO_RESULTS"
        lines = [f"- {s.name} ({s.code or 'N/A'}) - Semester {s.semester}" for s in results]
        return "\n".join(lines)


@tool
def get_department_information(department_code: str) -> str:
    """Get basic information about a department by its code (e.g. CSE, ECE, MECH, CIVIL)."""
    with get_db_context() as db:
        dept = db.query(Department).filter(Department.code == department_code.upper()).first()
        if not dept:
            return "NO_RESULTS"
        subject_count = db.query(Subject).filter(Subject.department_id == dept.id).count()
        return f"Department: {dept.name} ({dept.code}). Subjects on record: {subject_count}."


@tool
def get_academic_calendar(keyword: Optional[str] = None) -> str:
    """Get academic calendar events, optionally filtered by a keyword (e.g. 'exam', 'break', 'semester')."""
    with get_db_context() as db:
        query = db.query(AcademicCalendar)
        if keyword:
            query = query.filter(AcademicCalendar.event_name.ilike(f"%{keyword}%"))
        results = query.order_by(AcademicCalendar.start_date).all()
        if not results:
            return "NO_RESULTS"
        lines = []
        for e in results:
            date_range = f"{e.start_date}" + (f" to {e.end_date}" if e.end_date else "")
            lines.append(f"- {e.event_name}: {date_range}. {e.description or ''}")
        return "\n".join(lines)


ALL_TOOLS = [
    search_notice,
    get_exam_schedule,
    get_syllabus,
    get_department_information,
    get_academic_calendar,
]

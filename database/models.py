"""
SQLAlchemy ORM models for the AI Student Support Assistant.

Tables:
- students
- chat_sessions
- chat_messages
- notices
- exam_schedule
- departments
- subjects
- academic_calendar
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Date
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)   # e.g. "CSE"
    name = Column(String(200), nullable=False)                # e.g. "Computer Science and Engineering"

    subjects = relationship("Subject", back_populates="department")
    students = relationship("Student", back_populates="department")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    name = Column(String(200), nullable=False)
    code = Column(String(30), nullable=True)
    year = Column(Integer, nullable=False)       # 1..4
    semester = Column(Integer, nullable=False)   # 1..8

    department = relationship("Department", back_populates="subjects")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    year = Column(Integer, nullable=True)
    semester = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    department = relationship("Department", back_populates="students")
    sessions = relationship("ChatSession", back_populates="student")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(64), primary_key=True, index=True)  # uuid string
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    title = Column(String(200), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="sessions")
    messages = relationship(
        "ChatMessage", back_populates="session", order_by="ChatMessage.created_at"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)   # "user" | "assistant"
    content = Column(Text, nullable=False)
    sources = Column(Text, nullable=True)        # JSON string of source docs
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")


class Notice(Base):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    department_code = Column(String(20), nullable=True)  # null = all departments
    posted_on = Column(Date, default=datetime.utcnow)


class ExamSchedule(Base):
    __tablename__ = "exam_schedule"

    id = Column(Integer, primary_key=True, index=True)
    department_code = Column(String(20), nullable=False)
    year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    subject_name = Column(String(200), nullable=False)
    exam_date = Column(Date, nullable=False)
    exam_time = Column(String(50), nullable=True)
    room = Column(String(50), nullable=True)


class AcademicCalendar(Base):
    __tablename__ = "academic_calendar"

    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(300), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)

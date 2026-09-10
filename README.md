AI Student Support Assistant

An AI-powered academic support system for college students.

The system allows students to ask questions about college regulations, exams, syllabus, notices, departments, and other academic information using natural language.

Features
AI-based student support
RAG for searching college documents
Conversational memory
SQLite database
LangGraph agent workflow
Local Gemma LLM using Ollama
ChromaDB for document search
PDF and TXT document support
Source-based answers
Local and privacy-friendly
No paid AI API required
How It Works
Student
   ↓
Web Application
   ↓
FastAPI
   ↓
LangGraph
   ↓
RAG / SQLite / Memory
   ↓
Gemma + Ollama
   ↓
Answer

RAG

RAG is used to find information from college documents.

Document
   ↓
Text Extraction
   ↓
Chunking
   ↓
Embeddings
   ↓
ChromaDB
   ↓
Relevant Information
   ↓
Gemma
   ↓
Answer


RAG can be used for:

College regulations
Examination rules
Syllabus
Academic calendar
FAQs
Notices
Department information

Adding a new document does not retrain Gemma. The document is simply added to the ChromaDB knowledge base.

Database

SQLite is used for structured information and application data.

It stores:

Student information
Chat sessions
Chat messages
Notices
Exam schedules
Subjects
Departments
Academic calendar
Conversational Memory

The assistant can remember useful information from previous conversations.

For example:

Student:
I am a third-year CSE student.

Assistant:
Okay, I will remember your academic context.

Student:
What subjects should I prepare?

Assistant:
Here are the relevant subjects...


RAG and Memory are different:

RAG → Finds information from college documents.
Memory → Stores and retrieves conversation information.
Technology Stack
Python
FastAPI
LangChain
LangGraph
Gemma
Ollama
ChromaDB
Sentence Transformers
SQLite
SQLAlchemy
Pydantic
HTML
CSS
JavaScript
Pytest
Project Structure
ai_student_support/
│
├── agent/
├── llm/
├── rag/
├── database/
├── memory/
├── api/
├── frontend/
├── data/
├── tests/
│
├── app.py
├── requirements.txt
├── .env.example
└── README.md

Installation
1. Install Ollama

Install Ollama and download Gemma:

ollama pull gemma2:2b


Check the model:

ollama list

2. Create Virtual Environment
python -m venv venv


Windows:

venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Configure Environment
copy .env.example .env

5. Run the Application
python app.py


Open:

http://localhost:8000

API Documentation

Swagger UI:

http://localhost:8000/docs


Main API:

POST /api/chat
POST /api/students
GET  /api/students/{id}
GET  /api/chat/history/{session_id}
GET  /api/notices
GET  /api/exam-schedule
GET  /api/subjects
GET  /api/health

Testing

Run:

pytest tests/ -v

Admin Panel

Admin page:

http://localhost:8000/static/admin.html


Administrators can upload PDF and TXT documents and update the knowledge base.

Example Questions
What is the attendance requirement?

When is the CSE semester examination?

What subjects are included in third-year CSE?

Are there any new notices?

When does the next semester begin?

What departments are available?

Privacy

The system is designed to run locally.

Student
   ↓
FastAPI
   ├── SQLite
   ├── ChromaDB
   └── Ollama
          ↓
        Gemma


No external cloud LLM or paid AI API is required.

Limitations
Answer quality depends on the uploaded documents.
Small local models may have limited reasoning ability.
Outdated documents may produce outdated answers.
AI responses should be verified against official college information.
Future Improvements
Authentication
Student accounts
Mobile application
Multi-language support
Voice support
DOCX support
Admin dashboard
Notifications
Hybrid search
Streaming responses
Project Status

Status: Active Development

Type: AI / Generative AI / RAG

Deployment: Local / Self-Hosted

Use Case: College Student Support

License

This project is developed for educational, academic, and research purposes.

Vision

To make college academic information easy to access through a reliable, intelligent, and privacy-friendly AI assistant.

Ask questions naturally. Get trusted answers.


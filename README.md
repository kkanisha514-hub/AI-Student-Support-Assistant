

 # AI Student Support Assistant

 ### An Intelligent, Local-First Academic Support Platform for College Students

 The **AI Student Support Assistant** is an intelligent academic information and student-support system that enables students to interact with college knowledge through a natural-language conversational interface.

 The platform combines **Retrieval-Augmented Generation (RAG)**, **agentic workflows**, **persistent conversational memory**, **structured database tools**, and a **locally hosted Large Language Model (LLM)** to provide reliable and context-aware responses.

 The system is designed with a **local-first and privacy-oriented architecture**, eliminating the need for paid cloud AI APIs, external LLM providers, or API keys.

---

 ## Project Overview

 Students frequently need to search across multiple sources to obtain academic and administrative information, including:

 - College regulations
- Examination rules
- Academic calendars
- Syllabi
- Department information
- Notices
- FAQs
- Examination schedules
- Subject information

 The AI Student Support Assistant consolidates these information sources into a single conversational platform.

 Instead of manually searching documents or database records, students can ask questions using natural language.

 ### Example

```
Student:
What is the attendance requirement?

AI Assistant:
According to the college regulations, students must satisfy
the prescribed attendance requirements to be eligible for
the semester examination.

Source:
College Regulations — Page 1
```

---

 # Key Objectives

 The primary objectives of this project are to:

 1. Provide a centralized AI-based student support system.
2. Enable natural-language access to college information.
3. Retrieve answers from trusted institutional documents.
4. Integrate structured college data with an AI agent.
5. Maintain conversational context across multiple interactions.
6. Reduce hallucinated or unsupported responses.
7. Keep student data and AI processing within the local environment.
8. Provide an extensible architecture suitable for real-world deployment.

---

 # Core Features

 ## 1\. Retrieval-Augmented Generation

 The system uses a RAG pipeline to retrieve relevant information from institutional documents before generating an answer.

 Supported knowledge sources include:

 - PDF documents
- TXT documents
- College regulations
- Examination rules
- Syllabus
- Academic calendars
- FAQs
- Notices
- Department information
- Institutional guidelines

 ### RAG Pipeline

```
Document
    │
    ▼
Text Extraction
    │
    ▼
Document Chunking
    │
    ▼
Embedding Generation
    │
    ▼
ChromaDB
    │
    ▼
Semantic Retrieval
    │
    ▼
Relevant Context
    │
    ▼
Local LLM
    │
    ▼
Grounded Response
```

 The system can retain source and page metadata so that retrieved information can be associated with its original document.

---

 # 2\. Agentic Question Routing

 The application uses **LangGraph** to orchestrate the AI workflow.

 Instead of sending every question directly to the language model, the system determines the most appropriate processing path.

```
                         User Question
                              │
                              ▼
                     ┌─────────────────┐
                     │  LangGraph Agent│
                     └────────┬────────┘
                              │
                    Intent Classification
                              │
          ┌───────────┬───────┼────────┬───────────┐
          │           │       │        │           │
          ▼           ▼       ▼        ▼           ▼
         RAG         Tool   Memory   Direct     Combined
          │           │       │        │           │
          ▼           ▼       ▼        ▼           ▼
      ChromaDB      SQLite  Profile   LLM      Multi-step
          │           │       │        │
          └───────────┴───────┴────────┘
                              │
                              ▼
                     Response Generation
                              │
                              ▼
                       Student Response
```

 This architecture allows the assistant to select the appropriate information source based on the question.

---

 # 3\. Structured Database Tools

 The assistant integrates structured college data through LangChain tools.

 ### Available Tools

 | Tool | Function |
| --- | --- |
| `search_notice` | Searches institutional notices |
| `get_exam_schedule` | Retrieves examination schedules |
| `get_syllabus` | Retrieves syllabus information |
| `get_department_information` | Retrieves department details |
| `get_academic_calendar` | Retrieves academic events |

 Structured queries such as examination schedules are handled directly through SQLite instead of relying solely on semantic retrieval.

 This improves reliability for exact, structured information.

---

 # 4\. Persistent Conversational Memory

 The system maintains student context across conversations.

 For example:

```
Student:
I am a Computer Science student in third year.

Assistant:
Understood. I will use your CSE and third-year
context when answering relevant questions.

Student:
What subjects should I prepare?

Assistant:
Based on your academic context, the relevant subjects
include...
```

 The system can maintain:

 - Student name
- Department
- Academic year
- Semester
- Conversation history
- Session information

 Persistent data is stored using SQLite.

---

 # 5\. Hallucination Control

 Reliability is a major design consideration.

 The assistant is instructed to generate answers based on retrieved knowledge or verified structured data.

 If relevant information cannot be found, the system should explicitly indicate that the information is unavailable.

 Example:

```
I could not find sufficient information about this
topic in the available college knowledge base.
Please verify the information with the college
administration or official documentation.
```

 This approach reduces the risk of presenting unsupported information as fact.

---

 # 6\. Local AI Processing

 The project uses **Gemma through Ollama** for local language-model inference.

```
Student
   │
   ▼
FastAPI
   │
   ▼
LangGraph
   │
   ▼
RAG / SQLite / Memory
   │
   ▼
Gemma
   │
   ▼
Response
```

 No external cloud LLM API is required.

 ### Benefits

 - No paid API subscription
- No API key required
- Local inference
- Improved data privacy
- Works without sending student conversations to external LLM providers
- Suitable for development and academic demonstrations

---

 # Technology Stack

 | Layer | Technology |
| --- | --- |
| Programming Language | Python 3.11+ |
| Agent Framework | LangGraph |
| LLM Framework | LangChain |
| Language Model | Gemma |
| LLM Runtime | Ollama |
| RAG | LangChain |
| Vector Database | ChromaDB |
| Embeddings | Sentence Transformers |
| Relational Database | SQLite |
| ORM | SQLAlchemy |
| Backend | FastAPI |
| Validation | Pydantic |
| Frontend | HTML, CSS, JavaScript |
| Testing | Pytest |

---

 # System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                │
│                  Student / Faculty                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    WEB FRONTEND                             │
│                   HTML / CSS / JS                           │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST / JSON
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     FASTAPI BACKEND                         │
│                      api/routes.py                          │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    LANGGRAPH AGENT                          │
│                      agent/graph.py                         │
│                                                             │
│  Context Loading → Intent Classification → Processing       │
└──────────────┬──────────────────┬─────────────────┬─────────┘
               │                  │                 │
               ▼                  ▼                 ▼
        ┌─────────────┐    ┌─────────────┐   ┌─────────────┐
        │     RAG     │    │   DATABASE  │   │   MEMORY    │
        │             │    │    TOOLS    │   │             │
        └──────┬──────┘    └──────┬──────┘   └──────┬──────┘
               │                  │                 │
               ▼                  ▼                 ▼
          ChromaDB              SQLite           SQLite
               │                  │                 │
               └──────────────────┼─────────────────┘
                                  │
                                  ▼
                       ┌────────────────────┐
                       │   GEMMA / OLLAMA   │
                       │     Local LLM      │
                       └─────────┬──────────┘
                                 │
                                 ▼
                       ┌────────────────────┐
                       │   FINAL RESPONSE   │
                       │  + SOURCES         │
                       └────────────────────┘
```

---

 # Project Structure

```
ai_student_support/
│
├── agent/
│   ├── __init__.py
│   ├── state.py
│   ├── tools.py
│   ├── prompts.py
│   └── graph.py
│
├── llm/
│   ├── __init__.py
│   └── gemma.py
│
├── rag/
│   ├── __init__.py
│   ├── loader.py
│   ├── embeddings.py
│   ├── ingest.py
│   └── retriever.py
│
├── database/
│   ├── __init__.py
│   ├── models.py
│   ├── database.py
│   └── seed.py
│
├── memory/
│   ├── __init__.py
│   └── memory.py
│
├── api/
│   ├── __init__.py
│   ├── routes.py
│   └── schemas.py
│
├── frontend/
│   ├── index.html
│   ├── admin.html
│   ├── style.css
│   └── script.js
│
├── data/
│   └── documents/
│
├── tests/
│   ├── test_database.py
│   ├── test_memory.py
│   ├── test_tools.py
│   ├── test_rag.py
│   └── test_api.py
│
├── app.py
├── requirements.txt
├── .env.example
└── README.md
```

---

 # Database Design

 The application uses SQLite for structured information and persistent application data.

 ### Database Tables

 | Table | Purpose |
| --- | --- |
| `students` | Student profiles |
| `chat_sessions` | Conversation sessions |
| `chat_messages` | Persistent chat history |
| `notices` | College notices |
| `exam_schedule` | Examination schedules |
| `departments` | Department information |
| `subjects` | Subject and syllabus information |
| `academic_calendar` | Academic events |

 ### Relationship Overview

```
                    departments
                         │
             ┌───────────┴───────────┐
             │                       │
             ▼                       ▼
        students                  subjects
             │
             ▼
       chat_sessions
             │
             ▼
       chat_messages

exam_schedule ───── department_code

academic_calendar ───── academic events

notices ───── department_code
```

---

 # Knowledge Base Management

 The system supports dynamic document ingestion.

 Administrators can upload:

```
PDF
TXT
```

 documents through the administration interface.

 ### Document Processing

```
Upload
  │
  ▼
Document Validation
  │
  ▼
Text Extraction
  │
  ▼
Metadata Extraction
  │
  ▼
Chunking
  │
  ▼
Embedding Generation
  │
  ▼
ChromaDB Indexing
  │
  ▼
Available for Retrieval
```

 New documents can therefore become available to the assistant without retraining the language model.

---

 # RAG vs Structured Database

 The project intentionally uses both RAG and relational database tools.

 ### RAG is used for:

 - Regulations
- Policies
- Handbooks
- FAQs
- College documents
- PDF content
- General institutional information

 ### SQLite tools are used for:

 - Examination schedules
- Subjects
- Departments
- Notices
- Academic calendar
- Student profiles

 This separation allows the system to use the most appropriate retrieval method for each type of information.

---

 # Installation

 ## Prerequisites

 Ensure the following are installed:

 - Python 3.11 or later
- Ollama
- Git
- Visual Studio Code

---

 ## Step 1 — Install Ollama

 Install Ollama and download the required Gemma model.

```
ollama pull gemma2:2b
```

 Verify the model:

```
ollama list
```

 If Ollama is not running:

```
ollama serve
```

---

 ## Step 2 — Open the Project

```
cd ai_student_support
```

---

 ## Step 3 — Create a Virtual Environment

```
python -m venv venv
```

 Activate it:

```
venv\Scripts\activate
```

---

 ## Step 4 — Install Dependencies

```
pip install -r requirements.txt
```

---

 ## Step 5 — Configure Environment

 Create the environment file:

```
copy .env.example .env
```

 Update the configuration only if your Ollama installation uses a different model or port.

---

 # Running the Application

 Start the backend:

```
python app.py
```

 The application will initialize:

```
✓ SQLite database
✓ Database tables
✓ Demo data
✓ Knowledge-base documents
✓ ChromaDB index
✓ FastAPI server
```

 Open the application:

```
http://localhost:8000
```

---

 # API Documentation

 FastAPI provides interactive API documentation.

 ### Swagger UI

```
http://localhost:8000/docs
```

 ### Available Endpoints

 | Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/chat` | Process a student question |
| POST | `/api/students` | Create a student profile |
| GET | `/api/students/{id}` | Retrieve student information |
| GET | `/api/chat/history/{session_id}` | Retrieve conversation history |
| GET | `/api/notices` | Retrieve notices |
| GET | `/api/exam-schedule` | Retrieve examination schedules |
| GET | `/api/subjects` | Retrieve subjects |
| GET | `/api/health` | Application health check |

---

 # Example API Request

```
{
  "message": "What is the attendance requirement?",
  "session_id": null,
  "student_id": null
}
```

 ### Example Response

```
{
  "answer": "According to the college regulations...",
  "sources": [
    {
      "source": "College Regulations",
      "page": 1
    }
  ]
}
```

---

 # Testing

 Install Pytest:

```
pip install pytest
```

 Run the test suite:

```
pytest tests/ -v
```

 ### Test Modules

```
test_database.py
    Database and ORM tests

test_memory.py
    Student profile and memory tests

test_tools.py
    Database tool tests

test_rag.py
    Document retrieval tests

test_api.py
    REST API tests
```

 The complete chat workflow requires Ollama and the configured Gemma model to be running locally.

---

 # Example Use Cases

 ## Academic Assistance

```
What are the attendance requirements?
```

 ## Examination Information

```
When is the CSE semester examination?
```

 ## Syllabus Assistance

```
What subjects are included in the third-year CSE syllabus?
```

 ## College Information

```
What departments are available in the college?
```

 ## Administrative Support

```
How can I apply for a bonafide certificate?
```

 ## Notices

```
Are there any new notices for CSE students?
```

 ## Academic Calendar

```
When does the next semester begin?
```

---

 # Administrative Document Upload

 The administrator interface is available at:

```
http://localhost:8000/static/admin.html
```

 Administrators can:

 - Upload documents
- View indexed documents
- Remove outdated documents
- Trigger knowledge-base updates

 ### Supported Formats

```
.pdf
.txt
```

 For TXT documents, page-level metadata can be supplied using:

```
[SOURCE: College Regulations, PAGE: 1]

Attendance requirements...

[SOURCE: College Regulations, PAGE: 2]

Examination eligibility...
```

---

 # Important RAG Concept

 ### Uploading a document does not retrain Gemma.

 The process is:

```
New Document
     │
     ▼
Embedding
     │
     ▼
ChromaDB
     │
     ▼
Retrieved when relevant
     │
     ▼
Gemma generates the answer
```

 The LLM itself remains unchanged.

 This makes knowledge-base updates fast and computationally inexpensive.

---

 # Security Considerations

 The current project is intended primarily for **local development, academic demonstration, and controlled environments**.

 The administration endpoints should not be exposed publicly without authentication.

 Before production deployment, consider implementing:

 - Authentication
- Authorization
- Role-based access control
- Secure file validation
- File-size restrictions
- Rate limiting
- HTTPS
- Database access controls
- Audit logging
- Session isolation
- Secure environment-variable management

---

 # Limitations

 Although the system is designed to provide grounded responses, it has several limitations.

 - Local small language models may produce less accurate reasoning than larger models.
- Ambiguous questions may result in incorrect intent classification.
- The quality of RAG responses depends on the quality of the uploaded documents.
- Outdated documents may produce outdated answers.
- Current institutional information should always be verified against official sources.
- The current administration interface does not include full authentication.
- The system should not replace official academic or administrative decisions.

---

 # Future Development

 The architecture is designed to support future improvements.

 ### Planned Enhancements

 - 🔐 Authentication and authorization
- 👤 Student-specific accounts
- 📱 Mobile application
- 🌐 Multi-language support
- 🎙️ Voice interaction
- 📄 DOCX document support
- 📊 Administrative analytics
- 🔔 Automated notice notifications
- 📅 Calendar integration
- ⚡ Streaming responses
- 🧠 Improved intent classification
- 🔍 Hybrid keyword + semantic search
- 🧑‍🏫 Faculty and administrator dashboards
- 📈 Student-support analytics
- 🔗 Multi-tool agent workflows

---

 # Project Advantages

 | Capability | Traditional System | AI Student Assistant |
| --- | --- | --- |
| Natural-language interaction | ❌ | ✅ |
| Document-based question answering | Limited | ✅ |
| Semantic search | ❌ | ✅ |
| Database integration | Limited | ✅ |
| Conversational memory | ❌ | ✅ |
| Source-aware responses | Limited | ✅ |
| Local LLM | ❌ | ✅ |
| No paid AI API | ❌ | ✅ |
| Dynamic knowledge-base updates | Limited | ✅ |

---

 # Privacy & Data Architecture

 The system follows a local-first architecture.

```
Student
   │
   ▼
Local Web Application
   │
   ▼
FastAPI
   │
   ├──────────────► SQLite
   │
   ├──────────────► ChromaDB
   │
   └──────────────► Ollama
                         │
                         ▼
                       Gemma
```

 Student conversations, database information, vector data, and LLM inference can remain within the local environment.

 No external cloud LLM service is required for the core system.

---

 # Project Significance

 This project demonstrates the practical integration of modern AI technologies into an educational information system.

 It combines:

```
Artificial Intelligence
        +
Natural Language Processing
        +
Retrieval-Augmented Generation
        +
Agentic AI
        +
Vector Search
        +
Relational Databases
        +
Persistent Memory
        +
REST APIs
        +
Web Technologies
```

 The result is a modular AI platform that can be adapted for colleges, universities, departments, training institutes, and other educational organizations.

---

 # Conclusion

 The **AI Student Support Assistant** provides a practical approach to building a reliable, privacy-oriented academic support system using locally hosted AI.

 By combining **RAG for document knowledge**, **SQLite for structured information**, **LangGraph for intelligent workflow orchestration**, **persistent memory for personalization**, and **Gemma/Ollama for local language generation**, the system provides a flexible foundation for an institutional AI assistant.

 > **Ask questions naturally. Retrieve trusted information. Get contextual answers.**

---

 # Project Status

 **Status:** Active Development

 **Project Type:** AI / Machine Learning / Generative AI / RAG

 **Deployment Model:** Local / Self-Hosted

 **Primary Use Case:** College Student Support

---

 # License

 This project is developed for educational, academic, and research purposes.

---

 ## Developed With

 **Python • LangChain • LangGraph • Gemma • Ollama • ChromaDB • SQLite • FastAPI • SQLAlchemy • HTML • CSS • JavaScript • Pytest**

---

 ### ⭐ Project Vision

 > **To make academic information accessible through a reliable, intelligent, and privacy-friendly conversational interface.**
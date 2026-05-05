# SJBIT Q&A API

A FastAPI-based intelligent Q&A system for SJBIT (SJB Institute of Technology), Bangalore.
The system answers SJBIT-related questions using a local database and Groq AI as fallback.

## How It Works
User Question
↓
Check SQLite Database
↓
Found? → Return answer (source: database)
↓
Not Found? → Ask Groq AI with SJBIT-only prompt
↓
Return answer (source: groq_ai)

## Features

- Answers only SJBIT-related questions
- SQLite database for fast, accurate answers
- Groq AI (LLaMA 3.3) as fallback for unknown questions
- Blocks non-SJBIT questions using prompt engineering
- REST API built with FastAPI
- API key secured using environment variables

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | API framework |
| SQLite | Local knowledge base |
| Groq API | AI fallback (LLaMA 3.3) |
| Python-dotenv | Secure API key management |
| Uvicorn | ASGI server |

## Project Structure
sjbit-qa-api/
├── main.py          # Main API code
├── sjbit.db         # SQLite database
├── .env             # API key (not pushed)
├── .gitignore       # Ignores .env and venv
└── README.md        # Project documentation

## Setup and Installation

### 1. Clone the repository
```bash
git clone https://github.com/91647Mamatha/sjbit-qa-api.git
cd sjbit-qa-api
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install fastapi uvicorn openai python-dotenv
```

### 4. Create .env file
```bash
touch .env
```
Add your Groq API key inside .env:
GROQ_API_KEY=your_groq_api_key_here

### 5. Run the API
```bash
uvicorn main:app --reload
```

API runs at: http://localhost:8000

## API Endpoints

### Health Check
GET /
Response:
```json
{
    "status": "SJBIT Q&A API is running"
}
```

### Ask a Question
POST /ask
Request body:
```json
{
    "question": "What courses does SJBIT offer?"
}
```
Response (from database):
```json
{
    "question": "What courses does SJBIT offer?",
    "answer": "SJBIT offers B.E. in CSE, ECE, EEE, ME, CE, ISE, AI&ML...",
    "source": "database"
}
```
Response (from Groq AI):
```json
{
    "question": "What is the ranking of SJBIT?",
    "answer": "SJBIT is ranked...",
    "source": "groq_ai"
}
```

## Testing in Postman
Method  : POST
URL     : http://localhost:8000/ask
Headers : Content-Type: application/json
Body    : raw → JSON

## Example Questions to Test

| Question | Source |
|---|---|
| What courses does SJBIT offer? | database |
| Where is SJBIT located? | database |
| What is the ranking of SJBIT? | groq_ai |
| Who is the principal of SJBIT? | groq_ai |
| What is the capital of India? | blocked by AI |

## Security

- API key stored in .env file
- .env added to .gitignore
- API key never hardcoded in source code


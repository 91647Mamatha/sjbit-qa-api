from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()

app = FastAPI(title="SJBIT Q&A API")

# ── GROQ CLIENT ────────────────────────────────────────────────
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ── DATABASE SETUP ─────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("sjbit.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    """)

    sjbit_data = [
    ("What is SJBIT?",
     "SJBIT (SJB Institute of Technology) is an engineering college in Bangalore, Karnataka, India. Affiliated to VTU, established in 2008 by SJB Trust."),

    ("Where is SJBIT located?",
     "SJBIT is located at BGS Health and Education City, Uttarahalli-Kengeri Road, Bangalore - 560060."),

    ("What courses does SJBIT offer?",
     "SJBIT offers B.E. in CSE, ECE, EEE, ME, CE, ISE, AI&ML. Also offers MCA, MBA, and M.Tech."),

    ("What is the contact information for SJBIT?",
     "Phone: 080-28437973, Email: info@sjbit.edu.in, Website: www.sjbit.edu.in"),
]
    cursor.execute("SELECT COUNT(*) FROM qa")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO qa (question, answer) VALUES (?, ?)",
            sjbit_data
        )
        print(f"✅ Loaded {len(sjbit_data)} SJBIT records into database")

    conn.commit()
    conn.close()


# ── SEARCH DATABASE ────────────────────────────────────────────
def search_db(question: str):
    conn = sqlite3.connect("sjbit.db")
    cursor = conn.cursor()

    # Match full question directly
    cursor.execute("""
        SELECT answer FROM qa
        WHERE LOWER(question) LIKE LOWER(?)
        LIMIT 1
    """, (f"%{question.lower()}%",))
    
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


# ── ASK GROQ AI ────────────────────────────────────────────────
def ask_groq(question: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """You are an expert assistant for SJBIT 
(SJB Institute of Technology), Bangalore, India.
ONLY answer questions related to SJBIT.
If the question is NOT about SJBIT, say:
'I can only answer SJBIT-related questions.'
Be factual, helpful, and concise."""
            },
            {
                "role": "user",
                "content": question
            }
        ],
        temperature=0.4,
        max_tokens=600
    )
    return response.choices[0].message.content


# ── REQUEST BODY ───────────────────────────────────────────────
class Question(BaseModel):
    question: str


# ── MAIN ENDPOINT ──────────────────────────────────────────────
@app.post("/ask")
def ask_sjbit(q: Question):
    if not q.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        # STEP 1 — check database first
        db_answer = search_db(q.question)
        if db_answer:
            return {
                "question": q.question,
                "answer": db_answer,
                "source": "database"
            }

        # STEP 2 — not in DB, ask Groq AI
        ai_answer = ask_groq(q.question)
        return {
            "question": q.question,
            "answer": ai_answer,
            "source": "groq_ai"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── HEALTH CHECK ───────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "SJBIT Q&A API is running"}


# ── INIT DB ON STARTUP ─────────────────────────────────────────
init_db()
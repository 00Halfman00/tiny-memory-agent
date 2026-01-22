import sqlite3
from pathlib import Path
from agents import trace

db_path = Path("memory") / Path("questions.db")
db_path.parent.mkdir(parents=True, exist_ok=True)
DB = db_path.absolute()


def init_db():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT
        );
        """
        )
        conn.commit()


init_db()


def record_question_with_no_answer(question: str) -> str:
    try:
        with trace(
            "record_question_with_no_answer",
            metadata={"question": question},
        ):
            with sqlite3.connect(DB) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO questions (question, answer) VALUES (?, NULL)",
                    (question,),
                )
                conn.commit()

        return "Recorded question with no answer"

    except Exception as e:
        with trace(
            "record_question_with_no_answer_error",
            metadata={
                "question": question,
                "error": str(e),
            },
        ):
            pass
        raise


def get_questions_with_no_answer() -> str:
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, question FROM questions WHERE answer IS NULL")
        rows = cursor.fetchall()
        if rows:
            return "\n".join(f"Question id {row[0]}: {row[1]}" for row in rows)
        else:
            return "No questions with no answer found"


def get_questions_with_answer() -> str:
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT question, answer FROM questions WHERE answer IS NOT NULL"
        )
        rows = cursor.fetchall()
        return "\n".join(f"Question: {row[0]}\nAnswer: {row[1]}\n" for row in rows)


def record_answer_to_question(id: int, answer: str) -> str:
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE questions SET answer = ? WHERE id = ?", (answer, id))
        conn.commit()
        return "Recorded answer to question"

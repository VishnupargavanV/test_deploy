import sqlite3

class HumanInTheLoopAgent:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_feedback_table()

    def _create_feedback_table(self):
        """Create the feedback table in the database if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    task_id TEXT PRIMARY KEY,
                    student_id TEXT,
                    feedback TEXT
                )
            """)
            conn.commit()

    def collect_feedback(self, task_id, student_id, feedback):
        """Save feedback for a specific task."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO feedback (task_id, student_id, feedback)
                VALUES (?, ?, ?)
            """, (task_id, student_id, feedback))
            conn.commit()

    def get_feedback(self, task_id):
        """Retrieve feedback for a specific task."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT feedback FROM feedback WHERE task_id = ?
            """, (task_id,))
            result = cursor.fetchone()
            return result[0] if result else ""

    def get_all_feedback(self, student_id):
        """Retrieve all feedback for a specific student."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT task_id, feedback FROM feedback WHERE student_id = ?
            """, (student_id,))
            result = cursor.fetchall()
            return {row[0]: row[1] for row in result}

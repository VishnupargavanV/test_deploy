import sqlite3

class FeedbackAgent:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_all_feedback(self, student_id):
        """
        Retrieve all feedback for a specific student from the database.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT task_id, feedback FROM feedback
                WHERE student_id = ?
            """, (student_id,))
            feedback_data = cursor.fetchall()
            conn.close()
            feedback_dict = {task_id: feedback for task_id, feedback in feedback_data}
            return feedback_dict

        except Exception as e:
            print(f"Error fetching feedback: {e}")
            return {}

    def collect_feedback(self, task_id, student_id, feedback):
        """
        Collect and store feedback for a specific student and task.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (task_id, student_id, feedback)
                VALUES (?, ?, ?)
                ON CONFLICT(task_id, student_id)
                DO UPDATE SET feedback = ?
            """, (task_id, student_id, feedback, feedback))

            conn.commit()
            conn.close()
            print("Feedback collected successfully.")
        except Exception as e:
            print(f"Error submitting feedback: {e}")
            return False

        return True

    def create_feedback_table(self):
        """
        Create the feedback table in the database if it does not exist.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    task_id INTEGER,
                    student_id INTEGER,
                    feedback TEXT,
                    PRIMARY KEY (task_id, student_id)
                )
            """)

            conn.commit()
            conn.close()
            print("Feedback table created.")
        except Exception as e:
            print(f"Error creating feedback table: {e}")


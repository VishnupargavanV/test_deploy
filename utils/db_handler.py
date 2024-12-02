import sqlite3

class DBHandler:
    def __init__(self, db_path="study_roadmap.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.initialize_database()
        
    def execute_query(self, query, params=()):
        """Execute a query and return the result."""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def initialize_database(self):
        # Create students table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            strengths TEXT,
            weaknesses TEXT,
            opportunities TEXT,
            threats TEXT,
            exam_scores TEXT,
            target_score INTEGER
        )
        """)
        # Create progress table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            task_id TEXT,
            week INTEGER,
            subject TEXT,
            status TEXT,
            completion INTEGER,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
        """)
        # Create feedback table
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            task_id TEXT,
            feedback TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (task_id) REFERENCES progress (task_id)
        )
        """)
        self.conn.commit()

    def add_student(self, student_data):
        self.cursor.execute("""
        INSERT INTO students (name, strengths, weaknesses, opportunities, threats, exam_scores, target_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student_data['name'],
            student_data['strengths'],
            student_data['weaknesses'],
            student_data['opportunities'],
            student_data['threats'],
            student_data['exam_scores'],
            student_data['target_score']
        ))
        self.conn.commit()

    def get_student_by_name(self, name):
        self.cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        return self.cursor.fetchone()

    def add_progress(self, student_id, task_id, week, subject, status, completion):
        self.cursor.execute("""
        INSERT INTO progress (student_id, task_id, week, subject, status, completion)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (student_id, task_id, week, subject, status, completion))
        self.conn.commit()

    def update_progress(self, task_id, completion):
        self.cursor.execute("""
        UPDATE progress
        SET completion = ?, status = ?
        WHERE task_id = ?
        """, (completion, "Completed" if completion == 100 else "In Progress", task_id))
        self.conn.commit()

    def add_feedback(self, student_id, task_id, feedback):
        # Check if feedback already exists for this task
        self.cursor.execute("SELECT * FROM feedback WHERE student_id = ? AND task_id = ?", (student_id, task_id))
        if self.cursor.fetchone():
            raise ValueError("Feedback for this task already exists.")

        self.cursor.execute("""
        INSERT INTO feedback (student_id, task_id, feedback)
        VALUES (?, ?, ?)
        """, (student_id, task_id, feedback))
        self.conn.commit()

    def get_feedback(self, student_id, task_id):
        self.cursor.execute("SELECT feedback FROM feedback WHERE student_id = ? AND task_id = ?", (student_id, task_id))
        return self.cursor.fetchone()

    def get_progress(self, student_id):
        query = """
        SELECT task_id, week, subject, status, completion 
        FROM progress
        WHERE student_id = ?
        """
        self.cursor.execute(query, (student_id,))
        return self.cursor.fetchall()

    def close_connection(self):
        """Close the database connection."""
        self.conn.close()

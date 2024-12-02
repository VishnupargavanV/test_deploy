class ProgressMonitorAgent:
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.progress = {}

    def initialize_progress(self, roadmap, student_id):
        if not isinstance(roadmap, list):
            raise ValueError("Roadmap should be a list of tasks.")
        
        for task in roadmap:
            if not isinstance(task, dict):
                raise ValueError("Each task in the roadmap should be a dictionary.")
            
            task_id = f"{student_id}_{task['week']}_{task['subject']}"
            self.progress[task_id] = {
                "status": task.get("status", "Pending"),
                "completion": 0,
                "student_id": student_id
            }
            self.db_handler.add_progress(student_id, task_id, task['week'], task['subject'], "Pending", 0)

    def update_progress(self, task_id, completion):
        query = "SELECT task_id FROM progress WHERE task_id = ?"
        result = self.db_handler.execute_query(query, (task_id,))
        if result:
            status = "Completed" if completion == 100 else "In Progress"
            self.db_handler.update_progress(task_id, completion)
        
            if task_id in self.progress:
                self.progress[task_id]['completion'] = completion
                self.progress[task_id]['status'] = status
        else:
            raise KeyError(f"Task ID {task_id} not found in progress tracker.")

    def get_progress(self, student_id):
        query = "SELECT task_id, week, subject, status, completion FROM progress WHERE student_id = ?"
        progress_data = self.db_handler.execute_query(query, (student_id,))
        progress_list = []
        for task in progress_data:
            progress_list.append({
                "task_id": task[0],
                "week": task[1],
                "subject": task[2],
                "status": task[3],
                "completion": task[4]
            })
        return progress_list

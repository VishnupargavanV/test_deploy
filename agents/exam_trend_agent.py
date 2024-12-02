class ExamTrendAgent:
    def __init__(self, llm_handler):
        self.llm_handler = llm_handler

    def analyze_trends(self, student_data):
        prompt = f"""
        Analyze the exam trends for {student_data['student_name']}:
        - Past Scores: {student_data['exam_scores']}
        - Recent practice test results: {student_data['practice_test_results']}
        - Goal: {student_data['target_score']}
        
        Highlight performance trends (improving, stable, declining) and suggest strategies to reach the goal.
        Provide output in JSON format.
        """
        response = self.llm_handler.generate_content(prompt)
        return response

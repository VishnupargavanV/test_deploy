import openai 

class RoadmapAgent:
    def __init__(self, llm_handler):
        self.llm_handler = llm_handler

    def generate_roadmap(self, student_data):
        """
        Generate a study roadmap for the student based on their data.
        :param student_data: A dictionary containing the student's data
        :return: A list of tasks for the study roadmap
        """
        try:
            target_score = student_data.get("target_score", "No target score provided")
            exam_scores = student_data.get("exam_scores", "No exam scores provided.")
            strengths = student_data.get("strengths", "No strengths provided.")
            weaknesses = student_data.get("weaknesses", "No weaknesses provided.")
            available_time = student_data.get("available_time", "No time data provided.")
            subjects = student_data.get("subjects", ["No subjects specified"])

            prompt = f"Create a personalized study roadmap for a student with the following information:\n" \
                     f"Target Score: {target_score}\n" \
                     f"Current Exam Scores: {exam_scores}\n" \
                     f"Strengths: {strengths}\n" \
                     f"Weaknesses: {weaknesses}\n" \
                     f"Available Time for Study: {available_time}\n" \
                     f"Subjects to be studied: {', '.join(subjects)}\n" \
                     f"Provide a detailed weekly study plan for this student, prioritizing subjects based on their strengths and weaknesses."

            roadmap = self.llm_handler.generate_study_roadmap(prompt)
            return roadmap

        except Exception as e:
            print(f"Error in RoadmapAgent processing: {e}")
            raise

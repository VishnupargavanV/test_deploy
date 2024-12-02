class ActionPlanAgent:
    def __init__(self, llm_handler):
        self.llm_handler = llm_handler

    def create_plan(self, swot_analysis, trend_analysis):
        prompt = f"""
        Based on the following analyses, create a personalized action plan for the student:
        
        SWOT Analysis:
        {swot_analysis}
        
        Exam Trend Analysis:
        {trend_analysis}
        
        Provide specific actions for each subject, resources needed, and a timeline.
        Output the plan in JSON format.
        """
        response = self.llm_handler.generate_content(prompt)
        return response

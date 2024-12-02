import openai  
import json

class SWOTAgent:
    def __init__(self, llm_handler):
        """
        Initializes the SWOTAgent with a given LLM handler.
        """
        self.llm_handler = llm_handler

    def process(self, student_data):
        """
        Generate a SWOT analysis for the student based on their data.
        :param student_data: A dictionary containing the student's data
        :return: A dictionary with SWOT analysis (strengths, weaknesses, opportunities, threats)
        """
        try:
            strengths = student_data.get("strengths", "No information provided.")
            weaknesses = student_data.get("weaknesses", "No information provided.")
            opportunities = student_data.get("opportunities", "No information provided.")
            threats = student_data.get("threats", "No information provided.")
            prompt = f"Generate a SWOT analysis for a student with the following details:\n" \
                     f"Strengths: {strengths}\n" \
                     f"Weaknesses: {weaknesses}\n" \
                     f"Opportunities: {opportunities}\n" \
                     f"Threats: {threats}\n" \
                     f"Provide a detailed SWOT analysis based on these points."
            
            response = self.llm_handler.generate_swot_analysis(prompt)
            
            return response

        except Exception as e:
            print(f"Error in SWOTAgent processing: {e}")
            raise

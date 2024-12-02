import json
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMHandler:
    def __init__(self, api_key: str):
        self.model = ChatGroq(
            groq_api_key="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",
            model_name="llama-3.1-70b-versatile",
            temperature=0.7,
            max_tokens=7000,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def generate_content(self, prompt: str) -> dict:
        try:
            formatted_prompt = f"""
            {prompt}
            
            Please provide your response in valid JSON format only, without any markdown or additional formatting.
            """
            
            messages = [HumanMessage(content=formatted_prompt)]
            response = self.model.invoke(messages)
            content = response.content.strip()
            print(f"Raw response: {content}")
            result = json.loads(content)
            return result

        except json.JSONDecodeError:
            raise ValueError("The response is not valid JSON.")
        except Exception as e:
            print(f"Error generating content: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def query(self, prompt: str, response_type: str = "dict") -> dict:
        try:
            formatted_prompt = f"""
            {prompt}
            
            Please provide your response in valid JSON format only, without any markdown or additional formatting.
            """
            
            messages = [HumanMessage(content=formatted_prompt)]
            response = self.model.invoke(messages)
            content = response.content.strip()
            result = json.loads(content)
            
            if response_type == "dict" and not isinstance(result, dict):
                raise ValueError("The response is not a valid JSON object.")
            elif response_type == "list" and not isinstance(result, list):
                raise ValueError("The response is not a valid JSON list.")
            
            return result

        except json.JSONDecodeError:
            raise ValueError("The response is not valid JSON.")
        except Exception as e:
            print(f"Error generating content: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def generate_swot_analysis(self, prompt: str) -> dict:
        try:
            formatted_prompt = f"""
            {prompt}
            
            Please provide your response in valid JSON format only, without any markdown or additional formatting.
            """
            
            messages = [HumanMessage(content=formatted_prompt)]
            response = self.model.invoke(messages)
            content = response.content.strip()
            result = json.loads(content)
            
            if not isinstance(result, dict):
                raise ValueError("The response is not a valid JSON object.")
            
            return result

        except json.JSONDecodeError:
            raise ValueError("The response is not valid JSON.")
        except Exception as e:
            print(f"Error generating SWOT analysis: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def generate_study_roadmap(self, prompt: str) -> list:
        try:
            formatted_prompt = f"""
            {prompt}
            
            Please provide your response in valid JSON format only, without any markdown or additional formatting.
            The response should be a JSON array of task objects, where each task object has the following structure:
            {{
                "week": <week_number>,
                "subject": <subject_name>,
                "start_date": <start_date>,
                "status": <status>
            }}
            """
            
            messages = [HumanMessage(content=formatted_prompt)]
            response = self.model.invoke(messages)
            content = response.content.strip()
            
            roadmap = json.loads(content)
            if not isinstance(roadmap, list):
                raise ValueError("The response is not a valid JSON list.")
            return roadmap

        except json.JSONDecodeError:
            raise ValueError("The response is not valid JSON.")
        except Exception as e:
            print(f"Error generating study roadmap: {e}")
            raise

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

            roadmap = self.llm_handler.query(prompt, response_type="list")
            return roadmap

        except Exception as e:
            print(f"Error in RoadmapAgent processing: {e}")
            raise

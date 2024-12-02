import os
import sys

from tenacity import retry, stop_after_attempt, wait_exponential
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_groq import ChatGroq
import streamlit as st
from dotenv import load_dotenv
import os
from utils.data_manager import StudentDataManager
from utils.llm_handler import LLMHandler
from agents.swot_agent import SWOTAgent
from agents.roadmap_agent import RoadmapAgent
from agents.progress_agent import ProgressMonitorAgent
from agents.hitl_agent import HumanInTheLoopAgent
from agents.action_plan_agent import ActionPlanAgent
from agents.exam_trend_agent import ExamTrendAgent
from utils.db_handler import DBHandler
import json
from langchain.schema import HumanMessage
load_dotenv()
API_KEY = st.secrets["general"]["GEMINI_API_KEY"] 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "assets", "student.csv")
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "study_roadmap.db")

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "assets"), exist_ok=True)

def main():
    st.title("AI Study Roadmap System")
    
    if not API_KEY:
        st.error("API Key not found. Please check your .env file.")
        return
    
    role = st.sidebar.selectbox("Select Role", ["Student", "Parent", "Teacher"])
    data_manager = StudentDataManager(DATA_PATH)
    llm_handler = LLMHandler(API_KEY)
    db_handler = DBHandler(DB_PATH)

    swot_agent = SWOTAgent(llm_handler)
    roadmap_agent = RoadmapAgent(llm_handler)
    progress_monitor = ProgressMonitorAgent(db_handler)
    hitl_agent = HumanInTheLoopAgent(DB_PATH)
    action_plan_agent = ActionPlanAgent(llm_handler)
    exam_trend_agent = ExamTrendAgent(llm_handler)

    students = data_manager.get_all_students()
    selected_student = st.sidebar.selectbox("Select Student", students)

    if selected_student:
        student_data = data_manager.get_student_data(selected_student)
        
        if role == "Parent":
            st.sidebar.subheader("Student Data (View Only)")
            st.sidebar.json(student_data) 
        elif role == "Teacher":
            st.sidebar.subheader("Student Data (Editable)")
            st.sidebar.json(student_data)  
        elif role == "Student":
            st.sidebar.subheader("Student Data")
            st.sidebar.json(student_data) 

        if role in ["Teacher", "Student"]:
            if st.button("Generate SWOT Analysis"):
                try:
                    swot_analysis = swot_agent.process(student_data)
                    st.subheader("SWOT Analysis")
                    st.json(swot_analysis)
                except Exception as e:
                    st.error(f"Error generating SWOT analysis: {e}")

        if role in ["Teacher", "Student"]:
            if st.button("Generate Study Roadmap"):
                try:
                    if 'student_id' not in student_data:
                        st.error("Student ID is missing in student data.")
                        return

                    roadmap = roadmap_agent.generate_roadmap(student_data)

                    if not isinstance(roadmap, list):
                        st.error("Generated roadmap is not a list.")
                        return

                    progress_monitor.initialize_progress(roadmap, student_data['student_id'])
                    st.subheader("Study Roadmap")
                    st.json(roadmap)
                except Exception as e:
                    st.error(f"Error generating roadmap: {e}")

        if role in ["Teacher", "Student"]:
            st.header("Track Progress")
            try:
                progress = progress_monitor.get_progress(student_data['student_id'])
                for idx, task in enumerate(progress):
                    unique_key = f"{task['task_id']}_{task['week']}_{task['subject']}_{idx}"
                    with st.expander(f"Week {task['week']} - {task['subject']}"):
                        st.write(task)
                        completion = st.slider(
                            f"Completion for {task['subject']}",
                            0,
                            100,
                            task['completion'],
                            key=f"{unique_key}_slider" 
                        )
                        if st.button(
                            f"Update Progress for {task['subject']} (Week {task['week']})", 
                            key=f"{unique_key}_button" 
                        ):
                            progress_monitor.update_progress(task['task_id'], completion)
                            st.success("Progress updated!")
            except Exception as e:
                st.error(f"Error fetching progress: {e}")

        if role in ["Teacher", "Student"]:
            if st.button("Generate Action Plan"):
                try:
                    swot_analysis = swot_agent.process(student_data)
                    trend_analysis = exam_trend_agent.analyze_trends(student_data)
                    action_plan = action_plan_agent.create_plan(swot_analysis, trend_analysis)
                    st.subheader("Action Plan")
                    st.json(action_plan)
                except Exception as e:
                    st.error(f"Error generating action plan: {e}")
        if role in ["Teacher", "Student"]:
            if st.button("Generate Exam Trend Insights"):
                try:
                    exam_trends = exam_trend_agent.analyze_trends(student_data)
                    st.subheader("Exam Trend Insights")
                    st.json(exam_trends)
                except Exception as e:
                    st.error(f"Error generating exam trend insights: {e}")
        if role == "Teacher":
            st.header("Human-in-the-Loop Feedback")
            try:
                feedback_collected = hitl_agent.get_all_feedback(student_data['student_id']) 
                for idx, task in enumerate(progress):
                    with st.expander(f"Feedback for Week {task['week']} - {task['subject']}"):
                        unique_key = f"{task['task_id']}_{task['week']}_{task['subject']}_{idx}_feedback"
                        feedback = st.text_area(
                            f"Provide feedback for {task['subject']} (Week {task['week']})",
                            feedback_collected.get(task['task_id'], ""),
                            key=unique_key  
                        )
                        if st.button(f"Submit Feedback for {task['subject']} (Week {task['week']})", key=f"{unique_key}_button"):
                            hitl_agent.collect_feedback(task['task_id'], student_data['student_id'], feedback)
                            st.success("Feedback submitted!")
            except Exception as e:
                st.error(f"Error managing feedback: {e}")

if __name__ == "__main__":
    main()

groq_api_key = st.secrets["groq"]["api_key"]
class LLMHandler:
    def __init__(self, api_key: str):
        self.model = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-70b-versatile",
            temperature=0.7,
            max_tokens=7000,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def query(self, prompt: str) -> list:
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
            
            # Ensure the response is valid JSON
            roadmap = json.loads(content)
            if not isinstance(roadmap, list):
                raise ValueError("The response is not a valid JSON list.")
            return roadmap

        except json.JSONDecodeError:
            raise ValueError("The response is not valid JSON.")
        except Exception as e:
            print(f"Error generating content: {e}")
            raise

import pandas as pd
import os

class StudentDataManager:
    def __init__(self, csv_path: str):
        if os.path.exists(csv_path):
            self.df = pd.read_csv(csv_path)
        else:
            raise FileNotFoundError(f"CSV file not found at {csv_path}")

    def get_all_students(self):
        return self.df['student_name'].unique().tolist()

    def get_student_data(self, student_name: str):
        student_row = self.df[self.df['student_name'] == student_name].iloc[0]
        return student_row.to_dict()

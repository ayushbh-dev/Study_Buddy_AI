# helpers.py
import os
import streamlit as st
import pandas as pd
from src.generator.question_generator import QuestionGenerator

def rerun():
    """Triggers a rerun of the Streamlit app."""
    st.session_state['rerun_trigger'] = not st.session_state.get('rerun_trigger', False)

class QuizManager:
    def __init__(self):
        """Initializes the QuizManager, ensuring user_answers are stored in the session state."""
        self.questions = []
        # --- FIX: Initialize user_answers in session_state to preserve them ---
        if 'user_answers' not in st.session_state:
            st.session_state.user_answers = {}
        self.results = []

    def generate_questions(self, generator: QuestionGenerator, topic: str, question_type: str, difficulty: str, num_questions: int):
        """Generates new questions and resets the quiz state."""
        self.questions = []
        # --- FIX: Reset the stored answers for a new quiz ---
        st.session_state.user_answers = {}
        self.results = []

        try:
            for _ in range(num_questions):
                if question_type == "Multiple Choice":
                    question = generator.generate_mcq(topic, difficulty.lower())
                    self.questions.append({
                        'type': 'MCQ',
                        'question': question.question,
                        'options': question.options,
                        'correct_answer': question.correct_answer
                    })
                else:
                    question = generator.generate_fill_blank(topic, difficulty.lower())
                    self.questions.append({
                        'type': 'Fill in the blank',
                        'question': question.question,
                        'correct_answer': question.answer
                    })
        except Exception as e:
            st.error(f"Error generating questions: {e}")
            return False
        
        return True

    def attempt_quiz(self):
        """Displays the quiz questions and captures user answers in the session state."""
        for i, q in enumerate(self.questions):
            st.markdown(f"""
            <div class="question-container">
                <p><strong>Question {i+1}:</strong> {q['question']}</p>
            </div>
            """, unsafe_allow_html=True)

            # --- FIX: Store and retrieve answers from st.session_state using a unique key ---
            if q['type'] == 'MCQ':
                st.session_state.user_answers[i] = st.radio(
                    f"Select an answer for Question {i+1}",
                    q['options'],
                    key=f"mcq_{i}",
                    index=None, # Prevents a default selection
                    label_visibility="collapsed"
                )
            else:
                st.session_state.user_answers[i] = st.text_input(
                    f"Fill in the blank for Question {i+1}",
                    key=f"fill_blank_{i}",
                    label_visibility="collapsed"
                )

    def evaluate_quiz(self):
        """Evaluates the quiz by comparing stored user answers with correct answers."""
        self.results = []
        
        # --- FIX: Iterate through questions and the stored answers from session_state ---
        for i, q in enumerate(self.questions):
            user_ans = st.session_state.user_answers.get(i, "") # Get answer, default to empty string
            is_correct = False

            if q['type'] == 'MCQ':
                is_correct = (user_ans == q["correct_answer"])
            else:
                is_correct = (str(user_ans).strip().lower() == q['correct_answer'].strip().lower())
            
            result_dict = {
                'question_number': i + 1,
                'question': q['question'],
                'question_type': q["type"],
                'user_answer': user_ans,
                'correct_answer': q["correct_answer"],
                "is_correct": is_correct
            }
            self.results.append(result_dict)

    def generate_result_dataframe(self):
        """Generates a Pandas DataFrame from the quiz results."""
        if not self.results:
            return pd.DataFrame()
        return pd.DataFrame(self.results)

    def save_to_csv(self, filename_prefix="quiz_results"):
        """Saves the quiz results to a CSV file."""
        if not self.results:
            st.warning("No results to save!")
            return None
        
        df = self.generate_result_dataframe()

        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{filename_prefix}_{timestamp}.csv"

        os.makedirs('results', exist_ok=True)
        full_path = os.path.join('results', unique_filename)

        try:
            df.to_csv(full_path, index=False)
            st.success(f"Results saved successfully to `{full_path}`")
            return full_path
        except Exception as e:
            st.error(f"Failed to save results: {e}")
            return None
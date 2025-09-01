# application.py
import os
import streamlit as st
from dotenv import load_dotenv
from src.utils.helpers import QuizManager
from src.generator.question_generator import QuestionGenerator

# Load environment variables
load_dotenv()

def apply_custom_css():
    """Applies custom CSS for a black sidebar and a white content area."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

        /* --- General Body Styles for White Theme --- */
        body {
            font-family: 'Poppins', sans-serif;
            background-color: #ffffff; /* --- White background for main content --- */
            color: #212529;             /* --- Dark black text for main content --- */
        }

        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* --- Header Styling for Light Theme --- */
        .header {
            background-color: #f8f9fa;
            padding: 2.0rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            text-align: center;
            margin-bottom: 2rem;
            border: 1px solid #dee2e6;
        }
        .header h1 {
            color: #160f7a;
            font-weight: 700;
            margin: 10;
        }

        /* --- Sidebar Styling (Black Container) --- */
        [data-testid="stSidebar"] {
            background-color: #000103; /* --- CHANGE: Dark background for sidebar --- */
            padding: 1.5rem;
        }
        
        /* --- Text and Headers inside Sidebar --- */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {
            color: #ffffff; /* --- CHANGE: White text for all elements in sidebar --- */
        }
        
        /* --- Button styling --- */
        .stButton>button {
            background-color: #2d2782;
            color: white;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            border: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #a9bdde;
            transform: translateY(-2px);
        }
        
        /* --- Question & Result Card Styling --- */
        .question-container, .result-card {
            background-color: #ffffff;
            color: #212529;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            box-shadow: 0 6px 20px rgba(0,0,0,0.08);
            border: 1px solid #dee2e6;
        }
        
        .result-card.correct { border-left: 5px solid #28a745; }
        .result-card.incorrect { border-left: 5px solid #dc3545; }
        
        /* --- Score Display --- */
        .score-container {
            background-color: #ffffff;
            color: #4a148c;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            font-size: 1.75rem;
            font-weight: 700;
            margin-bottom: 2rem;
            box-shadow: 0 6px 20px rgba(0,0,0,0.08);
            border: 1px solid #dee2e6;
        }

        </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Study Buddy AI", page_icon="🧠", layout="wide")
    apply_custom_css()

    # Initialize session state variables
    if 'quiz_manager' not in st.session_state:
        st.session_state.quiz_manager = QuizManager()
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False
    if 'rerun_trigger' not in st.session_state:
        st.session_state.rerun_trigger = False

    # --- HEADER ---
    st.markdown('<div class="header"><h1>🧠 Study Buddy AI Quiz Generator</h1></div>', unsafe_allow_html=True)
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.header("Quiz Settings")
        topic = st.text_input("Enter a Topic", placeholder="e.g., Python Programming")
        question_type = st.selectbox("Select Question Type", ["Multiple Choice", "Fill in the Blank"])
        difficulty = st.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"], index=1)
        num_questions = st.number_input("Number of Questions", min_value=1, max_value=10, value=5)

        if st.button("✨ Generate Quiz"):
            if not topic:
                st.warning("Please enter a topic to generate the quiz.")
            else:
                with st.spinner("Generating your quiz... 🤓"):
                    st.session_state.quiz_submitted = False
                    # Assuming QuestionGenerator is correctly imported and works
                    generator = QuestionGenerator() 
                    success = st.session_state.quiz_manager.generate_questions(
                        generator, topic, question_type, difficulty, num_questions
                    )
                    st.session_state.quiz_generated = success
                    if not success:
                        st.error("Failed to generate the quiz. Please try again.")
                    st.rerun()

    # --- MAIN CONTENT ---
    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        st.header("Here's Your Quiz! 📝")
        st.session_state.quiz_manager.attempt_quiz()

        if st.button("Submit Quiz"):
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            st.rerun()

    if st.session_state.quiz_submitted:
        st.header("Quiz Results 📊")
        results_df = st.session_state.quiz_manager.generate_result_dataframe()

        if not results_df.empty:
            correct_count = int(results_df["is_correct"].sum())
            total_questions = len(results_df)
            score_percentage = (correct_count / total_questions) * 100
            
            st.markdown(
                f'<div class="score-container">Your Score: {score_percentage:.2f}% ({correct_count}/{total_questions})</div>',
                unsafe_allow_html=True
            )

            for _, result in results_df.iterrows():
                card_class = "correct" if result['is_correct'] else "incorrect"
                icon = "✅" if result['is_correct'] else "❌"
                
                st.markdown(f"""
                <div class="result-card {card_class}">
                    <p><strong>{icon} Question {result['question_number']}:</strong> {result['question']}</p>
                    <p><strong>Your Answer:</strong> {result['user_answer']}</p>
                    {'<p><strong>Correct Answer:</strong> ' + str(result['correct_answer']) + '</p>' if not result['is_correct'] else ''}
                </div>
                """, unsafe_allow_html=True)

            if st.button("Save Results"):
                saved_file = st.session_state.quiz_manager.save_to_csv()
                if saved_file and os.path.exists(saved_file):
                    with open(saved_file, 'rb') as f:
                        st.download_button(
                            label="Download Results CSV",
                            data=f,
                            file_name=os.path.basename(saved_file),
                            mime='text/csv'
                        )
        else:
            st.warning("No results available to display.")

if __name__ == "__main__":
    main()

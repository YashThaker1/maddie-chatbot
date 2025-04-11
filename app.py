import streamlit as st
import openai
import os
import time
from dotenv import load_dotenv

# Load OpenAI API key
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# Page config
st.set_page_config(page_title="Maddie Interview Coach", page_icon="🤍", layout="centered")

# Initialize session state
for key in ["name", "question_count", "question_type", "job_description", "questions", "question_index", "feedback", "user_answer", "qa_summary", "interview_complete", "name_prompt_shown", "question_count_prompt", "question_type_prompt", "job_description_prompt"]:
    if key not in st.session_state:
        if key in ["name", "question_type", "job_description", "feedback", "user_answer"]:
            st.session_state[key] = ""
        elif key in ["questions", "qa_summary"]:
            st.session_state[key] = []
        elif key == "question_index":
            st.session_state[key] = 0
        elif key == "interview_complete":
            st.session_state[key] = False
        else:
            st.session_state[key] = False

# Styling
st.markdown("""
    <style>
    html, body, [class*="css"] {
        background-color: #f3e8ff;
        color: #1f1f1f;
    }
    .chat-bubble {
        background-color: #ede9fe;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        display: flex;
        gap: 1rem;
        align-items: flex-start;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .chat-bubble img {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
    }
    .chat-text {
        font-size: 1rem;
        line-height: 1.5;
        color: #1f1f1f;
    }
    .question-box {
        background-color: #ffffff;
        border-left: 5px solid #c084fc;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #1f1f1f;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #ffffff !important;
        color: #1f1f1f !important;
    }
    .stButton > button {
        background: linear-gradient(to right, #c084fc, #a855f7) !important;
        color: white !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 0.6em 1.5em !important;
        font-size: 1em;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("👋 Meet Maddie — Your Interview Coach")

# Typing response

def maddie_says(message, delay=0.02):
    placeholder = st.empty()
    bubble_start = """
        <div class='chat-bubble'>
            <img src='https://i.imgur.com/hpiP4pY.png'>
            <div class='chat-text'>
    """
    bubble_end = "</div></div>"
    display = ""
    for char in message:
        display += char
        placeholder.markdown(bubble_start + display + bubble_end, unsafe_allow_html=True)
        time.sleep(delay)

# Flow
if not st.session_state.name:
    if not st.session_state.name_prompt_shown:
        maddie_says("Hi, I'm Maddie, your personal interview coach...")
        st.session_state.name_prompt_shown = True

    with st.form("name_form"):
        name_input = st.text_input("Your name:", placeholder="Enter your name...")
        submitted = st.form_submit_button("Next")
        if submitted and name_input.strip():
            st.session_state.name = name_input.strip().title()
            st.session_state.rerun_after_name = True

elif not st.session_state.question_count:
    if not st.session_state.question_count_prompt:
        maddie_says(f"Great to meet you, {st.session_state.name}! How many questions would you like to practice today?")
        st.session_state.question_count_prompt = True
    cols = st.columns(3)
    if cols[0].button("6 Questions"):
        st.session_state.question_count = 6
        st.session_state.rerun_after_question_count = True
        st.stop()
    if cols[1].button("12 Questions"):
        st.session_state.question_count = 12
        st.session_state.rerun_after_question_count = True
        st.stop()
    if cols[2].button("20 Questions"):
        st.session_state.question_count = 20
        st.session_state.rerun_after_question_count = True
        st.stop()

elif not st.session_state.question_type:
    if not st.session_state.question_type_prompt:
        maddie_says("Would you like to start with behavioral questions, technical ones, or a mix of both?")
        st.session_state.question_type_prompt = True
    cols = st.columns(3)
    if cols[0].button("Behavioral"):
        st.session_state.question_type = "behavioral"
        st.experimental_rerun()
    if cols[1].button("Technical"):
        st.session_state.question_type = "technical"
        st.experimental_rerun()
    if cols[2].button("Both"):
        st.session_state.question_type = "both"
        st.experimental_rerun()

elif not st.session_state.job_description:
    if not st.session_state.job_description_prompt:
        maddie_says(f"Awesome, {st.session_state.name}! Please paste the job description below, and I’ll pull up your questions 📄")
        st.session_state.job_description_prompt = True

    with st.form("job_description_form"):
        job_input = st.text_area("Paste the job description:", placeholder="Paste or write the job description here...")
        submitted = st.form_submit_button("Next")

        if submitted and job_input.strip():
            st.session_state.job_description = job_input.strip()
            st.session_state.rerun_after_job = True
            st.stop()

else:
    index = st.session_state.question_index
    questions = st.session_state.questions
    total_qs = len(questions)
    current_q = questions[index]

    st.markdown(f"#### 🧑‍💼 Question {index + 1} of {total_qs}")
    maddie_says(f"Here's your next interview question:\n\n{current_q}")

    st.session_state.user_answer = st.text_area("🗣️ Your answer:", value=st.session_state.user_answer, height=150)

    if st.button("Submit Answer ➡️"):
        with st.spinner("Maddie is reviewing your answer..."):
            feedback_prompt = f"You are Maddie, a friendly but professional AI interview coach. Give clear, constructive, and encouraging feedback on this answer.\n\nQuestion: {current_q}\nAnswer: {st.session_state.user_answer}\n\nFeedback:"
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": feedback_prompt}],
            )
            feedback = response.choices[0].message.content
            st.session_state.feedback = feedback
            st.session_state.qa_summary.append({
                "question": current_q,
                "answer": st.session_state.user_answer,
                "feedback": feedback
            })

    if st.session_state.feedback:
        maddie_says(st.session_state.feedback)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔁 Retry This Question"):
                st.session_state.feedback = ""
                st.session_state.user_answer = ""
                st.experimental_rerun()
        st.stop()
with col2:
    if index + 1 < total_qs:
        if st.button("Next Question ➡️"):
            st.session_state.question_index += 1
            st.session_state.feedback = ""
            st.session_state.user_answer = ""
            st.experimental_rerun()
    else:
        if st.button("✅ Finish Interview"):
            st.session_state.interview_complete = True
            st.experimental_rerun()
if st.session_state.interview_complete:
    st.markdown("## 🎉 Interview Summary")
    for i, qa in enumerate(st.session_state.qa_summary, 1):
        st.markdown(f"**Q{i}:** {qa['question']}")
        st.markdown(f"**Your Answer:** {qa['answer']}")
        st.markdown(f"**Maddie's Feedback:** {qa['feedback']}")
        st.markdown("---")

# ✅ Safe rerun triggers placed at the base level
if st.session_state.get("rerun_after_question_count"):
    st.session_state.rerun_after_question_count = False
    st.experimental_rerun()
    st.stop()
st.stop()
if st.session_state.get("rerun_after_name"):
    st.session_state.rerun_after_name = False
    st.experimental_rerun()
    st.stop()
st.stop()

if st.session_state.get("rerun_after_job"):
    with st.spinner("Maddie is reviewing the job description..."):
        q_type = st.session_state.question_type
        n = st.session_state.question_count
        if q_type == "both":
            n1, n2 = n // 2, n - (n // 2)
            prompt = f"You're an expert interviewer. Based on the job description below, write {n1} behavioral and {n2} technical interview questions that progressively increase in difficulty.\n\nJob Description:\n{st.session_state.job_description}\n\nQuestions:"
        else:
            prompt = f"You're an expert interviewer. Based on the job description below, write {n} {q_type} interview questions.\n\nJob Description:\n{st.session_state.job_description}\n\nQuestions:"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        questions_text = response.choices[0].message.content
        st.session_state.questions = [q.strip("- ").strip() for q in questions_text.split("\n") if q.strip()]
        st.session_state.rerun_after_job = False
        st.success("✅ Questions are ready! Let's begin.")
        st.experimental_rerun()
st.stop()

import streamlit as st
import os
import datetime

def render_sidebar():
    with st.sidebar:
        st.header("✨ Interact")
        st.text_area("💬 Leave a comment")
        st.button("📤 Share")

        # Feedback box
        feedback = st.text_input("📝 Feedback")

        if st.button("💾 Submit Feedback"):
            if feedback.strip():
                save_feedback(feedback)
                st.success("✅ Thank you! Your feedback has been saved.")
            else:
                st.warning("⚠️ Please enter feedback before submitting.")

        st.header("🤝 Sponsors")
        st.markdown("Sponsor logos or ads here...")

def save_feedback(feedback_text):
    """Append feedback to a file with timestamp."""
    os.makedirs("data", exist_ok=True)   # create folder if not exists
    file_path = os.path.join("data", "feedback.csv")

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Save feedback
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f'"{timestamp}","{feedback_text}"\n')

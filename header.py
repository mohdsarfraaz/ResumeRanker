import streamlit as st
import uuid

def render_header():
    theme = st.get_option("theme.base") or "light"

    if theme == "dark":
        TITLE = "#ff1a1a"      # your cyan
        SUB   = "#ff4d4d"
        INFO_BG = "#2c2c2c"
        INFO_TX = "#76ffb3"
    else:
        TITLE = "#2E86C1"
        SUB   = "#333333"
        INFO_BG = "#e8f5e9"
        INFO_TX = "#1b5e20"

    css_id = str(uuid.uuid4())
    st.markdown(
        f"""
        <style id="{css_id}">
        :root {{
          --title-color: {TITLE};
          --subtitle-color: {SUB};
          --info-bg: {INFO_BG};
          --info-text: {INFO_TX};
        }}

        /* ✅ RESET any old gradient/text-fill that blocks the color */
        .header-container .main-title {{
          background: none !important;
          -webkit-background-clip: initial !important;
          -webkit-text-fill-color: var(--title-color) !important;
          color: var(--title-color) !important;
          text-shadow: none !important;
        }}

        .header-container {{
          text-align:center;
          margin-bottom:25px;
        }}
        .header-container img {{
          width:97%;
          max-height:220px;
          object-fit:cover;
          border-radius:12px;
          margin-bottom:20px;
        }}
        .header-container .subtitle {{
          font-size:20px;
          margin-bottom:15px;
          color: var(--subtitle-color) !important;
          font-style: italic;
        }}
        .header-container .info-box {{
          font-size:18px;
          padding:12px 20px;
          border-radius:10px;
          width:70%;
          margin:auto;
          background: var(--info-bg) !important;
          color: var(--info-text) !important;
          font-weight:600;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="header-container">
            <h1 class="main-title">📄 Resume Ranker</h1>
            <div class="subtitle">Smart Resume Shortlisting System for HR Professionals</div>
            <img src="https://img.freepik.com/premium-photo/finding-right-candidate_968957-19679.jpg" alt="Banner">
            <div class="info-box">💡 Great teams are built by hiring the right talent. Let’s make it faster & smarter!</div>
        </div>
        """,
        unsafe_allow_html=True
    )

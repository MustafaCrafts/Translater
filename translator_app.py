import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langdetect import detect, LangDetectException
import speech_recognition as sr
import pyttsx3
from datetime import datetime

# Configuration
api_key = "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"
MODEL_NAME = "mixtral-8x7b-32768"

# Supported Languages
LANGUAGES = {
    "English": "en",
    "Turkish": "tr",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Russian": "ru",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar",
    "Hindi": "hi",
    "Urdu": "ur"
}

# Initialize Model
model = ChatGroq(
    model_name=MODEL_NAME,
    api_key=api_key,
    temperature=0.1
)

# Enhanced Prompt Template
prompt = ChatPromptTemplate.from_messages([    
    ("system", """You are a professional translation engine. Follow these rules:
1. Strict 1:1 translation only
2. Preserve cultural context
3. Maintain original formatting
4. No explanations, notes, or comments
5. Formality: {formality}
6. Source language: {src_lang}
ONLY RETURN THE TRANSLATED TEXT WITHOUT ANY FORMATTING OR METADATA."""),
    
    ("human", "Translate to {target_lang}: {text}"),
])

chain = prompt | model

# Custom CSS
def inject_css():
    st.markdown(f"""
    <style>
        .main {{
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            padding: 30px;
            font-family: 'Inter', sans-serif;
        }}
        .stTextInput input, .stTextArea textarea {{
            border-radius: 20px;
            padding: 18px;
            border: 2px solid rgba(0,0,0,0.2) !important;
            background: rgba(255,255,255,0.8) !important;
            color: #000000 !important;
            font-size: 18px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: #7a00ff;
            box-shadow: 0 0 15px rgba(122,0,255,0.3);
        }}
        .stButton button {{
            width: 100%;
            border: none;
            border-radius: 15px;
            background: linear-gradient(135deg, #7a00ff, #ff00e5);
            color: white;
            padding: 15px 30px;
            font-size: 18px;
            font-weight: 600;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .stButton button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(122,0,255,0.3);
        }}
        .translation-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
        }}
        .box {{
            background: rgba(255,255,255,0.8) !important;
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border: 2px solid #000000 !important;
            font-size: 20px;
            color: #000000 !important;
            line-height: 1.6;
            backdrop-filter: blur(5px);
        }}
        .sidebar .sidebar-content {{
            background: linear-gradient(195deg, #0f0c29, #302b63);
            color: white;
            padding: 30px;
            border-right: 1px solid rgba(255,255,255,0.1);
        }}
        .header-accent {{
            background: linear-gradient(90deg, #7a00ff, #ff00e5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em;
            display: inline-block;
            margin-right: 10px;
        }}
        .glow {{
            animation: glow 2s ease-in-out infinite alternate;
            font-size: 2.5em;
            display: inline-block;
        }}
        @keyframes glow {{
            from {{ text-shadow: 0 0 10px #7a00ff; }}
            to {{ text-shadow: 0 0 20px #ff00e5, 0 0 30px #ff00e5; }}
        }}
        .neon-border {{
            position: relative;
            overflow: hidden;
        }}
        .neon-border::before {{
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #7a00ff, #ff00e5, #7a00ff);
            z-index: -1;
            animation: border-animation 3s linear infinite;
            background-size: 400%;
            border-radius: 20px;
        }}
        @keyframes border-animation {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        .history-grid {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
            padding: 15px 0;
        }}
        .timestamp {{
            font-size: 0.9em;
            color: #7a00ff;
            margin-bottom: 8px;
        }}
    </style>
    """, unsafe_allow_html=True)

# Function to read text aloud
def speak_text(text):
    speech_engine = pyttsx3.init()
    speech_engine.setProperty('rate', 150)
    speech_engine.setProperty('volume', 0.9)
    speech_engine.say(text)
    speech_engine.runAndWait()

# Main App
def main():
    inject_css()

    # Initialize session state
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'last_translation' not in st.session_state:
        st.session_state.last_translation = ""

    # Header with corrected HTML rendering
    st.markdown(
        "<h1>🪐 <span class='header-accent'>Nexus</span><span class='glow'>Translate</span></h1>", 
        unsafe_allow_html=True
    )

    # Sidebar Settings
    with st.sidebar:
        st.header("⚙️ Quantum Settings")
        formality = st.selectbox("Formality Level", ["Auto", "Formal", "Informal"])
        st.markdown("---")
        st.download_button(
            "📥 Export Timeline",
            "\n".join([f"{h['timestamp']} | {h['source']} → {h['translation']}" 
                      for h in st.session_state.history]),
            "quantum_translations.txt"
        )

    # Main Interface
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        with st.container():
            st.markdown("### 🌌 Input Sphere")
            text_input = st.text_area(
                "Enter text to translate", 
                "Hello, world!", 
                height=250, 
                label_visibility="collapsed"
            )
            
            # Language Detection
            auto_detect = st.checkbox("Auto-detect language", True)
            detected_lang = "Unknown"
            
            if auto_detect and text_input.strip():
                try:
                    detected_lang_code = detect(text_input)
                    src_lang_name = next(
                        (k for k, v in LANGUAGES.items() if v == detected_lang_code),
                        "Unknown"
                    )
                    st.markdown(
                        f"<div class='timestamp'>Detected language: {src_lang_name}</div>",
                        unsafe_allow_html=True
                    )
                    detected_lang = src_lang_name
                except LangDetectException:
                    st.warning("Language detection failed")
                    detected_lang = "Unknown"
            elif not auto_detect:
                detected_lang = st.selectbox("Select Source Language", list(LANGUAGES.keys()))
            
            # Voice Input
            if st.button("🎤 Cosmic Voice Input", use_container_width=True):
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    st.markdown(
                        "<div class='timestamp'>Listening to quantum vibrations...</div>", 
                        unsafe_allow_html=True
                    )
                    try:
                        audio = recognizer.listen(source, timeout=5)
                        text_input = recognizer.recognize_google(audio)
                        st.success(f"🪐 Cosmic input: {text_input}")
                    except sr.UnknownValueError:
                        st.error("Quantum interference detected - please repeat")
                    except sr.RequestError:
                        st.error("Galactic connection unstable")
                    except Exception as e:
                        st.error(f"Stellar anomaly detected: {str(e)}")

    with col2:
        with st.container():
            st.markdown("### 🪐 Output Dimension")
            target_lang = st.selectbox("Target Language", list(LANGUAGES.keys()))
            
            if st.button("🚀 Hyper-Translate", use_container_width=True):
                if text_input.strip():
                    with st.spinner("🌀 Warping through linguistic dimensions..."):
                        try:
                            # Convert language names to codes
                            src_lang_code = LANGUAGES.get(detected_lang, "en")
                            target_lang_code = LANGUAGES[target_lang]

                            response = chain.invoke({
                                "target_lang": f"{target_lang} ({target_lang_code})",
                                "text": text_input.strip(),
                                "formality": formality,
                                "src_lang": f"{detected_lang} ({src_lang_code})"
                            })
                            result = response.content.strip()
                            
                            # Update session state
                            st.session_state.history.insert(0, {
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "source": text_input,
                                "translation": result,
                                "language": target_lang
                            })
                            st.session_state.last_translation = result
                            
                            # Display result
                            st.markdown(f"""
                            <div class="neon-border">
                                <div class="box">
                                    {result}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            # Automatically play translation
                            speak_text(result)
                        
                        except Exception as e:
                            st.error(f"Quantum fluctuation detected: {str(e)}")
                else:
                    st.warning("Input field contains cosmic void")

            # Voice Output
            if st.session_state.last_translation:
                if st.button("🔊 Sonic Playback", use_container_width=True):
                    speak_text(st.session_state.last_translation)

    # Translation History
    if st.session_state.history:
        with st.expander("⏳ Temporal Translation Archive", expanded=True):
            for item in st.session_state.history[:5]:
                st.markdown(f"""
                <div class="translation-card">
                    <div class="timestamp">{item['timestamp']}</div>
                    <div class="history-grid">
                        <div style="border-right: 2px solid rgba(255,255,255,0.1); padding-right: 20px">
                            {item['source']}
                        </div>
                        <div style="color: #7a00ff">
                            <strong>{item['language']}:</strong> {item['translation']}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 20px; color: #666">
        <div style="margin-bottom: 10px">
            <span style="margin: 0 15px">🌐 Neural Matrix v2.1</span>
            <span style="margin: 0 15px">⚡ Quantum Processing</span>
            <span style="margin: 0 15px">🔒 Entanglement Encryption</span>
        </div>
        © 2024 NexusTranslate Technologies • Transcending Linguistic Boundaries
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
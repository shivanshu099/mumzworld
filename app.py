import streamlit as st
import time
import base64
from audio_recorder_streamlit import audio_recorder
from internal_tools import transcribe_audio, text_to_speech
from agent import process_query
from langchain_core.messages import HumanMessage, AIMessage

# Helper to read image as base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        return ""

img_b64 = get_base64_image("mommy_image.webp")

# Page configuration
st.set_page_config(
    page_title="Mumzworld Gift Finder",
    page_icon="🎁",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for premium, modern glassmorphism styling
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

    body, .stApp {{
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        background-attachment: fixed;
        color: #1a1a1a !important;
    }}
    
    .header-container {{
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem;
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 30px;
        margin: 2rem auto 3rem auto;
        max-width: 900px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        gap: 30px;
    }}
    
    .header-image {{
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        box-shadow: 0 8px 25px rgba(248, 87, 166, 0.4);
        border: 4px solid white;
        transition: transform 0.3s ease;
    }}
    
    .header-image:hover {{
        transform: scale(1.05);
    }}

    .header-text-container {{
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}

    .brand-title {{
        font-family: 'Outfit', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        padding: 0;
        background: linear-gradient(135deg, #f857a6, #ff5858);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px;
    }}
    
    .tagline {{
        font-size: 1.2rem;
        font-weight: 400;
        color: #555;
        margin-top: 5px;
    }}
    
    .chat-container {{
        max-width: 800px;
        margin: 0 auto;
        padding-bottom: 120px;
    }}
    
    /* Streamlit Chat Customization */
    .stChatMessage {{
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.6);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        color: #1a1a1a !important;
    }}
    
    .stChatMessage p, .stChatMessage div {{
        color: #1a1a1a !important;
    }}
    
    /* Input Area Styling */
    .stChatInputContainer {{
        padding: 10px;
        border-radius: 30px;
    }}
    
    .mic-container {{
        position: fixed;
        bottom: 30px; 
        right: 75px; /* Adjusting to place it precisely inside the chat input box on the right */
        z-index: 99999;
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 8px;
        background: linear-gradient(135deg, #9b59b6 0%, #3498db 100%); /* Unique purple-blue gradient */
        border-radius: 50%;
        box-shadow: 0 4px 15px rgba(155, 89, 182, 0.4);
        transition: transform 0.2s;
    }}
    
    .mic-container:hover {{
        transform: scale(1.1);
    }}
    
    </style>
    """,
    unsafe_allow_html=True,
)

# Header Section
image_html = f'<img src="data:image/webp;base64,{img_b64}" class="header-image" />' if img_b64 else ''

st.markdown(
    f"""
    <div class="header-container">
        {image_html}
        <div class="header-text-container">
            <h1 class="brand-title">Mumzworld AI</h1>
            <p class="tagline">Find the perfect gift, effortlessly in English & Arabic ✨</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.messages.append({"role": "assistant", "content": "Welcome to Mumzworld! I can help you find the perfect gift. Tell me what you're looking for, the age group, and your budget.\n\nمرحباً بك في ممزورلد! يمكنني مساعدتك في العثور على الهدية المثالية. أخبرني بما تبحث عنه، والفئة العمرية، وميزانيتك."})

if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# Display Chat Messages
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# Input Area (Mic floats over chat_input via CSS)
st.markdown('<div class="mic-container">', unsafe_allow_html=True)
audio_bytes = audio_recorder(
    text="",
    recording_color="#ffeb3b",
    neutral_color="#ffffff",  
    icon_name="microphone",
    icon_size="2x",
)
st.markdown('</div>', unsafe_allow_html=True)

prompt = st.chat_input("Type your message here... / اكتب رسالتك هنا...")

# Process Voice Input
if audio_bytes and audio_bytes != st.session_state.last_audio:
    st.session_state.last_audio = audio_bytes
    with st.spinner("🎙️ Transcribing..."):
        transcribed_text = transcribe_audio(audio_bytes)
        if transcribed_text and not transcribed_text.startswith("["):
            prompt = transcribed_text
        elif transcribed_text:
            st.error(transcribed_text)

# Process Text Input
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("✨ Searching for the perfect gifts..."):
            try:
                response = process_query(prompt, st.session_state.history)
                message_placeholder.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.session_state.history.append(HumanMessage(content=prompt))
                st.session_state.history.append(AIMessage(content=response))
            except Exception as e:
                st.error(f"Error connecting to AI: {e}")

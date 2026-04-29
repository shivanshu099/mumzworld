"""
Internal tools for the VisaPro Chatbot.
Provides speech-to-text (listening) and text-to-speech (voice output) functionality.
"""
import io
import re
import speech_recognition as sr
from gtts import gTTS


def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe audio bytes (WAV format) to text using Google's free Speech Recognition API.
    
    Args:
        audio_bytes: Raw audio data in WAV format from the browser recorder.
        
    Returns:
        Transcribed text string, or an error message prefixed with '['.
    """
    if not audio_bytes:
        return ""
    
    recognizer = sr.Recognizer()
    
    try:
        audio_stream = io.BytesIO(audio_bytes)
        
        with sr.AudioFile(audio_stream) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio_data = recognizer.record(source)
        
        text = recognizer.recognize_google(audio_data)
        return text
    
    except sr.UnknownValueError:
        return "[Could not understand the audio. Please try again.]"
    except sr.RequestError as e:
        return f"[Speech recognition service error: {e}]"
    except Exception as e:
        return f"[Audio processing error: {e}]"


def _clean_text_for_speech(text: str) -> str:
    """Strip markdown formatting and emoji for cleaner TTS output."""
    # Remove markdown bold/italic
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Remove markdown links [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Remove special box-drawing / decorative chars
    text = re.sub(r'[═─━┃│┌┐└┘├┤┬┴┼▌▐░▒▓█]', '', text)
    # Remove emoji (common unicode ranges)
    text = re.sub(
        r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
        r'\U0001F900-\U0001F9FF\U00002702-\U000027B0\U0000FE00-\U0000FE0F'
        r'\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002600-\U000026FF'
        r'\U0000231A-\U0000231B\U00002328\U000023CF\U000023E9-\U000023F3'
        r'\U000023F8-\U000023FA\U000025AA-\U000025AB\U000025B6\U000025C0'
        r'\U000025FB-\U000025FE\U00002934-\U00002935\U00002B05-\U00002B07'
        r'\U00002B1B-\U00002B1C\U00002B50\U00002B55\U00003030\U0000303D'
        r'\U00003297\U00003299]+', '', text
    )
    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def text_to_speech(text: str, lang: str = "en") -> bytes:
    """
    Convert text to speech audio bytes (MP3 format) using Google TTS.
    
    Args:
        text: The text to speak.
        lang: Language code (default "en").
        
    Returns:
        MP3 audio bytes, or empty bytes on failure.
    """
    if not text:
        return b""
    
    try:
        clean_text = _clean_text_for_speech(text)
        if not clean_text:
            return b""

        tts = gTTS(text=clean_text, lang=lang, slow=False)
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        return audio_buffer.read()
    except Exception as e:
        print(f"[TTS Error]: {e}")
        return b""

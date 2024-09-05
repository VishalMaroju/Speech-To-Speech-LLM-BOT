import streamlit as st
import ollama as ol
from voice import record_voice
from gtts import gTTS  # Import Google Text-to-Speech
from io import BytesIO  # For in-memory audio playback
import base64  # For encoding audio to be playable in Streamlit

st.set_page_config(page_title="🎙️ Voice Bot", layout="wide")
st.title("🎙️ Speech Bot")
st.sidebar.title("`Speak with LLMs` \n`in any language`")


def language_selector():
    lang_options = ["ar", "de", "en", "es", "fr", "it", "ja", "nl", "pl", "pt", "ru", "zh"]
    with st.sidebar:
        return st.selectbox("Speech Language", ["en"] + lang_options)


def llm_selector():
    ollama_models = [m['name'] for m in ol.list()['models']]
    with st.sidebar:
        return st.selectbox("LLM", ollama_models)


def print_txt(text):
    # Check if text contains Arabic characters
    if any("\u0600" <= c <= "\u06FF" for c in text):
        text = f"<p style='direction: rtl; text-align: right;'>{text}</p>"
    st.markdown(text, unsafe_allow_html=True)


def print_chat_message(message):
    text = message["content"]
    if message["role"] == "user":
        st.write(f"**User:** {text}")
    else:
        st.write(f"**Assistant:** {text}")
        text_to_speech(text)  # Convert AI response to speech


def text_to_speech(text, lang='en', save_audio=False, filename="output.mp3"):
    """Convert text to speech and play it in Streamlit. Optionally save as an audio file."""
    try:
        tts = gTTS(text=text, lang=lang)
        
        # Save to a BytesIO object for in-memory playback in Streamlit
        audio_bytes = BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        # Optionally save to a file
        if save_audio:
            tts.save(filename)
            st.success(f"Audio saved as {filename}")
        
        # Encode audio in base64 to play in Streamlit
        audio_base64 = base64.b64encode(audio_bytes.read()).decode()
        st.audio(f"data:audio/mp3;base64,{audio_base64}", format="audio/mp3")
    except Exception as e:
        st.error(f"Error converting text to speech: {e}")


def main():
    model = llm_selector()
    with st.sidebar:
        question = record_voice(language=language_selector())

    # Init chat history for a model
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}
    if model not in st.session_state.chat_history:
        st.session_state.chat_history[model] = []
    chat_history = st.session_state.chat_history[model]

    # Print conversation history
    for message in chat_history:
        print_chat_message(message)

    if question:
        user_message = {"role": "user", "content": question}
        print_chat_message(user_message)
        chat_history.append(user_message)
        response = ol.chat(model=model, messages=chat_history)
        answer = response['message']['content']
        ai_message = {"role": "assistant", "content": answer}
        print_chat_message(ai_message)
        chat_history.append(ai_message)

        # Truncate chat history to keep 20 messages max
        if len(chat_history) > 20:
            chat_history = chat_history[-20:]

        # Update chat history
        st.session_state.chat_history[model] = chat_history


if __name__ == "__main__":
    main()

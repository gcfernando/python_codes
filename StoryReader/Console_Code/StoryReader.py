# Developer ::> Gehan Fernando

import pyttsx3
from PyPDF2 import PdfReader
import time

def select_voice(engine, preferred_gender='female'):
    voices = engine.getProperty('voices')
    # Try to find a voice matching preferred gender, fallback to default
    for voice in voices:
        if preferred_gender.lower() in voice.name.lower() or preferred_gender.lower() in voice.id.lower():
            return voice.id
    return voices[1].id  # fallback to first voice

def read_pdf_aloud(file_path, voice_id=None, rate=150, volume=1.0):
    try:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            speaker = pyttsx3.init()

            # Set voice if specified
            if voice_id:
                speaker.setProperty('voice', voice_id)
            speaker.setProperty('rate', rate)
            speaker.setProperty('volume', volume)  # volume: 0.0 to 1.0

            total_pages = len(reader.pages)
            print(f"Starting to read '{file_path}', {total_pages} pages...\n")

            for page_num in range(total_pages):
                content = reader.pages[page_num].extract_text()
                if content:
                    print(f"Reading page {page_num + 1}...")
                    speaker.say(content)
                    speaker.runAndWait()
                    # Small pause between pages for better pacing
                    time.sleep(0.5)
            print("\nFinished reading the story. Hope you enjoyed it!")
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    speaker = pyttsx3.init()

    # Automatically select a female voice if available
    chosen_voice = select_voice(speaker, preferred_gender='female')

    read_pdf_aloud("Story.pdf", voice_id=chosen_voice, rate=150, volume=0.9)

# Developer ::> Gehan Fernando
# Import necessary libraries
import customtkinter as ctk
import tkinter.messagebox as msgbox
from gtts import gTTS
import pygame

class TextToAudio(ctk.CTk):
    # Constructor method for initializing the application window
    def __init__(self):
        super().__init__()

        # Set the title of the window
        self.title(self.__screenTitle())

        # Set the appearance and color theme of the window
        ctk.set_appearance_mode("dark")  # Dark mode for the UI
        ctk.set_default_color_theme("blue")  # Set default color theme to blue

        # Set the window size and position
        width = 500
        height = 420
        self.geometry(f"{width}x{height}")

        # Center the window on the screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Disable window resizing
        self.resizable(False, False)

        # Create and place the "Enter Text Below" label
        self.label = ctk.CTkLabel(self, text="Enter Text Below:", font=("Consolas", 16))
        self.label.place(x=10, y=10, anchor="nw")

        # Create and place the textbox for inputting text
        self.textbox = ctk.CTkTextbox(
            self,
            width=480,
            height=250,
            font=("Consolas", 14),
            border_width=2,
            corner_radius=6
        )
        self.textbox.place(x=10, y=50)
        self.after(100, self.textbox.focus_set)  # Set focus to the textbox when the app loads

        # Create and place the "Select Language" label
        self.lang_label = ctk.CTkLabel(self, text="Select Language:", font=("Consolas", 14))
        self.lang_label.place(x=10, y=320)

        # Create and place the dropdown for selecting language
        self.language_option = ctk.CTkOptionMenu(
            self,
            values=[item["name"] for item in self.__language_list()],
            width=200
        )
        self.language_option.place(x=140, y=320)

        # Create and place the Play button, which will trigger the audio play
        self.play_button = ctk.CTkButton(self, text="Play", corner_radius=10, command=self.__generate_and_play_audio)
        self.play_button.place(x=10, y=370)

        # Create and place the Reset button to clear the text in the textbox
        self.reset_button = ctk.CTkButton(self, text="Reset", corner_radius=10, command=self.__reset_textbox)
        self.reset_button.place(x=160, y=370)

        # Create and place the Exit button to close the application
        self.exit_button = ctk.CTkButton(self, text="Exit", corner_radius=10, fg_color="red", text_color="white", command=self.destroy)
        self.exit_button.place(x=345, y=370)

    # Private method to return a list of available languages and their configurations
    def __language_list(self):
        return [
            {"name": "English (Australia)", "lang": "en", "tld": "com.au"},
            {"name": "English (United Kingdom)", "lang": "en", "tld": "co.uk"},
            {"name": "English (United States)", "lang": "en", "tld": "us"},
            {"name": "English (Canada)", "lang": "en", "tld": "ca"},
            {"name": "English (India)", "lang": "en", "tld": "co.in"},
            {"name": "English (Ireland)", "lang": "en", "tld": "ie"},
            {"name": "English (South Africa)", "lang": "en", "tld": "co.za"},
            {"name": "English (Nigeria)", "lang": "en", "tld": "com.ng"},
            {"name": "French (Canada)", "lang": "fr", "tld": "ca"},
            {"name": "French (France)", "lang": "fr", "tld": "fr"},
            {"name": "Portuguese (Brazil)", "lang": "pt", "tld": "com.br"},
            {"name": "Portuguese (Portugal)", "lang": "pt", "tld": "pt"},
            {"name": "Spanish (Mexico)", "lang": "es", "tld": "com.mx"},
            {"name": "Spanish (Spain)", "lang": "es", "tld": "es"},
            {"name": "Spanish (United States)", "lang": "es", "tld": "us"}
        ]

    # Private method to return the title of the screen
    def __screenTitle(self):
        return "Text to Audio Converter"

    # Private method to get the language dictionary by its name
    def __get_language_by_name(self, name):
        # Searching for the language dictionary by its name
        for language in self.__language_list():
            if language["name"] == name:
                return language
        return None  # Return None if no matching language is found

    # Private method to reset the textbox content
    def __reset_textbox(self):
        # Delete all the content in the textbox
        self.textbox.delete("1.0", "end")

    # Private method to generate and play the audio (shortcut for generating and playing)
    def __generate_and_play_audio(self):
        if self.__generate() is not None:
            # If audio generation is successful, play the audio
            self.__play_audio()

    # Private method to generate audio from text
    def __generate(self, fileName="output.mp3"):
        # Get the text from the textbox
        text = self.textbox.get("1.0", "end-1c")

        # Check if the textbox is empty or contains only whitespace
        if not text.strip():
            # Show a warning message if no text is entered or if it's only whitespace
            msgbox.showwarning(title=self.__screenTitle(), message="Please enter some text to convert.")
            return None

        # Get the selected language from the dropdown
        language = self.language_option.get()
        languagePack = self.__get_language_by_name(language)

        # Check if a valid language is selected
        if languagePack is None:
            msgbox.showwarning(title=self.__screenTitle(), message="Please select a valid language.")
            return None

        # Get the language and top-level domain (TLD) for the selected language
        lang = languagePack["lang"]
        tld = languagePack["tld"]

        # Generate the speech using gTTS (Google Text-to-Speech)
        tts = gTTS(text, lang=lang, tld=tld, slow=False)
        tts.save(fileName)  # Save the audio to a file

        return fileName # Return the name of the generated audio file

    # Private method to play the generated audio file
    def __play_audio(self, fileName="output.mp3"):
        # Initialize the pygame display (required for pygame.mixer to work)
        pygame.display.set_mode((1, 1))  # We don't need an actual window, just need to initialize the display

        # Initialize pygame mixer to play the MP3 file
        pygame.mixer.init()

        # Load and play the MP3 file
        pygame.mixer.music.load(fileName)
        pygame.mixer.music.play()

        # Set the event when the music finishes playing
        pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

        # Event loop: process events and stop when the music ends
        while True:
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    # Stop the music and release resources
                    pygame.mixer.music.stop()
                    pygame.mixer.quit()  # This will stop the mixer and release resources

                    return  # Exit the loop once the music has finished


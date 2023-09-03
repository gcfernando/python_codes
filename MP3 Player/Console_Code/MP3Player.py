# Developer ::> Gehan Fernando
# import libraries
import pygame, os, random, sys, time
from colorama import Fore

def prevent_sleep_windows():
    import ctypes
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)

os.system('cls')
current_song_index = 0
music_folder = input("Enter file name folder path : ")

music_files = [os.path.join(music_folder, filename) for filename in os.listdir(music_folder) if filename.endswith(".mp3")]

if not music_files:
    sys.exit()

random.shuffle(music_files)

pygame.mixer.init(frequency=96000, size=32, channels=2, buffer=4096)

# Prevent sleep/screensaver
prevent_sleep_windows()

pygame.mixer.music.load(music_files[current_song_index])
pygame.mixer.music.play()

print(Fore.GREEN + "Now playing\t:", os.path.basename(music_files[current_song_index]))
if len(music_files) > 1:
    print(Fore.YELLOW + "Next up\t\t:", os.path.basename(music_files[(current_song_index + 1) % len(music_files)]))

while True:
    if not pygame.mixer.music.get_busy():
        if (current_song_index + 1) == len(music_files):
            pygame.quit()
            sys.exit()

        current_song_index = (current_song_index + 1) % len(music_files)

        pygame.mixer.music.load(music_files[current_song_index])
        pygame.mixer.music.play()

        os.system('cls')
        print(Fore.GREEN + "Now playing\t:", os.path.basename(music_files[current_song_index]))
        if current_song_index < len(music_files) - 1:
            print(Fore.YELLOW + "Next up\t\t:", os.path.basename(music_files[(current_song_index + 1) % len(music_files)]))
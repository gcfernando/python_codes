# # Developer ::> Gehan Fernando
# # import libraries
import pygame
import os
import random
import sys
import time
from colorama import Fore, init
from mutagen.mp3 import MP3
import threading
import ctypes # Keep for sleep prevention

# Initialize colorama
init(autoreset=True)
IS_WINDOWS = os.name == 'nt'

# Function to set console window title
def set_console_title(title):
    """Sets the console window title."""
    if IS_WINDOWS:
        try:
            ctypes.windll.kernel32.SetConsoleTitleW(str(title))
        except Exception as e:
            print(Fore.YELLOW + f"Warning: Could not set console title on Windows: {e}")
    else:
        # Use ANSI escape code for other systems (Linux, macOS)
        try:
            sys.stdout.write(f"\x1b]0;{title}\a")
            sys.stdout.flush()
        except Exception as e:
            # Might fail if not running in a real terminal (e.g., IDE output)
            print(Fore.YELLOW + f"Warning: Could not set terminal title: {e}")

# Function to prevent sleep/screensaver (Windows)
def prevent_sleep_windows():
    try:
        ES_CONTINUOUS = 0x80000000
        ES_SYSTEM_REQUIRED = 0x00000001
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
        print(Fore.MAGENTA + "System sleep prevention activated (Windows).")
    except AttributeError:
        print(Fore.YELLOW + "Sleep prevention only available on Windows.")
    except Exception as e:
        print(Fore.RED + f"Error activating sleep prevention: {e}")

# Clear console
os.system('cls' if IS_WINDOWS else 'clear')

# --- Configuration ---
music_folder = input("Enter music folder path: ")
CROSSFADE_MS = 5000          # Duration of the fade effect (5 seconds)
CROSSFADE_START_TIME_S = 15  # Start fade 15 seconds before song ends
# --- End Configuration ---

# Get all mp3 files
try:
    music_files = [os.path.join(music_folder, f) for f in os.listdir(music_folder) if f.lower().endswith(".mp3")]
except FileNotFoundError:
    print(Fore.RED + f"Error: Folder not found '{music_folder}'")
    sys.exit()
except Exception as e:
    print(Fore.RED + f"Error accessing folder '{music_folder}': {e}")
    sys.exit()


# Exit if no music found
if not music_files:
    print(Fore.RED + "No .mp3 files found in the given folder.")
    sys.exit()

# Shuffle the playlist
random.shuffle(music_files)
print(Fore.CYAN + f"Found {len(music_files)} tracks. Playlist shuffled.")

# --- Pygame Mixer Initialization ---
try:
    pygame.init() # Initialize all Pygame modules
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048) # Standard init
    pygame.mixer.set_num_channels(2) # Explicitly set 2 channels
    channel1 = pygame.mixer.Channel(0)
    channel2 = pygame.mixer.Channel(1)
    print(Fore.GREEN + "Pygame initialized successfully.")
except pygame.error as e:
    print(Fore.RED + f"Error initializing pygame: {e}")
    print(Fore.YELLOW + "Make sure you have audio drivers installed and configured.")
    sys.exit()
# --- End Pygame Mixer Initialization ---

# Prevent system sleep (if on Windows)
if IS_WINDOWS:
    set_console_title("GC MP3 Player")
    prevent_sleep_windows()

# --- Global State ---
current_song_index = -1 # Start at -1 so the first increment makes it 0
active_channel = channel1
inactive_channel = channel2
current_sound = None # Sound object currently playing (or fading out)
next_sound = None # Sound object PRELOADED for the NEXT track
current_song_start_time = 0
current_song_length_s = 0
program_running = True
preload_thread = None # Thread for preloading
# --- End Global State ---

# Function to get song length safely
def get_song_length(file_path):
    try:
        audio = MP3(file_path)
        if audio.info is not None:
             # Add a small buffer/tolerance? Maybe not needed if timing is relative.
             return audio.info.length
        else:
             print(Fore.YELLOW + f"\nWarning: Could not read metadata (no info) for {os.path.basename(file_path)}. Using default length.")
             return 300 # Default to 5 minutes
    except Exception as e:
        print(Fore.RED + f"\nError reading metadata for {os.path.basename(file_path)}: {e}")
        return 300 # Default to 5 minutes

# Animation function
def show_animation():
    animation_state = 0
    while program_running:
        dots = '.' * (animation_state % 4)
        print(Fore.CYAN + f"Playing{dots}      ", end='\r', flush=True)
        animation_state += 1
        time.sleep(0.5)
    print(" " * 20, end='\r') # Clear animation line on exit

# --- Preloading Function (runs in a separate thread) ---
def preload_song(file_path):
    global next_sound
    try:
        # print(f"\n[Thread] Preloading: {os.path.basename(file_path)}") # Debug
        loaded_sound = pygame.mixer.Sound(file_path)
        next_sound = loaded_sound # Update the global variable atomically (relatively safe for assignment)
        # print(f"\n[Thread] Preload SUCCESS: {os.path.basename(file_path)}") # Debug
    except pygame.error as e:
        print(Fore.RED + f"\n[Thread] Error pre-loading sound {os.path.basename(file_path)}: {e}")
        next_sound = None # Ensure it's None if preloading fails
    except Exception as e:
        print(Fore.RED + f"\n[Thread] Unexpected error pre-loading sound {os.path.basename(file_path)}: {e}")
        next_sound = None

# --- Function to start preloading the next track ---
def start_next_preload():
    global preload_thread, next_sound
    # If a preload thread is already running, let it finish or error out.
    # Starting a new one will target the correct *next* song based on the current index.

    # Calculate index for the song *after* the one that is about to start playing
    next_load_index = (current_song_index + 1) % len(music_files)

    # Only preload if there are multiple songs
    if len(music_files) > 1 :
        next_load_path = music_files[next_load_index]
        # We don't clear next_sound here, as play_next_song consumes it.
        # The preload_song function will overwrite it when done.
        preload_thread = threading.Thread(target=preload_song, args=(next_load_path,), daemon=True)
        preload_thread.start()


# --- Function to load and play the next song ---
def play_next_song():
    global current_song_index, current_sound, active_channel, inactive_channel
    global current_song_start_time, current_song_length_s, next_sound, preload_thread

    previous_song_index_before_increment = current_song_index

    # Increment index for the song starting NOW
    current_song_index = (current_song_index + 1) % len(music_files)
    current_song_path = music_files[current_song_index]
    current_song_filename = os.path.basename(current_song_path) # <-- Get filename only

    # --- Get the sound object to play ---
    # Grab the preloaded sound if it's ready
    sound_to_play = next_sound
    # Set next_sound to None *immediately* to signify it's been consumed
    # Prevents accidentally using the same preloaded sound twice if things happen fast
    next_sound = None

    if sound_to_play is None:
        # Preloading failed or hasn't finished, load synchronously (will cause glitch here!)
        print(Fore.YELLOW + f"\nWarning: Preload not ready for {os.path.basename(current_song_path)}. Loading now...")
        try:
            # --- SYNCHRONOUS LOAD (Fallback) ---
            sound_to_play = pygame.mixer.Sound(current_song_path)
            # --- END SYNCHRONOUS LOAD ---
        except pygame.error as e:
            print(Fore.RED + f"\nError loading sound {os.path.basename(current_song_path)}: {e}")
            print(Fore.YELLOW + "Skipping track.")
            current_sound = None # Ensure no stale sound object reference
            pygame.time.wait(100)
            # Try preloading the one after the failed one immediately
            start_next_preload()
            return False # Indicate failure
        except Exception as e:
            print(Fore.RED + f"\nUnexpected error loading sound {os.path.basename(current_song_path)}: {e}")
            print(Fore.YELLOW + "Skipping track.")
            current_sound = None
            pygame.time.wait(100)
            start_next_preload()
            return False # Indicate failure

    # --- Get Length & Print Info ---
    current_song_length_s = get_song_length(current_song_path)

    # >>> Set Console Title <<<
    set_console_title(f"GC MP3 Player : {current_song_filename}")
    # >>> ------------- <<<

    os.system('cls' if IS_WINDOWS else 'clear')

    # Display Previous Song (Only if not the very first song)
    if previous_song_index_before_increment >= 0:
        prev_display_index = previous_song_index_before_increment
        print(Fore.WHITE + f"{'Previous':<10}: {os.path.basename(music_files[prev_display_index])}")

    # Display Current Song
    print(Fore.GREEN + f"{'Now':<10}: {os.path.basename(current_song_path)} ({time.strftime('%M:%S', time.gmtime(current_song_length_s))})")

    # Display Next Song
    next_print_index = (current_song_index + 1) % len(music_files)
    if len(music_files) > 1:
        print(Fore.YELLOW + f"{'Next up':<10}: {os.path.basename(music_files[next_print_index])}")
    print("\n")

    # --- START CROSSFADE IMMEDIATELY (Less blocking now) ---
    # 1. Fade out the sound on the currently active channel
    #    'current_sound' still holds the sound object of the track ending.
    if active_channel.get_busy() and current_sound is not None:
        active_channel.fadeout(CROSSFADE_MS)

    # 2. Start playing the new sound (preloaded or loaded fallback) with fade-in
    inactive_channel.set_volume(1.0) # Ensure channel starts at full potential volume
    inactive_channel.play(sound_to_play, fade_ms=CROSSFADE_MS)

    # --- Critical Timing: Record start time AFTER play command ---
    current_song_start_time = pygame.time.get_ticks()

    # 3. Swap channels and update the 'current_sound' reference
    active_channel, inactive_channel = inactive_channel, active_channel
    current_sound = sound_to_play # The new sound is now the current one

    # --- START PRELOADING FOR THE *NEXT* TRANSITION ---
    # This now happens *after* the current fade has begun.
    start_next_preload()

    return True # Indicate success
# --- End Function ---


# --- Main Loop ---
clock = pygame.time.Clock()
need_to_play_next = True
crossfade_triggered = False

# Start animation thread
animation_thread = threading.Thread(target=show_animation, daemon=True)
animation_thread.start()

# --- Initial Preload ---
# Start preloading the very first track in the background *before* the loop
if music_files:
    current_song_index = -1 # Set index correctly for start_next_preload
    start_next_preload()
    print("Preloading first track...")
    # Optional: Wait a very short time to increase chances of first preload finishing
    # Adjust based on typical file size/disk speed if needed.
    # time.sleep(1.0) # e.g., wait 1 second


while program_running:
    # Event handling (e.g., for pygame.QUIT if a window were present)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            program_running = False
            break
    if not program_running:
        break # Exit main loop if QUIT event received

    # --- Play Next Song If Needed ---
    if need_to_play_next:
        if not play_next_song():
             # If loading/playing failed, wait briefly and loop will retry
             print(Fore.YELLOW + "Attempting next track after error...")
             pygame.time.wait(1000)
             need_to_play_next = True # Explicitly ensure retry
        else:
            # Song started successfully
            need_to_play_next = False
            crossfade_triggered = False # Reset trigger for the new song

    # --- Check for Crossfade Trigger Time ---
    # Conditions: Not already trying to play next, channel busy, sound object exists, length known, not already triggered
    if not need_to_play_next and active_channel.get_busy() and current_sound is not None and current_song_length_s > 0 and not crossfade_triggered:
        elapsed_ms = pygame.time.get_ticks() - current_song_start_time
        # Prevent elapsed time exceeding song length in calculation (handles minor inaccuracies)
        elapsed_s = min(elapsed_ms / 1000.0, current_song_length_s)
        remaining_s = current_song_length_s - elapsed_s

        # Check if remaining time is within the trigger window
        if remaining_s <= CROSSFADE_START_TIME_S:
            # print(f"\nTriggering crossfade! Remaining: {remaining_s:.1f}s") # Debug
            need_to_play_next = True
            crossfade_triggered = True

    # --- Handle Unexpected Song End / End of Playlist ---
    # Conditions: Not already trying to play next, BOTH channels idle
    elif not need_to_play_next and not active_channel.get_busy() and not inactive_channel.get_busy():
         # Check if a song *was* playing (current_sound exists) or if it's just initial idle state
         if current_sound is not None or current_song_index >= 0 : # Check if at least one song has played or started
             if len(music_files) <= 1:
                 print("\nSingle song finished or playback stopped.")
                 program_running = False
             else:
                 # print("Triggering next song due to idle channels.") # Debug
                 need_to_play_next = True
                 current_sound = None # Clear the sound reference as it stopped


    # Control loop speed
    clock.tick(40) # Check ~40 times per second (slightly increased rate)

# --- Cleanup ---
print("\nPlaylist finished or program interrupted. Shutting down.")
program_running = False # Signal threads to stop

# Wait briefly for animation thread
if animation_thread.is_alive():
    animation_thread.join(timeout=1.0)

# Stop any preload thread that might be running
if preload_thread is not None and preload_thread.is_alive():
    print("Waiting briefly for preload thread...")
    # We don't forcefully stop it, just give it a moment to finish IO
    preload_thread.join(timeout=0.5)

# Stop channels explicitly before quitting mixer
print("Stopping channels...")
channel1.stop()
channel2.stop()
pygame.mixer.quit()
print("Pygame mixer quit.")
pygame.quit() # Quit Pygame itself
print("Pygame quit.")
sys.exit()

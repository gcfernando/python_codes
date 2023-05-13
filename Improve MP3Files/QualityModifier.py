# Developer ::> Gehan Fernando
# import libraries
import os, random
from pydub import AudioSegment

# Defining a list of available frequencies, modes, and bitrates.
FREQUENCIES = [8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000, 96000, 192000]
MODES = ['mono', 'stereo', 'joint_stereo', 'dual_mono']
BITRATES = ['32k', '64k', '96k', '128k', '192k', '256k', '320k']

# Function to prompt the user to select the desired bitrate and return the selected value.
def select_bit_rate():
    print(f"BitRates (Kbps) => {', '.join(BITRATES)}")
    return input("Select BitRate (Kbps): ")

# Function to prompt the user to select the desired mode and return the selected value.
def select_mode():
    print(f"Modes => {', '.join(MODES)}")
    return input("Select Mode: ")

# Function to prompt the user to select the desired frequency and return the selected value.
def select_frequency():
    print(f"Frequencies => {', '.join(str(f) for f in FREQUENCIES)}")
    return input("Select Frequency: ")

# Function to prompt the user to enter the file path or folder path and return the selected value.
def select_file_or_folder():
    return input("Enter the file path or folder path: ")

# Function to optimize a single audio file.
def optimize_file(path, bit_rate, mode, frequency):
    # Get the file name from the path
    fileName = os.path.basename(path)
    try:
        # Load the audio file using Pydub
        audio = AudioSegment.from_file(path)

        # Check the selected mode and number of audio channels and adjust as needed
        if mode in ['joint_stereo', 'dual_mono'] and audio.channels == 1:
            audio = audio.set_channels(2)
        elif mode == 'mono' and audio.channels == 2:
            audio = audio.set_channels(1)
        elif mode == 'joint_stereo' and audio.channels == 2:
            # If joint stereo mode is selected and the audio has 2 channels, create a 4-channel audio file
            audio_4ch = AudioSegment.silent(duration=len(audio), frame_rate=audio.frame_rate)
            left_channel = audio.split_to_mono()[0]
            right_channel = audio.split_to_mono()[1]
            # Mix the left and right channels with panning to create a left-right mix
            left_right_mix = left_channel.overlay(right_channel, position=0, loop=True).pan(-0.5).fade_out(50).fade_in(50)
            # Mix the left and right channels again with panning to create a center mix
            center_mix = left_channel.overlay(right_channel, position=0, loop=True).pan(0).fade_out(50).fade_in(50)
            # Combine the left-right and center mixes into a 4-channel audio file
            audio_4ch = audio_4ch.overlay(left_right_mix, position=0)
            audio_4ch = audio_4ch.overlay(center_mix, position=2)
            audio = audio_4ch
        elif mode == 'dual_mono' and audio.channels == 2:
            # If dual mono mode is selected and the audio has 2 channels, randomly select one channel to keep
            audio = audio.set_channels(2)
            audio = audio.split_to_mono()[0] if random.choice([True, False]) else audio.split_to_mono()[1]

        # Export the optimized audio file to a temporary file
        output_file = f"{os.path.splitext(path)[0]}_temp.mp3"
        audio.export(output_file, format="mp3", bitrate=bit_rate, parameters=["-codec:a", "libmp3lame", "-ar", str(frequency), "-qscale:a", "0"])

        # Replace the original file with the optimized file
        os.replace(output_file, path)
        print(f"{fileName} successfully optimized")
    except Exception as e:
        print(f"{fileName} not successfully optimized")

def optimize_files(path, bit_rate, mode, frequency):
    if os.path.isfile(path):
        optimize_file(path, bit_rate, mode, frequency)
    elif os.path.isdir(path):
        music_files = [os.path.join(path, filename) for filename in os.listdir(path) if filename.endswith(".mp3")]
        for music_file in music_files:
            optimize_file(music_file, bit_rate, mode, frequency)
    else:
        print("Invalid path entered.")

if __name__ == "__main__":
    os.system("cls")
    file_or_folder = select_file_or_folder()
    print('\r\n')
    bit_rate = select_bit_rate()
    mode = select_mode()
    frequency = select_frequency()
    print('\r\n')
    optimize_files(file_or_folder, bit_rate, mode, frequency)
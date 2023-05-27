# Developer ::> Gehan Fernando
# Import libraries
import os
import eyed3

# Clear the terminal screen
os.system('cls')

# Define the path to the MP3 file
mp3_file_path = "C:\Gehan\Projects\Python\Aathadi Aathadi.mp3"

# Load the MP3 file
audio_file = eyed3.load(mp3_file_path)

# Print the tag information if available
if audio_file.tag:
    print(f"Title: {audio_file.tag.title}")
    print(f"Artist: {audio_file.tag.artist}")
    print(f"Album: {audio_file.tag.album}")
    print(f"Album Artist: {audio_file.tag.album_artist}")
    print(f"Genre: {audio_file.tag.genre}")
    print(f"Track Number: {audio_file.tag.track_num}")

    # Print the year only if it is available in the metadata
    if audio_file.tag.getBestDate():
        print(f"Year: {audio_file.tag.getBestDate().year}")

# Print the audio information if available
if audio_file.info:
    print(f"Sample Rate: {audio_file.info.sample_freq}")
    print(f"Bitrate: {audio_file.info.bit_rate[1] // 1000} kbps")
    print(f"Duration: {audio_file.info.time_secs} seconds")
    print(f"Channels: {audio_file.info.mode}")

# Print the file size
file_size = os.path.getsize(mp3_file_path)
print(f"File Size: {round(file_size / (1024 * 1024), 2)} MB")
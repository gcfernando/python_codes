1. Install AudioSegment library
2. Download and copy ffmpeg.exe, ffplay.exe, and ffprobe.exe to Source folder


About

This Python script is designed to optimize audio files in the MP3 format by adjusting their bitrate, mode, and frequency. The script uses the Pydub library to load, manipulate, and export audio files.

The script prompts the user to select the desired bitrate, mode, and frequency for optimization and to provide the file path or folder path for the audio files to be optimized. The available options for bitrate, mode, and frequency are predefined as a list in the script.

The script then optimizes the audio files in the selected folder or the single file provided by the user, according to the selected options for bitrate, mode, and frequency. The optimization process involves adjusting the audio channels, if necessary, and exporting the optimized audio file to a temporary file with the selected bitrate, mode, and frequency. 

Finally, the original audio file is replaced with the optimized file.

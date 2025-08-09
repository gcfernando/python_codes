# Developer ::> Gehan Fernando
import lyricsgenius
import re
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
# Initialize Genius API (replace with your own token)
genius = lyricsgenius.Genius('L6w22551_2-VcfuJ1PgmtWgy697EjSVuL1iNJ53aClFStcaXopDc3b7-LOgxub3l')

# Optional Genius settings
genius.remove_section_headers = True
genius.skip_non_songs = True
genius.excluded_terms = ["(Remix)", "(Live)"]

# Input: song title and artist
song_title = "Sapphire"
artist_name = "Ed Sheeran"

# Search for the song
song = genius.search_song(title=song_title, artist=artist_name)

# Check if song was found
if song:
    # Clean the lyrics
    clean_lyrics = re.sub(r'\[.*?\]', '', song.lyrics).strip()

    # Print song metadata and lyrics
    print(f"🎵 Title: {song.title}")
    print(f"🎤 Artist: {song.artist}")
    print(f"💿 Album: {song.album.full_title}")
    print("\n🎶 Lyrics:\n")
    print(clean_lyrics[:1000] + "...\n")  # print first 1000 characters only
else:
    print("Song not found.")

# L6w22551_2-VcfuJ1PgmtWgy697EjSVuL1iNJ53aClFStcaXopDc3b7-LOgxub3l
from imdb import Cinemagoer
import requests

ip="IP address of your server"

# Function to fetch movie details from IMDb using IMDbPY library
def get_movie_details(imdb_id):
    ia = Cinemagoer()  # Use Cinemagoer class
    try:
        # Extract the IMDb ID without 'tt'
        imdb_id = imdb_id[2:]
        movie = ia.get_movie(imdb_id)
        return movie
    except Exception as e:
        print(f"Error fetching movie details for IMDb ID {imdb_id}: {e}")
        return None

# Function to create a playlist.m3u8 file
def create_playlist(movie_ids):
    playlist_content = "#EXTM3U\n"

    for imdb_id in movie_ids:
        movie = get_movie_details(imdb_id)

        if movie is not None:
            # Extracting movie details from IMDb data
            movie_name = movie['title']
            genre = movie.get('genres', ['Unknown'])[0]

            # Fetch TV logo from IMDb API
            tv_logo_url = movie.get('full-size cover url', '')

            # Adding entry to the playlist
            playlist_content += f"#EXTINF:-1 tvg-id=\"{movie_name}\" tvg-logo=\"{tv_logo_url}\" group-title=\"{genre}\",{movie_name}\n"
            playlist_content += f"http://{ip}/stream/{imdb_id}\n"
            print(f"Added {movie_name} to playlist")

    # Writing to the playlist file
    with open("playlist.m3u8", "w") as playlist_file:
        playlist_file.write(playlist_content)

# Read movie ids from movie_list.txt
with open("imdb_id.txt", "r") as file:
    movie_ids = [line.strip() for line in file.readlines()]

# Create playlist.m3u8
create_playlist(movie_ids)

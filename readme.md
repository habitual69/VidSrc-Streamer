# VidSrc Streamer

#### Overview

VidSrc Streamer is a Python application designed to simplify the process of fetching direct stream URLs for movies based on IMDb IDs from the VidSrc website. Additionally, it offers a convenient script for generating IPTV playlists, compatible with IPTV players, VLC, and other similar media players.

#### Components

This project comprises two primary components:

1. **m3u8parser.py**: This script acts as the core streaming component. Users can access it through a web API to retrieve direct stream URLs for movies and series. To stream content, simply use the following URL format:

   ```
   http://localhost:8000/stream/<imdb_id>
   ```

   Replace `<imdb_id>` with the IMDb ID of the movie you wish to stream on VLC Player. The script also supports caching links in an SQLite3 database for quicker retrieval.

2. **playlistcreator.py**: This script facilitates the creation of IPTV playlists (playlist.m3u8 files) containing movie details. These playlists can be seamlessly utilized with IPTV players or VLC Player. To generate a playlist, follow these steps:

   - Create a file named `imdb_id.txt` containing one IMDb or TMDB ID per line.
   - Execute the script using Python:

     ```bash
     python playlistcreator.py
     ```

   The script will generate a playlist.m3u8 file with movie details and URLs that are compatible with IPTV players.

#### Getting Started

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/habitual69/VidSrc-Streamer.git
   ```

2. Navigate to the project directory:

   ```bash
   cd VidSrc-Streamer
   ```

3. Install the required Python libraries:

   ```bash
   pip install -r requirements.txt
   ```

#### Using m3u8parser.py

To stream a movie using VLC Player, use the following URL format:

```
http://localhost:8000/stream/<imdb_id>
```

Replace `<imdb_id>` with the IMDb ID of the movie you want to stream. The script will fetch the direct stream URL from the VidSrc website.

#### Using playlistcreator.py

To generate an IPTV playlist (playlist.m3u8) with movie details for use with IPTV players:

1. Create a file named `imdb_id.txt` in the project directory. Each line should contain one IMDb or TMDB ID for the movies or series you want to include in the playlist.

   Example `imdb_id.txt` contents:

   ```
   tt0111161
   tt0068646
   tt0468569
   tt0071562
   ```

2. Run the script:

   ```bash
   python playlistcreator.py
   ```

   The script will create a `playlist.m3u8` file with movie details and URLs that can be used with IPTV players.

#### Docker Support

To run VidSrc Streamer in a Docker container, follow these steps:

1. Build the Docker image:

   ```bash
   docker build -t vidsrc-streamer .
   ```

2. Create a Docker container from the image:

   ```bash
   docker run -d -p 8000:8000 vidsrc-streamer
   ```

Now, you can access VidSrc Streamer at `http://localhost:8000/stream/<imdb_id>`.

#### Sample IPTV Playlist

A sample IPTV playlist (playlist.m3u8) is included, containing movie details for your reference.

#### License

This project is licensed under the MIT License. Please refer to the [LICENSE](LICENSE) file for further details.

from fastapi import FastAPI, HTTPException, Response, Depends
from typing import Optional
from helper.vidsrc_extractor import VidSrcExtractor
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import requests
import time
import sqlite3

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Add CORS middleware
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_vidsrc_extractor() -> VidSrcExtractor:
    return VidSrcExtractor()

# SQLite database initialization
DATABASE_FILE = "stream_cache.db"

def initialize_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS stream_cache (
                      imdb_id TEXT PRIMARY KEY,
                      stream_url TEXT
                   )''')
    conn.commit()
    conn.close()

initialize_database()

def insert_stream(imdb_id, stream_url):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO stream_cache (
                      imdb_id, stream_url)
                      VALUES (?, ?)''',
                   (imdb_id, stream_url))
    conn.commit()
    conn.close()

def get_stream_from_database(imdb_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''SELECT stream_url FROM stream_cache
                      WHERE imdb_id=?''',
                   (imdb_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None

def delete_stream_from_database(imdb_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM stream_cache WHERE imdb_id=?''', (imdb_id,))
    conn.commit()
    conn.close()


@app.get("/stream/{imdb_id}", response_class=Response)
async def get_stream_content(
    imdb_id: str,
    vse: VidSrcExtractor = Depends(get_vidsrc_extractor),
):
    cached_stream = get_stream_from_database(imdb_id)
    if cached_stream:
        try:
            response = requests.head(cached_stream)
            if response.status_code == 200:
                response = requests.get(cached_stream)
                return Response(content=response.content, media_type="text/plain")
            else:
                # Remove the invalid entry from the database
                delete_stream_from_database(imdb_id)
        except requests.RequestException:
            # Ignore errors and proceed with fetching a new URL
            pass

    try:
        # Fetch the stream URL from VidSrcExtractor
        stream_url, _ = vse.get_vidsrc_stream("VidSrc PRO", "movie", imdb_id, "eng", None, None)

        if not stream_url:
            logging.warning(f"Stream not found for IMDb ID: {imdb_id}")
            raise HTTPException(status_code=404, detail="Stream not found")

        response = requests.get(stream_url)
        response.raise_for_status()

        # Cache the stream URL
        insert_stream(imdb_id, stream_url)

        return Response(content=response.content, media_type="text/plain")

    except requests.RequestException as e:
        logging.error(f"Error fetching stream content for IMDb ID {imdb_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching stream content")
    except Exception as e:
        logging.error(f"Unexpected error for IMDb ID {imdb_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("m3u8parser:app", host="0.0.0.0", port=8000, reload=True)

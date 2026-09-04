import os
import subprocess
import threading
from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS


# --------------------------------------------------
# Configuration
# --------------------------------------------------

DATA_DIR = Path(
    os.environ.get("DATA_DIR", "/var/data")
)

MUSIC_DIR = DATA_DIR / "music"
SYNC_FILE = DATA_DIR / "playlist.spotdl"

MUSIC_DIR.mkdir(parents=True, exist_ok=True)


# Put your Spotify playlist URL in a Render
# environment variable called PLAYLIST_URL.
PLAYLIST_URL = os.environ.get("PLAYLIST_URL")


# Prevent two people from syncing simultaneously.
sync_lock = threading.Lock()


# --------------------------------------------------
# Flask
# --------------------------------------------------

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/sync": {
            "origins": "*"
        },
        r"/download/*": {
            "origins": "*"
        }
    }
)


# --------------------------------------------------
# Health check
# --------------------------------------------------

@app.route("/")
def home():
    return jsonify({
        "status": "online"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })


# --------------------------------------------------
# Sync
# --------------------------------------------------

@app.route("/sync", methods=["POST"])
def sync_playlist():

    if not PLAYLIST_URL:
        return jsonify({
            "error": "PLAYLIST_URL has not been configured."
        }), 500


    # Only allow one sync operation at a time.
    if not sync_lock.acquire(blocking=False):

        return jsonify({
            "error": "A sync is already running. Please try again shortly."
        }), 409


    try:

        # Record the files that existed before sync.
        before = {
            path.name
            for path in MUSIC_DIR.iterdir()
            if path.is_file()
        }


        # --------------------------------------------------
        # FIRST RUN
        # --------------------------------------------------
        #
        # If the .spotdl file doesn't exist yet, initialize
        # synchronization using:
        #
        # spotdl sync PLAYLIST_URL --save-file playlist.spotdl
        #
        # After that, subsequent runs use:
        #
        # spotdl sync playlist.spotdl
        #

        if not SYNC_FILE.exists():

            command = [
                "python",
                "-m",
                "spotdl",
                "sync",
                PLAYLIST_URL,
                "--save-file",
                str(SYNC_FILE),
                "--output",
                str(MUSIC_DIR / "{artists} - {title}.{output-ext}")
            ]

        else:

            command = [
                "python",
                "-m",
                "spotdl",
                "sync",
                str(SYNC_FILE),
                "--output",
                str(MUSIC_DIR / "{artists} - {title}.{output-ext}")
            ]


        # Run spotDL.
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=3600
        )


        # spotDL failed.
        if result.returncode != 0:

            return jsonify({
                "error": "spotDL failed.",
                "details": result.stderr[-5000:]
            }), 500


        # --------------------------------------------------
        # Determine newly downloaded files
        # --------------------------------------------------

        after = {
            path.name
            for path in MUSIC_DIR.iterdir()
            if path.is_file()
        }

        new_files = sorted(after - before)


        # Only return files that actually exist.
        files = []

        for filename in new_files:

            path = MUSIC_DIR / filename

            if path.is_file():

                files.append({
                    "name": filename,
                    "url": "/download/" + filename
                })


        return jsonify({
            "success": True,
            "new_files": files
        })


    except subprocess.TimeoutExpired:

        return jsonify({
            "error": "spotDL took too long and was stopped."
        }), 504


    except Exception as error:

        return jsonify({
            "error": str(error)
        }), 500


    finally:

        sync_lock.release()


# --------------------------------------------------
# Download endpoint
# --------------------------------------------------

@app.route("/download/<path:filename>")
def download_file(filename):

    # Resolve the requested file.
    requested_file = (MUSIC_DIR / filename).resolve()

    # Resolve the music directory.
    music_directory = MUSIC_DIR.resolve()


    # Prevent path traversal.
    if music_directory not in requested_file.parents:

        return jsonify({
            "error": "Invalid file."
        }), 400


    if not requested_file.is_file():

        return jsonify({
            "error": "File not found."
        }), 404


    return send_from_directory(
        MUSIC_DIR,
        requested_file.name,
        as_attachment=True
    )


# --------------------------------------------------
# Run locally
# --------------------------------------------------

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )

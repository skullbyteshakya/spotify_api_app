import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from datetime import datetime

def manage_spotify_playlists():
    try:
        # Load environment variables from .env file
        load_dotenv()
        
        # Replace these with your actual Spotify API credentials
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        redirect_uri = 'http://localhost:8888/callback'

        # Define the required scopes - added playlist-modify-public for creating playlists
        scope = "user-library-read playlist-read-private playlist-read-collaborative playlist-modify-public"

        # Set up OAuth
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope
        ))

        # Get current user's info
        user_info = sp.current_user()
        print("\nUser Profile:")
        print("-" * 50)
        print(f"Username: {user_info['display_name']}")
        print(f"Profile URL: {user_info['external_urls']['spotify']}")
        print(f"Followers: {user_info['followers']['total']}")

        # Get user's playlists
        playlists = sp.current_user_playlists()
        print("\nYour Playlists:")
        print("-" * 50)
        for idx, playlist in enumerate(playlists['items'], 1):
            print(f"{idx}. {playlist['name']} - {playlist['tracks']['total']} tracks")

        # Find the "Songs-chan" playlist
        source_playlist_id = None
        for playlist in playlists['items']:
            if playlist['name'] == "Songs-chan":
                source_playlist_id = playlist['id']
                break

        if not source_playlist_id:
            print("\nError: Couldn't find playlist named 'Songs-chan'")
            return

        # Get all tracks from the source playlist
        kanye_tracks = []
        results = sp.playlist_tracks(source_playlist_id)
        tracks = results['items']
        
        # Get all tracks (handling pagination)
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        # Filter Kanye West songs
        for track in tracks:
            # Check if any of the artists is Kanye West
            for artist in track['track']['artists']:
                if artist['name'].lower() in ['kanye west', 'ye']:
                    kanye_tracks.append(track['track']['uri'])
                    break

        if not kanye_tracks:
            print("\nNo Kanye West songs found in the playlist.")
            return

        # Create new playlist
        current_date = datetime.now().strftime("%Y-%m-%d")
        new_playlist_name = f"Kanye Songs from Songs-chan ({current_date})"
        new_playlist = sp.user_playlist_create(
            user_info['id'],
            new_playlist_name,
            public=True,
            description=f"Kanye West songs extracted from Songs-chan playlist on {current_date}"
        )

        # Add tracks to new playlist (handling Spotify's 100 tracks per request limit)
        for i in range(0, len(kanye_tracks), 100):
            batch = kanye_tracks[i:i + 100]
            sp.playlist_add_items(new_playlist['id'], batch)

        print(f"\nSuccess! Created new playlist '{new_playlist_name}'")
        print(f"Found {len(kanye_tracks)} Kanye West songs")
        print(f"Playlist URL: {new_playlist['external_urls']['spotify']}")

    except spotipy.SpotifyException as e:
        print(f"Authentication Error: {e}")
        print("Please check your client ID and secret.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    manage_spotify_playlists()
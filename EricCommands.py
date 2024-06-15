from datetime import datetime, date
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import EricUtils
import re

load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET  = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_DEVICE_ID = os.getenv('SPOTIFY_DEVICE_ID')

scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, scope=scope, redirect_uri='http://google.com/callback/'))

class Command:
    def __init__(self, user_query: str | None) -> None:
        self.user_query = user_query
    
    def primary(self):
        pass
    
    def secondary(self):
        pass


class SayTime(Command):
    def primary(self):
        now = datetime.now()
        return "It's currently " + now.strftime('%I:%M%p')


class PlayPause(Command):
    def primary(self):
        playback = sp.current_playback()
        
        if playback != None:
            if playback['is_playing']:
                sp.pause_playback(SPOTIFY_DEVICE_ID)
        else:
            sp.start_playback(SPOTIFY_DEVICE_ID)
            
        return None


class GetPlayingSong(Command):
    def primary(self):
        current = sp.current_user_playing_track()
        song = current['item']['name']
        
        artists = []
        for k in current['item']['artists']:
            if k['type'] == 'artist':
                artists.append(k['name'])
        
        if len(artists) == 1:
            artists = artists[0]
        elif len(artists) == 2:
            artists = ' and '.join(artists)
        else:
            artists = ', '.join(artists[:-1]) + ', and' + artists[-1]        
        return f"{song} by {artists}"


class SetSpotifyVolume(Command):
    def primary(self):
        if 'set spotify volume to' in self.user_query:
            volume = int(re.search(r'\d+', self.user_query).group())
            sp.volume(int(volume))
        elif 'set the spotify volume to' in self.user_query:
            volume = volume = int(re.search(r'\d+', self.user_query).group())
            sp.volume(int(volume))
        return None

def search_song(query: str):
    print(query)
    artist = query.split('by')[1]
    track = query.split('by')[0]
    result_raw = sp.search(f"{track} {artist}", limit=1, offset=0, type="track", market="GB")
    print(result_raw)
    result = result_raw['tracks']['items'][0][list(result_raw['tracks']['items'][0].keys())[0]]['uri']
    print(result)
    return result
    
class SearchSong(Command):        
    def primary(self):
        if 'play the song' in self.user_query:
            query = self.user_query.split('play the song')[1].strip()
            search_song(query)
            sp.start_playback(SPOTIFY_DEVICE_ID, search_song(query))
        elif 'play' in self.user_query:
            query = self.user_query.split('play')[1].strip()
            sp.start_playback(SPOTIFY_DEVICE_ID, search_song(query))
        else:
            return EricUtils.UserQueryError("Command 'play' needed for searching songs.")
        
        return None
    

class AddSongToQueue(Command):
    def primary(self):
        if 'to my queue' in self.user_query:
            user_query = self.user_query.replace('to my queue', '')
        else:
            user_query = self.user_query.replace('to the queue', '')
            
        if 'add the song' in user_query:
            query = user_query.split('add the song')[1].strip()
            sp.add_to_queue(search_song(query), SPOTIFY_DEVICE_ID)
        elif 'add' in user_query:
            query = user_query.split('add')[1].strip()
            sp.add_to_queue(search_song(query), SPOTIFY_DEVICE_ID)
        
        return f"Successfully added {query.split('by')[0]} to your queue."


class SkipSong(Command):
    def primary(self):
        sp.next_track()
        
        return None


class PlayMainPlaylist(Command):
    def primary(self):
        sp.start_playback(SPOTIFY_DEVICE_ID, "https://open.spotify.com/playlist/1QjJZaw3mysDIPaRlXIfH7")
        return None

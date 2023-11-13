import spotipy
from spotipy.oauth2 import SpotifyOAuth
import sqlite3
import json
import os
from lyricsgenius import Genius
import re

'''
export SPOTIPY_CLIENT_ID=b9b4e8153b9b461aa388e0a6746431ae
export SPOTIPY_CLIENT_SECRET=21b770eec6b642e29c4372c27903f946
export SPOTIPY_REDIRECT_URI=https://localhost:8888/callback
'''

def read_json(cache_filename):
    '''
    '''
    try:
        full_path = os.path.join(os.path.dirname(__file__), cache_filename)
        file = open(full_path)
        file_data = file.read()
        file.close()
        json_data = json.loads(file_data)
        return json_data
    except:
        return {}


def write_json(cache_filename, dict):
    '''
    '''  
    json_str = json.dumps(dict, indent=4)
    file = open(cache_filename, 'w')
    file.write(json_str)
    file.close()


def get_artist_albums_using_cache(artist_id, cache_filename):
    '''
    '''
    loaded_data = read_json(cache_filename)
    if artist_id in loaded_data:
        # print(f'Using cache for artist_id: {artist_id}')
        return loaded_data[artist_id]
    else:
        # print(f'Fetching data for artist_id: {artist_id}')
        try:
            # set up spotipy
            scope = "user-library-read"
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
            r = sp.artist_albums(artist_id, album_type='album', limit=50)
            if len(r) > 0:
                loaded_data[artist_id] = r
                write_json(cache_filename, loaded_data)
        except:
            print('Exception')
            return None


def get_albums_dict(albums_cache_filename):
    json_data = read_json(albums_cache_filename)
    for artist_id in json_data:
        albums_d = {}
        albums = json_data[artist_id]['items']
        for album in albums:
            album_id = album['id']
            album_name = album['name']
            if album_name in albums_d or album_name + ' (Deluxe)' in albums_d:
                continue
            else:
                albums_d[album_name] = album_id
        
        # pretty = json.dumps(albums_d, indent=4)
        # print(pretty)

        return albums_d


def get_album_tracks_using_cache(albums_dict, tracks_cache_filename):
    '''
    '''
    json_data = read_json(tracks_cache_filename)
    for album in albums_dict:
        if album in json_data:
            # print(f'Using cache for album: {album}')
            pass
        else:
            # print(f'Fetching data for album: {album}')
            try:
                # set up spotipy
                scope = "user-library-read"
                sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
                r = sp.album_tracks(albums_dict[album])
                if len(r) > 0:
                    json_data[album] = r
                    write_json(tracks_cache_filename, json_data)
            except:
                print('Exception')
                return None



def open_database(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn


def make_albums_table(albums_dict, cur, conn, num_inserts):
    '''
    '''
    cur.execute("CREATE TABLE IF NOT EXISTS Albums (id INTEGER PRIMARY KEY, album TEXT)")
    albums = list(albums_dict.keys())
    
    cur.execute('select count(album) from Albums')
    count = cur.fetchone()[0]
    while count < len(albums) and num_inserts < 25:
        cur.execute("INSERT OR IGNORE INTO Albums (id,album) VALUES (?,?)",(count,albums[count]))
        cur.execute('select count(album) from Albums')
        count = cur.fetchone()[0]
        num_inserts += 1
    conn.commit()
    print(count, "albums in database")
    return num_inserts


def make_tracks_table(tracks_cache_filename, cur, conn, num_inserts):
    '''
    '''
    cur.execute("CREATE TABLE IF NOT EXISTS Tracks (title TEXT PRIMARY KEY, album_id INTEGER, lyrics_id INTEGER)")

    json_data = read_json(tracks_cache_filename)

    track_d = {}
    for album in json_data:

        cur.execute('select id from Albums where album = ?', (album,))
        album_id = cur.fetchone()[0]

        album_tracks = json_data[album]['items']

        for i in range(len(album_tracks)):
            track = album_tracks[i]
            title = track['name']
            track_d[title] = album_id
    
    # pretty = json.dumps(track_d, indent=4)
    # print(pretty)

    cur.execute('select count(title) from Tracks')
    count = cur.fetchone()[0]
    all_titles = list(track_d.keys())
    while count < len(track_d) and num_inserts < 25:
        cur.execute("INSERT OR IGNORE INTO Tracks (title,album_id,lyrics_id) VALUES (?,?,?)",(all_titles[count],track_d[all_titles[count]],count))
        cur.execute('select count(title) from Tracks')
        count = cur.fetchone()[0]
        num_inserts += 1
    conn.commit()
    print(count, "track in database")
    return num_inserts


def get_album_lyrics_using_cache(access_token, cur, conn):
    
    # Execute the SELECT statement to search for the album
    cur.execute("SELECT album FROM Albums")
        
    # Retrieve the results of the query
    albums = cur.fetchall()
    # print(albums)
    
    # Connect to the Genius API using the `Genius` object
    genius = Genius(access_token)
    genius.remove_section_headers = True
    genius.timeout = 20

    # album = genius.search_album('Views', 'Drake')
    # album.save_lyrics()
    
    for index in range(len(albums)):
        
        album_name = albums[index][0]
        album_name = album_name.replace(' (Deluxe)', '')
        album_name = album_name.replace("'", '\u2019')
        cache_filename = 'album' + str(index) + '_lyrics.json'
        json_data = read_json(cache_filename)
        
        # print(json_data['name'].lower())
        # print(album_name.lower())
        
        if json_data['name'].lower() == album_name.lower():
            # print(f'Using cache for album lyrics: {album_name}')
            pass
        else:
            # print(f'Fetching data for album lyrics: {album_name}')
            try:
                # Search for the album using the `search_album` method
                album = genius.search_album(album_name, 'Drake')

                # Save the lyrics for all of the tracks in the album to a file using the `save_lyrics` method of the `Album` object
                album.save_lyrics(filename='album' + str(index) + '_lyrics')
            except:
                print("Exception")
        

def get_all_lyrics_cache(all_lyrics_cache, cur):

    json_data = read_json(all_lyrics_cache)

    cur.execute("SELECT album FROM Albums")
    albums = cur.fetchall()
    for index in range(len(albums)):
        curr_cache_filename = 'album' + str(index) + '_lyrics.json'
    
        if curr_cache_filename in json_data:
            # print(f'Using cache for {curr_cache_filename}')
            pass
        else:
            # print(f'Fetching data for {curr_cache_filename}')
            try:
                curr_lyrics_data = read_json(curr_cache_filename)
                if len(curr_lyrics_data) > 0:
                    json_data[curr_cache_filename] = curr_lyrics_data
                    write_json(all_lyrics_cache, json_data)
            except:
                print('Exception')
                return None


def make_lyrics_table(all_lyrics_cache_filename, cur, conn, num_inserts):
    '''
    '''
    cur.execute("CREATE TABLE IF NOT EXISTS Lyrics (id INTEGER PRIMARY KEY, lyrics Text)")

    json_data = read_json(all_lyrics_cache_filename)
    # print(len(json_data))
    # exit

    lyrics_d = {}
    count = 0
    for album in json_data:

        # cur.execute('select id from Albums where album = ?', (album,))
        # album_id = cur.fetchone()[0]

        album_tracks = json_data[album]['tracks']

        for i in range(len(album_tracks)):
            track = album_tracks[i]
            lyrics = track['song']['lyrics']
            lyrics_d[count] = lyrics
            count += 1

    # print(len(lyrics_d), 'is the length of lyrics_d')
    # pretty = json.dumps(track_d, indent=4)
    # print(pretty)
    
    cur.execute('select count(id) from Lyrics')
    count = cur.fetchone()[0]
    # all_titles = list(track_d.keys())
    while count < len(lyrics_d) and num_inserts < 25 and count <= 242:
        cur.execute("INSERT OR IGNORE INTO Lyrics (id,lyrics) VALUES (?,?)",(count,lyrics_d[count]))
        cur.execute('select count(id) from Lyrics')
        count = cur.fetchone()[0]
        num_inserts += 1
    conn.commit()
    print(count, "lyrics in database")
    return num_inserts
    

def main():

    dir_path = os.path.dirname(os.path.realpath(__file__))

    albums_cache_filename = dir_path + '/' + 'albums_cache.json'
    tracks_cache_filename = dir_path + '/' + 'tracks_cache.json'

    # carti
    # artist_id = '699OTQXzgjhIYAHMy9RyPD'

    # drake
    artist_id = '3TVXtAsR1Inumwj472S9r4'

    get_artist_albums_using_cache(artist_id, albums_cache_filename)

    albums_dict = get_albums_dict(albums_cache_filename)
    get_album_tracks_using_cache(albums_dict, tracks_cache_filename)

    cur, conn = open_database('artist.db')

    num_inserts = 0

    num_inserts = make_albums_table(albums_dict, cur, conn, num_inserts)
    num_inserts = make_tracks_table(tracks_cache_filename, cur, conn, num_inserts)

    all_lyrics_cache_filename = dir_path + '/' + 'all_lyrics_cache.json'
    get_all_lyrics_cache(all_lyrics_cache_filename, cur)

    make_lyrics_table(all_lyrics_cache_filename, cur, conn, num_inserts)

    # lyrics_cache_list = make_lyrics_cache_list(cur)

    # lyrics_cache_filename = dir_path + '/' + 'album0_lyrics.json'

    # for lyrics_cache in lyrics_cache_list:
    #     lyrics_cache_filename = dir_path + '/' + lyrics_cache
    #     make_lyrics_table(lyrics_cache_filename, cur, conn, num_inserts)

    # LYRIC GENIUS

    access_token = "2iJsfr57QmSN6BoVkRHMCpX6ego21l36FvlflKlTCIeDNULc-LIhro64fDzcloUa"

    get_album_lyrics_using_cache(access_token, cur, conn)

    conn.close()

if __name__ == "__main__":
    main()

import json
import unittest
import os
import requests
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
from lyricsgenius import Genius

def get_albums(access_token, db_path):
    # Connect to the database

    conn = sqlite3.connect(db_path)

    # Create a cursor
    cursor = conn.cursor()

    # # Execute the SELECT statement to search for the album
    cursor.execute("SELECT album FROM Albums")
        
    # Retrieve the results of the query

    results = cursor.fetchall()

    # album_name = "Whole Lotta Red"
    # artist_name = "Playboi Carti"
    # print("Query results:", results)

    # Connect to the Genius API using the `Genius` object
    genius = Genius(access_token)

    while results:
        album_name = results.pop(0)[0]
        try:
             # Search for the album using the `search_album` method
            album = genius.search_album(album_name)

            # Save the lyrics for all of the tracks in the album to a file using the `save_lyrics` method of the `Album` object
            if not os.path.exists(album_name):
                album.save_lyrics()
        except FileExistsError:
        #     # Print an error message if an exception is thrown
            print("This album's lyrics are already saved.")

    # if len(results) > 0:
    #     for album_name in results:
    #         # try:
    #             album = genius.search_album(album_name[0])

    #             # print(album_name)

    #             for i, track in enumerate(album.tracks):
    #                 try:

    #                     album.save_lyrics()
    #                 except:
    #                     print("Error saving lyrics", track.title)
    #                     continue

    #                 if track.lyrics:    
    #                 # Insert the lyrics data into the database
    #                     cursor.execute("INSERT OR IGNORE INTO Tracks (lyrics) VALUES (?)", (track.lyrics))

    #                 if i == 24:
    #                     break

    #         # except:
    #         #     print("Error searching for album:", album_name[0])
    #         #     continue
            
    # Commit the transaction
    conn.commit()

    # insert_lyrics("lyrics.db", "Playboi Carti")

    # Close the connection
    conn.close()

import json
import sqlite3

def parse_json(json_files, db_path):
    try:
        # Connect to the database and create a cursor to execute SQL statements
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if the table exists before creating it
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Lyrics'")
        if not cursor.fetchone():
            cursor.execute("CREATE TABLE Lyrics (id INTEGER PRIMARY KEY, lyrics TEXT)")

        for json_file in json_files:
            # Parse the JSON data from the file
            with open(json_file, 'r') as f:
                data = json.load(f)

            # Use a list comprehension to create a list of tuples containing the lyrics for each track in the JSON data
            track_lyrics = [(track['song']['lyrics']) for track in data['tracks']]

            # Insert all of the track lyrics into the "Lyrics" table in a single query
            cursor.executemany("INSERT INTO Lyrics (lyrics) VALUES (?)", track_lyrics)

        # Commit any changes made to the database and close the connection
        conn.commit()

    except Exception as e:
        # Handle any errors that may occur
        print(e)

    finally:
        conn.close()

def main():
    ACCESS_TOKEN = "2iJsfr57QmSN6BoVkRHMCpX6ego21l36FvlflKlTCIeDNULc-LIhro64fDzcloUa"
    DB_PATH = "artist.db"
    json_files = ["Lyrics_HerLoss.json", "Lyrics_HonestlyNevermind.json", "Lyrics_CertifiedLoverBoy.json", "Lyrics_DarkLaneDemoTapes.json", "Lyrics_CarePackage.json", "Lyrics_SoFarGone.json", "Lyrics_Scorpion.json", "Lyrics_MoreLife.json", "Lyrics_Views.json", "Lyrics_WhataTimeToBeAlive.json", "Lyrics_IfYoureReadingThisItsTooLate.json", "Lyrics_NothingWasTheSame.json", "Lyrics_TakeCare.json", "Lyrics_ThankMeLater.json"]
    get_albums(ACCESS_TOKEN, DB_PATH)
    parse_json(json_files, DB_PATH)

if __name__ == "__main__":
    main()
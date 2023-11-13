import os
import json
import requests
import matplotlib.pyplot as plt
import sqlite3
from collections import Counter
import re


def write_json(cache_filename, dict):
    '''
    '''  
    json_str = json.dumps(dict, indent=4)
    file = open(cache_filename, 'w')
    file.write(json_str)
    file.close()


def discography_wordcount(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT Lyrics.lyrics FROM Lyrics JOIN Tracks ON Lyrics.id = Tracks.lyrics_id")
    # SELECT Lyrics.lyrics FROM Lyrics JOIN Tracks ON Lyrics.id = Tracks.lyrics_id JOIN Albums ON Tracks.album_id = Albums.id WHERE Tracks.album_id = [ID_OF_ALBUM]"
    results = cur.fetchall()
    # print(len(results))

    # Create a dictionary to store the word counts
    word_counts = {}

    # test_lyrics = ["Dreams Money Can Buy Lyrics[Intro: Jai Paul]\nOoh-ooh-ooh, ooh-ooh-ooh-ooh\nOoh-ooh-ooh, ooh-ooh-ooh-ooh\nOoh-ooh-ooh, ooh-ooh-ooh-ooh\nOoh-ooh-ooh, ooh-ooh, ooh-ooh\n\n[Chorus: Jai Paul]\nDon't fuck with me, don't fuck with me\nDon't fuck with me, don't fuck with me\nDon't fuck with me, don't fuck with me (Don't)\n\n[Verse 1: Drake]\nI got car money, fresh start money\nI want Saudi money, I want art money\nI want women to cry and pour out they heart for me\nAnd tell me how much they hate it when they apart from me\nYeah, and lately I do bitches the meanest\nTell 'em I love 'em and don't ever mean it\nWe go on dates, I send the Maybach out in neighborhoods\nThey never seen it\nThat shit is dangerous, but it's so convenient, I ain't lying\nYeah, and comfortable I sit\nThat manual Ferrari Italia's some fly shit\nIt's sitting at the house like I bought it in '96\n'Cause honestly I'm too fucking busy to drive stick, I swear\nToo fucking busy, too busy fuckin'\nThis nigga girl, but to me she wasn't\nBeen hot before they open doors for me, pre-heated oven\nI'm in this ho\nBut I ain't finished though, it's been a minute though\nMy newest girl from back home got issues with parents\nAnd some charges, how the fuck can I get her to Paris?\nLuckily, I'm the greatest my country's ever seen\nSo chances are I get the border to issue me clearance\nDreams money can buy\nEverybody yelled \"Surprise!\", I wasn't surprised\nThat's only 'cause I been waiting on it, nigga\nSo fuck whoever hating on a nigga\nOf course...\nSee Drake LiveGet tickets as low as $162You might also like[Chorus]\nDon't fuck with me, don't fuck with me (Don't)\nDon't fuck with me, don't fuck with me (Don't)\nDon't fuck with me, don't fuck with me (Don't)\nDon't fuck with me, don't fuck with me (Don't)\n\n[Verse 2: Drake]\nFood from India, she in Charlotte Olympias\nWe talked music for hours, she never mentioned ya\nCan't tell you how much I love when niggas think they got it\nAnd I love the fact that line made 'em think about it\nYMCMB\nThese niggas make it so hard to be friendly\nWhen I know part of it's envy\nTryna fill the shoes, nigga, so far, these are empty\nI take 'em off in the house because the throw carpets are Fendi\nOoh! I never seen the car you claim to drive\nOr, shit, I seen it; you just ain't inside\nAnd I feel like lately, it went from top five to remaining five\nMy favorite rappers either lost it or they ain't alive\nAnd they tryna bring us down, me, Weezy, and Stunna\nWe stayed up, Christmas lights in the middle of summer\nAnd if the girl standing next to me got a fat ass\nThen I'll probably give her my number\nYeah, I throw my dollars up high\nAnd they land on the stage you dance on\nWe got company coming over\nWould it kill you to put some pants on?\nDreams money can buy\nThey told me it's like a high, and it wasn't a lie, yeah\nJust have some good pussy waiting on a nigga\nAnd fuck whoever hating on a nigga\nAw, yeah\n[Chorus: Jai Paul]\nDon't fuck with me, don't fuck with me (Don't)\nDon't fuck with me, don't fuck with me (Don't)\nDon't fuck with me, don't fuck with me (Don't)\nDon't fuck with me, don't fuck with me (Don't)\n\n[Outro: Jai Paul]\nDon't\nDon't fuck with me, don't fuck with me\nDon't45Embed"]

    # for lyrics in test_lyrics:
    #     words = lyrics.split()
    # Iterate over the retrieved rows
    for lyrics in results:
        # Split the lyrics into individual words
        words = lyrics[0].lower().split()

        # Iterate over the words in the lyrics
        for word in words:
            word = word.strip('(),')
            # If the word is not already in the dictionary, add it with a count of 1
            if word not in word_counts:
                word_counts[word] = 1
            # If the word is already in the dictionary, increment its count by 1
            else:
                word_counts[word] += 1

    # Sort the word counts in descending order by count
    sorted_word_counts = dict(sorted(word_counts.items(), key=lambda x: x[1],)[-50:])

    # print(len(sorted_word_counts))
    pretty = json.dumps(sorted_word_counts, indent=4)
    print(pretty)

     # for word, count in sorted_word_counts:
    #     print(f"{word}: {count}")

    # Print the most common words and their counts
    counts = [sorted_word_counts[word] for word in sorted_word_counts]
    words = list(sorted_word_counts.keys())
    plt.figure(figsize=(12,8))
    plt.barh(words, counts)
    plt.xlabel('Counts')
    plt.ylabel('Words')
    plt.title("Most Common Words in Drake's Discography")
    plt.tight_layout()
    plt.show()
    
    return sorted_word_counts

def love_per_album(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT Albums.album, Lyrics.lyrics FROM Lyrics JOIN Tracks ON Lyrics.id = Tracks.lyrics_id JOIN Albums ON Tracks.album_id = Albums.id")
    results = cur.fetchall()
    print(results[-1])

    love_counts = {}

    # test_lyrics = ["Dreams Money Can Buy Lyrics[Intro: Jai Paul]\nOoh-ooh-ooh, ooh-ooh-ooh-ooh\nOoh-ooh-ooh, ooh-ooh-ooh-ooh\nOoh-ooh-ooh, ooh-ooh-ooh-ooh\nOoh-ooh-ooh, ooh-ooh, ooh-ooh\n\n[Chorus: Jai Paul]\nDon't fuck with me, don't fuck with me\nDon't fuck with me, don't fuck with me\nDon't fuck with me, don't fuck with me (Don't)\n\n[Verse 1: Drake]\nI got car money, fresh start money\nI want Saudi money, I want art money\nI want women to cry and pour out they heart for me\nAnd tell me how much they hate it when they apart from me\nYeah, and lately I do bitches the meanest\nTell 'em I love 'em and don't ever mean it\nWe go on dates, I send the Maybach out in neighborhoods\nThey never seen it\nThat shit is dangerous, but it's so convenient, I ain't lying\nYeah, and comfortable I sit\nThat manual Ferrari Italia's some fly shit\nIt's sitting at the house like I bought it in '96\n'Cause honestly I'm too fucking busy to drive stick, I swear\nToo fucking busy, too busy fuckin'\nThis nigga girl, but to me she wasn't\nBeen hot before they open doors for me, pre-heated oven\nI'm in this ho\nBut I ain't finished though, it's been a minute though\nMy newest girl from back home got issues with parents\nAnd some charges, how the fuck can I get her to Paris?\nLuckily, I'm the greatest my country's ever seen\nSo chances are I get the border to issue me clearance\nDreams money can buy\nEverybody yelled \"Surprise!\", I wasn't surprised\nThat's only 'cause I been waiting on it, nigga\nSo fuck whoever hating on a nigga\nOf course...\nSee Drake LiveGet tickets as low as $162You might also like[Chorus]\nDon't fuck with me, don't fuck with me (Don't)\nDon't fuck with me, don't fuck with me (Don't)\nDon't fuck with me, don't fuck with me (Don't)\nDon't fuck with me, don't fuck with me (Don't)\n\n[Verse 2: Drake]\nFood from India, she in Charlotte Olympias\nWe talked music for hours, she never mentioned ya\nCan't tell you how much I love when niggas think they got it\nAnd I love the fact that line made 'em think about it\nYMCMB\nThese niggas make it so hard to be friendly\nWhen I know part of it's envy\nTryna fill the shoes, nigga, so far, these are empty\nI take 'em off in the house because the throw carpets are Fendi\nOoh! I never seen the car you claim to drive\nOr, shit, I seen it; you just ain't inside\nAnd I feel like lately, it went from top five to remaining five\nMy favorite rappers either lost it or they ain't alive\nAnd they tryna bring us down, me, Weezy, and Stunna\nWe stayed up, Christmas lights in the middle of summer\nAnd if the girl standing next to me got a fat ass\nThen I'll probably give her my number\nYeah, I throw my dollars up high\nAnd they land on the stage you dance on\nWe got company coming over\nWould it kill you to put some pants on?\nDreams money can buy\nThey told me it's like a high, and it wasn't a lie, yeah\nJust have some good pussy waiting on a nigga\nAnd fuck whoever hating on a nigga\nAw, yeah\n[Chorus: Jai Paul]\nDon't fuck with me, don't fuck with me (Don't)\nDon't fuck with me, don't fuck with me (Don't)\nDon't fuck with me, don't fuck with me (Don't)\nDon't fuck with me, don't fuck with me (Don't)\n\n[Outro: Jai Paul]\nDon't\nDon't fuck with me, don't fuck with me\nDon't45Embed"]

    # for lyrics in test_lyrics:
    #     words = lyrics.split()
    # Iterate over the retrieved rows
    for album, lyrics in results:
        # love_counts[album] = 0
        # Split the lyrics into individual words
        words = lyrics.lower().split()

        # Iterate over the words in the lyrics
        for word in words:
            word = word.strip('(),')
            # If the word is not already in the dictionary, add it with a count of 1
            if word == 'love':
                love_counts[album] = love_counts.get(word, 0) + 1
            # If the word is already in the dictionary, increment its count by 1
            # else:
            #     word_counts[word] += 1
    
    pretty = json.dumps(love_counts, indent=4)
    print(pretty)

    # Sort the word counts in descending order by count
    sorted_word_counts = dict(sorted(word_counts.items(), key=lambda x: x[1],)[-50:])
    # print(len(sorted_word_counts))
    pretty = json.dumps(sorted_word_counts, indent=4)
    print(pretty)


def main():
    db_path = "artist.db"
    sorted_word_counts = discography_wordcount(db_path)


    dir_path = os.path.dirname(os.path.realpath(__file__))
    calculations_filename = dir_path + '/' + 'calculations.json'
    write_json(calculations_filename, sorted_word_counts)



    # love_per_album(db_path)


if __name__ == '__main__':
    main()

import urllib.request
import urllib.parse
import pydub
import os
from stream import Stream
from muzisapi.api import stream_from_values

audio_url = 'http://f.muzis.ru/{name}'

def concatenate_audio(songs_list, params=None):
    # TODO: добавить параметры слкеивания
    """
    Склеиваем треки в один большой
    :param songs_list: [<Song>, ...]
    :type songs_list: list[<Song>]
    :return: concatenated audio
    :rtype: pydub.AudioSegment
    """
    song_urls = get_song_urls(songs_list)
    sounds = []
    for url in song_urls:
        local_filename, _headers = urllib.request.urlretrieve(audio_url.format(name=url), filename=url)
        sounds.append(pydub.AudioSegment.from_mp3(local_filename))
        os.remove(local_filename)
    playlist = pydub.AudioSegment.empty()
    for sound in sounds:
        playlist += sound
    return playlist


def get_song_urls(playlist):
    return [song['file_mp3'] for song in playlist]

def get_playlist(db, user_id):
    name = db.current.find_one({'user_id': user_id})['name']

    playlist = dict(db.playlists.find_one({'name': name}))
    values = [playlist.pop('g', None), playlist.pop('e', None), playlist.pop('t', None)]
    values = {'values': ','.join(['{}:200'.format(x) for x in values if x])}

    return stream_from_values(values)[:playlist['l'] if 'l' in playlist else 10]


def generate_audio(db, user_id):
    name = db.current.find_one({'user_id': user_id})['name']

    try:
        os.mkdir('files')
    except:
        pass

    playlist = get_playlist(db, user_id)
    concatenated = concatenate_audio(playlist)
    concatenated.export('files/{}.mp3'.format(name), format='mp3')
    return playlist, 'http://162.243.2.164/{}.mp3'.format(urllib.parse.quote(name))

def generate_stream(db, user_id):
    name = db.current.find_one({'user_id': user_id})['name']

    playlist = get_playlist(db, user_id)
    song_urls = get_song_urls(playlist)

    # TODO: DB: GET PLAYLIST NAME or ID
    s = Stream(name, song_urls)
    s.cache_songs()
    s.start()

    # TODO DB!!!
    db.streams.insert_one({'stream_id': stream_id, 'user_id': update.message.from_user.id})

    return s.get_stream_url()
import urllib.request
import urllib.parse
import pydub
import os
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
    song_names = [song['file_mp3'] for song in songs_list]
    sounds = []
    for file_name in song_names:
        local_filename, _headers = urllib.request.urlretrieve(audio_url.format(name=file_name),
                                                              filename=file_name)
        sounds.append(pydub.AudioSegment.from_mp3(local_filename))
        os.remove(local_filename)
    playlist = pydub.AudioSegment.empty()
    for sound in sounds:
        playlist += sound
    return playlist


def generate_audio(db, user_id):
    name = db.current.find_one({'user_id': user_id})['name']

    playlist = dict(db.playlists.find_one({'name': name}))
    values = [playlist.pop('g', None), playlist.pop('e', None), playlist.pop('t', None)]
    values = {'values': ','.join(['{}:200'.format(x) for x in values if x])}

    res = stream_from_values(values)[:playlist['l'] if 'l' in playlist else 10]

    concatenated = concatenate_audio(res)
    concatenated.export('files/{}.mp3'.format(name), format='mp3')
    return res, 'http://162.243.2.164/{}.mp3'.format(urllib.parse.quote(name))

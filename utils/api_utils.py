import urllib.request
import pydub
import os

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




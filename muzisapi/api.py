import requests

base_url = 'http://muzis.ru/api/{method}'

url_stream_from_values = 'stream_from_values.api'
url_stream_from_lyrics = 'stream_from_lyrics.api'


def stream_from_values(data):
    url = base_url.format(method=url_stream_from_values)

    return requests.post(url, data).json()['songs']


def stream_from_lyrics(data):
    url = base_url.format(method=url_stream_from_lyrics)
    return requests.post(url, data).json()['songs']

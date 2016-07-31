def get_playlist_params(handler, plst_name):
    """
    Выводим список параметров плейлиста по его имени
    :param handler:
    :param plst_name:
    :return:
    """
    plst = handler.db.playlists.find_one({'name': plst_name})
    names = dict(handler.config['names'])
    text_json = {k: v for k, v in plst.items() if k in names}
    reversed_items = {k: {vv: kk for kk, vv in v.items()} for k, v in handler.config['buttons'].items()}
    return '\n'.join(['_{}: {}_'.format(names[k], reversed_items[k][v])
                      for k, v in text_json.items()]
                     )

BASE_DIR = 'E:/Microsoft/LogNet - General/'
CACHE_DIR = BASE_DIR + 'RawLogsCache/'


def get_bingchat_path(file_id):
    return CACHE_DIR + '20240116_bing_text_mining/' + file_id


def get_ja3_path(file_id):
    return CACHE_DIR + '20231224_bing_ja3/' + file_id

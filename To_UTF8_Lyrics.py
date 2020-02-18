#-*- coding:utf-8 -*- #

import os

path = './'
for root, dirs, files in os.walk(path):
    lyric_fs = [file for file in files if file.endswith('.lrc')]
    for lyric_f in lyric_fs:
        with open(os.path.join(root, lyric_f), 'rb') as f:
            b_lyrics = f.read()
            try:
                gb_lyrics = b_lyrics.decode('gb2312')
            except UnicodeDecodeError:
                continue
            utf_lyrics = gb_lyrics.encode('utf-8')
        with open(os.path.join(root, lyric_f), 'wb') as f:
            f.write(utf_lyrics)
            print('Recode [' + lyric_f + '] to UTF-8')


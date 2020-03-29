# -*- coding:utf-8 -*- #

'''
    Created on Sunday Feb 16 22:46 2020
    Author           : Mi-Dora
    Email            : 1239988498@qq.com
    Last edit date   : Feb 19 16:08 2020
'''

'''
*******************************************************************************
Description:
    This file is used to transcode .lrc file from "GB2312" to "UTF-8".
    In case messy code shown on some players.
*******************************************************************************
'''

import os

path = 'F:/MusicDownload/Walkman'

if os.path.exists('lyrics_log.txt'):
    os.remove('lyrics_log.txt')
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
        if os.path.exists('lyrics_log.txt'):
            with open('lyrics_log.txt', 'a') as log:
                log.write('Recode [' + lyric_f + '] to UTF-8\n')
        else:
            with open('lyrics_log.txt', 'w') as log:
                log.write('Recode [' + lyric_f + '] to UTF-8\n')

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

from mutagen import flac, mp3, dsf, wavpack, File, id3, MutagenError
import os
import shutil

path = 'D:/Desktop/Temp/Walkman'
sub_cover_path = 'D:/Pictures/Cover'
audio_suffix = ('.flac', '.mp3', '.wav', '.dff', '.ape', '.dsf')

no_cover = []
has_type = []
MutagenErrors = []


def cut_suffix(name):
    suffix = name.split('.')[-1]
    suffix_len = len(suffix) + 1
    cut = name[:-suffix_len]
    return cut


def remove_cover_file(abs_audio_fs):
    for abs_audio_f in abs_audio_fs:
        os.remove(cut_suffix(abs_audio_f) + '.jpg')


def match_logic(root, audio_f):
    # Try to match in Cover Folder
    priority = 100
    matched = ''
    loc_root = root[len(path):]
    audio_name = cut_suffix(audio_f)
    artist = loc_root.split('\\')[0].split('/')[0]
    album = loc_root.split('\\')[-1].split('/')[-1]  # [album] can be identical with [artist]
    for cover_root, _, files in os.walk(sub_cover_path):
        for file in files:
            cover_name = cut_suffix(file)
            if audio_name.find(cover_name) != -1:
                priority = 0
                matched = os.path.join(cover_root, file)
                break
            elif album.find(cover_name) != -1:
                if priority > 1:
                    priority = 1
                    matched = os.path.join(cover_root, file)
            elif artist.find(cover_name) != -1:
                if priority > 2:
                    priority = 2
                    matched = os.path.join(cover_root, file)
    if matched:
        shutil.copy(matched, os.path.join(root, audio_name + matched[-4:]))
        return True
    return False


def cover_substitute(root, audio_f):
    if sub_cover_path and match_logic(root, audio_f):
        return
    jpgs = []
    for _, _, files in os.walk(root):
        jpgs = [file for file in files if file.endswith('.jpg')]
    if len(jpgs) == 0:
        no_cover.append(audio_f)
    else:
        try:
            shutil.copy(os.path.join(root, jpgs[0]), os.path.join(root, cut_suffix(audio_f) + '.jpg'))
        except:
            pass


def find_audio(path='./'):
    abs_audio_fs = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(audio_suffix):
                abs_audio_fs.append(os.path.join(root, file))
                export_cover(root, file)
                if file.split('.')[-1] not in has_type:
                    has_type.append(file.split('.')[-1])
        # The order of covers exported may influence the result.
        # So check again for audio with no cover
        for file in files:
            if file in no_cover:
                no_cover.remove(file)
                cover_substitute(root, file)
    return abs_audio_fs


def export_cover(root, audio_f):
    if audio_f.endswith('.mp3'):
        export_mp3(root, audio_f)
    elif audio_f.endswith('.flac'):
        export_flac(root, audio_f)
    # elif audio_f.endswith('.wav'):
    #     export_wav(root, audio_f)
    # else:
    #     print('Sorry! Type [' + audio_f.split('.')[-1] + '] is not supported yet.')


def check_cover(audio_f):
    metadata = File(audio_f)
    try:
        x = metadata.pictures
        if x:
            return True
    except Exception:
        pass
    if 'covr' in metadata:
        return True
    return False


def export_mp3(root, audio_f):
    metadata = File(os.path.join(root, audio_f))
    try:
        artwork = metadata.tags['APIC:'].data
        # title = metadata.tags["TIT2"].text[0]
        if os.path.exists(os.path.join(root, audio_f[:-4] + '.jpg')):
            return
        with open(os.path.join(root, audio_f[:-4]) + '.jpg', 'wb') as img:
            img.write(artwork)
            print('Export ' + os.path.join(root, audio_f[:-4]) + '.jpg')
    except:
        cover_substitute(root, audio_f)


def export_flac(root, audio_f):
    metadata = File(os.path.join(root, audio_f))
    try:
        data = metadata.pictures[0].data
        if os.path.exists(os.path.join(root, audio_f[:-5] + '.jpg')):
            return
        with open(os.path.join(root, audio_f[:-5] + '.jpg'), 'wb') as jpg_f:
            jpg_f.write(data)
            print('Export ' + os.path.join(root, audio_f[:-5]) + '.jpg')
    except IndexError:
        cover_substitute(root, audio_f)

# def export_wav(root, audio_f):
#     metadata = wavpack.(os.path.join(root, audio_f))
#     try:
#         data = metadata.pictures[0].data
#         with open(os.path.join(root, audio_f[:-5] + '.jpg'), 'wb') as jpg_f:
#             jpg_f.write(data)
#             print('Export ' + os.path.join(root, audio_f[:-5]) + '.jpg')
#     except IndexError:
#         cover_substitute(root, audio_f)

def insert_flac(abs_audio_f):
    cover = cut_suffix(abs_audio_f) + '.jpg'
    mime = u"image/jpeg"
    if not os.path.exists(cover):
        cover = cut_suffix(abs_audio_f) + '.png'
        mime = u"image/png"
        if not os.path.exists(cover):
            # print('Cover for [' + abs_audio_f + '] not found.')
            return
    audio = flac.FLAC(abs_audio_f)
    audio.clear_pictures()
    with open(cover, 'rb') as img_f:
        pic = flac.Picture()
        pic.data = img_f.read()
        pic.type = id3.PictureType.COVER_FRONT
        pic.mime = mime
        # pic.width = 500
        # pic.height = 500
        audio.add_picture(pic)
        try:
            audio.save()
        except MutagenError:
            MutagenErrors.append(abs_audio_f)


def insert_mp3(abs_audio_f):
    cover = cut_suffix(abs_audio_f) + '.jpg'
    mime = u"image/jpeg"
    if not os.path.exists(cover):
        cover = cut_suffix(abs_audio_f) + '.png'
        mime = u"image/png"
        if not os.path.exists(cover):
            # print('Cover for [' + abs_audio_f + '] not found.')
            return
    audio = id3.ID3(abs_audio_f)

    with open(cover, 'rb') as albumart:
        audio['APIC'] = id3.APIC(
            encoding=3,
            mime='image/jpeg',
            type=3, desc=u'Cover',
            data=albumart.read()
        )

    audio.save()
    # metadata = File(abs_audio_f)
    # with open(cover, 'rb') as img_f:
    #     metadata.tags.add(id3.APIC(encoding=3,  # 3 is for utf-8
    #                                mime=mime,  # image/jpeg or image/png
    #                                type=id3.PictureType.COVER_FRONT,  # 3 is for the cover image
    #                                data=img_f.read()
    #                                )
    #                       )
    #     metadata.save()


def insert_cover(abs_audio_fs, rm_cvr_f=False, overlap=False):
    for abs_audio_f in abs_audio_fs:
        if not overlap and check_cover(abs_audio_f):
            continue
        if abs_audio_f.endswith('.flac'):
            insert_flac(abs_audio_f)
        # elif abs_audio_f.endswith('.mp3'):
        #     insert_mp3(abs_audio_f)
        if rm_cvr_f:
            os.remove(cut_suffix(abs_audio_f) + '.jpg')
        # else:
        #     print('Sorry! Type [' + abs_audio_f.split('.')[-1] + '] is not supported yet.')


if __name__ == '__main__':
    abs_audio_files = find_audio(path)
    insert_cover(abs_audio_files, overlap=True)
    for audio in no_cover:
        print('No substitute found for ' + audio)
    print('Audio type included:\n', has_type)
    print('MutagenError:\n', MutagenErrors)
    with open('cover_log.txt', 'w') as log:
        if len(no_cover) > 0:
            log.write('No substitute found for:\n')
        else:
            log.write('All audio matches well!\n')
            print('All audio matches well!')
        for audio in no_cover:
            log.write('\t' + audio + '\n')
        log.write('Audio type included:\n' + str(has_type) + '\n')
        log.write('MemoryError:\n' + str(MutagenErrors) + '\n')



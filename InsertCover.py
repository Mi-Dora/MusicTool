#-*- coding:utf-8 -*- #

from mutagen import flac, mp3, dsf, wavpack, File, id3, MutagenError
import os
# import cv2
import shutil


path = './'
audio_suffix = ('.flac', '.mp3', '.wav', '.dff', '.ape', '.dsf')
no_cover = []
has_type = []
MutagenErrors = []

def cut_suffix(name):
    suffix = name.split('.')[-1]
    suffix_len = len(suffix)+1
    cut = name[:-suffix_len]
    return cut


def cover_substitute(root, audio_f):
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
    return abs_audio_fs


def export_cover(root, audio_f):
    if audio_f.endswith('.mp3'):
        export_mp3(root, audio_f)
    elif audio_f.endswith('.flac'):
        export_flac(root, audio_f)
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
        with open(os.path.join(root, audio_f[:-4]) + '.jpg', 'wb') as img:
            img.write(artwork)
            print('Export ' + os.path.join(root, audio_f[:-4]) + '.jpg')
    except:
        cover_substitute(root, audio_f)


def export_flac(root, audio_f):
    metadata = File(os.path.join(root, audio_f))
    try:
        data = metadata.pictures[0].data
        with open(os.path.join(root, audio_f[:-5] + '.jpg'), 'wb') as jpg_f:
            jpg_f.write(data)
            print('Export ' + os.path.join(root, audio_f[:-5]) + '.jpg')
    except IndexError:
        cover_substitute(root, audio_f)


def insert_flac(abs_audio_f):
    cover = abs_audio_f[:-5] + '.jpg'
    if os.path.exists(cover):
        audio = flac.FLAC(abs_audio_f)
        audio.clear_pictures()
        with open(cover, 'rb') as jpg_f:
            pic = flac.Picture()
            pic.data = jpg_f.read()
            pic.type = id3.PictureType.COVER_FRONT
            pic.mime = u"image/jpeg"
            # pic.width = 500
            # pic.height = 500
            audio.add_picture(pic)
            try:
                audio.save()
            except MutagenError:
                MutagenErrors.append(abs_audio_f)
    else:
        print('Cover for [' + abs_audio_f + '] not found.')


def insert_mp3(abs_audio_f):
    metadata = File(abs_audio_f)
    cover = abs_audio_f[:-4] + '.jpg'
    if os.path.exists(cover):
        with open(cover, 'rb') as jpg_f:
            metadata.tags.add(id3.APIC(encoding=3,  # 3 is for utf-8
                                       mime='image/jpeg',  # image/jpeg or image/png
                                       type=id3.PictureType.COVER_FRONT,  # 3 is for the cover image
                                       data=jpg_f.read()
                                       )
                              )
            metadata.save()


def insert_cover(abs_audio_fs, remove_cover_file=False, overlap=False):
    for abs_audio_f in abs_audio_fs:
        if not overlap and check_cover(abs_audio_f):
            continue
        if abs_audio_f.endswith('.flac'):
            insert_flac(abs_audio_f)
        elif abs_audio_f.endswith('.mp3'):
            insert_mp3(abs_audio_f)
        if remove_cover_file:
            os.remove(cut_suffix(abs_audio_f) + '.jpg')
        # else:
        #     print('Sorry! Type [' + abs_audio_f.split('.')[-1] + '] is not supported yet.')


if __name__ == '__main__':
    abs_audio_fs = find_audio(path)
    insert_cover(abs_audio_fs, overlap=True)
    for audio in no_cover:
        print('No substitute found for ' + audio)
    print('Audio type included:\n', has_type)
    print('MutagenError:\n', MutagenErrors)
    with open('log.txt', 'w') as log:
        log.write(u'No substitute found for:\n')
        for audio in no_cover:
            log.write(audio + '\n')
        log.write(u'Audio type included:\n' + str(has_type) + '\n')
        log.write(u'MemoryError:\n' + str(MutagenErrors) + '\n')
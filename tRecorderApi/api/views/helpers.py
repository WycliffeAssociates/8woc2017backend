import hashlib
import os
import re

from pydub import AudioSegment


def md5Hash(filename):
    hash_md5 = hashlib.md5()
    try:
        with open(filename, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return ""


def getFileName(location):
    return location.split(os.sep)[-1]


def getFilePath(location):
    list = location.split(os.sep)[3:]
    return "/".join(list)


def highPassFilter(location):
    song = AudioSegment.from_wav(location)
    new = song.high_pass_filter(80)
    new.export(location, format="wav")


def zip_files_root_directory():
    uuid_name = str(time.time()) + str(uuid.uuid4())
    project_root_directory = os.path.join(
        settings.BASE_DIR, 'media/export', uuid_name)
    if not os.path.exists(project_root_directory):
        return os.makedirs(project_root_directory)
    return project_root_directory


def remove_file_tree(project_root_directory):
    shutil.rmtree(project_root_directory)


def path(directory, project_name=None, file_extension=None):
    return os.path.join(settings.BASE_DIR,
                        directory,
                        project_name + file_extension)

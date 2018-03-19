import json
import os
import pickle
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from platform import system as system_name
from raven.contrib.django.raven_compat.models import client
from ..models.language import Language
from ..models.book import Book
from ..models.anthology import Anthology
from ..models.version import Version
from ..models.mode import Mode
from ..models.project import Project
from ..models.chapter import Chapter
from ..models.chunk import Chunk
import logging

import urllib3

from ..file_transfer.tinytag import TinyTag

logger = logging.getLogger(__name__)


class FileUtility:
    @staticmethod
    def root_dir(root_dir_of):
        directory = ''
        for dir in root_dir_of:
            directory = os.path.join(directory, dir)
        base_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))

        uuid_name = str(time.time()) + str(uuid.uuid4())
        root_directory = os.path.join(base_dir, directory, uuid_name)

        if not os.path.exists(root_directory):
            os.makedirs(root_directory)
        return root_directory

    def copy_files_from_src_to_dest(self, location_list):
        for location in location_list:
            shutil.copy2(location["src"], location["dst"])

    def import_project(self, directory):
        bad_files = []
        project_manifest = self.open_manifest_file(directory)
        language = Language.import_language(project_manifest["language"])
        anthology = Anthology.import_anthology(project_manifest["anthology"])
        book = Book.import_book(project_manifest["book"], anthology)
        version = Version.import_version(project_manifest["version"])
        mode = Mode.import_mode(project_manifest["mode"])
        project = Project.import_project(
            version, mode, anthology, language, book)

        for chapters in project_manifest["manifest"]:
            number = chapters["chapter"]
            checking_level = chapters["checking_level"]
            chapter = Chapter.import_chapter(project, number, checking_level)

            for chunks in chapters["chunks"]:
                startv = chunks["startv"]
                endv = chunks["endv"]
                chunk = Chunk.import_chunk(chapter, startv, endv)

                for take in chunks["takes"]:
                    from ..models.take import Take
                    file = os.path.join(directory, take["name"])
                    try:
                        meta = TinyTag.get(file)
                    except Exception as e:
                        os.remove(file)
                        bad_files.append(take["name"])
                        continue

                    markers = self.get_markers(meta)
                    rating = take["rating"]
                    duration = meta.duration
                    self.push_audio_processing_to_background(file)
                    Take.import_takes(FileUtility.relative_path(file), duration, markers, rating, chunk)
        if len(bad_files) > 0:
            return bad_files, 202
        return 'ok', 200

    @staticmethod
    def get_markers(meta):
        a = meta.artist
        lastindex = a.rfind("}") + 1
        substr = a[:lastindex]
        take_info = json.loads(substr)
        markers = json.dumps(take_info['markers'])
        return markers

    @staticmethod
    def open_manifest_file(directory):

        try:
            manifest_path = os.path.join(directory, 'manifest.json')
            manifest = json.load(open(manifest_path))
            return manifest
        except FileNotFoundError:
            shutil.rmtree(directory)
            logger.error("File Not Found: ", manifest_path)

    @staticmethod
    def push_audio_processing_to_background(take):
        return take

    @staticmethod
    def processTrFile(file, directory):
        with open(os.path.join(directory, "source.tr"), 'wb') as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
            try:
                FNULL = open(os.devnull, 'wb')
                base_dir = os.path.dirname(os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__))))

                path = os.path.join(base_dir, "aoh", "aoh.jar")
                file_path = os.path.join(os.path.join(directory, "source.tr"))

                subprocess.check_output(
                    ['java', '-jar', path, '-x', file_path],
                    stderr=subprocess.STDOUT
                )

                temp_file.close()
                os.remove(os.path.join(directory, 'source.tr'))

                FNULL.close()

                return 'ok', 200

            except Exception as e:
                shutil.rmtree(directory)
                return str(e), 400

    def create_path(self, root_dir, lang_slug, version, book_slug, chapter_number):
        path = os.path.join(root_dir, lang_slug, version,
                            book_slug, chapter_number)

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def create_folder_path(self, root_dir, lang, version, book):
        return os.path.join(root_dir, lang, version, book)

    def create_chapter_path(self, root_dir, lang, version, book, chapter_number):
        path = os.path.join(self.create_folder_path(
            root_dir, lang, version, book), chapter_number)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def take_location(self, take_location):
        return os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__)
                    )
                )
            ),
            take_location
        )

    @staticmethod
    def relative_path(location):
        return os.path.relpath(location, os.path.dirname("tRecorderApi"))

    def copy_files_from_src_to_dest(self, location_list):

        for location in location_list:
            shutil.copy2(location["src"], location["dst"])

    def copy_files(self, src, dst):
        base_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        shutil.copy2(os.path.join(base_dir, src), dst)
        return os.path.join(dst, os.path.basename(src))

    def project_file(self, project_name, dir_of, file_extension):
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), dir_of,
                            project_name + file_extension)

    def remove_dir(self, dir_to_remove):
        shutil.rmtree(dir_to_remove)

    @staticmethod
    def remove_file(file):
        os.remove(file)

    def rename(self, oldname, newname):
        os.rename(oldname, newname)

    def create_tr_path(self, media, tmp, filename):
        base_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_dir, media, tmp, filename + ".tr")

    def compile_into_tr(self, root_dir):
        base_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        FNULL = open(os.devnull, 'w')
        subprocess.call(
            ['java', '-jar', os.path.join(
                base_dir, 'aoh', 'aoh.jar'), '-c', '-tr', root_dir],
            stdout=FNULL, stderr=subprocess.STDOUT)
        FNULL.close()

    @staticmethod
    def check_if_path_exists(path):
        path_exist = os.path.exists(path)
        return path_exist

import datetime
import json
import logging
import os
import shutil
import subprocess
import time
import uuid

from api.file_transfer.tinytag import TinyTag
from api.models.anthology import Anthology
from api.models.book import Book
from api.models.chapter import Chapter
from api.models.chunk import Chunk
from api.models.language import Language
from api.models.mode import Mode
from api.models.project import Project
from api.models.version import Version

logger = logging.getLogger(__name__)

class CleanupType:
    TAKE = 1
    COMMENT = 2
    NAME_AUDIO = 3
    EXPORT = 4


class CleanupType:
    TAKE = 1
    COMMENT = 2
    NAME_AUDIO = 3
    EXPORT = 4


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

    @staticmethod
    def copy_files_from_src_to_dest(location_list):
        for location in location_list:
            shutil.copy2(location["src"], location["dst"])

    def import_project(self, directory, task, title, started):
        bad_files = []
        project_manifest = self.open_manifest_file(directory)
        language = Language.import_language(project_manifest["language"])
        anthology = Anthology.import_anthology(project_manifest["anthology"])
        book = Book.import_book(project_manifest["book"], anthology)
        version = Version.import_version(project_manifest["version"])
        mode = Mode.import_mode(project_manifest["mode"])
        project = Project.import_project(
            version, mode, anthology, language, book)

        title = project_manifest["language"]["name"] + " - " + \
            project_manifest["book"]["name"]
        total_takes = self.manifest_takes_count(project_manifest["manifest"])
        takes_added = 0
        current_take = 0

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

                    current_take += 1
                    task.update_state(state='PROGRESS',
                                      meta={
                                          'current': current_take,
                                          'total': total_takes,
                                          'name': task.name,
                                          'started': started,
                                          'title': title,
                                          'message': 'Adding takes to database...',
                                          'details': {
                                              'lang_slug': project_manifest["language"]["slug"],
                                              'lang_name': project_manifest["language"]["name"],
                                              'book_slug': project_manifest["book"]["slug"],
                                              'book_name': project_manifest["book"]["name"],
                                              'result': take["name"],
                                          }
                                      })

                    try:
                        meta = TinyTag.get(file)
                    except Exception:
                        os.remove(file)
                        bad_files.append(take["name"])
                        continue

                    markers = self.get_markers(meta)
                    rating = take["rating"]
                    duration = meta.duration
                    self.push_audio_processing_to_background(file)
                    Take.import_takes(self.relative_path(file), duration, markers, rating, chunk)
                    takes_added += 1

        add_info = ""
        if len(bad_files) > 0:
            add_info = 'Bad files: ' + ', '.join(bad_files)

        return {
            'name': task.name,
            'started': started,
            'finished': datetime.datetime.now(),
            'title': title,
            'message': 'Upload complete!',
            'details': {
                'lang_slug': project_manifest["language"]["slug"],
                'lang_name': project_manifest["language"]["name"],
                'book_slug': project_manifest["book"]["slug"],
                'book_name': project_manifest["book"]["name"],
                'result': "Imported {0} files of {1}. {2}".format(takes_added, total_takes, add_info),
            }
        }

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
        except Exception as e:
            shutil.rmtree(directory)
            logger.error("Error: ", e.message)

    @staticmethod
    def manifest_takes_count(manifest):
        takes_count = 0
        for chapters in manifest:
            for chunks in chapters["chunks"]:
                takes_count += len(chunks["takes"])

        return takes_count

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

    @staticmethod
    def convert_and_compress(file_transfer, takes, file_format):
        files_list = []
        for take in takes:
            path, take_contents = file_transfer.audio_utility.convert_in_memory(take, file_format)
            files_list.append({
                "file_path": path,
                "file_contents": take_contents
            })

        return file_transfer.archive_project.archive_in_memory(files_list)

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

    @staticmethod
    def file_name(location):
        return os.path.basename(location)

    def copy_files_from_src_to_dest(self, location_list, task, title, started):
        current_take = 0
        for location in location_list:
            shutil.copy2(location["src"], location["dst"])

            current_take += 1
            progress = int((current_take / len(location_list) * 100) / 3)  # 1/3 of overall task
            task.update_state(state='PROGRESS',
                              meta={
                                  'current': progress,
                                  'total': 100,
                                  'name': task.name,
                                  'started': started,
                                  'title': title,
                                  'message': 'Copying takes...',
                                  'details': {
                                      'result': location["fn"],
                                  }
                              })

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

    def __cleanup_files(self, cleanup_type):
        fs_records = []
        db_records = []

        if cleanup_type == CleanupType.TAKE:
            from ..models import Take
            target_dir = ['media', 'dump']
            file_format = ".wav"

            takes = Take.objects.all()
            for take in takes:
                db_records.append(take.location)
        elif cleanup_type == CleanupType.COMMENT:
            from ..models import Comment
            target_dir = ['media', 'dump', 'comments']
            file_format = ".mp3"

            comments = Comment.objects.all()
            for comment in comments:
                db_records.append(comment.location)
        elif cleanup_type == CleanupType.NAME_AUDIO:
            from ..models import User
            target_dir = ['media', 'dump', 'name_audios']
            file_format = ".mp3"

            users = User.objects.all()
            for user in users:
                if user.name_audio != "":
                    db_records.append(user.name_audio)
        elif cleanup_type == CleanupType.EXPORT:
            target_dir = ['media', 'export']
            file_format = ".zip"
        else:
            return 0

        directory = ''
        for dir in target_dir:
            directory = os.path.join(directory, dir)
        base_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))))
        root_directory = os.path.join(base_dir, directory)

        for subdir, dirs, files in os.walk(root_directory):
            for file in files:
                filepath = os.path.join(subdir, file)

                if filepath.endswith(file_format):
                    if cleanup_type != CleanupType.EXPORT:
                        fs_records.append(self.relative_path(filepath))
                    else:
                        mtime = os.path.getmtime(filepath)
                        last_modified_date = datetime.datetime.fromtimestamp(mtime)
                        diff = datetime.datetime.now() - last_modified_date
                        # Include files for deletion older than 24 hours
                        if diff.seconds > 24*60*60:
                            fs_records.append(self.relative_path(filepath))

        orphans = frozenset(fs_records).difference(db_records)

        for location in orphans:
            filename = os.path.join(base_dir, location)
            if os.path.isfile(filename):
                self.remove_file(filename)

        return len(orphans)

    def cleanup_orphans(self):
        total_removed = 0

        # cleanup takes
        total_removed += self.__cleanup_files(CleanupType.TAKE)
        # cleanup comments
        total_removed += self.__cleanup_files(CleanupType.COMMENT)
        # cleanup user name audios
        total_removed += self.__cleanup_files(CleanupType.NAME_AUDIO)
        # cleanup old (24 hours) zip files in export folder
        total_removed += self.__cleanup_files(CleanupType.EXPORT)

        return total_removed

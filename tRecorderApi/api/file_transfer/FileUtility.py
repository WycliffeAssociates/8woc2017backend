import datetime
import json
import logging
import os
import shutil
import subprocess
import time
import uuid
from collections import MutableMapping
from contextlib import suppress

from django.contrib.auth.hashers import make_password

from api.file_transfer.tinytag import TinyTag
from api.models.anthology import Anthology
from api.models.book import Book
from api.models.chapter import Chapter
from api.models.chunk import Chunk
from api.models.language import Language
from api.models.mode import Mode
from api.models.project import Project
from api.models.version import Version
from api.models.user import User

from api.models import Comment

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

    def import_project(self, directory, user, update_progress, task_args):
        bad_files = []
        project_manifest = self.open_manifest_file(directory)
        language = Language.import_language(project_manifest["language"])
        anthology = Anthology.import_anthology(project_manifest["anthology"])
        book = Book.import_book(project_manifest["book"], anthology)
        version = Version.import_version(project_manifest["version"])
        mode = Mode.import_mode(project_manifest["mode"])
        if "users" in project_manifest:
            users_info = project_manifest["users"]
        project = Project.import_project(
            version, mode, anthology, language, book)

        if not os.path.exists(os.path.join("media", "dump", "comments")):
            os.makedirs(os.path.join("media", "dump", "comments"))

        if not os.path.exists(os.path.join("media", "dump", "name_audios")):
            os.makedirs(os.path.join("media", "dump", "name_audios"))

        total_takes = self.manifest_takes_count(project_manifest["manifest"])
        takes_added = 0
        current_take = 0

        for chapters in project_manifest["manifest"]:
            number = chapters["chapter"]
            checking_level = chapters["checking_level"]
            chapter = Chapter.import_chapter(project, number, checking_level)
            if "comments" in chapters:
                comments = chapters["comments"]
                if len(comments) > 0:
                    for comment in comments:
                        comt_path = os.path.join(directory, FileUtility.file_name(comment["location"]))
                        owner = None
                        if os.path.exists(comt_path):
                    	    os.rename(comt_path, comment["location"])
                        if "users" in project_manifest and "user_id" in comment:
                            owner = self.manifest_take_owner(project_manifest["users"], comment["user_id"], directory)
                        Comment.import_comment(comment, "chapter", chapter.id, owner)
            for chunks in chapters["chunks"]:
                startv = chunks["startv"]
                endv = chunks["endv"]
                chunk = Chunk.import_chunk(chapter, startv, endv)
                if "comments" in chunks:
                    comments = chunks["comments"]
                    if len(comments) > 0:
                        for comment in comments:
                            comt_path = os.path.join(directory, FileUtility.file_name(comment["location"]))
                            owner = None
                            if os.path.exists(comt_path):
                            	os.rename(comt_path, comment["location"])
                            if "users" in project_manifest and "user_id" in comment:
                                owner = self.manifest_take_owner(project_manifest["users"], comment["user_id"], directory)
                            Comment.import_comment(comment, "chunk", chunk.id, owner)
                for take in chunks["takes"]:

                    from api.models.take import Take
                    file = os.path.join(directory, take["name"])
                    if not os.path.isfile(file):
                        bad_files.append(take["name"])
                        continue

                    current_take += 1

                    if update_progress and task_args:
                        # 2/2 of overall task
                        progress = int(((current_take / total_takes * 100) / 2) + (100 / 2))

                        new_task_args = task_args + (progress, 100, 'Importing takes into database...',
                                                     {
                                                         'user_icon_hash': user["icon_hash"],
                                                         'user_name_audio': user["name_audio"],
                                                         'project_id': project.id,
                                                         'mode': mode.slug,
                                                         'lang_slug': project_manifest["language"]["slug"],
                                                         'lang_name': project_manifest["language"]["name"],
                                                         'book_slug': project_manifest["book"]["slug"],
                                                         'book_name': project_manifest["book"]["name"],
                                                         'result': take["name"],
                                                     })
                        update_progress(*new_task_args)

                    try:
                        meta = TinyTag.get(file)
                    except Exception:
                        os.remove(file)
                        bad_files.append(take["name"])
                        continue

                    owner = None

                    if "users" in project_manifest and "user_id" in take:
                        owner = self.manifest_take_owner(project_manifest["users"], take["user_id"], directory)

                    markers = self.get_markers(meta)
                    rating = take["rating"]
                    duration = meta.duration
                    self.push_audio_processing_to_background(file)
                    take_obj = Take.import_takes(self.relative_path(file), duration, markers, rating, chunk, owner)
                    if "comments" in take:
                        comments = take["comments"]
                        if len(comments) > 0:
                            for comment in comments:
                                comt_path = os.path.join(directory, FileUtility.file_name(comment["location"]))
                                owner = None
                                if os.path.exists(comt_path):
                            	    os.rename(comt_path, comment["location"])
                                if "users" in project_manifest and "user_id" in comment:
                                    owner = self.manifest_take_owner(project_manifest["users"], comment["user_id"], directory)
                                Comment.import_comment(comment, "take", take_obj.id, owner)
                    takes_added += 1

        add_info = ""
        if len(bad_files) > 0:
            add_info = 'Bad files: ' + ', '.join(bad_files)

        return {
            'user_icon_hash': user["icon_hash"],
            'user_name_audio': user["name_audio"],
            'project_id': project.id,
            'mode': mode.slug,
            'lang_slug': project_manifest["language"]["slug"],
            'lang_name': project_manifest["language"]["name"],
            'book_slug': project_manifest["book"]["slug"],
            'book_name': project_manifest["book"]["name"],
            'result': "Imported {0} files of {1}. {2}".format(takes_added, total_takes, add_info),
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

            with open(manifest_path) as manifest_file:
                manifest = json.load(manifest_file)
                return manifest
        except Exception as e:
            shutil.rmtree(directory)
            logger.error("Error: ", str(e))

    def generate_manifest_dictionary(self, project, takes):
        manifest = {
            "language": {
                "slug": project["lang_slug"],
                "name": project["lang_name"]
            },
            "book": {
                "slug": project["book_slug"],
                "name": project["book_name"],
                "number": project["book_number"]
            },
            "version": {
                "slug": project["version_slug"],
                "name": project["version_name"]
            },
            "anthology": {
                "slug": project["anthology_slug"],
                "name": project["anthology_name"]
            },
            "mode": {
                "slug": project["mode_slug"],
                "name": project["mode_name"],
                "type": project["mode_type"]
            },
            "users": [],
            "manifest": []
        }

        for take in takes:
            chapter = take.chunk.chapter
            chunk = take.chunk

            chapter_obj = None
            chunk_obj = None

            for chapter_dic in manifest["manifest"]:
                if chapter_dic["chapter"] == chapter.number:
                    chapter_obj = chapter_dic

                    for chunk_dic in chapter_dic["chunks"]:
                        if chunk_dic["startv"] == chunk.startv:
                            chunk_obj = chunk_dic

            take_obj = {
                "name": self.file_name(take.location),
                "location": take.location,
                "rating": take.rating,
                "published": take.published,
                "user_id": None if not take.owner else take.owner.id,
                "comments": []
            }

            if take_obj["user_id"] and \
                    not any(dic.get('id', "") == take_obj["user_id"] for dic in manifest["users"]):
                user_obj = {
                    "id": take.owner.id,
                    "icon_hash": take.owner.icon_hash,
                    "name_audio": self.file_name(take.owner.name_audio),
                    "location": take.owner.name_audio
                }
                manifest["users"].append(user_obj)

            for comment in take.comments.all():
                comment_obj = {
                    "name": self.file_name(comment.location),
                    "location": comment.location,
                    "user_id": None if not comment.owner else comment.owner.id
                }
                take_obj["comments"].append(comment_obj)

                if comment_obj["user_id"] and \
                        not any(dic.get('id', "") == comment_obj["user_id"] for dic in manifest["users"]):
                    user_obj = {
                        "id": comment.owner.id,
                        "icon_hash": comment.owner.icon_hash,
                        "name_audio": self.file_name(comment.owner.name_audio),
                        "location": comment.owner.name_audio
                    }
                    manifest["users"].append(user_obj)

            if not chunk_obj:
                chunk_obj = {
                    "startv": chunk.startv,
                    "endv": chunk.endv,
                    "comments": [],
                    "takes": [take_obj]
                }

                for comment in chunk.comments.all():
                    comment_obj = {
                        "name": self.file_name(comment.location),
                        "location": comment.location,
                        "user_id": None if not comment.owner else comment.owner.id
                    }
                    chunk_obj["comments"].append(comment_obj)

                    if comment_obj["user_id"] and \
                            not any(dic.get('id', "") == comment_obj["user_id"] for dic in manifest["users"]):
                        user_obj = {
                            "id": comment.owner.id,
                            "icon_hash": comment.owner.icon_hash,
                            "name_audio": self.file_name(comment.owner.name_audio),
                            "location": comment.owner.name_audio
                        }
                        manifest["users"].append(user_obj)

                if chapter_obj:
                    chapter_obj["chunks"].append(chunk_obj)
            else:
                chunk_obj["takes"].append(take_obj)

            if not chapter_obj:
                chapter_obj = {
                    "chapter": chapter.number,
                    "checking_level": chapter.checked_level,
                    "published": chapter.published,
                    "chunks": [chunk_obj],
                    "comments": []
                }

                for comment in chapter.comments.all():
                    comment_obj = {
                        "name": self.file_name(comment.location),
                        "location": comment.location,
                        "user_id": 0 if not comment.owner else comment.owner.id
                    }
                    chapter_obj["comments"].append(comment_obj)

                    if comment_obj["user_id"] and \
                            not any(dic.get('id', "") == comment_obj["user_id"] for dic in manifest["users"]):
                        user_obj = {
                            "id": comment.owner.id,
                            "icon_hash": comment.owner.icon_hash,
                            "name_audio": self.file_name(comment.owner.name_audio),
                            "location": comment.owner.name_audio
                        }
                        manifest["users"].append(user_obj)

                manifest["manifest"].append(chapter_obj)

        return manifest

    @staticmethod
    def create_manifest_file(directory, manifest):
        with open(os.path.join(directory, "manifest.json"), 'w') as outfile:
            json.dump(manifest, outfile)

    def delete_keys_from_dict(self, dictionary, keys):
        for key in keys:
            with suppress(KeyError):
                del dictionary[key]
        for value in dictionary.values():
            if isinstance(value, MutableMapping):
                self.delete_keys_from_dict(value, keys)

    @staticmethod
    def manifest_takes_count(manifest):
        """
        The number of takes in manifest
        :param manifest: manifest data
        :return: Integer
        """
        takes_count = 0
        for chapters in manifest:
            for chunks in chapters["chunks"]:
                takes_count += len(chunks["takes"])

        return takes_count

    def manifest_take_owner(self, users, user_id, directory):
        """
        Get or create user that came from manifest
        :param users: List of user from manifest
        :param user_id: User id from manifest
        :param directory: Path to directory with user audio file
        :return: User instance
        """
        owner = None

        for user in users:
            if user["id"] == user_id:
                # Check if user exists
                owner = User.objects.filter(icon_hash=user["icon_hash"]).first()

                # if not, then create it
                if not owner:
                    audio_file = os.path.join(directory, user["name_audio"])
                    dest_file = os.path.join("media", "dump", "name_audios", user["name_audio"])
                    os.rename(audio_file, dest_file)

                    username = str(uuid.uuid1())[:8]
                    password = make_password("P@ssw0rd")
                    owner = User.objects.create(
                        icon_hash=user["icon_hash"],
                        username=username,
                        password=password,
                        name_audio=self.relative_path(dest_file)
                    )

        return owner

    def get_project_files(self, directory, manifest):
        file_location_list = []

        # manifest
        location = {
            "type": "manifest",
            "fname": "manifest.json",
            "src": os.path.join(directory, "manifest.json"),
            "dst": directory
        }
        file_location_list.append(location)

        # user name audio files
        for user in manifest["users"]:
            location = {
                "type": "user",
                "fname": user["name_audio"],
                "src": user["location"],
                "dst": directory
            }
            file_location_list.append(location)

        # chapter comments
        for chapter in manifest["manifest"]:
            for comment in chapter["comments"]:
                location = {
                    "type": "comment",
                    "fname": comment["name"],
                    "src": comment["location"],
                    "dst": directory
                }
                file_location_list.append(location)

            for chunk in chapter["chunks"]:
                # chunk comments
                for comment in chunk["comments"]:
                    location = {
                        "type": "comment",
                        "fname": comment["name"],
                        "src": comment["location"],
                        "dst": directory
                    }
                    file_location_list.append(location)

                for take in chunk["takes"]:
                    # takes
                    location = {
                        "type": "take",
                        "fname": take["name"],
                        "src": take["location"],
                        "dst": directory
                    }
                    file_location_list.append(location)

                    # take comments
                    for comment in take["comments"]:
                        location = {
                            "type": "comment",
                            "fname": comment["name"],
                            "src": comment["location"],
                            "dst": directory
                        }
                        file_location_list.append(location)

        return file_location_list

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

    def create_path(self, *args):
        path = os.path.join(*args)

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

    def copy_files_from_src_to_dest(self, location_list, project, user, update_progress, task_args):
        current_take = 0
        for location in location_list:
            if location["type"] != "manifest":
                shutil.copy2(location["src"], location["dst"])

            current_take += 1
            if project and update_progress and task_args:
                # 1/3 of overall task
                progress = int((current_take / len(location_list) * 100) / 3)

                new_task_args = task_args + (progress, 100, 'Copying takes...', {
                    'user_icon_hash': user["icon_hash"],
                    'user_name_audio': user["name_audio"],
                    'lang_slug': project["lang_slug"],
                    'lang_name': project["lang_name"],
                    'book_slug': project["book_slug"],
                    'book_name': project["book_name"],
                    'result': location["fname"]
                })
                update_progress(*new_task_args)

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
                        if diff.seconds > 24 * 60 * 60:
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

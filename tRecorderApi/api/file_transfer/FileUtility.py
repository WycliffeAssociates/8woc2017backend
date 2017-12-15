import json
import os
import pickle
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
import uuid

import urllib3
from tinytag import TinyTag


class FileUtility:
    @staticmethod
    def root_dir(root_dir_of):
        directory = ''
        for dir in root_dir_of:
            directory += dir + "/"
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        uuid_name = str(time.time()) + str(uuid.uuid4())
        root_directory = os.path.join(base_dir, directory + uuid_name)

        if not os.path.exists(root_directory):
            os.makedirs(root_directory)
        return root_directory

    def copy_files_from_src_to_dest(self, location_list):
        for location in location_list:
            shutil.copy2(location["src"], location["dst"])

    def process_uploaded_takes(self, directory, Take, ext):

        manifest = ''
        for root, dirs, files in os.walk(directory):
            for f in files:
                abpath = os.path.join(root, os.path.basename(f))
                if f == "manifest.json":
                    manifest = json.load(open(abpath))
                    continue
                relpath = self.get_relative_path(abpath)
                try:
                    meta = TinyTag.get(abpath)  # get metadata for every file
                except LookupError as e:
                    return {'error': 'bad_wave_file'}, 400

                metadata, take_info = self.parse_metadata(meta, abpath)

                if metadata == 'bad meta':
                    return metadata, take_info
                # highPassFilter(abpath)
                is_source_file = False
                if ext == 'tr':
                    is_source_file = True
                    manifest = self.create_manifest(take_info, metadata)

                Take.saveTakesToDB(take_info, relpath, metadata, manifest, is_source_file)
                # if ext == 'tr':
                #     os.remove(os.path.join(directory, "source.tr"))

        return 'ok', 200

    @staticmethod
    def create_manifest(meta, info):
        dict = {"language":  meta["language"],
                "anthology":  meta["anthology"],
                "book":       meta["book"],
                "version":    meta["version"],
                "mode":       meta["mode"]
        }

        return dict

    def parse_metadata(self, meta, abpath):
        try:
            a = meta.artist
            lastindex = a.rfind("}") + 1
            substr = a[:lastindex]
            take_info = json.loads(substr)

            bookcode = take_info['book']
            bookname = self.getBookByCode(bookcode)
            langcode = take_info['language']
            langname = self.getLanguageByCode(langcode)

            lng_book_dur = {
                "langname": langname,
                "bookname": bookname,
                "duration": meta.duration
            }
            return lng_book_dur, take_info
        except Exception as e:
            return 'bad meta', 400

    @staticmethod
    def get_relative_path(location):
        reg = re.search('(media\/.*)$', location)
        return reg.group(1)

    @staticmethod
    def getLanguageByCode(code):
        url = 'http://td.unfoldingword.org/exports/langnames.json'
        http = urllib3.PoolManager()
        request = http.request('GET', url)
        languages = []
        try:
            languages = json.loads(request.data.decode('utf8'))
            with open('language.json', 'wb') as fp:
                pickle.dump(languages, fp)
        except urllib.error.URLError as e:
            with open('language.json', 'rb') as fp:
                languages = pickle.load(fp)

        ln = ""
        for dicti in languages:
            if dicti["lc"] == code:
                ln = dicti["ln"]
                break
        return ln

    @staticmethod
    def getBookByCode(code):
        with open('books.json') as books_file:
            books = json.load(books_file)

        bn = ""
        for dicti in books:
            if dicti["slug"] == code:
                bn = dicti["name"]
                break
        return bn

    @staticmethod
    def processTrFile(file, directory):
        with open(os.path.join(directory, "source.tr"), 'wb') as temp_file:
            for chunk in file.chunks():
                temp_file.write(chunk)
            try:
                FNULL = open(os.devnull, 'wb')
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

                path = os.path.join(base_dir, 'aoh/aoh.jar')
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
        path = os.path.join(root_dir, lang_slug, version, book_slug, chapter_number).replace("\\","/")

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def create_folder_path(self, root_dir, lang, version, book):
        return os.path.join(root_dir, lang, version, book)

    def create_chapter_path(self, root_dir, lang,version,book,chapter_number):
        path = os.path.join(self.create_folder_path(root_dir,lang, version, book), chapter_number)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def take_location(self, take_location):
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            take_location)

    @staticmethod
    def relative_path(location):
        reg = re.search('(media\/.*)$', location)
        return reg.group(1)

    def copy_files_from_src_to_dest(self, location_list):

        for location in location_list:
            shutil.copy2(location["src"], location["dst"])

    def copy_files(self, src, dst):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_dir, media, tmp, filename + ".tr")

    def compile_into_tr(self, root_dir):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        FNULL = open(os.devnull, 'w')
        subprocess.call(
            ['java', '-jar', os.path.join(
                base_dir, 'aoh/aoh.jar'), '-c', '-tr', root_dir],
            stdout=FNULL, stderr=subprocess.STDOUT)
        FNULL.close()

    @staticmethod
    def check_if_path_exists(path):
        path_exist = os.path.exists(path)
        return path_exist


import os
import re
import shutil
import subprocess
import time
import uuid


class FileUtility:
    def root_dir(self, root_dir_of):
        directory = ''
        for dir in root_dir_of:
            directory += dir + os.sep
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        uuid_name = str(time.time()) + str(uuid.uuid4())
        root_directory = os.path.join(base_dir, directory + uuid_name)
        if not os.path.exists(root_directory):
            os.makedirs(root_directory)
        return root_directory

    def create_path(self, root_dir, lang_slug, version, book_slug, chapter_number):
        path = os.path.join(root_dir, lang_slug, version, book_slug, chapter_number)

        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def create_folder_path(self, root_dir, lang, version, book):
        return os.path.join(root_dir, lang, version, book)

    def create_chapter_path(self, root_dir, chapter_number):
        path = os.path.join(root_dir, chapter_number)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def take_location(self, take_location):
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                            take_location)

    def relative_path(self, location):
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

    def remove_file(self, file):
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

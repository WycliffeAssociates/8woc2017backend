from .ArchiveProject import ArchiveProject
import zipfile


class ZipIt(ArchiveProject):

    def archive(self):
        pass

    @staticmethod
    def extract(file, directory):
        try:
            zip_file = zipfile.ZipFile(file)
            zip_file.extractall(directory)
            zip_file.close()
            return 'ok', 200, "zip"

        except zipfile.BadZipfile:
                return "bad_zip_file", 400


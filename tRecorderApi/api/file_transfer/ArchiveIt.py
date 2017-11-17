import zipfile

from .ArchiveProject import ArchiveProject


class ArchiveIt(ArchiveProject):
    def archive(self, root_dir, project_file, files_in_zip, remove_dir):
        with zipfile.ZipFile(project_file, 'w') as zipped_f:
            for file in files_in_zip:
                zipped_f.write(file, file.replace(root_dir, ""))

        remove_dir(root_dir)
        return project_file

    def extract(self):
        pass

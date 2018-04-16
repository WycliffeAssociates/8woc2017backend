import datetime

from .FileTransfer import FileTransfer
from api.tasks import extract_and_save_project


class Upload(FileTransfer):

    # these objects come from file transfer
    def __init__(self, archive_project, audio_utility, file_utility):
        super().__init__(archive_project, audio_utility, file_utility)

    def upload(self, file):
        directory = self.file_utility.root_dir(['media', 'dump'])

        task = extract_and_save_project.delay(self, file, directory,
                                              title='Upload and import project',
                                              started=datetime.datetime.now())

        return task.id

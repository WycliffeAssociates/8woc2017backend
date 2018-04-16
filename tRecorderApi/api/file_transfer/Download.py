import datetime
import os

from .FileTransfer import FileTransfer
from api.tasks import download_project


class Download(FileTransfer):
    def __init__(self, archive_project, audio_utility, file_utility):
        super().__init__(archive_project, audio_utility, file_utility)

    def download(self, project_name, location_list, root_dir, file_format):
        title = "Download project"
        started = datetime.datetime.now()
        task = download_project.delay(self, project_name, root_dir, location_list, file_format, title, started)

        return task.id


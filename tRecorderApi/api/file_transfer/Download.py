import datetime

from .FileTransfer import FileTransfer
from api.tasks import download_project, export_project


class Download(FileTransfer):
    def __init__(self, archive_project, audio_utility, file_utility):
        super().__init__(archive_project, audio_utility, file_utility)

    def download(self, project, takes, file_format, user):
        title = "Download project"
        started = datetime.datetime.now()

        user_data = {
            "icon_hash": user.icon_hash,
            "name_audio": user.name_audio
        }
        task = download_project.delay(self, project, takes, file_format,
                                      title=title,
                                      started=started,
                                      user=user_data)

        return task.id

    def export(self, project, location_list, root_dir, file_format, user):
        title = "Export project"
        started = datetime.datetime.now()

        user_data = {
            "icon_hash": user.icon_hash,
            "name_audio": user.name_audio
        }

        task = export_project.delay(self, project, root_dir, location_list, file_format,
                                    title=title,
                                    started=started,
                                    user=user_data)
        return task.id

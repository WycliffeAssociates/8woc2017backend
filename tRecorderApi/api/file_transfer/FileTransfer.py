from abc import ABCMeta


class FileTransfer(metaclass=ABCMeta):
    def __init__(self, archive_project, audio_utility, file_utility):
        self.archive_project = archive_project
        self.audio_utility = audio_utility
        self.file_utility = file_utility

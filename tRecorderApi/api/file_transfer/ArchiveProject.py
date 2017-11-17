from abc import ABCMeta, abstractmethod


class ArchiveProject(metaclass=ABCMeta):
    @abstractmethod
    def archive(self, project_file, root_dirs, converted_mp3):
        pass

    @abstractmethod
    def extract():
        pass

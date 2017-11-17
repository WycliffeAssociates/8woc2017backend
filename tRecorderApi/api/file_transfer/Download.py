from .FileTransfer import FileTransfer


class Download(FileTransfer):
    def __init__(self, archive_project, audio_utility, file_utility):
        super().__init__(archive_project, audio_utility, file_utility)

    def download(self, project_name, location_list, root_dir):
        self.file_utility.copy_files_from_src_to_dest(location_list)

        converted_list = self.audio_utility.convert_to_mp3(root_dir)

        project_file = self.file_utility.project_file(project_name, 'media/export', '.zip')

        return self.archive_project.archive(root_dir, project_file, converted_list, self.file_utility.remove_dir)

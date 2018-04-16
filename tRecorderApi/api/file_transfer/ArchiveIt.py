import zipfile
from .ArchiveProject import ArchiveProject


class ArchiveIt(ArchiveProject):
    def archive(self, root_dir, project_file, location_list, remove_dir, task, title, started):
        with zipfile.ZipFile(project_file, 'w') as zipped_f:
            current_take = 0
            for file in location_list:
                zipped_f.write(file["conv"], file["conv"].replace(root_dir, ""))

                current_take += 1
                progress = int(((current_take / len(location_list) * 100) / 3) + ((100 / 3) * 2))  # 3/3 of overall task
                task.update_state(state='PROGRESS',
                                  meta={
                                      'current': progress,
                                      'total': 100,
                                      'name': task.name,
                                      'started': started,
                                      'title': title,
                                      'message': 'Zipping takes...',
                                      'details': {
                                          'result': file["fn"],
                                      }
                                  })

        remove_dir(root_dir)
        return project_file

    def extract(self):
        pass

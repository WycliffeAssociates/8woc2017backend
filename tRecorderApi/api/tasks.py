import datetime
from zipfile import BadZipfile

import celery
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class BaseTask(celery.Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.update_state(state='FAILURE',
                          meta={
                               'name': self.name,
                               'message': "{0!r}".format(exc),
                               'details': {"result": repr(einfo)},
                               'title': kwargs["title"],
                               'started': kwargs["started"],
                               'finished': datetime.datetime.now(),
                          })


@shared_task(name='extract_and_save_project', base=BaseTask)
def extract_and_save_project(self, file, directory, title, started):
    task = extract_and_save_project
    task.update_state(state='STARTED',
                      meta={
                          'name': task.name,
                          'title': title,
                          'started': started,
                          'message': "Extracting files...",
                          'details': {}
                      })

    resp, stat = self.archive_project.extract(file, directory)
    if resp == 'ok':
        self.file_utility.remove_file(file)
        logger.info("File extracted and removed.")
        return self.file_utility.import_project(directory, task, title, started)
    else:
        self.file_utility.remove_file(file)
        logger.info("File extraction failed, so removed.")

        raise BadZipfile(resp)


@shared_task(name='cleanup_orphan_files', base=BaseTask)
def cleanup_orphan_files(file_utility, title, started):
    task = cleanup_orphan_files
    task.update_state(state='STARTED',
                      meta={
                          'name': task.name,
                          'title': title,
                          'started': started,
                          'message': "Deleting orphan files...",
                          'details': {}
                      })

    files_removed = file_utility.cleanup_orphans()
    logger.info("{0} files have been removed".format(files_removed))
    return {
        'name': cleanup_orphan_files.name,
        'title': title,
        'message': "Cleaning files complete.",
        'details': {"result": "{0} files have been removed".format(files_removed)},
        'started': started,
        'finished': datetime.datetime.now(),
    }


@shared_task(name='download_project')
def download_project(self, project_name, root_dir, location_list, file_format, title, started):
    task = download_project
    task.update_state(state='STARTED',
                      meta={
                          'name': task.name,
                          'title': title,
                          'started': started,
                          'message': "Starting download...",
                          'details': {}
                      })

    self.file_utility.copy_files_from_src_to_dest(
        location_list,
        task,
        title,
        started)  # 1/3 of overall progress

    converted_list = self.audio_utility.convert_to_mp3(
        location_list,
        file_format,
        task,
        title,
        started)  # 2/3 of overall progress

    project_file = self.file_utility.project_file(project_name, 'media/export', '.zip')
    zip_abs_location = self.archive_project.archive(
        root_dir,
        project_file,
        converted_list,
        self.file_utility.remove_dir,
        task,
        title,
        started
    )  # 3/3 of overall progress

    zip_rel_location = self.file_utility.relative_path(zip_abs_location)

    return {
            'name': download_project.name,
            'title': title,
            'message': "Download is ready.",
            'details': {"result": zip_rel_location},
            'started': started,
            'finished': datetime.datetime.now(),
        }

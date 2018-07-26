import datetime
import uuid
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
                              'message': "Process failed",
                              'details': {
                                  "user_icon_hash": kwargs["user"]["icon_hash"],
                                  "user_name_audio": kwargs["user"]["name_audio"],
                                  "result": str(exc)
                              },
                              'title': kwargs["title"],
                              'started': kwargs["started"],
                              'finished': datetime.datetime.now(),
                          })


@shared_task(name='extract_and_save_project', base=BaseTask)
def extract_and_save_project(self, file, directory, title, started, user):
    task = extract_and_save_project
    update_started(task, title, started, 'Extracting files...', {})

    task_args = (task, title, started)

    resp, stat = self.archive_project.extract(file, directory, user, update_progress, task_args)
    if resp == 'ok':
        self.file_utility.remove_file(file)
        logger.info("File extracted and removed.")
        details = self.file_utility.import_project(directory, user, update_progress, task_args)

        return task_finished(task, title, started, 'Upload complete!', details)
    else:
        self.file_utility.remove_file(file)
        logger.info("File extraction failed, so removed.")

        raise BadZipfile(resp)


@shared_task(name='cleanup_orphan_files', base=BaseTask)
def cleanup_orphan_files(file_utility, title, started, user):
    task = cleanup_orphan_files
    update_started(task, title, started, 'Removing orphan files...', {
        'user_icon_hash': user["icon_hash"],
        'user_name_audio': user["name_audio"],
    })

    files_removed = file_utility.cleanup_orphans()
    logger.info("{0} files have been removed".format(files_removed))

    return task_finished(task, title, started, 'Cleanup complete.', {
        'user_icon_hash': user["icon_hash"],
        'user_name_audio': user["name_audio"],
        'result': "{0} files have been removed".format(files_removed)
    })


@shared_task(name='download_project', base=BaseTask)
def download_project(self, project, takes, file_format, title, started, user):
    task = download_project
    update_started(task, title, started, 'Download started', {
        'user_icon_hash': user["icon_hash"],
        'user_name_audio': user["name_audio"],
        'lang_slug': project["lang_slug"],
        'lang_name': project["lang_name"],
        'book_slug': project["book_slug"],
        'book_name': project["book_name"],
    })

    uuid_name = str(uuid.uuid1())[:8]
    project_name = project["lang_slug"] + "_" + project["version_slug"] + "_" + project["book_slug"] + "_" + uuid_name
    task_args = (task, title, started)

    root_dir = self.file_utility.root_dir(['media', 'export'])

    manifest = self.file_utility.generate_manifest_dictionary(project, takes)
    file_location_list = self.file_utility.get_project_files(root_dir, manifest)
    self.file_utility.create_manifest_file(root_dir, manifest)

    # Copy files to temporary folder
    self.file_utility.copy_files_from_src_to_dest(file_location_list, project, user,
                                                  update_progress, task_args)  # 1/3 of overall progress

    # Convert files to mp3 if it's needed
    converted_list = self.audio_utility.convert_to_mp3(file_location_list, file_format,
                                                       project, user,
                                                       update_progress, task_args)  # 2/3 of overall progress

    # Create zip archive
    project_file = self.file_utility.project_file(project_name, 'media/export', '.zip')
    zip_abs_location = self.archive_project.archive(root_dir, project_file, converted_list,
                                                    self.file_utility.remove_dir, project, user,
                                                    update_progress, task_args)  # 3/3 of overall progress

    zip_rel_location = self.file_utility.relative_path(zip_abs_location)

    return task_finished(task, title, started, 'Download is ready.', {
        'user_icon_hash': user["icon_hash"],
        'user_name_audio': user["name_audio"],
        'lang_slug': project["lang_slug"],
        'lang_name': project["lang_name"],
        'book_slug': project["book_slug"],
        'book_name': project["book_name"],
        'result': zip_rel_location
    })


@shared_task(name='export_project', base=BaseTask)
def export_project(self, project, root_dir, location_list, file_format, title, started, user):
    task = export_project
    update_started(task, title, started, 'Export started', {
        'user_icon_hash': user["icon_hash"],
        'user_name_audio': user["name_audio"],
        'lang_slug': project["lang_slug"],
        'lang_name': project["lang_name"],
        'book_slug': project["book_slug"],
        'book_name': project["book_name"],
    })

    uuid_name = str(uuid.uuid1())[:8]
    project_name = project["lang_slug"] + "_" + project["ver_slug"] + "_" + project["book_slug"] + "_" + uuid_name
    task_args = (task, title, started)

    # Copy files to temporary folder
    self.file_utility.copy_files_from_src_to_dest(location_list, project, user,
                                                  update_progress, task_args)  # 1/3 of overall progress

    # Convert files to mp3 if it's needed
    converted_list = self.audio_utility.convert_to_mp3(location_list, file_format,
                                                       project, user,
                                                       update_progress, task_args)  # 2/3 of overall progress

    # Create zip archive
    project_file = self.file_utility.project_file(project_name, 'media/export', '.zip')
    zip_abs_location = self.archive_project.archive(root_dir, project_file, converted_list,
                                                    self.file_utility.remove_dir, project, user,
                                                    update_progress, task_args)  # 3/3 of overall progress

    zip_rel_location = self.file_utility.relative_path(zip_abs_location)

    return task_finished(task, title, started, 'Export is ready.', {
        'user_icon_hash': user["icon_hash"],
        'user_name_audio': user["name_audio"],
        'lang_slug': project["lang_slug"],
        'lang_name': project["lang_name"],
        'book_slug': project["book_slug"],
        'book_name': project["book_name"],
        'result': zip_rel_location
    })


def update_started(task, title, started, message, details):
    task.update_state(state='STARTED',
                      meta={
                          'name': task.name,
                          'title': title,
                          'started': started,
                          'message': message,
                          'details': details
                      })


def update_progress(task, title, started, current, total, message, details):
    task.update_state(state='PROGRESS',
                      meta={
                          'current': current,
                          'total': total,
                          'name': task.name,
                          'started': started,
                          'title': title,
                          'message': message,
                          'details': details
                      })


def task_finished(task, title, started, message, details):

    return {
        'name': task.name,
        'title': title,
        'message': message,
        'details': details,
        'started': started,
        'finished': datetime.datetime.now(),
    }

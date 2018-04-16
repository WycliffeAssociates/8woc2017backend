import datetime

from django.http import JsonResponse

from api.file_transfer import FileUtility
from api.tasks import cleanup_orphan_files


def clean_orphans(request):
    task = cleanup_orphan_files.delay(FileUtility(), title='Clean orphan files', started=datetime.datetime.now())
    return JsonResponse({"response": "processing", "task_id": task.id})

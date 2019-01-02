from api.file_transfer.ArchiveIt import ArchiveIt
from api.file_transfer.AudioUtility import AudioUtility
from api.file_transfer.Download import Download
from api.file_transfer.FileUtility import FileUtility
from api.models import Take
from api.serializers import TakeForZipSerializer
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_description="Downloads the project based on given project id and file format",
    manual_parameters=[
        openapi.Parameter(
            name='id', in_=openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
            description="Id of a project",
        ), openapi.Parameter(
            name='chapters', in_=openapi.IN_PATH,
            type=openapi.TYPE_ARRAY,
            description="Filter by chapters",
        ), openapi.Parameter(
            name='file_format', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="It can be 'mp3' or 'wav'",
        )
    ]
))
class TransferViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Take.objects.all()
    serializer_class = TakeForZipSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        id = self.request.query_params.get('id')
        file_format = self.request.query_params.get('file_format')
        chapters = self.request.query_params.getlist('chapters[]')

        if id is None:
            id = kwargs.get("pk", None)

        if len(chapters) > 0:
            takes = Take.objects.filter(chunk__chapter__in=chapters) \
                .order_by('chunk__chapter__number', 'chunk__startv')
        else:
            takes = Take.objects.filter(chunk__chapter__project=id) \
                .order_by('chunk__chapter__number', 'chunk__startv')

        if len(takes) > 0:
            mode_type = "MULTI" if takes[0].chunk.chapter.project.mode.unit == 1 else "SINGLE"

            project = {
                "lang_slug": takes[0].chunk.chapter.project.language.slug,
                "lang_name": takes[0].chunk.chapter.project.language.name,
                "book_slug": takes[0].chunk.chapter.project.book.slug,
                "book_name": takes[0].chunk.chapter.project.book.name,
                "book_number": takes[0].chunk.chapter.project.book.number,
                "version_slug": takes[0].chunk.chapter.project.version.slug,
                "version_name": takes[0].chunk.chapter.project.version.name,
                "anthology_slug": takes[0].chunk.chapter.project.anthology.slug,
                "anthology_name": takes[0].chunk.chapter.project.anthology.name,
                "mode_slug": takes[0].chunk.chapter.project.mode.slug,
                "mode_name": takes[0].chunk.chapter.project.mode.name,
                "mode_type": mode_type
            }

            zip_it = Download(ArchiveIt(), AudioUtility(), FileUtility())

            task_id = zip_it.download(project, takes, file_format, request.user)
            return Response({"response": "processing", "task_id": task_id}, status=202)
        else:
            return Response({"response": "no_takes_in_project"}, status=200)

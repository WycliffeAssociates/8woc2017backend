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
class ExportViewSet(viewsets.ReadOnlyModelViewSet):
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
            takes = Take.objects.filter(chunk__chapter__in=chapters)
        else:
            takes = Take.objects.filter(chunk__chapter__project=id)

        if len(takes) > 0:
            language_slug = takes[0].chunk.chapter.project.language.slug
            language_name = takes[0].chunk.chapter.project.language.name
            book_slug = takes[0].chunk.chapter.project.book.slug
            book_name = takes[0].chunk.chapter.project.book.name
            version_slug = takes[0].chunk.chapter.project.version.slug
            project = {
                "lang_slug": language_slug,
                "lang_name": language_name,
                "book_slug": book_slug,
                "book_name": book_name,
                "ver_slug": version_slug
            }

            zip_it = Download(ArchiveIt(), AudioUtility(), FileUtility())

            root_dir = zip_it.file_utility.root_dir(['media', 'export'])
            take_location_list = []
            take_names_list = []
            for take in takes:
                file_name = zip_it.file_utility.file_name(take.location)
                if file_name in take_names_list:
                    continue
                take_names_list.append(file_name)
                location = {
                    "type": "take",
                    "fname": file_name,
                    "src": take.location,
                    "dst": zip_it.file_utility.create_path(
                        root_dir,
                        language_slug,
                        version_slug,
                        book_slug,
                        str(take.chunk.chapter).zfill(2))
                }
                take_location_list.append(location)

            task_id = zip_it.export(project, take_location_list, root_dir, file_format, request.user)
            return Response({"response": "processing", "task_id": task_id}, status=202)
        else:
            return Response({"response": "no_takes_in_project"}, status=200)

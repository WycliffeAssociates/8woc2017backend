import os

from api.file_transfer.ArchiveIt import ArchiveIt
from api.file_transfer.AudioUtility import AudioUtility
from api.file_transfer.Download import Download
from api.file_transfer.FileUtility import FileUtility
from api.models import Take
from api.serializers import TakeForZipSerializer
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pydub import AudioSegment
from rest_framework import viewsets
from rest_framework.response import Response

from io import BytesIO
import zipfile


@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_description="Downloads the project based on given project id and file format",
    manual_parameters=[
        openapi.Parameter(
            name='id', in_=openapi.IN_PATH,
            type=openapi.TYPE_INTEGER,
            description="Id of a project",
        ), openapi.Parameter(
            name='file_format', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="It can be 'mp3' or 'wav'",
        )
    ]
))
class ZipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Take.objects.all()
    serializer_class = TakeForZipSerializer

    def retrieve(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        id = self.request.query_params.get('id')
        file_format = self.request.query_params.get('file_format')
        if id is None:
            id = kwargs.get("pk", None)
        takes = Take.objects.filter(chunk__chapter__project=id)

        language_slug = takes[0].chunk.chapter.project.language.slug
        book_slug = takes[0].chunk.chapter.project.book.slug
        version_slug = takes[0].chunk.chapter.project.version.slug

        project_name = language_slug + "_" + version_slug + "_" + book_slug
        zip_it = Download(ArchiveIt(), AudioUtility(), FileUtility())
        zip_contents = zip_it.download2(takes, file_format)

        # with open('test.zip', 'wb') as f:
        #     f.write(in_memory_zip.getvalue())

        response = HttpResponse(zip_contents, content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="' + project_name + '.zip"'
        return response

# class ZipViewSet(viewsets.ReadOnlyModelViewSet):
#     queryset = Take.objects.all()
#     serializer_class = TakeForZipSerializer
#
#     def retrieve(self, request, *args, **kwargs):
#         return self.list(self, request, *args, **kwargs)
#
#     def list(self, request, *args, **kwargs):
#         id = self.request.query_params.get('id')
#         file_format = self.request.query_params.get('file_format')
#         if id is None:
#             id = kwargs.get("pk", None)
#         projects = Take.objects.filter(chunk__chapter__project=id)
#
#         language_slug = projects[0].chunk.chapter.project.language.slug
#         book_slug = projects[0].chunk.chapter.project.book.slug
#         version_slug = projects[0].chunk.chapter.project.version.slug
#
#         project_name = language_slug + "_" + version_slug + "_" + book_slug
#         zip_it = Download(ArchiveIt(), AudioUtility(), FileUtility())
#
#         root_dir = zip_it.file_utility.root_dir(['media', 'export'])
#         take_location_list = []
#         for project in projects:
#             location = {}
#             location['src'] = project.location
#             location['dst'] = zip_it.file_utility.create_path(root_dir, language_slug, version_slug,
#                                                               book_slug,
#                                                               str(project.chunk.chapter).zfill(2))
#             take_location_list.append(location)
#         zipped_file_location = zip_it.download(project_name, take_location_list, root_dir, file_format)
#         path = {"location": zip_it.file_utility.relative_path(zipped_file_location)}
#         return Response(path)

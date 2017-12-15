from api.models import Project, Language, Chapter, Take
from rest_framework import viewsets

from api.serializers import TakeForZipSerializer

from api.file_transfer.ArchiveIt import ArchiveIt
from api.file_transfer.AudioUtility import AudioUtility
from api.file_transfer.Download import Download
from api.file_transfer.FileUtility import FileUtility
from rest_framework.response import Response


class ZipViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Take.objects.all()
    serializer_class = TakeForZipSerializer

    def retrieve(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        id = self.request.query_params.get('id')
        if id is None:
            id = kwargs.get("pk", None)
        projects = Take.objects.filter(chunk__chapter__project=id)

        language_slug = projects[0].chunk.chapter.project.language.slug
        book_slug = projects[0].chunk.chapter.project.book.slug
        version_slug = projects[0].chunk.chapter.project.version.slug

        project_name = language_slug + "_" + version_slug + "_" + book_slug
        zip_it = Download(ArchiveIt(), AudioUtility(), FileUtility())

        root_dir = zip_it.file_utility.root_dir(['media', 'export'])
        take_location_list = []
        for project in projects:
            location = {}
            location['src'] = project.location
            location['dst'] = zip_it.file_utility.create_path(root_dir, language_slug, version_slug,
                                                              book_slug,
                                                              str(project.chunk.chapter))
            take_location_list.append(location)
        zipped_file_location = zip_it.download(project_name, take_location_list, root_dir)
        path = {"location": zip_it.file_utility.relative_path(zipped_file_location)}
        return Response(path)

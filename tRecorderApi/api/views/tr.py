from api.models import Take
from rest_framework import viewsets

from api.serializers import TakeForZipSerializer

from api.file_transfer.ArchiveIt import ArchiveIt
from api.file_transfer.AudioUtility import AudioUtility
from api.file_transfer.Download import Download
from api.file_transfer.FileUtility import FileUtility
from rest_framework.response import Response


class TrViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Take.objects.all()
    serializer_class = TakeForZipSerializer

    def retrieve(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        id = self.request.query_params.get('id')
        if id is None:
            id = kwargs.get("pk", None)

        takes = Take.objects.filter(chunk__chapter__project=id,
                                    chunk__chapter__project__published=True)

        if takes.count() > 0:
            language_slug = takes[0].chunk.chapter.project.language.slug
            book_slug = takes[0].chunk.chapter.project.book.slug
            version_slug = takes[0].chunk.chapter.project.version.slug
            tr_it = Download(ArchiveIt(), AudioUtility(), FileUtility())
            root_folder = tr_it.file_utility.root_dir(['media', 'tmp'])
            filename = language_slug + "_" + version_slug + "_" + book_slug

            tr_it.file_utility.create_folder_path(root_folder, language_slug, version_slug, book_slug)
            try:
                for take in takes:
                    chapter_folder = tr_it.file_utility.create_chapter_path(root_folder, language_slug,
                                                                            version_slug,
                                                                            book_slug,
                                                                            str(take.chunk.chapter).zfill(2))
                    file_path = tr_it.file_utility.copy_files(take.location, chapter_folder)
                    if file_path.endswith('.wav'):
                        file_path_mp3 = file_path.replace('.wav', '.mp3')
                        meta = {
                            "anthology": take.chunk.chapter.project.anthology.slug,
                            "language": take.chunk.chapter.project.language.slug,
                            "version": take.chunk.chapter.project.version.slug,
                            "slug": take.chunk.chapter.project.book.slug,
                            "book_number": str(take.chunk.chapter.project.book.number).zfill(2),
                            "mode": take.chunk.chapter.project.mode.slug,
                            "chapter": str(take.chunk.chapter).zfill(2),
                            "startv": take.chunk.startv,
                            "endv": take.chunk.endv,
                            "markers": take.markers
                        }
                        tr_it.audio_utility.write_meta(file_path, file_path_mp3, meta)
                        tr_it.file_utility.remove_file(file_path)
                tr_it.file_utility.compile_into_tr(root_folder)
                filename = tr_it.file_utility.create_tr_path('media', 'tmp', filename)
                tr_it.file_utility.rename(root_folder + ".tr", filename)
                tr_it.file_utility.remove_dir(root_folder)
            except Exception as e:
                return Response({"error": str(e)}, status=400)

            return Response({"location": tr_it.file_utility.relative_path(filename)}, status=200)

        return Response(status=400)

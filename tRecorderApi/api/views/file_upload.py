import json
import os
import shutil
import time
import uuid
import zipfile

from api.models import Book, Language, Take
from django.conf import settings
from .helpers import highPassFilter, getRelativePath
from rest_framework import views
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from tinytag import TinyTag


class FileUploadView(views.APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, filename, format='zip'):
        """ Normal upload """
        if request.method == 'POST' and request.data['file']:
            uuid_name = str(time.time()) + str(uuid.uuid4())
            upload = request.data["file"]

            # unzip files
            try:
                zip = zipfile.ZipFile(upload)
                folder_name = os.path.join(
                    settings.BASE_DIR, 'media/dump/' + uuid_name)

                zip.extractall(folder_name)
                zip.close()

                # extract metadata / get the apsolute path to the file to be
                # stored

                # Cache language and book to re-use later
                bookname = ''
                bookcode = ''
                langname = ''
                langcode = ''

                is_empty_zip = True  # for testing if zip file is empty
                # TODO:dirs is not used
                for root, dirs, files in os.walk(folder_name):
                    # TODO:change variable f into file
                    for f in files:
                        is_empty_zip = False
                        abpath = os.path.join(root, os.path.basename(f))
                        relpath = getRelativePath(abpath)
                        try:
                            meta = TinyTag.get(abpath)
                        except LookupError as e:
                            return Response({"error": "bad_wave_file"}, status=400)

                        if meta and meta.artist:
                            # TODO:find a proper name for a
                            a = meta.artist
                            lastindex = a.rfind("}") + 1
                            substr = a[:lastindex]
                            # TODO:find a proper name for pls
                            pls = json.loads(substr)

                            if bookcode != pls['slug']:
                                bookcode = pls['slug']
                                bookname = Book.getBookByCode(bookcode)
                            if langcode != pls['language']:
                                langcode = pls['language']
                                langname = Language.getLanguageByCode(langcode)

                            data = {
                                "langname": langname,
                                "bookname": bookname,
                                "duration": meta.duration
                            }

                            highPassFilter(abpath)
                            Take.prepareDataToSave(pls, relpath, data)
                        else:
                            return Response({"error": "bad_wave_file"}, status=400)

                if is_empty_zip:
                    return Response({"error": "bad_zip_file"}, status=400)
                return Response({"response": "ok"}, status=200)

            except zipfile.BadZipfile:
                return Response({"error": "bad_zip_file"}, status=400)
        else:
            return Response(status=404)

    @staticmethod
    def processFile(folderPath, filePath):
        """ File processor for resumable upload """
        # unzip files
        try:
            location = os.path.join(folderPath, filePath)
            uuid_name = str(time.time()) + str(uuid.uuid4())
            zip = zipfile.ZipFile(location)
            folder_name = os.path.join(
                settings.BASE_DIR, 'media/dump/' + uuid_name)

            zip.extractall(folder_name)
            zip.close()
            shutil.rmtree(folderPath, ignore_errors=True)

            # Cache language and book to re-use later
            bookname = ''
            bookcode = ''
            langname = ''
            langcode = ''

            is_empty_zip = True  # for testing if zip file is empty
            # TODO:dirs is not used
            for root, dirs, files in os.walk(folder_name):
                for f in files:
                    is_empty_zip = False
                    abpath = os.path.join(root, os.path.basename(f))
                    relpath = getRelativePath(abpath)
                    try:
                        meta = TinyTag.get(abpath)
                    except LookupError as e:
                        return {"error": "bad_wave_file"}

                    if meta and meta.artist:
                        a = meta.artist
                        lastindex = a.rfind("}") + 1
                        substr = a[:lastindex]
                        pls = json.loads(substr)

                        if bookcode != pls['slug']:
                            bookcode = pls['slug']
                            bookname = Book.getBookByCode(bookcode)
                        if langcode != pls['language']:
                            langcode = pls['language']
                            langname = Language.getLanguageByCode(langcode)

                        data = {
                            "langname": langname,
                            "bookname": bookname,
                            "duration": meta.duration
                        }

                        highPassFilter(abpath)
                        Take.prepareDataToSave(pls, relpath, data)
                    else:
                        return {"error": "bad_wave_file"}

            if is_empty_zip:
                return {"error": "bad_zip_file"}

            return {"response": "ok"}

        except zipfile.BadZipfile:
            return {"error": "bad_zip_file"}

import json
import os
import shutil
import subprocess
import time
import uuid

from api.models import Language, Book, Take
from django.conf import settings
from api.file_transfer import FileUtility
from rest_framework import views
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from tinytag import TinyTag


class UploadSourceFileView(views.APIView):
    parser_classes = (MultiPartParser,)

    def post(self, request, filename, format='tr'):
        if request.method == 'POST' and request.data['upload']:
            # TODO: remove this functionality
            response = {}
            uuid_name = str(time.time()) + str(uuid.uuid4())
            tempFolder = os.path.join(
                settings.BASE_DIR, "media/dump/" + uuid_name)
            if not os.path.exists(tempFolder):
                os.makedirs(tempFolder)
                data = request.data['upload']
                with open(os.path.join(tempFolder, "source.tr"), 'w') as temp_file:
                    for line in data:
                        temp_file.write(line)
        try:
            FNULL = open(os.devnull, 'w')
            out = subprocess.check_output(
                ['java', '-jar', os.path.join(
                    settings.BASE_DIR, 'aoh/aoh.jar'), '-x', tempFolder + "/source.tr"],
                stderr=subprocess.STDOUT
            )
            os.remove(os.path.join(tempFolder, "source.tr"))
            FNULL.close()

            bookname = ''
            bookcode = ''
            langname = ''
            langcode = ''

            for root, dirs, files in os.walk(tempFolder):
                for f in files:
                    abpath = os.path.join(root, os.path.basename(f))
                    relpath = FileUtility.relative_path(abpath)
                    meta = TinyTag.get(abpath)

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

                        # highPassFilter(abpath)
                        saved = Take.prepareDataToSave(
                            pls, relpath, data, True)
                        if "language" in saved and "language" not in response:
                            response["language"] = saved["language"]
                        if "book" in saved and "book" not in response:
                            response["book"] = saved["book"]
                    else:
                        return Response({"error": "bad_wave_file"}, status=400)
            return Response(response, status=200)
        except Exception as e:
            shutil.rmtree(tempFolder)
            return Response({"error": str(e)}, status=400)

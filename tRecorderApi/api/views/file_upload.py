from rest_framework import views, status
from rest_framework.parsers import JSONParser, FileUploadParser
import time
import uuid
import zipfile
import os
from tinytag import TinyTag
from rest_framework.response import Response
import json
from helpers import highPassFilter
from api.models import Book, Language, Take

class FileUploadView(views.APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, filename, format='zip'):
        if request.method == 'POST' and request.data['file']:
            uuid_name = str(time.time()) + str(uuid.uuid4())
            upload = request.data["file"]

            # unzip files
            try:
                zip = zipfile.ZipFile(upload)
                folder_name = 'media/dump/' + uuid_name

                zip.extractall(folder_name)
                zip.close()

                # extract metadata / get the apsolute path to the file to be stored

                # Cache language and book to re-use later
                bookname = ''
                bookcode = ''
                langname = ''
                langcode = ''

                is_empty_zip = True # for testing if zip file is empty

                for root, dirs, files in os.walk(folder_name):
                    for f in files:
                        is_empty_zip = False
                        abpath = os.path.join(root, os.path.basename(f))
                        try:
                            meta = TinyTag.get(abpath)
                        except LookupError as e:
                            return Response({"error": "bad_wave_file"}, status=400)
                        
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
                            
                            #highPassFilter(abpath)
                            Take.prepareDataToSave(pls, abpath, data)
                        else:
                            return Response({"error": "bad_wave_file"}, status=400)
                
                if is_empty_zip:
                    return Response({"error": "bad_zip_file"}, status=400)
                return Response({"response": "ok"}, status=200)

            except zipfile.BadZipfile:
                return Response({"error": "bad_zip_file"}, status=400)
        else:
            return Response(status=404)
from rest_framework import views, status
from rest_framework.parsers import JSONParser
from helpers import getTakesByProject
import time
import uuid
import os
import shutil
import pydub
import json
import subprocess
from rest_framework.response import Response
from django.http import HttpResponse
from django.core import files
from rest_framework.parsers import JSONParser, FileUploadParser
from tinytag import TinyTag
import urllib2
import pickle


class SourceFileView(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        #if not os.path.exists('media/tmp/'+lang+'_'+ver+'.tr'):
        data = request.data
        data["is_source"] = True
        takes = getTakesByProject(data)

        if 'language' in data and 'version' in data:
            if len(takes) > 0:
                uuid_name = str(time.time()) + str(uuid.uuid4())
                root_folder = 'media/tmp/' + uuid_name
                project_folder = root_folder + '/' + data['language'] + '/' + data['version']
                for take in takes:
                    chapter_folder = project_folder + '/' + take['book']['slug'] + '/' + str(
                        take['take']['chapter']).zfill(2)
                    if not os.path.exists(chapter_folder):
                        os.makedirs(chapter_folder)
                    shutil.copy2(take['take']['location'], chapter_folder)
                    file_name = os.path.basename(take['take']['location'])
                    file_path = chapter_folder + '/' + file_name
                    file_path_mp3 = file_path.replace('.wav', '.mp3')

                    meta = {
                        "anthology": take['take']["anthology"],
                        "language": take["language"]["slug"],
                        "version": take['take']["version"],
                        "slug": take['book']["slug"],
                        "book_number": str(take['book']["booknum"]).zfill(2),
                        "mode": take['take']["mode"],
                        "chapter": str(take['take']["chapter"]).zfill(2),
                        "startv": take['take']["startv"],
                        "endv": take['take']["endv"],
                        "markers": take['take']["markers"]
                    }

                    sound = pydub.AudioSegment.from_wav(file_path)
                    sound.export(file_path_mp3, format='mp3', tags={'artist': json.dumps(meta)})
                    os.remove(file_path)

                FNULL = open(os.devnull, 'w')
                subprocess.call(['java', '-jar', 'aoh/aoh.jar', '-c', '-tr', root_folder],
                                stdout=FNULL, stderr=subprocess.STDOUT)
                FNULL.close()
                os.rename(root_folder+'.tr', 'media/tmp/'+data['language']+'_'+data['version']+'.tr')
                shutil.rmtree(root_folder)
            else:
                return Response({"response": "nosource"}, status=403)
        else:
            return Response({"response": "notenoughparameters"}, status=403)

        source_file = open('media/tmp/' + data['language'] + '_' + data['version'] + '.tr', 'rb')
        response = HttpResponse(files.File(source_file), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="%s"' % (
            data['language'] + '_' + data['version'] + '.tr')
        source_file.close()
        return response


import io
import os
import zipfile

from django.conf import settings
from django.http import HttpResponse
from rest_framework import views
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from .helpers import getFileName, md5Hash, getFilePath
from ..file_transfer import FileUtility
from ..models import Chunk


class PushTakesView(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data
        if all(k in data["project"] for k in ('language', 'version', 'book')):
            takes_name_and_locations = []
            response_array = {
                "en-x-demo2_ulb_b42_mrk_c07_v31-32_t03.wav": "6d6f8d635297adb9b8e83f38e0634er4",
                "en-x-demo2_ulb_b42_mrk_c07_v14-16_t02.wav": "d51605fc59e04feb8db2045735f12800",
                "en-x-demo2_ulb_b42_mrk_c07_v02-04_t07.wav": "e80c058c73b83a76bb9a60c781c21d91",
                "en-x-demo2_ulb_b42_mrk_c07_v24-26_t02.wav": "2ab809fa13b5182de67b9892162ab670",
                "en-x-demo2_ulb_b42_mrk_c07_v17-19_t03.wav": "b5c7aacdcafca203ded43e130151bece",
                "en-x-demo2_ulb_b42_mrk_c07_v33-35_t04.wav": "c811f1fc8c2e4f0e9a3023117788f8f1",
                "en-x-demo2_ulb_b42_mrk_c07_v05_t02.wav": "82f7d1a6fa392b2100f90dbde1602f2e",
                "en-x-demo2_ulb_b42_mrk_c07_v11-13_t02.wav": "883c8e628f0bff7f7f60e16667b587a4",
                "en-x-demo2_ulb_b42_mrk_c07_v36-37_t02.wav": "84697692eef682f3537a87e58393e465",
                "en-x-demo2_ulb_b42_mrk_c07_v20-23_t10.wav": "c6832e0a287f94a47918c02e5a826832",
                "en-x-demo2_ulb_b42_mrk_c07_v27-28_t02.wav": "81cd316c41b9c7d6ad3bc8b4d3d1b5c2",
                "en-x-demo2_ulb_b42_mrk_c07_v29-30_t02.wav": "db3ce227b34a54bfaddaca42c2d33c6e",
                # "chapter.wav": "0a4af2fc1f922b083ab84ce695c30904",
                # "en-x-demo2_ulb_b42_mrk_c07_v01_t05.wav": "6be47559aeb09c0526fe5c9bf415d726",
                # "en-x-demo2_ulb_b42_mrk_c07_v06-07_t04.wav": "f2ebbcc59319b16b67f07b055ed5cc9b",
                # "en-x-demo2_ulb_b42_mrk_c07_v08-10_t04.wav": "f92d2bc9d8611b3dc7a8d720a71f0873"
            }

            project = Chunk.getChunksWithTakesByProject(data["project"])
            for chunk in project["chunks"]:
                for take in chunk['takes']:
                    location = os.path.join(settings.BASE_DIR, take['take']['location'])
                    file_name = getFileName(location)
                    file_hash = md5Hash(location)
                    if file_name not in response_array:
                        takes_name_and_locations.append(location)
                    elif file_hash != response_array[file_name]:
                        takes_name_and_locations.append(location)
                
            mf = io.StringIO()
            with zipfile.ZipFile(mf, 'w') as zipped_f:
                for audio in takes_name_and_locations:
                    zipped_f.write(audio, getFilePath(FileUtility.relative_path(audio)))
            response = HttpResponse(mf.getvalue(), content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=file.zip'
            return response
        else:
            return Response({"error": "not_enough_parameters"}, status=400)

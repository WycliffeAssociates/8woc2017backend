from rest_framework import views, status
from rest_framework.parsers import JSONParser
import json
from helpers import getFileName, md5Hash
from rest_framework.response import Response
from api.models import Chunk

class ExcludeFilesView(views.APIView):
    parser_classes = (JSONParser,)

    #The purpose of this request is to reduce the amount of unnecessary file uploads
    #during backup from translationRecorder
    def post(self, request):
        files_to_exclude = {}
        data = request.data
        #get the files associated with a particular project
        project = Chunk.getChunksWithTakesByProject(data)
        for chunk in project["chunks"]:
            for take in chunk['takes']:
                location = take['take']['location']
                #for all files in the project, compute the md5 hash
                files_to_exclude[getFileName(location)] = md5Hash(location)
        #return the md5 hashes of files we have, so that duplicates can be avoided
        return Response(files_to_exclude, status=200)
import os
import re
import shutil
import time
import uuid

from django.conf import settings
from .file_upload import FileUploadView
from rest_framework import views
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response


class ResumableFileUploadView(views.APIView):
    parser_classes = (MultiPartParser,)

    tempFolder = os.path.join(settings.BASE_DIR, 'media/tmp/')
    filePath = ''

    def post(self, request, filename, format='zip'):
        if request.method == 'POST' and request.data['file']:
            upload = request.data["file"]
            identifier = request.POST.get('resumableIdentifier')
            file_name = request.POST.get('resumableFilename')
            chunkNumber = request.POST.get('resumableChunkNumber')
            chunkSize = int(request.POST.get('resumableChunkSize'))
            currentChunkSize = int(
                request.POST.get('resumableCurrentChunkSize'))
            totalSize = int(request.POST.get('resumableTotalSize'))
            totalChunks = int(request.POST.get('resumableTotalChunks'))

            if not self.isChunkUploaded(identifier, file_name, chunkNumber):
                chunkPath = self.tempFolder + identifier + \
                    "/" + file_name + ".part" + chunkNumber
                try:
                    os.makedirs(self.tempFolder + identifier)
                except:
                    pass
                with open(chunkPath, 'w') as temp_file:
                    for line in upload:
                        temp_file.write(line)

                # check if the size of uploaded chunk is correct
                if os.path.isfile(chunkPath):
                    uplChunkSize = os.path.getsize(chunkPath)
                    print
                    'Chunk #{}: {} = {}'.format(
                        chunkNumber, currentChunkSize, uplChunkSize)
                    if int(currentChunkSize) != int(uplChunkSize):
                        # reupload chunk
                        return Response(status=204)

                    with open(os.path.join(self.tempFolder, identifier, 'progress'), 'a') as progress:
                        progress.write(chunkNumber + '\n')

            if self.isFileUploadComplete(identifier, totalChunks):
                if self.createFileAndDeleteTmp(identifier, file_name):
                    fileLocation = os.path.join(self.filePath, file_name)

                    # check if the size of uloaded file is correct
                    if os.path.isfile(fileLocation):
                        uplFileSize = os.path.getsize(fileLocation)
                        print
                        'File: {} = {}'.format(totalSize, uplFileSize)

                        if int(totalSize) != int(uplFileSize):
                            shutil.rmtree(self.filePath, ignore_errors=True)
                            return Response({"error": "file_is_corrupted"}, status=500)
                        else:
                            print
                            'Chunk #{} of {}'.format(chunkNumber, totalChunks)

                            status = 200
                            response = {}
                            if filename == "project":
                                response = FileUploadView.processFile(
                                    self.filePath, file_name)
                                if 'error' in response:
                                    status = 500

                            return Response(response, status=status)
                    else:
                        return Response({"error": "file_not_uploaded"}, status=500)

            return Response(status=200)

    def isChunkUploaded(self, identifier, filename, chunkNumber):
        if os.path.isfile(self.tempFolder + identifier + "/" + filename + ".part" + str(chunkNumber)):
            return True

        return False

    def isFileUploadComplete(self, identifier, totalChunks):
        lines = []
        with open(os.path.join(self.tempFolder, identifier, 'progress'), 'r') as f:
            lines = f.read().splitlines()

        return len(lines) == totalChunks

        # another approach
        """for x in range(totalChunks):
            if not self.isChunkUploaded(identifier, filename, x+1):
                return False

        return True;"""

    def createFileAndDeleteTmp(self, identifier, filename):
        folder = self.tempFolder + identifier
        uuid_name = str(time.time()) + str(uuid.uuid4())
        fileLocation = os.path.join(self.tempFolder, uuid_name, filename)

        if os.path.isfile(fileLocation):
            return False

        chunkFiles = []
        for root, dirs, files in os.walk(folder):
            for f in files:
                if f == 'progress':
                    continue

                abpath = os.path.join(root, os.path.basename(f))
                chunkFiles.append(abpath)

        self.sort_nicely(chunkFiles)

        if not os.path.exists(os.path.join(self.tempFolder, uuid_name)):
            os.makedirs(os.path.join(self.tempFolder, uuid_name))

        self.createFileFromChunks(chunkFiles, fileLocation)
        shutil.rmtree(self.tempFolder + identifier, ignore_errors=True)
        self.filePath = os.path.join(self.tempFolder, uuid_name)

        return True

    def createFileFromChunks(self, chunkFiles, destFile):
        with open(destFile, "wb") as final_file:
            for chunkFile in chunkFiles:
                try:
                    with open(chunkFile, "rb") as chunk:
                        final_file.write(chunk.read())
                except:
                    pass

        return os.path.isfile(destFile)

    def sort_nicely(self, l):
        """ Sort the given list in the way that humans expect."""
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(c)
                                    for c in re.split('([0-9]+)', key)]
        l.sort(key=alphanum_key)

    def get(self, request, filename, format='zip'):
        identifier = request.GET.get('resumableIdentifier')
        filename = request.GET.get('resumableFilename')
        chunkNumber = int(request.GET.get('resumableChunkNumber'))

        if self.isChunkUploaded(identifier, filename, chunkNumber):
            return Response(status=200)

        return Response(status=204)

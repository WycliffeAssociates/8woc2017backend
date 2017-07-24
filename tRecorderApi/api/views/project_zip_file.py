from rest_framework import views, status
from rest_framework.parsers import JSONParser
import time
import os
import uuid
import shutil
from tinytag import TinyTag
from pydub import AudioSegment
import zipfile
from rest_framework.response import Response
from django.http import HttpResponse
from api.models import Take

class ProjectZipFilesView(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data
        new_data = {}

        # filter the database with the given parameters
        if "language" in data:
            new_data["language"] = data["language"]
        if "version" in data:
            new_data["version"] = data["version"]
        if "book" in data:
            new_data["book"] = data["book"]

        if 'language' in new_data and 'version' in new_data and 'book' in new_data:
            new_data["is_source"] = False
            new_data["is_publish"] = True
            lst = Take.getTakesByProject(new_data)

            if len(lst) > 0:
                filesInZip = []
                uuid_name = str(time.time()) + str(uuid.uuid4())
                root_folder = 'media/export/' + uuid_name
                os.makedirs(root_folder)
                chapter_folder = ""
                project_name = new_data["language"] + \
                    "_" + new_data["version"] + \
                    "_" + new_data["book"]

                if not os.path.exists(root_folder):
                    os.makedirs(root_folder)

                # create list for locations
                locations = []
                for i in lst:
                    chapter_folder = root_folder + os.sep + i["language"]["slug"] + \
                        os.sep + i["take"]["version"] + \
                        os.sep + i["book"]["slug"] + \
                        os.sep + str(i["take"]["chapter"])
                    
                    if not os.path.exists(chapter_folder):
                        os.makedirs(chapter_folder)

                    loc = {}
                    loc["src"] = i["take"]["location"]
                    loc["dst"] = chapter_folder
                    locations.append(loc)

                # use shutil to copy the wav files to a new folder
                for loc in locations:
                    shutil.copy2(loc["src"], loc["dst"])

                # process of renaming/converting to mp3
                for subdir, dirs, files in os.walk(root_folder):
                    for file in files:
                        # store the absolute path which is is it's subdir and where the os step is
                        filePath = subdir + os.sep + file

                        if filePath.endswith(".wav"):
                            # Add to array so it can be added to the archive
                            sound = AudioSegment.from_wav(filePath)
                            filename = filePath.replace(".wav", ".mp3")
                            sound.export(filename, format="mp3")
                            filesInZip.append(filename)
                        else:
                            filesInZip.append(filePath)

                # Creating zip file
                with zipfile.ZipFile('media/export/' + project_name + '.zip', 'w') as zipped_f:
                    for members in filesInZip:
                        zipped_f.write(members, members.replace(root_folder,""))

                # delete the newly created wave and mp3 files
                shutil.rmtree(root_folder)

                with open('media/export/' + project_name + '.zip', 'rb') as zip_file:
                    response = HttpResponse(zip_file, content_type='application/zip')
                    response['Content-Disposition'] = 'attachment; filename='+project_name+'.zip'
                
                return response
            else:
                return Response({"error":"no_files"}, status=400)
        else:
            return Response({"error":"not_enough_parameters"}, status=400)
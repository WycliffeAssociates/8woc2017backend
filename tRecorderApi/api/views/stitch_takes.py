from pydub import AudioSegment
from rest_framework import views, status
from rest_framework.parsers import JSONParser
from api.models import Take, Language, Book, Comment, Project
import json
from rest_framework.response import Response
import os
from django.conf import settings
from api.file_transfer import FileUtility


class SourceStitchView(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data
        if "language" in data and "version" in data and "book" in data and "chapter" in data:
            chunks = Take.stitchSource(data)
            # chunks = list(chunks)
            chunks = sorted(chunks, key=lambda x: x.startv)
            loclst = []
            for chunk in chunks:
                takes = chunk.take_set.all()
                for take in takes:
                    # do not include takes that are not published
                    if take.is_publish is not True:
                        continue
                    loclst.append(
                        os.path.join(settings.BASE_DIR, take.location))

            if len(loclst) > 0:
                stitchedSource = AudioSegment.from_mp3(loclst[0])
                loclst.pop(0)
                for item in loclst:
                    stitchedSource = stitchedSource +\
                        AudioSegment.from_mp3(item)

                stitch_folder = os.path.join(settings.BASE_DIR, 'media/source')
                if not os.path.exists(stitch_folder):
                    os.makedirs(stitch_folder)

                project_name = data["language"] + "_" + data[
                    "version"] + "_" + data[
                    "book"] + "_" + str(data["chapter"])

                stitchedSource.export(
                    os.path.join(
                        stitch_folder,
                        project_name + ".mp3"
                    ),
                    format="mp3"
                )
            else:
                return Response({"error": "no_published_takes"}, status=400)
        else:
            return Response({"error": "not_enough_parameters"}, status=400)

        return Response(
            {
                "location":
                FileUtility.relative_path(
                    os.path.join(
                        stitch_folder,
                        project_name + ".mp3"
                    )
                )
            },
            status=200)


# cod flow
"""
# Check if language,version,book,chapter in data,else
# If language,version,boo,chapter is not found in data ,
 responses with message "not_enough_paramters"(status=400)

//database call
# Makes a method call in Take for gettings chunks(method in the take
is cmmented)

//creates list of take locations
# Chunks are sorted by starv
# Sets all takes to chunks
# Loops through takes
# Continues if take.is_published is not true
# Creates list of take locations
# Check if location list size is greater than 0,else
# If location list is less than 0,
 response with message "no published_takes"(status=400)

//stitch takes together
# Get the first item pass it to pydub and pop it off the list
# Loop through the remaining list and concatenate all the list in string form
# Creates media/source folder if does not exists
# Creates project_name string
# Exports the stitched as media/source/project_name.mp3
# Responses is location to stiched takes
"""

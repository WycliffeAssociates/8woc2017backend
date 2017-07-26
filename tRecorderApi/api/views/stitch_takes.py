from pydub import AudioSegment
from rest_framework import views, status
from rest_framework.parsers import JSONParser
from api.models import Take, Language, Book, User, Comment, Project
import json
from rest_framework.response import Response
import os



class SourceStitchView(views.APIView):
    parser_classes = (JSONParser,)
    def post(self, request):
        data = request.data
        data["is_source"] = True
        if "language" in data and "version" in data and "book" in data and "chapter" in data:
            lst = Take.stitchSource(data)
            lst = list(lst)
            lst = sorted(lst, key = lambda x: x["startv"])
            loclst = []
            for chunky in lst:
                take = Take.objects.filter(chunk = chunky["id"]).values()
                take = list(take)
                loclst.append(take[0]["location"])

            stitchedSource = AudioSegment.from_mp3(loclst[0])
            loclst.pop(0)
            print(type(stitchedSource))
            for item in loclst:
                sound1 = stitchedSource
                sound2 = AudioSegment.from_mp3(item)
                stitchedSource = sound1 + sound2
            stitch_folder = 'media/source'
            if not os.path.exists(stitch_folder):
                os.makedirs(stitch_folder)
            project_name = str(data["language"]) + "_" + str(data["book"]) + "_" + str(data["version"]) + "_" + str(data["chapter"])
            stitchedSource.export("./media/source/" + project_name + ".mp3", format="mp3")

            return Response(loclst, status = 200)

        else:
            return Response({"error": "not_enough_parameters"}, status=400)
        return Response(lst, status = 200)

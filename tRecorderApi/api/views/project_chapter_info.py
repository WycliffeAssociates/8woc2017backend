from rest_framework import views, status
from rest_framework.parsers import JSONParser
import json
from api.models import Take
from rest_framework.response import Response

class ProjectChapterInfoView(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        data = json.loads(request.body)
        allTakes = Take.objects.all().values()
        allTakes = allTakes.filter(version=data["version"])
        allTakes = allTakes.filter(book__slug=data["book"])
        allTakes = allTakes.filter(language__slug=data["language"])
        chap = {}
        chapters = []
        for take in allTakes:
            if take["chapter"] not in chapters:
                idv = {}
                idv["chapter"] = take["chapter"]
                idv["checked_level"] = take["checked_level"]
                idv["contributors"] = "Jerome"
                idv["percent_complete"] = 75
                idv["timestamp"] = 12
                chapters.append(idv)
        return Response(chapters, status = 200)
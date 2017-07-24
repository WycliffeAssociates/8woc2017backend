import json
from api.models import Take
from rest_framework import views
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from operator import itemgetter
from api.models import Chapter

class ProjectChapterInfoView(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data

        if "language" in data and "version" in data and "book" in data:
            dic = Chapter.getChaptersByProject(data)
            return Response(dic, status=200)
        else:
            return Response({"error": "not_enough_parameters"}, status=400)

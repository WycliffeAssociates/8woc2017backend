from rest_framework import views, status
from rest_framework.parsers import JSONParser
import json
from api.models import Take
from rest_framework.response import Response
from operator import itemgetter
from api.models import Project

class getVersionsView(views.APIView):
    parser_classes = (JSONParser,)

    def get(self, request):
        lst = Project.getVersionsByProject()
        return Response(lst, status = 200)

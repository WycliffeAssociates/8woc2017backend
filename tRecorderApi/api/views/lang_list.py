from rest_framework import views, status
from rest_framework.parsers import JSONParser
import json
from api.models import Take, Language
from rest_framework.response import Response
from operator import itemgetter
from api.models import Language

class getLangsView(views.APIView):
    parser_classes = (JSONParser,)

    def get(self, request):
        lst = Language.getLanguagesList()
        return Response(lst, status = 200)

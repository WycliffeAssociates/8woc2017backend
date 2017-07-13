from rest_framework import views, status
from rest_framework.parsers import JSONParser
import json
from api.models import Take
from rest_framework.response import Response
from operator import itemgetter

class getVersionsView(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        data = json.loads(request.body)
        allTakes = Take.objects.all().values()
        versions = []
        for take in allTakes:
            if take["version"] not in versions:
                versions.append(take["version"])
        return Response(versions, status = 200)

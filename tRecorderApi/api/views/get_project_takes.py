from rest_framework import views, status
from rest_framework.parsers import JSONParser
import json
from rest_framework.response import Response
from api.models import Take

class GetProjectTakesView(views.APIView):
    """This class handles the http POST requests."""
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data
        data["is_source"] = False
        lst = Take.getTakesByProject(data)

        return Response(lst, status=200)
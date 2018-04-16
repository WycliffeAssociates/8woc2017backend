from rest_framework import views, status
from rest_framework.parsers import JSONParser
import json
from ..models import Take
from rest_framework.response import Response

class UpdateProjectTakesView(views.APIView):
    """This class handles the http POST requests."""
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data

        if "filter" not in data or "fields" not in data:
            return Response({"response": "not_enough_parameters"}, status=400)

        try:
            result = Take.updateTakesByProject(data)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({"rows_affected": result}, status=200)
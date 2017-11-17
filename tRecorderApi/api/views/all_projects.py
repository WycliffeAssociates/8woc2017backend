from rest_framework import views
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from api.models import Project


class AllProjectsView(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data
        projects = Project.getProjects(data)

        return Response(projects, status=200)
from api.models import Project
from rest_framework import viewsets
from api.serializers import ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
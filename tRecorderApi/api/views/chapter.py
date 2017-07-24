from api.models import Chapter
from rest_framework import viewsets
from api.serializers import ChapterSerializer

class ChapterViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
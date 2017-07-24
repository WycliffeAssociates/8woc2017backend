from api.models import Chunk
from rest_framework import viewsets
from api.serializers import ChunkSerializer

class ChunkViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Chunk.objects.all()
    serializer_class = ChunkSerializer
from api.models import Chunk
from rest_framework import viewsets, views, status
from api.serializers import ChunkSerializer
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework.response import Response


class ChunkViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Chunk.objects.all()
    serializer_class = ChunkSerializer

class GetChunks(views.APIView):
    def post(self, request):
        data = request.data
        result = None
        Chunk.get_chunks(data)
        if result is None:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)

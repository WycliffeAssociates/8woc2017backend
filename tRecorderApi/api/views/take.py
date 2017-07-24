from api.models import Take
from rest_framework import viewsets, status
from api.serializers import TakeSerializer
from rest_framework.response import Response
import os
from django.forms.models import model_to_dict

class TakeViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Take.objects.all()
    serializer_class = TakeSerializer

    def list(self, request):
        queryset = Take.objects.all()
        serializer = TakeSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        try:
            os.remove(instance.location)
        except OSError:
            pass
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)
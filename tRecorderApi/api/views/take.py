from api.models import Take
from rest_framework import viewsets, status, views
from api.serializers import TakeSerializer
from rest_framework.response import Response
import os
import json
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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        if instance.markers:
            instance.markers = json.loads(instance.markers)
        else:
            instance.markers = {}

        take = model_to_dict(instance, fields=[
            "location","duration","rating",
            "date_modified","markers","id",
            "is_publish"
        ])
        # take["anthology"] = instance.chunk.chapter.project.anthology.id
        # take["version"] = instance.chunk.chapter.project.version
        # take["chapter"] = instance.chunk.chapter.number
        # take["mode"] = instance.chunk.chapter.project.mode
        # take["startv"] = instance.chunk.startv
        # take["endv"] = instance.chunk.endv

        return Response(take)

class GetTakes(views.APIView):
    def post(self, request):
        data = request.data
        if "chunk_id" in data:
            takes = Take.get_takes(data["chunk_id"])
            serialized_takes = TakeSerializer(takes, many=True).data
            return Response(serialized_takes, status=status.HTTP_200_OK)
        else:
            return Response(data=None, status=status.HTTP_400_BAD_REQUEST)
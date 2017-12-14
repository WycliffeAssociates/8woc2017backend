from api.models import Mode
from rest_framework import viewsets
from api.serializers import ModeSerializer

class ModeViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Mode.objects.all()
    serializer_class = ModeSerializer

    def build_params_filter(self, query):
        pk = query.get("id", None)
        slug = query.get("slug", None)
        filter = {}
        if pk is not None:
            filter["id"] = pk
        if slug is not None:
            filter["slug__iexact"] = slug
        return filter

    def get_queryset(self):
        queryset = Mode.objects.all()
        pk = self.kwargs.get("pk", None)
        if pk is not None:
            print(pk)
            return Mode.objects.filter(id=pk)
        else:
            filter = self.build_params_filter(self.request.query_params)
            return queryset.filter(**filter)

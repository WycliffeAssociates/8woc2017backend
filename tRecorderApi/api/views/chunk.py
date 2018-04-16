from ..models import Chunk
from ..serializers import ChunkSerializer
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from django.core.exceptions import SuspiciousOperation
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Return list of chunks based on given query string",
    manual_parameters=[
        openapi.Parameter(
            name='id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a chunk",
        ), openapi.Parameter(
            name='project_id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a project",
        ), openapi.Parameter(
            name='chapter_id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a chapter",
        )
    ]
))
class ChunkViewSet(viewsets.ModelViewSet):
    queryset = Chunk.objects.all()
    serializer_class = ChunkSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def build_params_filter(self, query):
        pk = query.get("id", None)
        project_id = query.get("project_id", None)
        chapter_id = query.get("chapter_id", None)
        filter = {}
        if pk is not None:
            filter["id"] = pk
        if project_id is not None:
            filter["chapter__project"] = project_id
        if chapter_id is not None:
            filter["chapter"] = chapter_id
        return filter

    def get_queryset(self):
        queryset = Chunk.objects.all()
        if self.request.query_params:
            filter = self.build_params_filter(self.request.query_params)
            if filter:
                return queryset.filter(**filter)
            else:
                raise SuspiciousOperation
        return queryset

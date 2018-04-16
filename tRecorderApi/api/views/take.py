from ..models import Take
from ..serializers import TakeSerializer
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from django.core.exceptions import SuspiciousOperation
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Return list of takes based on given query string",
    manual_parameters=[
        openapi.Parameter(
            name='id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a take",
        ), openapi.Parameter(
            name='published', in_=openapi.IN_QUERY,
            type=openapi.TYPE_BOOLEAN,
            description="Published status of a take",
        ), openapi.Parameter(
            name='project_id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a project",
        ), openapi.Parameter(
            name='chapter_id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a chapter",
        ), openapi.Parameter(
            name='chunk_id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a chunk",
        )
    ]
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_description='This end point is used for updating rating or published status of a take',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id'],
        properties={
            'published': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'rating': openapi.Schema(type=openapi.TYPE_INTEGER)
        }
    ),
))
class TakeViewSet(viewsets.ModelViewSet):
    queryset = Take.objects.all()
    serializer_class = TakeSerializer
    # permission_classes = (IsAuthenticated,)
    # authentication_classes = (TokenAuthentication,)

    def build_params_filter(self, query):
        pk = query.get("id", None)
        published = query.get("published", None)
        project_id = query.get("project_id", None)
        chapter_id = query.get("chapter_id", None)
        chunk_id = query.get("chunk_id", None)
        filter = {}
        if pk is not None:
            filter["id"] = pk
        if published is not None:
            filter['published'] = published.title()
        if project_id is not None:
            filter["chunk__chapter__project"] = project_id
        if chapter_id is not None:
            filter["chunk__chapter"] = chapter_id
        if chunk_id is not None:
            filter["chunk"] = chunk_id
        return filter

    def get_queryset(self):
        queryset = Take.objects.all()
        if self.request.query_params:
            filter = self.build_params_filter(self.request.query_params)
            if filter:
                return queryset.filter(**filter)
            else:
                raise SuspiciousOperation
        return queryset

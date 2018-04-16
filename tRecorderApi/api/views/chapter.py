from ..models import Chapter
from ..serializers import ChapterSerializer
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from api.serializers import ChapterSerializer
from django.core.exceptions import SuspiciousOperation
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Return list of anthologies based on given query string",
    manual_parameters=[
        openapi.Parameter(
            name='id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a chapter",
        ), openapi.Parameter(
            name='project_id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a project",
        ), openapi.Parameter(
            name='published', in_=openapi.IN_QUERY,
            type=openapi.TYPE_BOOLEAN,
            description="Published status of a chapter",
        ),
    ],
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_description='This end point is used for updating the checking level',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'published': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'checked_level': openapi.Schema(type=openapi.TYPE_INTEGER)
        }
    ),
))
class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    # TODO:Should we expose only REST methods we have used rather than exposing everything django CBV provides
    # http_method_names = ['get', 'list', 'patch', 'post']
    def build_params_filter(self, query):
        pk = query.get("id", None)
        project_id = query.get("project_id", None)
        published = query.get("published", None)
        filter = {}
        if pk is not None:
            filter["id"] = pk
        if project_id is not None:
            filter["project"] = project_id
        if published is not None:
            filter["published"] = published.title()
        return filter

    def get_queryset(self):
        queryset = Chapter.objects.all()
        if self.request.query_params:
            filter = self.build_params_filter(self.request.query_params)
            if filter:
                return queryset.filter(**filter)
            else:
                raise SuspiciousOperation
        return queryset

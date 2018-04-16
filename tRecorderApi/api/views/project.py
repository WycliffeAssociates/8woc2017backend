from ..models import Project
from ..serializers import ProjectSerializer
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from ..permissions import IsStaffOrReadOnly
from django.core.exceptions import SuspiciousOperation

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Return list of projects based on given query string",
    manual_parameters=[
        openapi.Parameter(
            name='id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a project",
        ), openapi.Parameter(
            name='published', in_=openapi.IN_QUERY,
            type=openapi.TYPE_BOOLEAN,
            description="Published status of a project",
        ), openapi.Parameter(
            name='lang', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="A language slug",
        ), openapi.Parameter(
            name='version', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="A version slug",
        ), openapi.Parameter(
            name='book', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="A book slug",
        ), openapi.Parameter(
            name='mode', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="A mode slug",
        ), openapi.Parameter(
            name='anth', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="An anthology slug",
        ),
    ]
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_description='This end point is used for updating the published status',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['published'],
        properties={
            'published': openapi.Schema(type=openapi.TYPE_BOOLEAN)
        }
    ),
))
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (IsStaffOrReadOnly,)

    def build_params_filter(self, query):
        pk = query.get("id", None)
        published = query.get("published", None)
        lang = query.get("lang", None)
        version = query.get("version", None)
        book = query.get("book", None)
        mode = query.get("mode", None)
        anth = query.get("anth", None)
        filter = {}
        if pk is not None:
            filter["id"] = pk
        if published is not None:
            filter["published"] = published.title()
        if lang is not None:
            filter["language__slug__iexact"] = lang
        if version is not None:
            filter["version__slug__iexact"] = version
        if book is not None:
            filter["book__slug__iexact"] = book
        if mode is not None:
            filter["mode__slug__iexact"] = mode
        if anth is not None:
            filter["anthology_slug_iexact"] = anth
        return filter

    def get_queryset(self):
        queryset = Project.objects.all()
        if self.request.query_params:
            filter = self.build_params_filter(self.request.query_params)
            if filter:
                return queryset.filter(**filter)
            else:
                raise SuspiciousOperation
        return queryset

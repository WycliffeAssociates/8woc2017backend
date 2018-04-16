from ..models import Take
from ..serializers import ExcludeFilesSerializer
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Return list of file names with md5 hash value based on given query string",
    manual_parameters=[
        openapi.Parameter(
            name='lang', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="A language slug",
        ), openapi.Parameter(
            name='anth', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="A anthology slug",
        ), openapi.Parameter(
            name='version', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="A version slug",
        ), openapi.Parameter(
            name='book', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="A book slug",
        )
    ]
))
class ExcludeFilesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Take.objects.all()
    serializer_class = ExcludeFilesSerializer

    def build_params_filter(self, query):
        lang = query.get("lang", None)
        anth = query.get("anth", None)
        version = query.get("version", None)
        book = query.get("book", None)
        filter = {}
        if lang is not None:
            filter["chunk__chapter__project__language__slug__iexact"] = lang
        if anth is not None:
            filter["chunk__chapter__project__anthology__slug__iexact"] = anth
        if version is not None:
            filter["chunk__chapter__project__version__slug__iexact"] = version
        if book is not None:
            filter["chunk__chapter__project__book__slug__iexact"] = book
        return filter

    def get_queryset(self):
        queryset = Take.objects.all()
        if self.request.query_params:
            filter = self.build_params_filter(self.request.query_params)
            if filter:
                return queryset.filter(**filter)
            return None
        return queryset

from ..models import Version
from ..serializers import VersionSerializer
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from django.core.exceptions import SuspiciousOperation
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Return list of takes based on given query string",
    manual_parameters=[
        openapi.Parameter(
            name='id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a version",
        ), openapi.Parameter(
            name='slug', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="A version slug",
        )
    ]
))
class VersionViewSet(viewsets.ModelViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    authentication_classes=(TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
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
        queryset = Version.objects.all()
        if self.request.query_params:
            filter = self.build_params_filter(self.request.query_params)
            if filter:
                return queryset.filter(**filter)
            else:
                raise SuspiciousOperation
        return queryset

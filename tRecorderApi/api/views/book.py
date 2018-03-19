from api.models import Book
from api.serializers import BookSerializer
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Return list of books based on given query string",
    manual_parameters=[
        openapi.Parameter(
            name='id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a book",
        ), openapi.Parameter(
            name='slug', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="A book slug",
        ), openapi.Parameter(
            name='anth', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="An anthology slug",
        ), openapi.Parameter(
            name='num', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="A book number",
        ),
    ]
))
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes=(TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def build_params_filter(self, query):
        pk = query.get("id", None)
        slug = query.get("slug", None)
        anth = query.get("anth", None)
        num = query.get("num", None)
        filter = {}
        if pk is not None:
            filter["id"] = pk
        if slug is not None:
            filter["slug__iexact"] = slug
        if anth is not None:
            filter["anthology__slug__iexact"] = anth
        if num is not None:
            filter["number"] = num
        return filter

    def get_queryset(self):
        queryset = Book.objects.all()
        if self.request.query_params:
            filter = self.build_params_filter(self.request.query_params)
            if filter:
                return queryset.filter(**filter)
            return None
        return queryset

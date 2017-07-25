from api.models import Language
from rest_framework import viewsets
from api.serializers import LanguageSerializer

class LanguageViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
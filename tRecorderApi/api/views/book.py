from api.models import Book
from rest_framework import viewsets
from api.serializers import BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer
from api.models import Book
from rest_framework import viewsets
from api.serializers import BookSerializer
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import views, status


class BookViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class GetBooksView(views.APIView):
    parser_classes = (JSONParser,)

    @staticmethod
    def post(request):
        data = request.data
        book_filter ={}
        if "slug" in data:
            book_filter = Book.objects.filter(slug__iexact=data["slug"])
        if "anthology" in data:
            book_filter = Book.objects.filter(anthology__slug__iexact=data["anthology"]["slug"])
        book = Book.get_books(book_filter)
        return Response(book, status=200)
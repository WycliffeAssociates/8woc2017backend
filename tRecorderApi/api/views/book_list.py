from rest_framework import views, status
from rest_framework.parsers import JSONParser
import json
from api.models import Take, Language, Book
from rest_framework.response import Response
from operator import itemgetter
from api.models import Book

class getBooksView(views.APIView):
    parser_classes = (JSONParser,)

    def get(self, request):
        lst = Book.getBooksList()
        return Response(lst, status = 200)

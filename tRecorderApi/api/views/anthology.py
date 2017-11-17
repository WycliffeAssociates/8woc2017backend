from api.models import Anthology
from rest_framework import viewsets
from api.serializers import AnthologySerializer
from rest_framework.response import Response
from rest_framework.views import APIView

class AnthologyViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Anthology.objects.all()
    serializer_class = AnthologySerializer

class GetAnthologies(APIView):

    def get(self,request):
        return self.get_anthology()

    def post(self,request):
        return self.get_anthology(request.data['slug'])

    def get_anthology(self,slug=None):
        anthology_response = []
        if slug is not None:
            anthologies = Anthology.objects.filter(slug=slug)
        else:
            anthologies = Anthology.objects.all()

        for anthology in anthologies:
            nthology = {
                "slug": anthology.slug,
                "name": anthology.name
            }
            anthology_response.append(nthology)
        if len(anthology_response)!=0:
            return Response(anthology_response, status=200)
        else:
            return Response(anthology_response, status=204)

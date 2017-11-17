from api.models import Language
from rest_framework.response import Response
from rest_framework.views import APIView

class GetLanguages(APIView):

    def get(self,request):
        return self.get_lang()

    def post(self,request):
        return self.get_lang(request.data['slug'])

    def get_lang(self,slug=None):
        language_response = []
        if slug is not None:
            languages = Language.objects.filter(slug=slug)
        else:
            languages = Language.objects.all()

        for language in languages:
            lang = {
                "slug": language.slug,
                "name": language.name
            }
            language_response.append(lang)
        if len(language_response)!=0:
            return Response(language_response, status=200)
        else:
            return Response(language_response, status=204)

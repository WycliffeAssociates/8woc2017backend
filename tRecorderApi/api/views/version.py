from api.models import Version
from rest_framework.response import Response
from rest_framework.views import APIView


class GetVersions(APIView):

    def get(self, request):
        return self.get_version()

    def post(self, request):
        return self.get_version(request.data['slug'])

    def get_version(self, slug=None):
        version_response = []
        if slug is not None:
            versions = Version.objects.filter(slug=slug)
        else:
            versions = Version.objects.all()

        for version in versions:
            versn = {
                "slug": version.slug,
                "name": version.name
            }
            version_response.append(versn)
        if len(version_response) != 0:
            return Response(version_response, status=200)
        else:
            return Response(version_response, status=204)

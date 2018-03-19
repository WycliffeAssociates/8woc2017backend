import base64
import os
import uuid
import re
import time
import pydub
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password, check_password
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator

from api.file_transfer import FileUtility
from django.conf import settings
from ..models.user import User
from rest_framework import viewsets
from rest_framework import views
from ..serializers import UserSerializer
from rest_framework import status


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Return list of users based on given query string",
    manual_parameters=[
        openapi.Parameter(
            name='id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a user",
        ), openapi.Parameter(
            name='icon_hash', in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            description="Icon hash of a user",
        ), openapi.Parameter(
            name='is_social', in_=openapi.IN_QUERY,
            type=openapi.TYPE_BOOLEAN,
            description="Social status of a user. Whether a user was created via social media or identicon.",
        )
    ]
))
class UserViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = []
        query = self.request.query_params
        if len(query) == 0:
            return User.objects.filter(is_superuser=False)
        else:
            pk = query.get("id", None)
            icon_hash = query.get("icon_hash", None)
            is_social = query.get("is_social", None)
            if pk is not None:
                queryset = User.objects.filter(id=pk, is_superuser=False)
            if icon_hash is not None:
                queryset = User.objects.filter(icon_hash=icon_hash, is_superuser=False)
            if is_social is not None:
                if is_social == "true":
                    queryset = User.objects.filter(icon_hash__exact="", is_superuser=False)
                else:
                    queryset = User.objects.filter(is_superuser=False).exclude(icon_hash__exact="")

            if len(queryset) != 0:
                return queryset
            else:
                return None

    def destroy(self, request, pk=None):
        instance = self.get_object()
        try:
            os.remove(instance.name_audio)
        except OSError:
            pass
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

    def create(self, request):

        data = request.data

        if "iconHash" not in data or data["iconHash"].strip() == "":
            return Response({"error": "empty_icon_hash"}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(icon_hash=data["iconHash"])
        if created:
            if "nameAudio" not in data or data["nameAudio"].strip() == "":
                user.delete()
                return Response({"error": "empty_name_audio"}, status=status.HTTP_400_BAD_REQUEST)

            name_audio = data["nameAudio"]
            uuid_name = str(uuid.uuid1())[:8]

            nameaudios_folder = os.path.join(
                settings.BASE_DIR, "media", "dump", "name_audios")
            nameaudio_location = os.path.join(nameaudios_folder, uuid_name)
            relpath = FileUtility.relative_path(nameaudio_location)

            if not os.path.exists(nameaudios_folder):
                os.makedirs(nameaudios_folder)

            try:
                name = self.blob2base64decode(name_audio)
                with open(nameaudio_location + '.webm', 'wb') as audio_file:
                    audio_file.write(name)
                if os.path.isfile(nameaudio_location + '.webm'):
                    print(nameaudio_location + '.webm')
                    print("file exists")
                else:
                    print("file doesnt exist?")
                sound = pydub.AudioSegment.from_file(nameaudio_location + '.webm')
                sound.export(nameaudio_location + ".mp3", format='mp3')
                os.remove(nameaudio_location + ".webm")
            except Exception as e:
                user.delete()
                print(e)
                if os.path.isfile(nameaudio_location + '.webm'):
                    os.remove(nameaudio_location + '.webm')
                return Response({"error": "bad_audio"}, status=status.HTTP_400_BAD_REQUEST)

            password = make_password("P@ssw0rd-22")

            user.username = uuid_name
            user.password = password
            user.name_audio = relpath + ".mp3"
            user.save()

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "userId": user.pk,
            "nameAudio": user.name_audio
        }, status=status.HTTP_200_OK)

    def blob2base64decode(self, str):
        return base64.decodebytes(bytes(re.sub(r'^(.*base64,)', '', str), 'utf-8'))


class LoginUserView(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data

        if "iconHash" not in data or data["iconHash"].strip() == "":
            return Response({"error": "empty_icon_hash"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(icon_hash=data["iconHash"]).first()

        if user and check_password("P@ssw0rd-22", user.password):
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "userId": user.pk,
                "nameAudio": user.name_audio
            }, status=status.HTTP_200_OK)

        return Response({"error": "Wrong user"}, status=status.HTTP_400_BAD_REQUEST)


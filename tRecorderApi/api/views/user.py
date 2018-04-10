import base64
import os
import re
import uuid

import pydub
from ..file_transfer import FileUtility
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework import views
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from ..permissions import CanCreateOrDestroyOrReadonly
from ..models.user import User
from ..serializers import UserSerializer


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
    permission_classes = (CanCreateOrDestroyOrReadonly,)

    def retrieve(self, request, pk=None):
        if pk == 'me':
            user = request.user
        else:
            user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = []
        query = self.request.query_params
        if len(query) == 0:
            return User.objects.filter(is_superuser=False)
        else:
            pk = query.get("id", None)
            icon_hash = query.get("icon_hash", None)
            is_staff = query.get("is_staff", None)
            if pk is not None:
                queryset = User.objects.filter(id=pk, is_superuser=False)
            if icon_hash is not None:
                queryset = User.objects.filter(icon_hash=icon_hash, is_superuser=False)
            if is_staff is not None:
                if is_staff == "true":
                    queryset = User.objects.filter(is_staff=True, is_superuser=False)
                else:
                    queryset = User.objects.filter(is_staff=False, is_superuser=False)

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
        if "nameAudio" not in data or data["nameAudio"].strip() == "":
            return Response({"error": "empty_name_audio"}, status=status.HTTP_400_BAD_REQUEST)

        uuid_name = str(uuid.uuid1())[:8]
        name_audio_location = self.create_name_audio(data["nameAudio"], uuid_name)

        if name_audio_location is not None:
            if not User.objects.filter(icon_hash=data["iconHash"]).exists():
                user = self.create_user(data["iconHash"], uuid_name, name_audio_location)
                if user is not None:
                    token, created = Token.objects.get_or_create(user=user)

                    return Response({
                        "token": token.key,
                        "userId": user.pk,
                        "nameAudio": user.name_audio
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "user_exists"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "bad_name_audio"}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def blob2base64decode(str):
        return base64.decodebytes(bytes(re.sub(r'^(.*base64,)', '', str), 'utf-8'))

    def create_name_audio(self, name_audio, uuid_name):
        nameaudios_folder = os.path.join(
            settings.BASE_DIR, "media", "dump", "name_audios")
        nameaudio_location = os.path.join(nameaudios_folder, uuid_name)
        relpath = FileUtility.relative_path(nameaudio_location) + ".mp3"

        if not os.path.exists(nameaudios_folder):
            os.makedirs(nameaudios_folder)

        try:
            name = self.blob2base64decode(name_audio)
            with open(nameaudio_location + '.webm', 'wb') as audio_file:
                audio_file.write(name)
            sound = pydub.AudioSegment.from_file(nameaudio_location + '.webm')
            sound.export(nameaudio_location + ".mp3", format='mp3')
            os.remove(nameaudio_location + ".webm")
        except Exception:
            if os.path.isfile(nameaudio_location + '.webm'):
                os.remove(nameaudio_location + '.webm')
            return None

        return relpath

    def create_user(self, icon_hash, uuid_name, name_audio):
        password = make_password("P@ssw0rd-22")
        user = User.objects.create(
            icon_hash=icon_hash,
            username=uuid_name,
            password=password,
            name_audio=name_audio
        )

        return user


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

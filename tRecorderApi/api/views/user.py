import base64
import os
import re
import uuid

import pydub
from api.file_transfer import FileUtility
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework import views
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

from api.permissions import CanCreateOrDestroyOrReadonly
from api.models.user import User
from api.serializers import UserSerializer


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
    authentication_classes = (TokenAuthentication,)

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
            is_social = query.get("is_social", None)
            if pk is not None:
                queryset = User.objects.filter(id=pk, is_superuser=False)
            if icon_hash is not None:
                queryset = User.objects.filter(icon_hash=icon_hash, is_superuser=False)
            if is_social is not None:
                if is_social == "true":
                    queryset = User.objects.filter(is_social=True, is_superuser=False)
                else:
                    queryset = User.objects.filter(is_social=False, is_superuser=False)

            if len(queryset) != 0:
                return queryset
            else:
                return None

    def create(self, request):

        data = request.data
        is_social = False
        
        if "is_social" in data and data["is_social"]:
            is_social = True

        if "icon_hash" not in data or data["icon_hash"].strip() == "":
            return Response({"error": "empty_icon_hash"}, status=status.HTTP_400_BAD_REQUEST)
        if "name_audio" not in data or data["name_audio"].strip() == "":
            return Response({"error": "empty_name_audio"}, status=status.HTTP_400_BAD_REQUEST)

        uuid_name = str(uuid.uuid1())
        username = uuid_name[:8]
        name_audio_location = self.create_name_audio(data["name_audio"], uuid_name)

        if name_audio_location is not None:
            if not User.objects.filter(icon_hash=data["icon_hash"]).exists():
                user = self.create_user(data["icon_hash"], username, name_audio_location, is_social)
                if user is not None:
                    token, created = Token.objects.get_or_create(user=user)

                    return Response({
                        "token": token.key,
                        "user_id": user.pk,
                        "name_audio": user.name_audio
                    }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "user_exists"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "bad_name_audio"}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """
        User partial update
        """
        user = self.get_object()
        data = request.data

        if "name_audio" in data:
            uuid_name = str(uuid.uuid1())
            name_audio_location = self.create_name_audio(data["name_audio"], uuid_name)

            if name_audio_location is not None:
                data["name_audio"] = name_audio_location
            else:
                return Response({"error": "bad_name_audio"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def get_blob_from_base64(base64_str):
        return base64.decodebytes(bytes(re.sub(r'^(.*base64,)', '', base64_str), 'utf-8'))

    def create_name_audio(self, name_audio, uuid_name):
        nameaudios_folder = os.path.join(
            settings.BASE_DIR, "media", "dump", "name_audios")
        nameaudio_location = os.path.join(nameaudios_folder, uuid_name)
        relpath = FileUtility.relative_path(nameaudio_location)

        if not os.path.exists(nameaudios_folder):
            os.makedirs(nameaudios_folder)

        try:
            name = self.get_blob_from_base64(name_audio)
            with open(nameaudio_location + '.webm', 'wb') as audio_file:
                audio_file.write(name)
            sound = pydub.AudioSegment.from_file(nameaudio_location + '.webm')
            sound.export(nameaudio_location, format='mp3')
            os.remove(nameaudio_location + ".webm")
        except Exception:
            if os.path.isfile(nameaudio_location + '.webm'):
                os.remove(nameaudio_location + '.webm')
            return None

        return relpath

    def create_user(self, icon_hash, username, name_audio, is_social):
        password = make_password("P@ssw0rd")
        user = User.objects.create(
            icon_hash=icon_hash,
            username=username,
            password=password,
            name_audio=name_audio,
            is_social=is_social
        )

        return user


class LoginUserView(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data

        if "icon_hash" not in data or data["icon_hash"].strip() == "":
            return Response({"error": "empty_icon_hash"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(icon_hash=data["icon_hash"]).first()

        if user and check_password("P@ssw0rd", user.password):
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "user_id": user.pk,
                "name_audio": user.name_audio
            }, status=status.HTTP_200_OK)

        return Response({"error": "Wrong user"}, status=status.HTTP_400_BAD_REQUEST)

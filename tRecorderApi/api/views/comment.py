import base64
import os
import re
import time
import uuid

import pydub
from ..file_transfer import FileUtility
from ..models import Comment, Chapter, Chunk, Take
from ..serializers import CommentSerializer
from django.conf import settings
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from ..permissions import IsOwnerOrReadOnly


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Return list of comments based on given query string",
    manual_parameters=[
        openapi.Parameter(
            name='id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a comment",
        ), openapi.Parameter(
            name='chapter_id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a chapter",
        ), openapi.Parameter(
            name='chunk_id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a chunk",
        ), openapi.Parameter(
            name='take_id', in_=openapi.IN_QUERY,
            type=openapi.TYPE_INTEGER,
            description="Id of a take",
        )
    ]
))
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = []
        query = self.request.query_params
        if len(query) == 0:
            return Comment.objects.all()
        else:
            pk = query.get("id", None)
            chapter_id = query.get("chapter_id", None)
            chunk_id = query.get("chunk_id", None)
            take_id = query.get("take_id", None)
            if pk is not None:
                queryset = Comment.objects.filter(id=pk)
            if chapter_id is not None:
                queryset = Comment.get_comments(chapter_id=chapter_id)
            if chunk_id is not None:
                queryset = Comment.get_comments(chunk_id=chunk_id)
            if take_id is not None:
                queryset = Comment.get_comments(take_id=take_id)
            if len(queryset) != 0:
                return queryset
            else:
                return None

    def destroy(self, request, pk=None):
        instance = self.get_object()
        try:
            os.remove(instance.location)
        except OSError:
            pass
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

    def blob2base64Decode(self, str):
        return base64.decodebytes(bytes(re.sub(r'^(.*base64,)', '', str), 'utf-8'))

    def create(self, request):

        data = request.data

        if "comment" not in data \
                or "object" not in data or "type" not in data:
            return Response({"error": "not_enough_parameters"}, status=status.HTTP_400_BAD_REQUEST)

        comment = data["comment"]
        obj = data["object"]
        obj_type = data["type"]

        try:
            if obj_type == 'chapter':
                q_obj = Chapter.objects.get(pk=obj)
            elif obj_type == 'chunk':
                q_obj = Chunk.objects.get(pk=obj)
            elif obj_type == 'take':
                q_obj = Take.objects.get(pk=obj)
            else:
                raise ValueError("bad_object")

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        uuid_name = str(time.time()) + str(uuid.uuid4())
        comments_folder = os.path.join(
            settings.BASE_DIR, "media", "dump", "comments")
        comment_location = os.path.join(comments_folder, uuid_name)
        relpath = FileUtility.relative_path(comment_location)

        if not os.path.exists(comments_folder):
            os.makedirs(comments_folder)

        try:
            comment = self.blob2base64Decode(comment)
            with open(comment_location + '.webm', 'wb') as audio_file:
                audio_file.write(comment)
            if os.path.isfile(comment_location + '.webm'):
                print(comment_location + '.webm')
                print("file exists")
            else:
                print("file doesnt exist?")
            sound = pydub.AudioSegment.from_file(comment_location + '.webm')
            sound.export(comment_location + ".mp3", format='mp3')
            os.remove(comment_location + ".webm")
        except Exception as e:
            print(e)
            if os.path.isfile(comment_location + '.webm'):
                os.remove(comment_location + '.webm')
            return Response({"error": "bad_audio"}, status=status.HTTP_400_BAD_REQUEST)

        c = Comment.objects.create(
            location=relpath + ".mp3",
            content_object=q_obj,
            owner=request.user
        )
        c.save()

        serializer = self.get_serializer(c)
        return Response(serializer.data, status=status.HTTP_200_OK)

from api.models import Comment, Chapter, Chunk, Take
from rest_framework import viewsets, status
from rest_framework.response import Response
from api.serializers import CommentSerializer
import os
import re
import base64
import pydub
import time
import uuid
from api.file_transfer import FileUtility
from django.conf import settings


class CommentViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = Comment.objects.all()
        print(queryset)
        pk = self.kwargs.get("pk", None)
        if pk is not None:
            print(pk)
            return Comment.objects.filter(id=pk)
        else:
            query = self.request.query_params
            pk = query.get("id", None)
            chapter_id = query.get("chapter_id", None)
            chunk_id = query.get("chunk_id", None)
            take_id = query.get("take_id", None)
            filter = {}
            if pk is not None:
                queryset = Comment.objects.filter(id=pk)
            if chapter_id is not None:
                queryset = Comment.get_comments(chapter_id=chapter_id)
            if chunk_id is not None:
                queryset = Comment.get_comments(chunk_id=chunk_id)
            if take_id is not None:
                queryset = Comment.get_comments(take_id=take_id)
            return queryset

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
        )
        c.save()

        dic = {
            "location": relpath + ".mp3",
            "id": c.pk
        }

        return Response(dic, status=status.HTTP_200_OK)

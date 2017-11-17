from api.models import Comment
from rest_framework import viewsets, status, views
from api.serializers import CommentSerializer
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from django.forms.models import model_to_dict
from api.models import Take, Chapter, Chunk
import os
import re
import base64
import pydub
import uuid
import time
from django.conf import settings


class CommentViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    parser_classes = (JSONParser, MultiPartParser)

    # def create(self, request):

    #     data = request.data

    #     if "comment" not in data
    #         or "object" not in data
    #         or "type" not in data:
    #         return Response(
    #             {"error": "not_enough_parameters"},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     comment = data["comment"]
    #     obj = data["object"]
    #     obj_type = data["type"]

    #     try:
    #         if obj_type == 'chapter':
    #             q_obj = Chapter.objects.get(pk=obj)
    #         elif obj_type == 'chunk':
    #             q_obj = Chunk.objects.get(pk=obj)
    #         elif obj_type == 'take':
    #             q_obj = Take.objects.get(pk=obj)
    #         else:
    #             raise ValueError("bad_object")
    #     except Exception as e:
    #         return Response(
    #             {"error": str(e)},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     uuid_name = str(time.time()) + str(uuid.uuid4())
    #     comments_folder = os.path.join(
    #         settings.BASE_DIR,
    #         "media/dump/comments"
    #     )
    #     comment_location = os.path.join(comments_folder, uuid_name)
    #     relpath = getRelativePath(comment_location)

    #     if not os.path.exists(comments_folder):
    #         os.makedirs(comments_folder)

    #     try:
    #         comment = self.blob2base64Decode(comment)
    #         with open(comment_location + '.webm', 'wb') as audio_file:
    #             audio_file.write(comment)

    #         sound = pydub.AudioSegment.from_file(comment_location + '.webm')
    #         sound.export(comment_location + ".mp3", format='mp3')
    #         os.remove(comment_location + ".webm")
    #     except:
    #         if os.path.isfile(comment_location + '.webm'):
    #             os.remove(comment_location + '.webm')
    #         return Response(
    #             {"error": "bad_audio"},
    #             status=status.HTTP_400_BAD_REQUEST
    #         )

    #     c = Comment.objects.create(
    #         location=relpath + ".mp3",
    #         content_object=q_obj,
    #     )
    #     c.save()

    #     dic = {
    #         "location": relpath + ".mp3",
    #         "id": c.pk
    #     }

    #     return Response(dic, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        try:
            os.remove(instance.location)
        except OSError:
            pass
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

    def blob2base64Decode(self, str):
        return base64.decodestring(re.sub(r'^(.*base64,)', '', str))


class GetComments(views.APIView):
    def post(self, request):
        data = request.data
        if "chunk_id" in data:
            comments = Comment.get_comments(chunk_id=data["chunk_id"])
        elif "chapter_id" in data:
            comments = Comment.get_comments(chapter_id=data["chapter_id"])
        elif "take_id" in data:
            comments = Comment.get_comments(take_id=data["take_id"])
        else:
            return Response(None, status.HTTP_400_BAD_REQUEST)
        result, http_status = (
            (None, status.HTTP_400_BAD_REQUEST) if comments is None
            else (CommentSerializer(comments, many=True).data, status.HTTP_200_OK)
        )
        return Response(result, http_status)

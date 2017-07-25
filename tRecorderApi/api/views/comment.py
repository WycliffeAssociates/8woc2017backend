from api.models import Comment
from rest_framework import viewsets, status
from api.serializers import CommentSerializer
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, JSONParser
from helpers import getFilePath
from django.forms.models import model_to_dict
from api.models import Take, User, Chapter, Chunk
import os
import re
import base64
import pydub
import uuid
import time

class CommentViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT, PATCH, POST and DELETE requests."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    parser_classes = (JSONParser, MultiPartParser)

    def create(self, request):
        
        comment = request.data["comment"]
        user = request.data["user"]
        obj = request.data["object"]
        obj_type = request.data["type"]

        if obj_type == 'chapter':
            q_obj = Chapter.objects.get(pk=obj)
        elif obj_type == 'chunk':
            q_obj = Chunk.objects.get(pk=obj)
        elif obj_type == 'take':
            q_obj = Take.objects.get(pk=obj)
        else:
            return Response({"error": "wrong_object"}, status=status.HTTP_400_BAD_REQUEST)

        q_user = User.objects.get(pk=user)
        
        uuid_name = str(time.time()) + str(uuid.uuid4())
        comment_location = "media/dump/comments/" + uuid_name

        if not os.path.exists("media/dump/comments"):
            os.makedirs("media/dump/comments")

        comment = blob2base64Decode(comment)
        with open(comment_location + '.webm', 'wb') as audio_file:
            audio_file.write(comment)
        
        sound = pydub.AudioSegment.from_file(comment_location + '.webm')
        sound.export(comment_location + ".mp3", format='mp3')
        os.remove(comment_location + ".webm")

        Comment(
            location = comment_location + ".mp3",
            content_object = q_obj,
            user = q_user
        ).save()

        return Response({"location": comment_location + ".mp3"}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        try:
            os.remove(instance.location)
        except OSError:
            pass
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

def blob2base64Decode(str):
    return base64.decodestring(re.sub(r'^(.*base64,)', '', str))
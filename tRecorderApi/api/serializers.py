from rest_framework import serializers
from api.models import Language, Book, Take, Comment, Chapter, Chunk, Project, Anthology

class ProjectSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Project
        fields = '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Language
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Book
        fields = '__all__'

class ChapterSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Chapter
        fields = '__all__'

class ChunkSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Chunk
        fields = '__all__'

# class UserSerializer(serializers.ModelSerializer):
#     """Serializer to map the Model instance into JSON format."""

#     class Meta:
#         """Meta class to map serializer's fields with the model fields."""
#         model = User
#         fields = '__all__'

class TakeSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Take
        fields = '__all__'
        #fields = ('id', 'location', 'duration', 'rating', 'checked_level', 'project_id')
        #read_only_fields = ()

class CommentSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Comment
        fields = '__all__'

class AnthologySerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Anthology
        fields = '__all__'
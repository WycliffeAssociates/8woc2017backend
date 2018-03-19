from api.models import Language, Book, Take, Comment, Chapter, Chunk, Project, Anthology, Version, Mode, User
from rest_framework import serializers
from django.contrib.auth import get_user_model


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    completed = serializers.IntegerField()
    date_modified = serializers.DateTimeField()

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Project
        depth = 1
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
    date_modified = serializers.DateTimeField()
    contributors = serializers.CharField()
    has_comment = serializers.BooleanField(default=False)
    completed = serializers.IntegerField()

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Chapter
        depth = 1
        fields = '__all__'


class ChunkSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    has_comment = serializers.BooleanField(default=False)

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Chunk
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        exclude = ('is_staff', 'is_active', 'date_joined', 'password',
                   'last_login', 'user_permissions', 'groups', 'is_superuser',)


class TakeSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    has_comment = serializers.BooleanField(default=False)

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Take
        fields = '__all__'


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


class TakeForZipSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    # to include only desired fields of nested objects in the response

    # version_slug = serializers.CharField(source='chunk.chapter.project.version.slug')
    # book_slug = serializers.CharField(source='chunk.chapter.project.book.slug')
    # mode_slug = serializers.CharField(source='chunk.chapter.project.mode.slug')
    # anthology_slug = serializers.CharField(source='chunk.chapter.project.anthology.slug')
    # chapter = serializers.CharField(source='chunk.chapter.id')

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Take
        fields = '__all__'
        # 
        # fields = ('location', 'version_slug', 'book_slug', 'mode_slug', 'anthology_slug', 'chapter')
        # # read_only_fields = ()
        depth = 4


class VersionSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Version
        fields = '__all__'


class ModeSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Mode
        fields = '__all__'


class ExcludeFilesSerializer(serializers.ModelSerializer):

    md5hash = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Take
        fields = ('name','md5hash')

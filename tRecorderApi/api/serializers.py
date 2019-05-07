from .models import Language, Book, Take, Comment, Chapter, Chunk, Project, Anthology, Version, Mode, Task, Downloads
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


class CommentSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""

    owner_icon_hash = serializers.CharField(source='owner.icon_hash', allow_null=True)
    owner_name_audio = serializers.CharField(source='owner.name_audio', allow_null=True)

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Comment
        fields = ('id', 'location', 'date_modified', 'object_id',
                  'content_type', 'owner', 'owner_icon_hash', 'owner_name_audio')


class ChapterSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    date_modified = serializers.DateTimeField()
    contributors = serializers.CharField()
    comments = CommentSerializer(many=True, read_only=True)
    completed = serializers.IntegerField()
    total_chunks = serializers.IntegerField()
    uploaded_chunks = serializers.IntegerField()
    published_chunks = serializers.IntegerField()
    has_takes = serializers.BooleanField()

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Chapter
        depth = 1
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ('date_joined', 'password',
                   'last_login', 'user_permissions', 'groups', 'is_superuser',)


class TakeSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    take_num = serializers.IntegerField()
    comments = CommentSerializer(many=True, read_only=True)
    owner_icon_hash = serializers.CharField(source='owner.icon_hash', allow_null=True)
    owner_name_audio = serializers.CharField(source='owner.name_audio', allow_null=True)

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Take
        fields = '__all__'


class ChunkSerializer(serializers.ModelSerializer):
    """Serializer to map the Model instance into JSON format."""
    has_comment = serializers.BooleanField(default=False)
    comments = CommentSerializer(many=True, read_only=True)
    has_takes = serializers.BooleanField(default=False)
    published_take = TakeSerializer(many=False, read_only=True)

    class Meta:
        """Meta class to map serializer's fields with the model fields."""
        model = Chunk
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
        fields = ('name', 'md5hash')


class TaskSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    current = serializers.IntegerField(read_only=True)
    total = serializers.IntegerField(read_only=True)
    progress = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
    details = serializers.DictField(read_only=True)
    started = serializers.DateTimeField(read_only=True)
    finished = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance


class DownloadsSerializer(serializers.Serializer):
    name = serializers.CharField(read_only=True)
    url = serializers.CharField(read_only=True)

    def create(self, validated_data):
        return Downloads(filename=None, **validated_data)

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)
        return instance

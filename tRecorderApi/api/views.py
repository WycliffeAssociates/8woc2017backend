from django.http import HttpResponse, StreamingHttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.core import serializers
from rest_framework import viewsets, views, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FileUploadParser
from api.parsers import MP3StreamParser
from .serializers import LanguageSerializer, BookSerializer, UserSerializer
from .serializers import TakeSerializer, CommentSerializer
from .models import Language, Book, User, Take, Comment
from tinytag import TinyTag
from pydub import AudioSegment
from random import randint
import zipfile
import shutil
import urllib2
import pickle
import json
import pydub
import time
import uuid
import os, glob
from django.conf import settings

class LanguageViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT and DELETE requests."""
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

class BookViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT and DELETE requests."""
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class UserViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT and DELETE requests."""
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TakeViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT and DELETE requests."""
    queryset = Take.objects.all()
    serializer_class = TakeSerializer

    def destroy(self, request, pk = None):
        instance = self.get_object()
        try:
            os.remove(instance.location)
        except OSError:
            pass
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

class CommentViewSet(viewsets.ModelViewSet):
    """This class handles the http GET, PUT and DELETE requests."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def destroy(self, request, pk = None):
        instance = self.get_object()
        try:
            os.remove(instance.location)
        except OSError:
            pass
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)

class ProjectViewSet(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        data = json.loads(request.body)

        lst = []
        takes = Take.objects
        if "language" in data:
            takes = takes.filter(language__slug=data["language"])
        if "version" in data:
            takes = takes.filter(version=data["version"])
        if "book" in data:
            takes = takes.filter(book__slug=data["book"])
        if "chapter" in data:
            takes = takes.filter(chapter=data["chapter"])
        if "startv" in data:
            takes = takes.filter(startv=data["startv"])

        res = takes.values()

        for take in res:
            dic = {}
            # Include language name
            dic["language"] = Language.objects.filter(pk=take["language_id"]).values()[0]
            # Include book name
            dic["book"] = Book.objects.filter(pk=take["book_id"]).values()[0]
            # Include author of file
            user = User.objects.filter(pk=take["user_id"])
            if user:
                dic["user"] = user.values()[0]

            # Include comments
            dic["comments"] = []
            for cmt in Comment.objects.filter(file=take["id"]).values():
                dic2 = {}
                dic2["comment"] = cmt
                # Include author of comment
                cuser = User.objects.filter(pk=cmt["user_id"])
                if cuser:
                    dic2["user"] = cuser.values()[0]
                dic["comments"].append(dic2)

            # Parse markers
            if take["markers"]:
                take["markers"] = json.loads(take["markers"])
            else:
                take["markers"] = {}
            dic["take"] = take
            lst.append(dic)
        return Response(lst, status=200)

class ProjectZipFiles(views.APIView):
    parser_classes = (JSONParser,)
    def post(self, request):
        data = json.loads(request.body)
        lst = []
        wavfiles = []
        takes = Take.objects

        #filter the database with the given parameters
        if "language" in data:
            takes = takes.filter(language__slug=data["language"])
        if "version" in data:
            takes = takes.filter(version=data["version"])
        if "book" in data:
            takes = takes.filter(book__slug=data["book"])
        if "chapter" in data:
            takes = takes.filter(chapter=data["chapter"])
        if "startv" in data:
            takes = takes.filter(startv=data["startv"])

        #create list for locations
        test = []
        lst.append(takes.values())
        for i in lst[0]:
            test.append(i["location"])

        filesInZip = []

        #if an export folder in media doesn't exist, create one
        if not os.path.exists(os.path.join(settings.BASE_DIR, 'media/export/')):
            os.makedirs(os.path.join(settings.BASE_DIR, 'media/export/'))
        location = os.path.join(settings.BASE_DIR, 'media/export/')

        #use shutil to copy the wav files to a new file
        for loc in test:
            abpath = os.path.join(settings.BASE_DIR, loc)
            shutil.copy2(abpath, location)

        #process of renaming/converting to mp3
        for subdir, dirs, files in os.walk(location):
            
            for file in files:
                # store the absolute path which is is it's subdir and where the os step is
                filePath = subdir + os.sep + file

                if filePath.endswith(".wav") or filePath.endswith(".mp3"):
                    # Add to array so it can be added to the archive
                    inputFile = filePath.title().lower()
                    sound = AudioSegment.from_wav(inputFile)
                    fileName = file.title()[:-4].strip().replace(" ","").lower() + ".mp3"
                    sound.export(fileName, format="mp3")
                    filesInZip.append(fileName)

        # Creating zip file
        with zipfile.ZipFile('media/export/' + str(randint(0,20)) + 'zipped_file.zip', 'w') as zipped_f:
            for members in filesInZip:
                zipped_f.write(members)

        #delete the newly created mp3 files (files are still in zip)
        filelist = [ f for f in os.listdir(settings.BASE_DIR) if f.endswith(".mp3") ]

        #delete the mp3 files we copied
        for f in filelist:
            os.remove(f)
        directory=os.path.join(settings.BASE_DIR, 'media/export/')

        #delete the wav files we copied
        os.chdir(directory)
        files=glob.glob('*.wav')

        for filename in files:
            os.remove(filename)
        #currently returns list of the takes we have gathered but this can easily be changed 
        return Response(lst, status=200)

class FileUploadView(views.APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request, filename, format='zip'):
        if request.method == 'POST' and request.data['file']:
            uuid_name = str(time.time()) + str(uuid.uuid4())
            upload = request.data["file"]
            #unzip files

            try:
                zip = zipfile.ZipFile(upload)
                file_name = 'media/dump/' + uuid_name
                zip.extractall(file_name)
                zip.close()
                #extract metadata / get the apsolute path to the file to be stored

                # Cache language and book to re-use later
                bookname = ''
                bookcode = ''
                langname = ''
                langcode = ''

                for root, dirs, files in os.walk(file_name):
                    for f in files:
                        abpath = os.path.join(root, os.path.basename(f))
                        #abpath = os.path.abspath(os.path.join(root, f))
                        try:
                            meta = TinyTag.get(abpath)
                        except LookupError:
                            return Response({"response": "badwavefile"}, status=403)

                        a = meta.artist
                        lastindex = a.rfind("}") + 1
                        substr = a[:lastindex]
                        pls = json.loads(substr)

                        if bookcode != pls['slug']:
                            bookcode = pls['slug']
                            bookname = getBookByCode(bookcode)
                        if langcode != pls['language']:
                            langcode = pls['language']
                            langname = getLanguageByCode(langcode)

                        data = {
                            "langname": langname,
                            "bookname": bookname,
                            "duration": meta.duration
                            }
                        prepareDataToSave(pls, abpath, data)
                return Response({"response": "ok"}, status=200)
            except zipfile.BadZipfile:
                return Response({"response": "badzipfile"}, status=403)
        else:
            return Response(status=404)

class FileStreamView(views.APIView):
    parser_classes = (MP3StreamParser,)

    def get(self, request, filepath, format='mp3'):
        sound = pydub.AudioSegment.from_wav(filepath)
        file = sound.export()

        return StreamingHttpResponse(file)

def index(request):
    take = Take.objects.all().last()
    return render(request, 'index.html', {"lasttake":take})

def prepareDataToSave(meta, abpath, data):
    book, b_created = Book.objects.get_or_create(
        slug = meta["slug"],
        defaults={'slug': meta['slug'], 'booknum': meta['book_number'], 'name': data['bookname']},
    )
    language, l_created = Language.objects.get_or_create(
        slug = meta["language"],
        defaults={'slug': meta['language'], 'name': data['langname']},
    )
    markers = json.dumps(meta['markers'])

    take = Take(location=abpath,
                duration = data['duration'],
                book = book,
                language = language,
                rating = 0, checked_level = 0,
                anthology = meta['anthology'],
                version = meta['version'],
                mode = meta['mode'],
                chapter = meta['chapter'],
                startv = meta['startv'],
                endv = meta['endv'],
                markers = markers,
                user_id = 1) # TODO get author of file and save it to Take model
    take.save()

def getLanguageByCode(code):
    url = 'http://td.unfoldingword.org/exports/langnames.json'
    languages = []
    try:
        response = urllib2.urlopen(url)
        languages = json.loads(response.read())
        with open('language.json', 'wb') as fp:
            pickle.dump(languages, fp)
    except urllib2.URLError, e:
        with open ('language.json', 'rb') as fp:
            languages = pickle.load(fp)

    ln = ""
    for dicti in languages:
        if dicti["lc"] == code:
            ln = dicti["ln"]
            break
    return ln

def getBookByCode(code):
    with open('books.json') as books_file:
        books = json.load(books_file)

    bn = ""
    for dicti in books:
        if dicti["slug"] == code:
            bn = dicti["name"]
            break
    return bn

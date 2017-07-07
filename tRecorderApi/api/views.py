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
import zipfile
import urllib2
import pickle
import json
import pydub
import time
import uuid
import os, glob

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
    parser_classes = (JSONParser,)#
    def post(self, request):
        data = json.loads(request.body)#
        lst = []
        wavfiles = []
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

        test = []
        lst.append(takes.values())
        print(lst[0])
        for i in lst[0]:
            test.append(i["location"])
        #directory = '/Users/lcheng/Desktop/8woc2017backend/tRecorderApi/media/ExportRdy'

 #Create an empty array of files in the zip
        filesInZip = []
        location = os.path.dirname(test[0])
        print(location)
# for all files, sub-folders in a directory
        for subdir, dirs, files in os.walk(location):
            # look at all the files
            for file in files:
                # store the absolute path which is is it's subdir and where the os step is
                filePath = subdir + os.sep + file
                # if the file is audio
                if filePath.endswith(".wav") or filePath.endswith(".mp3"):
                    #print "4\n"
                    # Add to array so it can be added to the archive
                    inputFile = filePath.title().lower()
                    #print file.title().lower()
                    #print inputFile[:-3].strip().replace(" ","").upper()#
                    sound = AudioSegment.from_wav(inputFile)
                    #print sound
                    fileName = file.title()[:-4].strip().replace(" ","").lower() + ".mp3"
                    #print fileName
                    sound.export(fileName, format="mp3")
                    #print "6"
                    filesInZip.append(fileName)
                    #print filesInZip#
# using zip file create a file called zipped_file.zip
        # adding the members ot filesInZip array to the compressed file
        with zipfile.ZipFile('/Users/lcheng/Desktop/8woc2017backend/tRecorderApi/media/export/zipped_file.zip', 'w') as zipped_f:
            # for all the member in the array of files add them to the zip archive
            # doing this - this way also preserves exactly the directory location that the files sit in even before the main archive
            for members in filesInZip:
                zipped_f.write(members)

        filelist = [ f for f in os.listdir('/Users/lcheng/Desktop/8woc2017backend/tRecorderApi') if f.endswith(".mp3") ]
        for f in filelist:
            os.remove(f)
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
                        #abpath = os.path.join(root, os.path.basename(f))
                        abpath = os.path.abspath(os.path.join(root, f))
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

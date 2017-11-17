import datetime

from api.file_transfer.ArchiveIt import ArchiveIt
from api.file_transfer.AudioUtility import AudioUtility
from api.file_transfer.Download import Download
from api.file_transfer.FileUtility import FileUtility
from api.models import Project
from api.models import Take
from pytz import UTC
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView


class ZipProjectFiles(APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data

        project_to_find, chunk_list = self.chunk_list(data)

        if not chunk_list:
            return Response({"error", "not_enough_parameters"}, status=400)
        if len(chunk_list['chunks']) > 0:
            project_name = chunk_list['language']["slug"] + \
                           "_" + chunk_list['project']['version'] + \
                           "_" + chunk_list['book']['slug']

            zip_it = Download(ArchiveIt(), AudioUtility(), FileUtility())

            root_dir = zip_it.file_utility.root_dir(['media', 'export'])

            location_list = self.location_list(root_dir, chunk_list, zip_it.file_utility.create_path,
                                               zip_it.file_utility.take_location)

            zipped_file_location = zip_it.download(project_name, location_list, root_dir)
            return Response({"location": zip_it.file_utility.relative_path(zipped_file_location)}, status=200)
        else:
            return Response({"error": "no_files"}, status=400)

    def chunk_list(self, data):
        project_to_find = {}
        if 'language' in data and 'version' in data and 'book' in data:
            project_to_find['language'] = data['language']
            project_to_find['version'] = data['version']
            project_to_find['book'] = data['book']
            try:
                project_id = Project.project_id(data)
                take_list = Take.by_project_id(project_id)
                return project_to_find, take_list
            except Exception as e:
                return e
                # return project_to_find, self.fake_chunk_list()
        else:
            return project_to_find, []

    def fake_chunk_list(self):
        return {'chunks':
                    [{'endv': 1, 'startv': 1,
                      'takes': [
                          {'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Mary'},
                           'comments':
                               [{'comment': {
                                   'date_modified': datetime.datetime(2017, 10, 20, 18, 9, 16, 452326, tzinfo=UTC),
                                   u'id': 550,
                                   'location': u'media/dump/comments/1508522955.03ba0d2145-41fd-4c83-89f1-f2ccd92a3c5d.mp3'},
                                   'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Gertrude'}}],
                           'take': {'rating': 3, 'is_publish': True,
                                    'date_modified': datetime.datetime(2017, 10, 20, 17, 32, 15, 274426, tzinfo=UTC),
                                    'markers': {
                                        u'1': 0},
                                    'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v01_t05.wav',
                                    'duration': 6, u'id': 712}}], 'comments': [], u'id': 463}, {
                         'endv': 5, 'startv': 5, 'takes': [
                            {'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Mary'}, 'comments': [],
                             'take': {'rating': 3, 'is_publish': True,
                                      'date_modified': datetime.datetime(2017, 10, 20, 17, 32, 8, 620248,
                                                                         tzinfo=UTC), 'markers': {
                                     u'5': 0},
                                      'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v05_t02.wav',
                                      'duration': 9, u'id': 711}}], 'comments': [], u'id': 462}, {
                         'endv': 7, 'startv': 6,
                         'takes': [{'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Mary'},
                                    'comments': [{'comment': {
                                        'date_modified': datetime.datetime(2017, 10, 20, 19, 29, 24, 964115,
                                                                           tzinfo=UTC), u'id': 555,
                                        'location': u'media/dump/comments/1508527762.574bd2a05e-5d5f-4dac-9bb2-7e791939b4d0.mp3'},
                                        'user': {
                                            'picture': u'picture.jpg', 'agreed': True, 'name': u'Gertrude'}},
                                        {'comment': {
                                            'date_modified': datetime.datetime(2017, 10, 20, 19, 30, 44, 299460,
                                                                               tzinfo=UTC), u'id': 556,
                                            'location': u'media/dump/comments/1508527842.647dc6c70d-203b-41a0-a716-7527a95ad85a.mp3'},
                                            'user': {
                                                'picture': u'picture.jpg', 'agreed': True, 'name': u'Gertrude'}}],
                                    'take': {'rating': 0, 'is_publish': True,
                                             'date_modified': datetime.datetime(
                                                 2017, 10, 20, 17, 33, 49,
                                                 330280,
                                                 tzinfo=UTC), 'markers': {
                                            u'6': 0},
                                             'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v06-07_t04.wav',
                                             'duration': 17, u'id': 717}}], 'comments': [], u'id': 468}, {
                         'endv': 10, 'startv': 8,
                         'takes': [{'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Mary'},
                                    'comments': [{'comment': {
                                        'date_modified': datetime.datetime(2017, 10, 20, 19, 31, 43, 161385,
                                                                           tzinfo=UTC), u'id': 557,
                                        'location': u'media/dump/comments/1508527901.5484add13c-221c-49b0-a22a-8d3514d1743b.mp3'},
                                        'user': {
                                            'picture': u'picture.jpg', 'agreed': True, 'name': u'Gertrude'}}],
                                    'take': {'rating': 0, 'is_publish': True,
                                             'date_modified': datetime.datetime(
                                                 2017, 10, 20, 17, 33, 11,
                                                 474975,
                                                 tzinfo=UTC), 'markers': {
                                            u'8': 0},
                                             'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v08-10_t04.wav',
                                             'duration': 20, u'id': 715}}], 'comments': [], u'id': 466}, {
                         'endv': 13, 'startv': 11, 'takes': [
                            {'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Mary'}, 'comments': [],
                             'take': {'rating': 3, 'is_publish': False,
                                      'date_modified': datetime.datetime(2017, 10, 20, 17, 31, 58, 524294,
                                                                         tzinfo=UTC), 'markers': {
                                     u'11': 0},
                                      'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v11-13_t02.wav',
                                      'duration': 25, u'id': 710}}], 'comments': [], u'id': 461}, {
                         'endv': 16, 'startv': 14, 'takes': [
                            {'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Mary'}, 'comments': [],
                             'take': {'rating': 0, 'is_publish': True,
                                      'date_modified': datetime.datetime(2017, 10, 20, 17, 32, 35, 613796,
                                                                         tzinfo=UTC), 'markers': {
                                     u'14': 0},
                                      'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v14-16_t02.wav',
                                      'duration': 18, u'id': 713}}], 'comments': [], u'id': 464}, {
                         'endv': 26,
                         'startv': 24,
                         'takes': [],
                         'comments': [],
                         u'id': 472}, {
                         'endv': 28,
                         'startv': 27,
                         'takes': [
                             {
                                 'user': {
                                     'picture': u'picture.jpg',
                                     'agreed': True,
                                     'name': u'Mary'},
                                 'comments': [],
                                 'take': {
                                     'rating': 0,
                                     'is_publish': True,
                                     'date_modified': datetime.datetime(
                                         2017,
                                         10,
                                         20,
                                         17,
                                         34,
                                         44,
                                         632063,
                                         tzinfo=UTC), 'markers': {
                                         u'27': 0},
                                     'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v27-28_t02.wav',
                                     'duration': 20, u'id': 720}}], 'comments': [], u'id': 471}, {
                         'endv': 30, 'startv': 29, 'takes': [
                            {'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Mary'}, 'comments': [],
                             'take': {'rating': 0, 'is_publish': True,
                                      'date_modified': datetime.datetime(2017, 10, 20, 17, 34, 23, 648432,
                                                                         tzinfo=UTC), 'markers': {
                                     u'29': 0},
                                      'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v29-30_t02.wav',
                                      'duration': 14, u'id': 719}}], 'comments': [], u'id': 470}, {
                         'endv': 32, 'startv': 31, 'takes': [
                            {'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Mary'}, 'comments': [],
                             'take': {'rating': 0, 'is_publish': True,
                                      'date_modified': datetime.datetime(2017, 10, 20, 17, 32, 50, 867670,
                                                                         tzinfo=UTC), 'markers': {
                                     u'31': 0},
                                      'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v31-32_t03.wav',
                                      'duration': 14, u'id': 714}}], 'comments': [], u'id': 465}, {
                         'endv': 35, 'startv': 33, 'takes': [
                            {'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Mary'}, 'comments': [],
                             'take': {'rating': 0, 'is_publish': True,
                                      'date_modified': datetime.datetime(2017, 10, 20, 17, 34, 7, 410140,
                                                                         tzinfo=UTC), 'markers': {
                                     u'33': 0},
                                      'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v33-35_t04.wav',
                                      'duration': 17, u'id': 718}}], 'comments': [], u'id': 469}, {
                         'endv': 37, 'startv': 36, 'takes': [
                            {'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Mary'}, 'comments': [],
                             'take': {'rating': 0, 'is_publish': True,
                                      'date_modified': datetime.datetime(2017, 10, 20, 17, 33, 31, 716810,
                                                                         tzinfo=UTC), 'markers': {
                                     u'36': 0},
                                      'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v36-37_t02.wav',
                                      'duration': 19, u'id': 716}}], 'comments': [], u'id': 467}], 'project': {
            'is_publish': True, 'version': u'ulb', u'id': 29, 'anthology': u'nt', 'mode': u'chunk'}, 'book': {
            'slug': u'mrk', 'booknum': 42, 'name': u'Mark'}, 'chapter': {'is_publish': False, 'checked_level': 0,
                                                                         u'id': 36, 'comments': [],
                                                                         'number': 7}, 'language': {
            'slug': u'en-x-demo2', 'name': u'English demo2'}}

    def location_list(self, root_dir, chunk_list, chapter_dir, take_location):
        chapter_directory = ""
        locations = []
        for chunk in chunk_list["chunks"]:
            for take in chunk['takes']:
                lang = chunk_list['language']["slug"]
                version = chunk_list['project']['version']
                book = chunk_list['book']['slug']
                number = str(chunk_list['chapter']['number'])
                location = {}
                location["src"] = take_location(take["take"]["location"])
                location["dst"] = chapter_dir(root_dir, lang, version, book, str(number))
                locations.append(location)
        return locations

    # code flow
    """
    //dealing with data received
    1.Check project is in the data
    2.If project is not in data check language,version,book is not in data,then return not enough parameter
    3.Create an empty dictionary
    4.Check if project is in data
    5.if project is in data assign it to dictionary created,else
    6.check if language,book,version is in data
    7.If language,book,version is in data assign them to the created dictionary

    //dealing with database
    8.Fetch project(which is array of chunks with array of takes),database query
    9.Check if project exist

    //dealing with file system
    10.If porject exists,construct project_path
    11.Create directory for project(project_path) if it doesn't exist
    12.Loop through Chunks and create chapter_path
    13.Loop through takes in chunk
    14.Create array of takes location(source and destination)
    15.Copy takes to destination from source location

    //data manupulation and informing
    16.Converts moved .wav file to .mp3
    17.Zip the files and send response with location of files,else
    18.Send Response with status 400
    """

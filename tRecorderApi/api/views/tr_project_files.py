import datetime

from api.file_transfer.ArchiveIt import ArchiveIt
from api.file_transfer.AudioUtility import AudioUtility
from api.file_transfer.Download import Download
from api.file_transfer.FileUtility import FileUtility
from pytz import UTC
from rest_framework import views
from rest_framework.parsers import JSONParser
from rest_framework.response import Response


class TrProjectFiles(views.APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        data = request.data
        # project = Chunk.getChunksWithTakesByProject(new_data)
        chunk_list = self.fake_data()
        if len(chunk_list["chunks"]) > 0:
            tr_it = Download(ArchiveIt(), AudioUtility(), FileUtility())

            root_folder = tr_it.file_utility.root_dir(['media', 'tmp'])

            lang = chunk_list['language']["slug"]
            version = chunk_list['project']['version']
            book = chunk_list['book']['slug']

            filename = lang + '_' + version + '_' + book

            project_folder = tr_it.file_utility.create_folder_path(root_folder, lang, version, book)
            try:
                for chunk in chunk_list["chunks"]:
                    for take in chunk["takes"]:
                        chapter_folder = tr_it.file_utility.create_chapter_path(root_folder, str(
                            chunk_list['chapter']['number']).zfill(2))
                        file_path = tr_it.file_utility.copy_files(take['take']['location'], chapter_folder)

                        if file_path.endswith('.wav'):
                            file_path_mp3 = file_path.replace('.wav', '.mp3')
                            meta = {
                                "anthology": chunk_list['project']["anthology"],
                                "language": chunk_list["language"]["slug"],
                                "version": chunk_list['project']["version"],
                                "slug": chunk_list['book']["slug"],
                                "book_number": str(chunk_list['book']["booknum"]).zfill(2),
                                "mode": chunk_list['project']["mode"],
                                "chapter": str(chunk_list["chapter"]['number']).zfill(2),
                                "startv": chunk["startv"],
                                "endv": chunk["endv"],
                                "markers": take['take']["markers"]
                            }
                            tr_it.audio_utility.write_meta(file_path, file_path_mp3, meta)
                            tr_it.file_utility.remove_file(file_path)
                tr_it.file_utility.compile_into_tr(root_folder)
                filename = tr_it.file_utility.create_tr_path('media', 'tmp', filename)
                tr_it.file_utility.rename(root_folder + ".tr", filename)
                tr_it.file_utility.remove_dir(root_folder)
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        else:
            return Response({"response": "no_source_files"}, status=400)
        return Response({"location": tr_it.file_utility.relative_path(filename)}, status=200)

    def chunk_list(self, data):
        new_data = {}

        if "project" in data:
            new_data["project"] = data["project"]
        else:
            new_data["language"] = data["language"]
            new_data["version"] = data["version"]
            new_data["book"] = data["book"]
            new_data["is_publish"] = True

    def fake_data(self):
        return {'chunks':
                    [{'endv': 1, 'startv': 1,
                      'takes': [
                          {'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Mary'},
                           'comments': [{'comment': {
                               'date_modified': datetime.datetime(2017, 10, 20, 18, 9, 16, 452326,
                                                                  tzinfo=UTC), u'id': 550,
                               'location': u'media/dump/comments/1508522955.03ba0d2145-41fd-4c83-89f1-f2ccd92a3c5d.mp3'},
                               'user': {
                                   'picture': u'picture.jpg', 'agreed': True, 'name': u'Gertrude'}}],
                           'take': {'rating': 3,
                                    'is_publish': True,
                                    'date_modified': datetime.datetime(
                                        2017, 10, 20, 17, 32,
                                        15, 274426,
                                        tzinfo=UTC), 'markers': {
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
                                        'date_modified': datetime.datetime(2017, 10, 20, 19, 29, 24,
                                                                           964115,
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
                                    'take': {'rating': 0,
                                             'is_publish': True,
                                             'date_modified': datetime.datetime(
                                                 2017, 10, 20, 17, 33,
                                                 49, 330280,
                                                 tzinfo=UTC), 'markers': {
                                            u'6': 0},
                                             'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v06-07_t04.wav',
                                             'duration': 17, u'id': 717}}], 'comments': [], u'id': 468}, {
                         'endv': 10, 'startv': 8, 'takes': [
                            {'user': {'picture': u'picture.jpg', 'agreed': True, 'name': u'Mary'},
                             'comments': [{'comment': {
                                 'date_modified': datetime.datetime(2017, 10, 20, 19, 31, 43, 161385,
                                                                    tzinfo=UTC), u'id': 557,
                                 'location': u'media/dump/comments/1508527901.5484add13c-221c-49b0-a22a-8d3514d1743b.mp3'},
                                 'user': {
                                     'picture': u'picture.jpg', 'agreed': True, 'name': u'Gertrude'}}],
                             'take': {'rating': 0,
                                      'is_publish': True,
                                      'date_modified': datetime.datetime(
                                          2017, 10, 20, 17, 33,
                                          11, 474975,
                                          tzinfo=UTC), 'markers': {
                                     u'8': 0},
                                      'location': u'media/dump/1508520669.69f035b758-2ba2-4f71-a293-dec5c1c26a09/mrk/07/en-x-demo2_ulb_b42_mrk_c07_v08-10_t04.wav',
                                      'duration': 20, u'id': 715}}], 'comments': [], u'id': 466}, {
                         'endv': 13,
                         'startv': 11,
                         'takes': [],
                         'comments': [],
                         u'id': 461}, {
                         'endv': 16,
                         'startv': 14,
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
                                         32,
                                         35,
                                         613796,
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
            'slug': u'en-x-demo2', 'name': u'English demo2'
        }}

        # code flow
        """
        # checks if project in data
        # checks if one of language,version,book is not in data
        # returns Response("not_enough_parameters"), if any of the check is true
        # create empty object(new_data)
        # checks if data has project, if true sets project to new_data
        # sets language,version,book,is_published=True to new_data object
        
        //database
        #Gets chunks
        
        
        #checks the size of the chunk is >0
        #if false,no_source_files
        #constructs temp folder and filename
        #loops through project to get chunks
        #loops through chunk to get takes
        #constructs chapter_folder, if does not exists,creates it
        #copy take files to chapter_folder
        #stores file_name and file_path in respective variables
        #checks the extension of file,if ends with .wav repaces with .mp3
        #constructs meta data
        #writes meta data to file
        #removes file
        
        
        #uses java lib to bundle into tr file
        #renames the folder to .tr
        #returns location to .tr file
        """

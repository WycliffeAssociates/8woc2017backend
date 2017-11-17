from django.db import models


class Project(models.Model):
    version = models.ForeignKey("Version")
    mode = models.ForeignKey("Mode", on_delete=models.CASCADE)
    anthology = models.ForeignKey("Anthology")
    language = models.ForeignKey("Language")
    source_language = models.ForeignKey(
        "Language",
        related_name="language_source",
        blank=True,
        null=True
    )
    book = models.ForeignKey("Book")
    published = models.BooleanField(default=False)

    class Meta:
        ordering = ["language", "version", "book"]
        unique_together = (("version", "anthology", "language", "mode", "book"),)

    def __str__(self):
        return '{}-{}-{} ({})'.format(self.language, self.version, self.book, self.id)

    @staticmethod
    def project_id(data):
        filter = {}
        filter["language__slug__iexact"] = data["language"]
        filter["version__slug__iexact"] = data["version"]
        filter["book__slug__iexact"] = data["book"]
        project = Project.objects.filter(**filter)[0]
        return project


        # @staticmethod
        # def getProjects(data):
        #     project_list = []
        #     project_filter = {}

        #     project_filter["is_source"] = False
        #     if "language" in data:
        #         project_filter["language__slug"] = data["language"]
        #     if "version" in data:
        #         project_filter["version"] = data["version"]
        #     if "book" in data:
        #         project_filter["book__slug"] = data["book"]
        #     if "is_published" in data:
        #         project_filter["is_published"] = data["is_published"]

        #     #filter projects based on the project being requested
        #     projects = Project.objects.filter(**project_filter)

        #     for project in projects:
        #         dic = {}

        #         dic["id"] = project.id
        #         dic["version"] = project.version
        #         dic["is_publish"] = project.is_publish

        #         latest_take = Take.objects.filter(chunk__chapter__project=project) \
        #             .latest("date_modified")
        #         # Get contributors
        #         dic["contributors"] = []
        #         dic["date_modified"] = latest_take.date_modified
        #         availChunks = 0
        #         checklvl = 10
        #         chapters = project.chapter_set.all()
        #         for chapter in chapters:
        #             availChunks += 1
        #             if chapter.checked_level < checklvl:
        #                 checklvl = chapter.checked_level
        #             chunks = chapter.chunk_set.all()
        #             for chunk in chunks:
        #                 availChunks += 1
        #                 takes = chunk.take_set.all()
        #                 for take in takes:
        #                     try:
        #                         if take.user.name not in dic["contributors"]:
        #                             dic["contributors"].append(take.user.name)
        #                     except:
        #                         pass

        #         dic["checked_level"] = checklvl
        #         mode = project.mode
        #         bkname = project.book.slug
        #         chunkInfo = []
        #         for dirpath, dirnames, files in os.walk(os.path.abspath('static/chunks/')):
        #             if dirpath[-3:] == bkname:
        #                 for fname in os.listdir(dirpath):
        #                     f = open(os.path.join(dirpath, fname), "r")
        #                     sus = json.loads(f.read())
        #                     chunkInfo = sus
        #                 break
        #         totalChunk = float(len(chunkInfo))
        #         completed = int(round((availChunks / totalChunk) * 100))
        #         dic["completed"] = completed

        #             dic["language"] = model_to_dict(project.language,
        #                                             fields=["slug", "name"])

        #             dic["book"] = model_to_dict(project.book,
        #                                         fields=["booknum", "slug", "name"])


        #         lst.append(dic)

        #     return lst

        # @staticmethod
        # def getVersionsByProject():
        #     lst = []
        #     projects = Project.objects.filter(is_source=False)
        #     for project in projects:
        #         if project.version and project.language and project.book:
        #             lst.append(project.version)

        #     # distinct list
        #     lst = list(set(lst))
        #     return lst

        # @staticmethod
        # def getBooksOfExistingProjects():
        #     lst = []
        #     # get all projects
        #     projects = Project.objects.filter(is_source=False)
        #     for project in projects:
        #         # if the project has a version, language, and book, add it to the list
        #         if project.version and project.language and project.book:
        #             lst.append(model_to_dict(project.book))
        #     # distinct list
        #     lst = list({v['id']: v for v in lst}.values())
        #     return lst

        # @staticmethod
        # def getLanguagesList():
        #     lst = []
        #     projects = Project.objects.filter(is_source=False)
        #     for project in projects:
        #         if project.version and project.language and project.book:
        #             lst.append(model_to_dict(project.language))

        #     # distinct list
        #     lst = list({v['id']: v for v in lst}.values())
        #     return lst

        # @staticmethod
        # def getChaptersByProject(data):
        #     dic = {}
        #     filter = {}

        #     filter["language__slug"] = data["language"]
        #     filter["version"] = data["version"]
        #     filter["book__slug"] = data["book"]
        #     filter["is_source"] = False

        #     projects = Project.objects.filter(**filter)

        #     for project in projects:
        #         # Get chapters

        #         if not project.version or not project.language or not project.book:
        #             continue

        #         mode = project.mode
        #         bkname = project.book.slug

        #         latest_take = Take.objects.filter(chunk__chapter__project=project) \
        #             .latest("date_modified")

        #         chaps = []
        #         chapters = project.chapter_set.all()
        #         for chapter in chapters:
        #             chap_dic = {}
        #             chap_dic["id"] = chapter.id
        #             chap_dic["chapter"] = chapter.number
        #             chap_dic["checked_level"] = chapter.checked_level
        #             chap_dic["is_publish"] = chapter.is_publish

        #             # contains information about all chunks in a book
        #             chunkInfo = []
        #             for dirpath, dirnames, files in os.walk(os.path.abspath('static/chunks')):
        #                 if dirpath[-3:] == bkname:
        #                     for fname in os.listdir(dirpath):
        #                         f = open(os.path.join(dirpath, fname), "r")
        #                         sus = json.loads(f.read())
        #                         chunkInfo = sus
        #                     break

        #             # contains info about relevant chapter
        #             chunkstuff = []
        #             chapnum = chapter.number
        #             for chunk in chunkInfo:
        #                 if chunk["id"][:2] == str("%02d" % chapnum):
        #                     chunkstuff.append(chunk)

        #             percentComplete = 0
        #             chunks = chapter.chunk_set.all()

        #             if len(chunkstuff) > 0:
        #                 if mode == "chunk":
        #                     percentComplete = int(
        #                         round(len(chunks) / (len(chunkstuff)) * 100))
        #                 else:
        #                     versetotal = 0
        #                     for i in chunkstuff:
        #                         if int(i["lastvs"]) > versetotal:
        #                             versetotal = int(i["lastvs"])
        #                     if versetotal > 0:
        #                         percentComplete = int(
        #                             round((len(chunks) / versetotal) * 100))

        #             chap_dic["percent_complete"] = percentComplete
        #             chap_dic["date_modified"] = latest_take.date_modified

        #             # Get contributors
        #             chap_dic["contributors"] = []
        #             for chunk in chunks:
        #                 takes = chunk.take_set.all()
        #                 for take in takes:
        #                     try:
        #                         if take.user.name not in chap_dic["contributors"]:
        #                             chap_dic["contributors"].append(take.user.name)
        #                     except:
        #                         pass

        #             # Get comments
        #             chap_dic["comments"] = []
        #             for cmt in chapter.comments.all():
        #                 dic2 = {}
        #                 dic2["comment"] = model_to_dict(
        #                     cmt, fields=["location", "date_modified"])
        #                 # Include author of comment
        #                 try:
        #                     dic2["user"] = model_to_dict(
        #                         cmt.user, fields=["name", "agreed", "picture"])
        #                 except:
        #                     pass
        #                 chap_dic["comments"].append(dic2)

        #             chaps.append(chap_dic)

        #         dic["chapters"] = chaps

        #         # Get language
        #         try:
        #             dic["language"] = model_to_dict(project.language,
        #                                             fields=["slug", "name"])
        #         except:
        #             dic["language"] = {}

        #         # Get book
        #         try:
        #             dic["book"] = model_to_dict(project.book,
        #                                         fields=["booknum", "slug", "name"])
        #         except:
        #             dic["language"] = {}
        #         # Get Project ID
        #         try:
        #             dic["project_id"] = project.id
        #         except:
        #             dic["project_id"] = {}
        #         # Get is_publish
        #         try:
        #             dic["is_publish"] = project.is_publish
        #         except:
        #             dic["is_publish"] = {}
        #     return dic

        # @staticmethod
        # def updateTakesByProject(data):
        #     lst = []
        #     filter = {}
        #     fields = data["fields"]

        #     if "project" in data["filter"]:
        #         filter["chunk__chapter__project"] = data["filter"]["project"]
        #     if "language" in data["filter"]:
        #         filter["chunk__chapter__project__language__slug"] = data["filter"]["language"]
        #     if "version" in data["filter"]:
        #         filter["chunk__chapter__project__version"] = data["filter"]["version"]
        #     if "book" in data["filter"]:
        #         filter["chunk__chapter__project__book__slug"] = data["filter"]["book"]
        #     if "chapter" in data["filter"]:
        #         filter["chunk__chapter__number"] = data["filter"]["chapter"]
        #     if "startv" in data["filter"]:
        #         filter["chunk__startv"] = data["filter"]["startv"]
        #     if "is_publish" in data["filter"]:
        #         filter["chunk__chapter__is_publish"] = data["filter"]["is_publish"]

        #     return Take.objects.filter(**filter).update(**fields)

        # @staticmethod
        # def getChunksWithTakesByProject(data):
        #     data_dic = {}
        #     chunks_list = []
        #     filter = {}

        #     if "project" in data:
        #         filter["chapter__project"] = data["project"]
        #     if "language" in data:
        #         filter["chapter__project__language__slug"] = data["language"]
        #     if "version" in data:
        #         filter["chapter__project__version"] = data["version"]
        #     if "book" in data:
        #         filter["chapter__project__book__slug"] = data["book"]
        #     if "mode" in data:
        #         filter["chapter__project__mode"] = data["mode"]
        #     if "chapter" in data:
        #         filter["chapter__number"] = data["chapter"]
        #     if "startv" in data:
        #         filter["startv"] = data["startv"]
        #     if "endv" in data:
        #         filter["endv"] = data["endv"]

        #     chunks = Chunk.objects.filter(**filter)

        #     data_dic["chunks"] = []

        #     for chunk in chunks:
        #         chunk_dic = {}

        #         # Include language data
        #         try:
        #             if "language" not in data_dic:
        #                 data_dic["language"] = model_to_dict(chunk.chapter.project.language,
        #                                                      fields=["slug", "name"])
        #         except:
        #             pass
        #         # Include book data
        #         try:
        #             if "book" not in data_dic:
        #                 data_dic["book"] = model_to_dict(chunk.chapter.project.book,
        #                                                  fields=["booknum", "slug", "name"])
        #         except:
        #             pass

        #         # Include project data
        #         try:
        #             if "project" not in data_dic:
        #                 data_dic["project"] = model_to_dict(chunk.chapter.project,
        #                                                     fields=["id", "is_publish", "version",
        #                                                             "mode", "anthology"])
        #         except:
        #             pass

        #         # Include chapter data
        #         try:
        #             if "chapter" not in data_dic:
        #                 data_dic["chapter"] = model_to_dict(chunk.chapter,
        #                                                     fields=["id", "is_publish", "number",
        #                                                             "checked_level", "comments"])

        #                 # Include comments for chapter
        #                 data_dic["chapter"]["comments"] = []
        #                 for cmt in chunk.chapter.comments.all():
        #                     comm_dic = {}
        #                     comm_dic["comment"] = model_to_dict(
        #                         cmt, fields=["id", "location", "date_modified"])
        #                     # Include author of comment
        #                     try:
        #                         comm_dic["user"] = model_to_dict(
        #                             cmt.user, fields=["name", "agreed", "picture"])
        #                     except:
        #                         pass
        #                     data_dic["chapter"]["comments"].append(comm_dic)
        #         except:
        #             pass

        #         # Include comments for chunk
        #         chunk_dic["comments"] = []
        #         for cmt in chunk.comments.all():
        #             comm_dic = {}
        #             comm_dic["comment"] = model_to_dict(
        #                 cmt, fields=["id", "location", "date_modified"])
        #             # Include author of comment
        #             try:
        #                 comm_dic["user"] = model_to_dict(
        #                     cmt.user, fields=["name", "agreed", "picture"])
        #             except:
        #                 pass
        #             chunk_dic["comments"].append(comm_dic)

        #         # Include source file if any / TODO remove source from code and db
        #         """source_language = chunk.chapter.project.source_language
        #         if source_language and chunk.chapter.project.book:
        #             source_dic = {}
        #             source_dic["language"] = model_to_dict(source_language, fields=["slug","name"])

        #             source_take = Take.objects \
        #                 .filter(chunk__chapter__project__language__slug=source_dic["language"]["slug"]) \
        #                 .filter(chunk__chapter__project__version=data_dic["project"]["version"]) \
        #                 .filter(chunk__chapter__project__book__slug=data_dic["book"]["slug"]) \
        #                 .filter(chunk__chapter__project__mode=data_dic["project"]["mode"]) \
        #                 .filter(chunk__chapter__number=data_dic["chapter"]["number"]) \
        #                 .filter(chunk__startv=chunk.startv) \
        #                 .filter(chunk__endv=chunk.endv) \
        #                 .filter(chunk__chapter__project__is_source=True) \
        #                 .first()
        #             if source_take:
        #                 if source_take.markers:
        #                     source_take.markers = json.loads(source_take.markers)
        #                 else:
        #                     source_take.markers = {}

        #                 source_dic["take"] = model_to_dict(source_take, fields=[
        #                     "markers","location","id"
        #                 ])
        #                 source_dic["take"]["version"] = source_take.chunk.chapter.project.version
        #                 chunk_dic["source"] = source_dic"""

        #         # Include takes
        #         takes_list = []
        #         for take in chunk.take_set.all():
        #             if "is_publish" in data:
        #                 if take.is_publish != data["is_publish"]:
        #                     continue

        #             take_dic = {}

        #             # Include author of file
        #             try:
        #                 take_dic["user"] = model_to_dict(
        #                     take.user, fields=["name", "agreed", "picture"])
        #             except:
        #                 pass

        #             # Include comments for chunks
        #             take_dic["comments"] = []
        #             # for cmt in Comment.objects.filter(content_type=take.id).values():
        #             for cmt in take.comments.all():
        #                 comm_dic = {}
        #                 comm_dic["comment"] = model_to_dict(
        #                     cmt, fields=["id", "location", "date_modified"])
        #                 # Include author of comment
        #                 try:
        #                     comm_dic["user"] = model_to_dict(
        #                         cmt.user, fields=["name", "agreed", "picture"])
        #                 except:
        #                     pass
        #                 take_dic["comments"].append(comm_dic)

        #             # Parse markers
        #             if take.markers:
        #                 take.markers = json.loads(take.markers)
        #             else:
        #                 take.markers = {}

        #             take_dic["take"] = model_to_dict(take, fields=[
        #                 "location", "duration", "rating",
        #                 "date_modified", "markers", "id",
        #                 "is_publish"
        #             ])

        #             takes_list.append(take_dic)

        #         chunk_dic["takes"] = takes_list

        #         chunk_dic2 = model_to_dict(chunk, fields=[
        #             "startv", "endv", "id"
        #         ])

        #         chunk_dic = dict(chunk_dic.items() + chunk_dic2.items())

        #         data_dic["chunks"].append(chunk_dic)
        #     return data_dic

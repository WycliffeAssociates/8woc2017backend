
from Download import Download
from ZipIt import ZipIt
from AudioUtility import AudioUtility
from FileUtility import FileUtility
import time
import os


def converted_mp3(project, chapterDir):
        chapterDir = ""
        locations = []
        for chunk in project["chunks"]:
            for take in chunk['takes']:
                + os.sep + project['language']["slug"]
                + os.sep + project['project']['version']
                + os.sep + project['book']['slug'] + os.sep
                + str(project['chapter']['number'])

                if not os.path.exists(chapterDir):
                    os.makedirs(chapterDir)
                location = {}
                location["src"] = os.path.join(
                    settings.BASE_DIR, take["take"]["locationation"])
                location["dst"] = chapterDir
                locations.append(location)
        return locations


def dest_file(self, project):
    uuid_name = str(time.time()) + str(uuid.uuid4())
    root_directory = os.path.join(
        settings.BASE_DIR, 'media/export', uuid_name)
    project_name = project['language']["slug"]
    + "_" + project['project']['version']
    +"_" + project['book']['slug']
    return os.path.join(settings.BASE_DIR,
                        'media/export',
                        project_name + ".zip")

# downloading zip
zip = Download(ZipIt(), AudioUtility(), FileUtility())
print("Downloading....")
time.sleep(2)
rootDir = os.path.basename(os.path.dirname(os.path.realpath(__file__)))
location_list = [1, 2, 3, 4]
zip.download(rootDir, location_list)
print("zip completed.")

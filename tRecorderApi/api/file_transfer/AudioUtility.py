import json
import os

from pydub import AudioSegment


class AudioUtility:
    def high_pass_filter(self):
        pass

    def convert_to_mp3(self, root_directory, file_format):
        converted_mp3_list = []
        for subdir, dirs, files in os.walk(root_directory):
            for file in files:
                file_path = os.path.join(subdir, file)
                if file_format == 'zip':
                    if file_path.endswith(".wav"):
                        sound = AudioSegment.from_wav(file_path)

                        filename = file_path.replace(".wav", ".mp3")

                        sound.export(filename, format="mp3")

                        # Add to array so it can be added to the archive
                        converted_mp3_list.append(filename)
                    else:
                        converted_mp3_list.append(filename)
                else:
                    converted_mp3_list.append(file_path)
        return converted_mp3_list

    def write_meta(self, file_path, file_path_mp3, meta):
        sound = AudioSegment.from_wav(file_path)
        return sound.export(file_path_mp3, format='mp3', tags={'artist': json.dumps(meta)})

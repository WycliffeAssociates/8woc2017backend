import json

from pydub import AudioSegment


class AudioUtility:
    def high_pass_filter(self):
        pass

    def convert_to_mp3(self, location_list, file_format, project, user, update_progress, task_args):
        current_take = 0

        for i, file in enumerate(location_list):
            file_path = file["dst"] + "/" + file["fname"]
            if file_format == 'mp3' and file["type"] == "take":
                if file_path.endswith(".wav"):
                    sound = AudioSegment.from_wav(file_path)
                    file_path = file_path.replace(".wav", ".mp3")
                    sound.export(file_path, format="mp3")

                    # Converted file path
                    location_list[i]["final"] = file_path
                else:
                    location_list[i]["final"] = file_path
            else:
                location_list[i]["final"] = file_path

            current_take += 1

            if project and update_progress and task_args:
                # 2/3 of overall task
                progress = int(((current_take / len(location_list) * 100) / 3) + (100 / 3))

                new_task_args = task_args + (progress, 100, 'Converting takes...', {
                    'user_icon_hash': user["icon_hash"],
                    'user_name_audio': user["name_audio"],
                    'lang_slug': project["lang_slug"],
                    'lang_name': project["lang_name"],
                    'book_slug': project["book_slug"],
                    'book_name': project["book_name"],
                    'result': file["fname"]
                })
                update_progress(*new_task_args)

        return location_list

    def write_meta(self, file_path, file_path_mp3, meta):
        sound = AudioSegment.from_wav(file_path)
        return sound.export(file_path_mp3, format='mp3', tags={'artist': json.dumps(meta)})

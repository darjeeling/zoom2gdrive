#!/usr/bin/env python

from dotenv import load_dotenv, dotenv_values
import os
import re
import datetime
import pprint
import json
import requests
from zoomus import ZoomClient

load_dotenv()
config = dotenv_values(".env")
API_KEY = config.get("ZOOM_API_KEY")
API_SECRET = config.get("ZOOM_API_SECRET")
DESTINATION_DIR = config.get("DOWNLOAD_DIR")
client = ZoomClient(API_KEY, API_SECRET)

start_date = datetime.date.today() - datetime.timedelta(days=60)

for user in json.loads(client.user.list().content)["users"]:
    user_id = user["id"]
    for recording in json.loads(
        client.recording.list(user_id=user_id, start=start_date).content
    )["meetings"]:
        start_time_escaped = re.sub(r"(:)", "", recording["start_time"][:-3]).replace(
            "T", "_"
        )
        topic_escaped = recording["topic"].strip().replace(" ", "_")
        new_directory_name = f"{start_time_escaped}_{topic_escaped}"
        dest_dir = os.path.join(DESTINATION_DIR, new_directory_name)
        os.makedirs(dest_dir, exist_ok=True)

        for recording_file in recording["recording_files"]:
            # print(recording_file["download_url"])
            # print(recording_file["file_extension"])
            # print(recording_file["file_type"])
            url = recording_file["download_url"]
            local_filename = os.path.join(
                dest_dir,
                f'{recording_file["recording_type"]}.{recording_file["file_extension"]}',
            )
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(local_filename)

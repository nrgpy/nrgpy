from datetime import datetime
from nrgpy.utilities import date_check, draw_progress_bar
from .auth import nrg_api, upload_url
import os
import requests


class nrg_api_upload(nrg_api):

    def __init__(self, client_id='', client_secret='', filename='', rld_dir='', site_filter='', site_filter2='',
                 start_date='1970-01-01', end_date='2150-12-31'):

        super().__init__(client_id, client_secret)

        self.filename = filename
        self.rld_dir = rld_dir
        self.site_filter = site_filter
        self.site_filter2 = site_filter2
        self.start_date = start_date
        self.end_date = end_date
        self.headers = {"Authorization": "Bearer {}".format(self.session_token)}

        if filename:
            self.pad = 1
            self.counter = 1
            self.raw_count = 1
            self.progress_bar = False
            self.start_time = datetime.now()
            self.upload_file()

        if rld_dir:
            self.upload_directory()

    def upload_file(self):
        if self.progress_bar:
            draw_progress_bar(self.counter, self.raw_count, self.start_time)
        elif self.raw_count == 1:
            print("{0} | API | uploading {1} ... ".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), os.path.basename(self.filename)), end="", flush=True)
        else:
            print("{0} | API | uploading {1}/{2} ... {3} ... ".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(self.counter).rjust(self.pad), str(self.raw_count).ljust(self.pad), os.path.basename(self.filename)), end="", flush=True)

        self.encoded_rld_bytes = self.prepare_file_bytes(self.filename)

        data = {
            'filebytes': self.encoded_rld_bytes
        }

        self.response = requests.request("POST", upload_url, headers=self.headers, data=data)

        if self.progress_bar is False:
            if int(self.response.status_code) < 300:
                print("[OK]")
            else:
                print(f"[FAILED] {self.response.status_code}")

    def upload_directory(self, progress_bar=True):
        self.progress_bar = progress_bar
        self.start_time = datetime.now()

        self.files = [
            f for f in sorted(os.listdir(self.rld_dir))
            if self.site_filter in f and self.site_filter2 in f
            and f.lower().endswith("rld")
            and date_check(self.start_date, self.end_date, f)
        ]

        self.raw_count = len(self.files)
        self.pad = len(str(self.raw_count)) + 1
        self.counter = 1

        for rld in self.files:
            self.filename = os.path.join(self.rld_dir, rld)
            self.upload_file()
            self.counter += 1

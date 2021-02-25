from datetime import datetime
from nrgpy.utils.utilities import affirm_directory
from .auth import nrg_api, export_url
import os
import requests
import zipfile


class nrg_api_export(nrg_api):
    """Uses NRG hosted web-based API to download data in text format
    To sign up for the service, go to https://services.nrgsystems.com/

    Parameters
    ----------
    out_dir : str
        path to save exported data
    out_file : str
        (optional) filename to save
    serial_number : str or int
        serial number of data logger (like, 820612345)
    start_date : str
        "YYYY-MM-DD HH:MM:SS" format, if just date it will return the whole day
        times are in logger local time
    end_date : str
        "YYYY-MM-DD HH:MM:SS" format, if just date it will return the whole day
        times are in logger local time
    client_id : str
        provided by NRG Systems
    client_secret : str
        provided by NRG Systems
    save_file : bool
        (True) whether to save the result to file
    nec_file : str, optional
        path to NEC file for custom export formatting
    text_timestamps : bool
        get export data with text timestamps instead of datetime
    export_type : str
        [meas], samples, diag, comm

    Returns
    -------
    object
        export object that includes an nrgpy reader object

    Examples
    --------
    Download 3 days of data with an NEC file applied

    >>> import nrgpy
    >>> client_id = "contact support@nrgsystems.com for access"
    >>> client_secret = "contact support@nrgsystems.com for access"
    >>> exporter = nrgpy.nrg_api_export(
            client_id=client_id,
            client_secret=client_secret,
            out_dir=txt_dir,
            nec_file='12vbat.nec',
            serial_number=820600019,
            start_date="2020-05-01",
            end_date="2020-05-03",
            text_timestamps=False,
            save_file=False
        )
    >>> reader = exporter.reader
    >>> reader.format_site_data()
    >>> if reader:
    >>>     print(f"Site number               : {reader.site_number}")
    >>>     print(f"Site description          : {reader.site_description}")
    >>>     reader.interval_check = nrgpy.check_intervals(reader.data)
    >>> else:
    >>>     print("unable to get reader")
    """

    def __init__(self, out_dir='', serial_number='', out_file='',
                 start_date='2014-01-01', end_date='2023-12-31',
                 client_id='', client_secret='', nec_file='',
                 export_type='meas', text_timestamps=False, 
                 save_file=True,  **kwargs):

        super().__init__(client_id, client_secret)

        self.txt_file = f'{serial_number}_{start_date}_{end_date}.txt'.replace(':', '-').replace(' ', '_')

        self.filepath = os.path.join(out_dir, self.txt_file.replace('txt', 'zip'))
        self.out_dir = out_dir
        self.out_file = out_file
        affirm_directory(self.out_dir)

        # self.serial_number = str(serial_number)[-5:]  # removing... no longer necessary 2021-01-14
        self.serial_number = serial_number
        self.start_date = start_date
        self.end_date = end_date
        self.nec_file = nec_file
        self.export_type = export_type
        self.text_timestamps = text_timestamps

        if self.nec_file:
            self.encoded_nec_bytes = self.prepare_file_bytes(self.nec_file)
        else:
            self.encoded_nec_bytes = ''

        self.save_file = save_file
        self.reader = self.export()

    def export(self):
        from nrgpy.read.sympro_txt import sympro_txt_read

        self.headers = {"Authorization": "Bearer " + self.session_token}

        self.data = {
            'serialnumber': self.serial_number,
            # 'sitenumber': self.site_number,
            'startdate': self.start_date,
            'enddate': self.end_date,
            'exporttype': self.export_type,
            'necfilebytes': self.encoded_nec_bytes
        }

        self.request_time = datetime.now()
        self.resp = requests.post(data=self.data, url=export_url, headers=self.headers)
        self.request_duration = datetime.now() - self.request_time

        if self.resp.status_code == 200:
            with open(self.filepath, 'wb') as f:
                f.write(self.resp.content)

            with zipfile.ZipFile(self.filepath, 'r') as z:
                data_file = z.namelist()[0]
                z.extractall(self.out_dir)

            reader = sympro_txt_read(
                filename=os.path.join(self.out_dir, data_file),
                text_timestamps=self.text_timestamps
            )
            reader.format_site_data()

            try:
                self.serial_number = reader.logger_sn
                self.site_number = reader.site_number
            except AttributeError:
                pass

            os.remove(self.filepath)
            os.remove(os.path.join(self.out_dir, data_file))

            if self.save_file:
                if not self.out_file:
                    self.out_file = f'{self.site_number}_{self.start_date}_{self.end_date}.txt'.replace(':', '.').replace(' ', '')

                else:
                    self.out_file = os.path.join(self.out_dir, self.txt_file)
                reader.output_txt_file(standard=True, out_file=self.out_file)

            del self.data['necfilebytes']
            self.data['nec_file'] = self.nec_file
            reader.post_json = self.data

            return reader

        else:
            print(self.resp.status_code)
            print(self.resp.reason)
            return False

try:
    from nrgpy import logger
except ImportError:
    pass
import datetime
import time
import os
import subprocess
import shutil
import traceback
from nrgpy.utils.utilities import check_platform, windows_folder_path, linux_folder_path, affirm_directory, count_files, draw_progress_bar


class local(object):
    """nrgpy.convert_rwd.local - use local installation of Symphonie Data Retriever (SDR)
    to convert *.RWD files to *.TXT

    Parameters
    ----------
    filename : str
        if populated, a single file is exported
    encryption_pin : str
        four digit pin, only used for encrypted files
    sdr_path : str
        r'"C:/NRG/SymDR/SDR.exe"', may be any path
    file_filter : str
        filters files on text in filename
    rwd_dir : str (path-like)
        folder to check for RWD files
    out_dir : str (path-like)
        folder to save exported TXT files into
    wine_folder : str
        '~/.wine/drive_c/', for linux installations
    use_site_file : bool
        set to True to use local site file
    raw_mode : bool
        set to True to convert raw counts and voltages
    progress_bar : bool
        set to False to see individual file conversions
    show_result : bool
        set to False to hide prints to console

    Returns
    -------
    None

    Examples
    --------
    Convert a folder of RWD files to Text with SymphoniePRO Desktop Software

    >>> from nrgpy.convert_rwd import local
    >>> converter = local(
            rwd_dir='/path/to/rwd/files',
            out_dir=/path/to/txt/outputs,
            file_filter='1234202001', # for files from January 2020
        )

    >>> converter.convert()


    Convert a folder ... on Linux; this assumes you followed the instructions
    in the '''SDR_Linux_README.md''' file.

    >>> import getpass
    >>> import nrgpy

    >>> username = getpass.getuser()

    >>> rwd_dir = f"/home/{username}/data/symplus3/raw"
    >>> txt_dir = f"/home/{username}/data/symplus3/export"
    >>> wine_folder = f"/home/{username}/prefix32/drive_c"

    >>> converter = nrgpy.convert_rwd.local(
            rwd_dir=rwd_dir,
            out_dir=txt_dir,
            wine_folder=wine_folder
        )

    >>> converter.convert()

    """

    def __init__(self, rwd_dir='', out_dir='', filename='', encryption_pin='',
                 sdr_path=r'C:/NRG/SymDR/SDR.exe',
                 convert_type='meas', file_filter='',
                 wine_folder='~/.wine/drive_c/',
                 use_site_file=False, raw_mode=False, progress_bar=True, show_result=True, **kwargs):

        if encryption_pin != '':
            self.command_switch = '/z'  # noqueue with pin
        else:
            self.command_switch = '/q'  # noqueue (logger params)
        if use_site_file:
            self.command_switch = '/s'  # silent (site file params)
        if raw_mode:
            self.command_switch = '/r'  # silent (site file params)

        self.filename = filename
        self.progress_bar = progress_bar
        self.encryption_pin = encryption_pin
        self.sdr_path = windows_folder_path(sdr_path)[:-1]
        self.root_folder = "\\".join(self.sdr_path.split('\\')[:-2])
        self.RawData = self.root_folder + '\\RawData\\'
        self.ScaledData = self.root_folder + '\\ScaledData\\'
        self.file_filter = file_filter

        if 'site_filter' in kwargs and file_filter == '':
            self.file_filter = kwargs.get('site_filter')

        self.rwd_dir = rwd_dir  # windows_folder_path(rwd_dir) # rwd_dir must be in Windows format, even if using Wine
        self.show_result = show_result
        self.platform = check_platform()
        self.wine_folder = wine_folder
        self.check_sdr()
        logger.info("conversion initialized")

        if self.platform == 'win32':
            self.out_dir = windows_folder_path(out_dir)
            self.file_path_joiner = '\\'
        else:
            self.file_path_joiner = '/'
            self.out_dir = out_dir

        if self.filename:
            self.counter = 1
            self.rwd_dir = os.path.dirname(self.filename)
            self.file_filter = os.path.basename(self.filename)
            self.convert()


    def check_sdr(self):
        """determine if SDR is installed"""

        if self.platform == 'win32':
            # do the windows check
            try:
                os.path.exists(self.sdr_path)
                self.sdr_ok = True

            except:
                self.sdr_ok = False
                print('SDR not installed. Please install SDR or check path.\nhttps://www.nrgsystems.com/support/product-support/software/symphonie-data-retriever-software')
                logger.error("SDR not installed, aborting")

        else:
            # do the linux check
            try:
                subprocess.check_output(['wine','--version'])
            except NotADirectoryError:
                print('System not configured for running SDR.\n Please follow instructions in SDR_Linux_README.md to enable.')
                logger.error('System not configured for running SDR.\n Please follow instructions in SDR_Linux_README.md to enable.')

            try:
                subprocess.check_output(['wine',self.sdr_path,'/s','test.rwd'])
                affirm_directory(os.path.join(self.wine_folder, "NRG/ScaledData"))

                self.sdr_ok = True

                os.remove(os.path.join(self.wine_folder, "NRG/ScaledData/test.log"))

            except:
                self.sdr_ok = False
                print('SDR unable to start')
                print(traceback.format_exc())

    def convert(self):
        """process rwd files

        create list of RWD files that match filtering
        copy RWD files to RawData directory
        iterate through files
        """
        affirm_directory(self.out_dir)

        self._list_files()
        self._copy_rwd_files()

        self.raw_count = len(self.rwd_file_list)
        self.pad = len(str(self.raw_count)) + 1
        self.counter = 1
        self.convert_time = time.time()
        self.start_time = datetime.datetime.now()

        for f in sorted(self.rwd_file_list):
            site_num = f[:4]
            try:
                self._filename = "\\".join([self.RawData+site_num, f])
                self._single_file()
            except:
                print('file conversion failed on {}'.format(self._filename))
            self.counter += 1

        if self.raw_count > 1:
            txt_count = count_files(self.out_dir, self.file_filter.split(".")[0], 'txt', start_time=self.convert_time)
            log_count, log_files = count_files(self.out_dir, self.file_filter, 'log', show_files=True, start_time=self.convert_time)

            print('\n\nRWDs in    : {}'.format(self.raw_count))
            print('TXTs out   : {}'.format(txt_count))
            print('LOGs out   : {}'.format(log_count))

            if len(log_files) > 0:
                print('Log files created:')
                for _filename in log_files:
                    print('\t{}'.format(_filename))
            print('----------------\nDifference : {}'.format(self.raw_count - (txt_count + log_count)))

    def _list_files(self):
        """get list of files in rwd_dir"""

        self.dir_paths = []
        self.rwd_file_list = []

        if self.platform == 'win32':
            walk_path = self.rwd_dir
        else:
            walk_path = linux_folder_path(self.rwd_dir)

        for dirpath, subdirs, files in os.walk(walk_path):
            self.dir_paths.append(dirpath)
            for x in files:
                if x.startswith(self.file_filter) and x.lower().endswith('rwd'):
                    self.rwd_file_list.append(x)

    def _single_file(self):
        """process for converting a single file"""

        _f = self._filename

        if self.platform == 'linux':

            self.sdr_path = windows_folder_path(self.sdr_path)[:-1]
            _f = windows_folder_path(_f)[:-1]
            wine = 'wine'

        else:
            wine = ''

        self.cmd = [wine, '"'+self.sdr_path+'"', self.command_switch, self.encryption_pin, '"'+_f+'"']

        try:
            if self.show_result:
                if self.progress_bar:
                    draw_progress_bar(self.counter, self.raw_count, self.start_time)

                else:
                    print("Converting  {0}/{1}  {2}  ...  ".format(str(self.counter).rjust(self.pad), str(self.raw_count).ljust(self.pad), _f.split("\\")[-1]), end="", flush=True)

            subprocess.check_output(" ".join(self.cmd), shell=True)
            # subprocess.run(" ".join(self.cmd), stdout=subprocess.PIPE)

            if not self.progress_bar and not self.show_result:
                print("[DONE]")

            try:
                self._copy_txt_file()
            except:
                print('unable to copy {} to text folder'.format(_f))

        except:
            if not self.progress_bar and not self.show_result:
                print("[FAILED]")
            import traceback
            print(traceback.format_exc())

    def _copy_rwd_files(self):
        """copy RWD files from self.RawData to self.rwd_dir"""

        for f in sorted(self.rwd_file_list):

            if self.file_filter in f:
                site_num = f[:4]
                site_folder = os.path.join(self.RawData, site_num)

                if self.platform == 'linux':
                    site_folder = ''.join([self.wine_folder, '/NRG/RawData/', site_num])

                try:
                    affirm_directory(site_folder)
                except:
                    print("couldn't create {}".format(site_folder))
                    pass

                try:
                    # shutil.copy(os.path.join(self.rwd_dir, f), os.path.join(site_folder))
                    shutil.copy(self.rwd_dir + f, os.path.join(site_folder))
                except:
                    import traceback
                    print('unable to copy file to RawData folder:  {}'.format(f))

                    print(traceback.format_exc())
                    print(os.path.join(self.rwd_dir, f))
                    print(os.path.join(site_folder))

    def _copy_txt_file(self):
        """copy TXT file from self.ScaledData to self.out_dir"""

        try:
            txt_file_name = os.path.basename(self._filename)[:-4] + '.txt'
            txt_file_path = os.path.join(self.ScaledData, txt_file_name)
            out_path = self.file_path_joiner.join([self.out_dir, txt_file_name])

        except:
            print("could not do the needful")
            import traceback
            print(traceback.format_exc())

        if self.platform == 'linux':
            out_path = linux_folder_path(self.out_dir) + txt_file_name.split("\\")[-1]
            txt_file_path = ''.join([self.wine_folder, '/NRG/ScaledData/', txt_file_name.split("\\")[-1]])
            self.txt_file_path = txt_file_path

        try:
            shutil.copy(txt_file_path, out_path)

            try:
                os.remove(txt_file_path)
            except:
                print("{0} remains in {1}".format(txt_file_name, self.ScaledData))

        except:
            import traceback
            print(traceback.format_exc())
            print("Unable to copy {0} to {1}".format(txt_file_name,self.out_dir))

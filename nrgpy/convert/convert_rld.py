try:
    from nrgpy import logger
except ImportError:
    pass
from datetime import datetime
import os
import subprocess
import time
import traceback
from nrgpy.api.convert import nrg_api_convert
from nrgpy.utils.utilities import (
    check_platform,
    windows_folder_path,
    affirm_directory,
    count_files,
    is_sympro_running,
)


class local(object):
    """For handling NRG SymphoniePRO Data Logger raw data files in the *.rld format.

    This method uses locally installed SymphoniePRO Desktop software to convert *.rld files to txt format (tab-delimited-text).

    Parameters
    ----------
    rld_dir : str, optional (path-like)
        specify directory. Note for unc values, you
        will need to escape all forward slashes, e.g.
        rld_dir = "\\\\sol\\techsupport\\data\\"
        or use the r'\\path\to\dir' approach
    out_dir : str, optional (path-like)
        see note for rld_dir.
    encryption_pass : str
        specify data encryption password if logger is set up for that.
    hex_key : str
        specify if using hex data encryption key
    sympro_path : str
        default is "C:\Program Files (x86)\Renewable NRG Systems\SymPRO Desktop\SymPRODesktop.exe"
    process_type : str
        [convert], or import
    convert_type : str
        'meas', alternately specify 'comm', 'diag', 'sample', or 'events'
    nec : str
        path to nec file
    site_filter : str
        specify part or all of the file you'd like to filter on, like site_filter='123456_2018-09'
        would filter on site 123456 and only the month of September in 2018.
    site_file : bool or str
        set to True to use local ndb site file, or set to path to an alternate ndb site file

    Examples
    --------
    Convert a folder of RLD files to Text with SymphoniePRO Desktop Software

    >>> from nrgpy.convert_rld import local
    >>> converter = local(
            rld_dir='/path/to/rld/files',
            out_dir=/path/to/txt/outputs,
            file_filter='123456_2020-01', # for files from January 2020
        )
    >>> converter.convert()
    """

    def __init__(
        self,
        rld_dir="",
        out_dir="",
        encryption_pass="",
        hex_key="",
        filename="",
        sympro_path=r'"C:/Program Files (x86)/Renewable NRG Systems/SymPRO Desktop/SymPRODesktop.exe"',
        process_type="convert",
        convert_type="meas",
        nec="",
        site_filter="",
        site_file="",
        **kwargs,
    ):

        self.rld_dir = windows_folder_path(rld_dir)
        self.out_dir = windows_folder_path(out_dir)
        self.encryption_pass = encryption_pass
        self.hex_key = hex_key
        self.sympro_path = sympro_path
        self.process_type = process_type
        self.convert_type = convert_type
        self.nec = nec
        self.site_filter = site_filter
        self.site_file = site_file

        if "file_filter" in kwargs and site_filter == "":
            self.file_filter = kwargs.get("file_filter")
            self.site_filter = self.file_filter

        if check_platform() == "win32":
            if is_sympro_running():
                print(
                    "SymphoniePRO Desktop is already running. Please close it and try again."
                )
                logger.error(
                    "SymphoniePRO Desktop is already running so it could not be run"
                )

            elif filename:
                affirm_directory(self.out_dir)
                self.single_file(filepath=filename)
        else:
            print(
                """
convert_rld.local() method ONLY compatible with Windows OS.
Please use nrgpy.cloud_convert() method instead.

Alternately, follow the instructions for using SymphoniePRO Desktop
with wine here:

https://github.com/nrgpy/nrgpy/blob/master/SymPRODeskop_Linux_README.md            
            """
            )

    def directory(self):
        """processes all rld files in self.rld_dir, outputs to txt files to out_dir"""
        affirm_directory(self.out_dir)

        try:
            if self.encryption_pass:
                encryption = '/pass "{0}"'.format(self.encryption_pass)
            else:
                encryption = ""

        except:
            print("could not parse encryption_pass")

        try:
            if self.hex_key:
                encryption_key = '/key "{0}"'.format(self.hex_key)
            else:
                encryption_key = ""

        except:
            print("could not parse hex_key")

        try:
            if self.nec:
                nec = '/config "{0}"'.format(self.nec)
            else:
                nec = ""

        except:
            print("could not parse encryption_pass")

        try:
            if self.site_file:
                site_file = "/site "
            elif self.site_file:
                site_file = '/site "{0}"'.format(self.site_file)
            else:
                site_file = ""

        except:
            print("could not parse encryption_pass")

        try:
            rld_count = count_files(self.rld_dir, self.site_filter, "rld")
            self.start_time = time.time()
            logger.info("converting {0} files from {1}".format(rld_count, self.rld_dir))
            print("\nConverting {0} files from {1}\n".format(rld_count, self.rld_dir))
            print("Saving outputs to {0}".format(self.out_dir))

            cmd = [
                self.sympro_path,
                "/cmd",
                self.process_type,
                "/file",
                '"' + "\\".join([self.rld_dir, "*" + self.site_filter]) + '*.rld"',
                encryption,
                encryption_key,
                nec,
                site_file,
                "/type",
                '"' + self.convert_type + '"',
                "/outputdir",
                '"' + self.out_dir[:-1] + '"',
            ]

            # print('\nUsing command line script:\n{}'.format(" ".join(cmd)))
            self.cmd = cmd

            self.start = datetime.now()

            subprocess.run(" ".join(cmd), stdout=subprocess.PIPE)
            self.end = datetime.now()
            self.convert_time = str(self.end - self.start)

            logger.info("TXT files saved in {0}".format(self.out_dir))
            print("\nTXT files saved in {0}\n".format(self.out_dir))

            txt_count = count_files(
                self.out_dir, self.site_filter, "txt", start_time=self.start_time
            )
            log_count, log_files = count_files(
                self.out_dir,
                self.site_filter,
                "log",
                show_files=True,
                start_time=self.start_time,
            )

            logger.info(f"IN: {rld_count}, OUT: {txt_count}, FAILED: {log_count}")
            print("RLDs in    : {}".format(rld_count))
            print("TXTs out   : {}".format(txt_count))
            print("LOGs out   : {}".format(log_count))

            if len(log_files) > 0:
                print("Log files created:")
                for _filename in log_files:
                    print("\t{}".format(_filename))
            print(
                "----------------\nDifference : {}".format(
                    rld_count - (txt_count + log_count)
                )
            )

        except FileNotFoundError:
            logger.error(
                "SymphoniePRO Desktop Application not found: {0}".format(
                    self.sympro_path
                )
            )
            print(
                """
                  No instance of SymphoniePRO Desktop Application found.

                  Please follow the link below to download and install this software:
                  https://www.nrgsystems.com/support/product-support/software/symphoniepro-desktop-application

                  """
            )
        except:
            logger.error("unable to process files in {0}".format(self.rld_dir))
            logger.debug(traceback.format_exc())
            print("Unable to process files in directory")

    def convert(self):
        self.directory()

    def process(self):
        self.directory()

    def rename_rlds(self, **kwargs):
        """uses SymPRO utility NrgRldSiteSerialRename.exe to rename files with site number and logger serial number.

        This function is only compatible with Windows>=7 AND
        a local installation of SymphoniePRO Desktop software
        """

        try:
            renamer_path = kwargs.get(
                "renamer_path",
                r"C:/Program Files (x86)/Renewable NRG Systems/SymPRO Desktop/Default Application Files/Utilities/NrgRldSiteSerialRename.exe",
            )

            for f in os.listdir(self.rld_dir):

                filepath = self.rld_dir + f

                if f[-4:].lower() == ".rld" and self.site_filter in f:
                    rename_cmd = [renamer_path, '"' + filepath + '"']

                    try:
                        subprocess.run(" ".join(rename_cmd), stdout=subprocess.PIPE)
                    except:
                        logger.error("unable to rename {0}".format(f))
                        print("Unable to rename {0}".format(f))
                        pass

                else:
                    pass
        except:
            logger.error("Could not rename files")
            logger.debug(traceback.format_exc())
            print("Could not rename files")

    def single_file(self, filepath=""):
        self.filepath = filepath.replace("/", "\\")

        try:
            if self.encryption_pass:
                encryption = '/pass "{0}"'.format(self.encryption_pass)
            else:
                encryption = ""
        except:
            print("could not parse encryption_pass")

        try:
            if self.hex_key:
                encryption_key = '/key "{0}"'.format(self.hex_key)
            else:
                encryption_key = ""
        except:
            print("could not parse hex_key")

        try:
            if self.nec:
                nec = '/config "{0}"'.format(self.nec)
            else:
                nec = ""
        except:
            print("could not get nec file")

        try:
            if self.site_file:
                site_file = '/site "{0}"'.format(self.site_file)
            else:
                site_file = ""
        except:
            print("could not get site file")

        cmd = [
            self.sympro_path,
            "/cmd",
            "convert",
            "/file",
            '"' + self.filepath + '"',
            encryption,
            encryption_key,
            nec,
            site_file,
            "/type",
            '"' + self.convert_type + '"',
            "/outputdir",
            '"' + self.out_dir[:-1] + '"',
        ]
        self.cmd = cmd

        try:
            print("{0} ... \t".format(filepath), end="", flush=True)
            p = subprocess.run(
                " ".join(cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )

            if (
                "File does not" in p.stdout.decode()
                or "Decryption failed" in p.stdout.decode()
            ):
                print("[FAILED]")
                print(f"{p.stdout.decode()}")
                logger.error(f"{p.stdout.decode()}")

            else:
                logger.info(f"{p.stdout.decode()}")
                print("[DONE]")

        except:
            logger.error("processing {0} FAILED".format(filepath))
            logger.debug(traceback.format_exc())
            print("\n\t processing {0} [FAILED]".format(filepath))
            pass

        logger.info("files in {0} processed OK".format(self.rld_dir))
        logger.info("TXT files saved to {0}".format(self.out_dir))


nrg_convert_api = nrg_api_convert

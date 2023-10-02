import os
import pandas as pd


class convert_utf16le_to_utf8(object):
    """for making Spidar data files compatible with programs that do not support 
    utf-16-le character encoding

    Parameters
    ----------
    filename : str
        (optional) path of file to convert
    input_directory : str
        (optional) path of directory with files to convert
    output_directory : str
        (optional) path of directory store converted files in
    inplace : bool
        (False) if true, overwrites filename provided

    Returns
    -------
    None

    Examples
    --------

    convert single file

    >>> import nrgpy
    >>> filename = "/path/to/files/file.zip"
    >>> nrgpy.convert_utf16le_to_utf8(filename)

    convert directory of files

    >>> input_directory = "/path/to/files/"
    >>> nrgpy.convert_utf16le_to_utf8(input_directory=input_directory)
    """

    def __init__(
        self, filename="", input_directory="", output_directory="", inplace=False
    ):

        self.filename = filename
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.inplace = inplace

        if filename:
            self.single_file()

        elif input_directory:
            self.files = sorted(
                [
                    f
                    for f in os.listdir(self.input_directory)
                    if "avgwnd" in f.lower() or "rawwnd" in f.lower()
                ]
            )

            for f in self.files:
                self.filename = os.path.join(self.input_directory, f)
                self.single_file()

    def single_file(self):

        if self.inplace:
            out_file = self.filename.replace(".zip", ".csv")
        else:
            out_file = (
                self.filename.split(".")[0] + "_utf8." + self.filename.split(".")[-1]
            ).replace(".zip", ".csv")

        if self.output_directory:
            out_file = os.path.join(self.output_directory, os.path.basename(out_file))

        try:
            infile = pd.read_csv(
                self.filename, encoding="UTF_16_LE", parse_dates=True, index_col=[0]
            )
            infile.to_csv(out_file, encoding="UTF_8")
        except UnicodeDecodeError:
            pass

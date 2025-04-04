from collections import Counter
from datetime import datetime
import math
import pandas as pd
from typing import Union


def check_intervals(
    df: pd.DataFrame,
    verbose: bool=True,
    return_info: bool=False,
    show_all_missing_timestamps: bool=False,
    show_all_duplicate_timestamps: bool=False,
    interval: Union[int, str]="",
) -> Union[dict, None]:
    """checks for missing or duplicate intervals in a pandas dataframe with a "Timestamp" column

    Parameters
    ----------
    df : object
        the dataframe to be checked
    interval : int
         [deprecated] the averaging interval in seconds
    verbose : bool
        print results to terminal; False to skip
    return_info : bool
        set to True to return dict with below values
    show_all_missing_timestamps : bool
        set to True to show all missing timestamps in verbose option. otherwise, shows first and last 3.
    show_all_duplicate_timestamps : bool
        set to True to show all duplicate timestamps in verbose option. otherwise, shows first and last 3.

    Returns
    ----------
    dict
        actual_rows : int
            actual number of rows in data section of
            export file (1 subtracted for column headers)
        expected_rows : int
            expected number of rows (assumes 10 min. AVG),
            converts result to whole integer
        time_range : str
            range of time represented in export file
        first_interval : str
            file starting timestamp
        last_interval : str
            file ending timestamp
        missing_timestamps : list
            a list of missing timestamps
        duplicate_timestamps : list
            a list of duplicate timestamps

    Examples
    ----------
    ex. pass a reader.data dataframe for an interval check:

    >>>  reader = nrgpy.sympro_txt_read()
    instance created, no filename specified
    >>> reader.concat_txt(txt_dir="C:/data/sympro_data/000110/")
    ...
    >>> nrgpy.check_intervals(reader.data, interval=600)
    Starting timestamp        : 2019-01-01 00:00:00
    Ending timestamp          : 2019-07-01 04:50:00
    Data set Duration         : 181 days, 4:50:00
    Expected rows in data set : 26093
    Actual rows in data set   : 26093
    Data set complete.
    """
    if "horz" in "".join(df.columns).lower() or isinstance(
        df["Timestamp"][0], datetime
    ):
        df2 = df.copy()
        #  df2.Timestamp = df2.Timestamp.apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))  # noqa: E501
        df2.reset_index(level=0, inplace=True)
        _df = df2
        first_interval = _df["Timestamp"].min()
        last_interval = _df["Timestamp"].max()
    else:
        _df = df.copy()
        time_fmt = "%Y-%m-%d %H:%M:%S"
        first_interval = datetime.strptime(_df["Timestamp"].min(), time_fmt)
        last_interval = datetime.strptime(_df["Timestamp"].max(), time_fmt)

    duplicate_timestamps, _df = find_duplicate_intervals(_df)
    # delete duplicate intervals before doing the rest of the interval checks
    _df = _df.drop_duplicates(subset=["Timestamp"], keep="first")
    _df.reset_index(drop=True, inplace=True)

    interval = int(select_interval_length(_df))
    time_range = last_interval - first_interval
    expected_rows = int(time_range.total_seconds() / interval)
    actual_rows = len(_df) - 1
    loss_pct = 100 * ((expected_rows - actual_rows) / expected_rows)

    if abs(loss_pct) > 1:
        loss_pct = round(loss_pct)
    else:
        loss_pct = round(loss_pct, 3)

    if expected_rows != actual_rows:
        missing_timestamps, _df = find_missing_intervals(_df, interval)

    if verbose:
        print("Statistical interval      : {0} seconds".format(interval))
        print("Starting timestamp        : {0}".format(first_interval))
        print("Ending timestamp          : {0}".format(last_interval))
        print("Data set Duration         : {0}".format(time_range))
        print("Expected rows in data set : {0}".format(expected_rows))
        print("Actual rows in data set   : {0}".format(actual_rows))

        if expected_rows == actual_rows:
            print("\nData set complete.")

        else:
            print("Interval loss percentage  : {0}".format(loss_pct))
            print("\nMissing {0} timestamps:".format(len(missing_timestamps)))

            if len(missing_timestamps) <= 8 or show_all_missing_timestamps:
                for i, timestamp in enumerate(missing_timestamps):
                    print("\t{0}\t{1}".format(i + 1, timestamp))

            else:
                for timestamp in (
                    missing_timestamps[0:3] + ["..."] + missing_timestamps[-3:]
                ):
                    print("\t{0}\t{1}".format(" ", timestamp))

            print("Duplicate {0} timestamps:".format(len(duplicate_timestamps)))

            if len(duplicate_timestamps) <= 8 or show_all_duplicate_timestamps:
                for i, timestamp in enumerate(duplicate_timestamps):
                    print("\t{0}\t{1}".format(i + 1, timestamp))
            else:
                for timestamp in (
                    duplicate_timestamps[0:3] + ["..."] + duplicate_timestamps[-3:]
                ):
                    print("\t{0}\t{1}".format(" ", timestamp))

    if return_info:
        interval_info = {}
        interval_info["actual_rows"] = actual_rows
        interval_info["expected_rows"] = expected_rows
        interval_info["interval_length"] = interval
        interval_info["first_interval"] = first_interval
        interval_info["last_interval"] = last_interval
        interval_info["time_range"] = time_range
        interval_info["loss_pct"] = loss_pct

        try:
            interval_info["missing_timestamps"] = missing_timestamps
        except Exception:
            interval_info["missing_timestamps"] = []

        interval_info["duplicate_timestamps"] = duplicate_timestamps

        return interval_info
    
    return None


def find_missing_intervals(__df: pd.DataFrame, interval: Union[int, str]) -> tuple:
    """find gaps in data dataframe

    returns
    ----------
    list
        a list of all missing intervals
    """
    _df = __df.copy()
    _df["data"] = True
    _df["Timestamp"] = pd.to_datetime(_df["Timestamp"])
    _df.set_index("Timestamp", inplace=True)
    _df = _df.reindex(
        pd.date_range(
            start=_df.index[0], end=_df.index[-1], freq="{0}s".format(interval)
        )
    )

    missing_timestamps = []

    for index, row in _df.iterrows():
        try:
            if math.isnan(row["data"]):
                missing_timestamps.append(index)
        except TypeError:
            missing_timestamps.append(index)

    return missing_timestamps, _df


def find_duplicate_intervals(__df: pd.DataFrame) -> tuple:
    """find duplicate interval timestamps

    returns
    -------
    list
        a list of all duplicate intervals
    """
    _df = __df.copy()
    time_fmt = "%Y-%m-%d %H:%M:%S"
    observed_intervals = pd.to_datetime(_df["Timestamp"].values, format=time_fmt)
    unique_timestamps_set = set(observed_intervals)

    if len(observed_intervals) == len(unique_timestamps_set):
        duplicate_timestamps = []
    else:
        # Record duplicates using Counter
        timestamp_counter = Counter(observed_intervals)
        duplicate_timestamps = [
            timestamp for timestamp, count in timestamp_counter.items() if count > 1
        ]

    return duplicate_timestamps, _df


def select_interval_length(df: pd.DataFrame, seconds: bool = True) -> Union[int, float]:
    """returns the mode of the first 10 intervals of the data set

    parameters
    ----------
        reader : nrgpy reader object
        seconds : bool
            (True) set to False to get interval length in minutes

    returns
    -------
        int

    """
    from datetime import datetime

    formatter = "%Y-%m-%d %H:%M:%S"
    interval = []

    if len(df["Timestamp"]) < 3:
        raise ValueError("Insufficient number of timestamps for select_interval_length") 

    range_size = min(5, len(df["Timestamp"])-1)
    

    for i in range(range_size):
        try:
            interval.append(
                int(
                    (
                        datetime.strptime(df["Timestamp"].loc[i + 1], formatter)
                        - datetime.strptime(df["Timestamp"].loc[i], formatter)
                    ).seconds
                )
            )

        except Exception:
            formatter = "%Y-%m-%d %H:%M:%S.%f"
            interval.append(int((df["Timestamp"].iloc[i + 1] - df["Timestamp"].iloc[i]).seconds))

    try:
        if seconds:
            return select_mode_from_list(interval)
        return select_mode_from_list(interval) / 60
    except Exception:
        return False


def select_mode_from_list(lst: list) -> int:
    return max(set(lst), key=lst.count)


def check_for_missing_txt_files(txt_file_names):
    """check list of files for missing file numbers

    parameters
    ----------
    txt_file_names : list
        list of SymphoniePRO text file exports

    returns
    -------
    list
        "missing" text file numbers

    """

    missing_file_numbers = []

    for i, f in enumerate(sorted(txt_file_names)):
        file_number = int(f.split("_")[-2])

        if i > 0:
            if file_number - _file_number > 1:  # noqa: F821
                missing_file_numbers.append(f)

        _file_number = file_number

    return missing_file_numbers

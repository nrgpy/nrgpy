def check_intervals(df, verbose=True, return_info=False, show_all_missing_timestamps=False, interval=''):
    """checks for missing intervals in a pandas dataframe with a "Timestamp" column

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

    Returns
    ----------
    dict
        actual_rows
            (int)
            actual number of rows in data section of
            export file (1 subtracted for column headers)
        expected_rows
            (int)
            expected number of rows (assumes 10 min. AVG),
            converts result to whole integer
        time_range
            (str)
            range of time represented in export file
        first_interval
            (str)
            file starting timestamp
        last_interval
            (str)
            file ending timestamp
        missing_timestamps
            (list)
            a list of missing timestamps

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
    from datetime import datetime


    if "horz" in "".join(df.columns).lower() or isinstance(df['Timestamp'][0], datetime):
        df2 = df.copy()
        #  df2.Timestamp = df2.Timestamp.apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S"))
        df2.reset_index(level=0, inplace=True)
        _df = df2
        first_interval = _df['Timestamp'].min()
        last_interval = _df['Timestamp'].max()
    else:
        _df = df.copy()
        time_fmt = "%Y-%m-%d %H:%M:%S"
        first_interval = datetime.strptime(_df['Timestamp'].min(), time_fmt)
        last_interval = datetime.strptime(_df['Timestamp'].max(), time_fmt)


    interval = select_interval_length(_df)


    time_range = last_interval - first_interval

    expected_rows = int(time_range.total_seconds() / interval)
    actual_rows = len(df) - 1

    if expected_rows != actual_rows:
        missing_timestamps, _df = find_missing_intervals(_df, interval)


    if verbose == True:
        print('Statistical interval      : {0} seconds'.format(interval))
        print('Starting timestamp        : {0}'.format(first_interval))
        print('Ending timestamp          : {0}'.format(last_interval))
        print('Data set Duration         : {0}'.format(time_range))
        print('Expected rows in data set : {0}'.format(expected_rows))
        print('Actual rows in data set   : {0}'.format(actual_rows))
        print()

        if expected_rows == actual_rows:
            print('Data set complete.')

        else:
            print('Missing {0} timestamps:'.format(len(missing_timestamps)))

            if len(missing_timestamps) <= 8 or show_all_missing_timestamps == True:
                for i, timestamp in enumerate(missing_timestamps):
                    print("\t{0}\t{1}".format(i+1,timestamp))

            else:
                for timestamp in missing_timestamps[0:3] + ["..."] + missing_timestamps[-3:]:
                    print("\t{0}\t{1}".format(" ",timestamp))


    if return_info == True:

        interval_info = {}
        interval_info['actual_rows'] = actual_rows
        interval_info['expected_rows'] = expected_rows
        interval_info['first_interval'] = first_interval
        interval_info['last_interval'] = last_interval
        interval_info['time_range'] = time_range

        try:
            interval_info['missing_timestamps'] = missing_timestamps
        except:
            interval_info['missing_timestamps'] = None

        return interval_info


def find_missing_intervals(__df, interval):
    """find gaps in data dataframe
    Returns
    ----------
    list
        a list of all missing intervals
    """
    _df = __df.copy()
    import pandas as pd

    _df['data'] = True
    _df['Timestamp'] = pd.to_datetime(_df['Timestamp'])
    _df.set_index('Timestamp', inplace=True)
    _df = _df.reindex(pd.date_range(start=_df.index[0], end=_df.index[-1], freq='{0}s'.format(interval)))

    missing_timestamps = []

    for index, row in _df.iterrows():

        if row['data'] != True:
            missing_timestamps.append(index)

    return missing_timestamps, _df


def select_interval_length(df, seconds=True):
    """ get interval length of data set

    returns the mode of the first 10 intervals of the data set

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

    for i in range(10):
        try:
            interval.append(
                int(
                    (datetime.strptime(df['Timestamp'].loc[i+1], formatter) - datetime.strptime(df['Timestamp'].loc[i], formatter)
                    ).seconds)
                )

        except:
            formatter = "%Y-%m-%d %H:%M:%S.%f"
            interval.append(
                int(
                    (df['Timestamp'][i+1] - df['Timestamp'][i]).seconds)
                )

        # except:
        #    pass

    interval_s = select_mode_from_list(interval)
    interval_m = interval_s/60

    try:
        if seconds:
            return select_mode_from_list(interval)
        return select_mode_from_list(interval)/60
    except:
        return False


def select_mode_from_list(lst):
    """ """
    return max(set(lst), key=lst.count)


def check_for_missing_txt_files(txt_file_names):
    """ check list of files for missing file numbers

    Parameters
    ----------
    txt_file_names : list
        list of SymphoniePRO text file exports

    Returns
    -------
    list
        list of "missing" text file numbers

    """

    missing_file_numbers = []

    for i, f in enumerate(sorted(txt_file_names)):

        file_number = int(f.split("_")[-2])

        if i > 0:
            if file_number - _file_number > 1:
                missing_file_numbers.append(f)

        _file_number = file_number

    return missing_file_numbers

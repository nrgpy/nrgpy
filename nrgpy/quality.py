def check_intervals(df, interval=600, verbose=True, return_info=False):
    """checks for missing intervals in a pandas dataframe with a "Timestamp" column
    
    Parameters
    ----------
    df : object
        the dataframe to be checked
    interval : int
         default, 600; the averaging interval in seconds
    verbose : bool
        print results to terminal; False to skip
    return_info : bool
        set to True to return dict with below values

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

    >>>  from nrgpy.sympro_txt import sympro_txt_read
    >>>  reader = sympro_txt_read()
    instance created, no filename specified
    >>> reader.concat_txt(txt_dir="C:/data/sympro_data/000110/")
    ...
    >>> from nrgpy.quality import check_intervals
    >>> check_intervals(reader.data, interval=600)
    Starting timestamp        : 2019-01-01 00:00:00
    Ending timestamp          : 2019-07-01 04:50:00
    Data set Duration         : 181 days, 4:50:00
    Expected rows in data set : 26093
    Actual rows in data set   : 26093
    Data set complete.
    """
    if "horz" in "".join(df.columns):
        df2 = df.reset_index()
        df2[df2.columns[0]] = df2[df2.columns[0]].astype(str)
        _df = df2.copy()
    else:
        _df = df.copy()
    from datetime import datetime
    time_fmt = "%Y-%m-%d %H:%M:%S"
    first_interval = datetime.strptime(_df['Timestamp'].min(), time_fmt) 
    last_interval = datetime.strptime(_df['Timestamp'].max(), time_fmt)
    time_range = last_interval - first_interval
    expected_rows = int(time_range.total_seconds() / interval)
    actual_rows = len(df) - 1 
    if expected_rows != actual_rows:
        missing_timestamps, _df = find_missing_intervals(_df, interval)

    
    if verbose == True:
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
            i=1
            for timestamp in missing_timestamps:
                print("\t{0}\t{1}".format(i,timestamp))
                i+=1
    
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
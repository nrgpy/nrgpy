from datetime import datetime
from nrgpy.quality.quality import (
    check_for_missing_txt_files,
    check_intervals,
    find_duplicate_intervals,
    find_missing_intervals,
    select_interval_length,
    select_mode_from_list,
)
import pandas as pd


class TestQuality:
    def test_check_intervals(self, interval_check_df):
        # arrange
        df = interval_check_df
        print(df)
        # act
        result = check_intervals(df, return_info=True, verbose=False)
        # assert
        assert (
            result["interval_length"] == 300
        ), f'expected 300, got {result["interval_length"]}'  # noqa

    def test_find_missing_intervals(self, test_reader):
        # arrange
        df = test_reader.data
        df = df.drop(3)
        # act
        result, _df = find_missing_intervals(df, 60)
        # assert
        assert (
            datetime.strftime(result[0], "%Y-%m-%d %H:%M:%S") == "2022-03-17 00:03:00"
        )  # noqa

    def test_find_duplicate_timestamps(self, test_reader):
        # arrange
        df = test_reader.data
        df = pd.concat([df.iloc[:3], df.iloc[3:5], df.iloc[3:]]).reset_index(drop=True)
        # act
        result, _df = find_duplicate_intervals(df)
        # assert
        assert len(result) == 2, f"expected 2, got {len(result)}"

    def test_find_duplicate_timestamps_no_duplicates(self, test_reader):
        # arrange
        df = test_reader.data
        # act
        result, _df = find_duplicate_intervals(df)
        # assert
        assert len(result) == 0, f"expected 0, got {len(result)}"

    def test_select_mode_from_list(self):
        # arrange
        interval = [300, 300, 300, 300, 300, 300, 300, 300, 300, 300]
        # act
        result = select_mode_from_list(interval)
        # assert
        assert result == 300, f"expected 300, got {result}"

    def test_check_for_missing_files_none(self, test_file_directory):
        # arrange
        txt_file_names = [
            f.name for f in test_file_directory.iterdir() if f.name.startswith("004310")
        ]
        # act
        result = check_for_missing_txt_files(txt_file_names)
        # assert
        assert result == [], f"expected [], got {result}"

    def test_check_for_missing_files(self, test_file_directory):
        # arrange
        txt_file_names = [
            f.name for f in test_file_directory.iterdir() if f.name.startswith("004310")
        ]
        txt_file_names.append("004310_2022-03-17_00.00_000839_meas.txt")
        # act
        result = check_for_missing_txt_files(txt_file_names)
        # assert
        assert len(result) == 1, f"expected 1, got {len(result)}"

    def test_select_interval_length(self, interval_check_df):
        # arrange
        df = interval_check_df
        # act
        result = select_interval_length(df)
        # assert
        assert result == 300, f"expected 300, got {result}"

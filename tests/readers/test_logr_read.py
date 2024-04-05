import os
from nrgpy import LogrRead


class TestLogrRead:
    def test_logr_concat_9431_returns(self, test_file_directory):
        """Check that LOGR-S (model 9431) dat files are ingested by nrgpy.logr_read"""
        reader = LogrRead()
        reader.concat_txt(dat_dir=str(test_file_directory), file_filter="000511")

        assert (
            reader.site_description == "Crows Nest"
        ), f"Expected site number {reader.site_description} to be 'Crows Nest'"
        assert (
            len(reader.data) == 180
        ), f"Dataframe length {len(reader.data)} is not 180"

    def test_logr_concat_9432_returns(self, test_file_directory):
        """Check that LOGR|SOLAR (model 9432) dat files are ingested by nrgpy.logr_read"""
        reader = LogrRead()
        reader.concat_txt(dat_dir=str(test_file_directory), file_filter="000304")

        assert (
            reader.site_description == "Crows Nest Counters"
        ), f"Expected site number {reader.site_description} to be 'Crows Nest'"
        assert len(reader.data) == 41, f"Dataframe length {len(reader.data)} is not 180"
        assert len(reader.ch_info) > 1, "Expected channel info to be populated"

    def test_logr_read_9432_log_returns(self, test_file_directory):
        """Check that LOGR|SOLAR (model 9432) log files are ingested by nrgpy.logr_read"""
        filename = test_file_directory / "20240111_1339_000304_002995.log"
        reader = LogrRead(filename, drop_duplicates=False)

        assert (
            reader.site_description == "Crows Nest Counters"
        ), f"Expected site description {reader.site_description} to be 'Crows Nest Counters'"
        assert len(reader.data) == 1, f"Dataframe length {len(reader.data)} is not 1"

    def test_logr_concat_9432_log_returns(self, test_file_directory):
        """Check that LOGR|SOLAR (model 9432) log files are ingested by nrgpy.logr_read"""
        reader = LogrRead()
        reader.concat_txt(
            dat_dir=str(test_file_directory),
            file_type="log",
            file_filter="000304",
            drop_duplicates=False,
        )

        assert (
            reader.site_description == "Crows Nest Counters"
        ), f"Expected site description {reader.site_description} to be 'Crows Nest Counters'"
        assert len(reader.data) == 3, f"Dataframe length {len(reader.data)} is not 3"

    def test_logr_read_9432_diag_returns(self, test_file_directory):
        """Check that LOGR|SOLAR (model 9432) log files are ingested by nrgpy.logr_read"""
        filename = test_file_directory / "20240111_1339_000304_002995.diag"
        reader = LogrRead(filename, drop_duplicates=False)

        assert (
            reader.site_description == "Crows Nest Counters"
        ), f"Expected site description {reader.site_description} to be 'Crows Nest Counters'"
        assert len(reader.data) == 2, f"Dataframe length {len(reader.data)} is not 2"

    def test_logr_concat_9432_diag_returns(self, test_file_directory):
        """Check that LOGR|SOLAR (model 9432) log files are ingested by nrgpy.logr_read"""
        reader = LogrRead()
        reader.concat_txt(
            dat_dir=str(test_file_directory),
            file_type="diag",
            file_filter="000304",
            drop_duplicates=False,
        )

        assert (
            reader.site_description == "Crows Nest Counters"
        ), f"Expected site description {reader.site_description} to be 'Crows Nest Counters'"
        assert len(reader.data) == 41, f"Dataframe length {len(reader.data)} is not 41"

    def test_logr_output_txt_generates_file(self, test_file_directory):
        """Check that LOGR|SOLAR (model 9432) log files are ingested by nrgpy.logr_read"""
        reader = LogrRead()
        reader.concat_txt(
            dat_dir=str(test_file_directory),
            file_type="diag",
            file_filter="000304",
            drop_duplicates=False,
        )
        reader.output_txt_file(out_file=str(test_file_directory / "test_output.txt"))

        assert (
            test_file_directory / "test_output.txt"
        ).exists(), "Expected test_output.txt to be created"
        os.remove(test_file_directory / "test_output.txt")

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
        """Check that LOGR-SOLAR (model 9432) dat files are ingested by nrgpy.logr_read"""
        reader = LogrRead()
        reader.concat_txt(dat_dir=str(test_file_directory), file_filter="000304")

        assert (
            reader.site_description == "Crows Nest Counters"
        ), f"Expected site number {reader.site_description} to be 'Crows Nest'"
        assert len(reader.data) == 41, f"Dataframe length {len(reader.data)} is not 180"
        assert len(reader.ch_info) > 1, "Expected channel info to be populated"

    def test_logr_read_9432_log_returns(self, test_file_directory):
        """Check that LOGR-SOLAR (model 9432) log files are ingested by nrgpy.logr_read"""
        filename = str(test_file_directory / "20240111_1339_000304_002995.log")
        reader = LogrRead(filename, drop_duplicates=False)

        assert (
            reader.site_description == "Crows Nest Counters"
        ), f"Expected site description {reader.site_description} to be 'Crows Nest Counters'"
        assert len(reader.data) == 1, f"Dataframe length {len(reader.data)} is not 1"

    def test_logr_concat_9432_log_returns(self, test_file_directory):
        """Check that LOGR-SOLAR (model 9432) log files are ingested by nrgpy.logr_read"""
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

    def test_logr_concat_9460_log_returns(self, test_file_directory):
        """Check that LOGR-MET (model 9460) log files are ingested by nrgpy.logr_read"""
        reader = LogrRead()
        reader.concat_txt(
            dat_dir=str(test_file_directory),
            file_type="log",
            file_filter="_9460_",
            drop_duplicates=False,
        )

        assert (
            reader.site_description == "Sys_WRA_60m"
        ), f"Expected site description {reader.site_description} to be 'Sys_WRA_60m'"
        assert len(reader.data) == 21, f"Dataframe length {len(reader.data)} is not 21"

    def test_logr_read_9432_diag_returns(self, test_file_directory):
        """Check that LOGR-SOLAR (model 9432) log files are ingested by nrgpy.logr_read"""
        filename = str(test_file_directory / "20240111_1339_000304_002995.diag")
        reader = LogrRead(filename, drop_duplicates=False)

        assert (
            reader.site_description == "Crows Nest Counters"
        ), f"Expected site description {reader.site_description} to be 'Crows Nest Counters'"
        assert len(reader.data) == 2, f"Dataframe length {len(reader.data)} is not 2"

    def test_logr_concat_9432_diag_returns(self, test_file_directory):
        """Check that LOGR-SOLAR (model 9432) log files are ingested by nrgpy.logr_read"""
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
        """Check that LOGR-SOLAR (model 9432) log files are ingested by nrgpy.logr_read"""
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

    def test_logr_concat_cloud_concat_export_returns(
        self, cloud_export_concat_test_dir
    ):
        reader = LogrRead()
        reader.concat_txt(
            dat_dir=str(cloud_export_concat_test_dir),
            file_type="dat",
            file_filter="945800110",
            drop_duplicates=False,
        )

        assert (
            reader.site_description == "WRA_60m"
        ), f"Expected site description {reader.site_description} to be 'WRA_60m'"
        assert len(reader.data) == 12, f"Dataframe length {len(reader.data)} is not 12"

    def test_logr_output_txt_file_matches_original(self, test_file_directory):
        """Check that output_txt_file produces files that can be read back by LogrRead"""
        original_file = str(
            test_file_directory / "20260114_1700_9458_65432_003541_statistical.dat"
        )
        reader_original = LogrRead(original_file)

        # Store original data for comparison
        original_site_description = reader_original.site_description
        original_project = reader_original.project
        original_location = reader_original.location
        original_data_shape = reader_original.data.shape

        # Output to new text file
        output_file = str(test_file_directory / "test_output_comparison.txt")
        reader_original.output_txt_file(out_file=output_file)

        assert (
            test_file_directory / "test_output_comparison.txt"
        ).exists(), "Expected output file to be created"

        # Test that output file can be read back
        reader_output = LogrRead(output_file)

        assert (
            reader_output.site_description == original_site_description
        ), f"Expected site description {reader_output.site_description} to be '{original_site_description}'"
        assert (
            reader_output.project == original_project
        ), f"Expected project {reader_output.project} to be '{original_project}'"
        assert (
            reader_output.location == original_location
        ), f"Expected location {reader_output.location} to be '{original_location}'"
        assert len(reader_output.data.columns) == len(
            reader_original.data.columns
        ), f"Expected {len(reader_original.data.columns)} columns, got {len(reader_output.data.columns)}"
        assert len(reader_output.data) > 0, "Expected data rows in output file"

        os.remove(output_file)

    def test_logr_output_txt_file_preserves_channel_formatting(
        self, test_file_directory
    ):
        """Check that output_txt_file preserves blank lines between Channel blocks"""
        original_file = str(
            test_file_directory / "20260114_1700_9458_65432_003541_statistical.dat"
        )
        reader = LogrRead(original_file)

        output_file = str(test_file_directory / "test_whitespace_output.txt")
        reader.output_txt_file(out_file=output_file)

        # Read both files for comparison
        with open(original_file, "r", encoding="iso-8859-1") as f:
            original_content = f.read()
        with open(output_file, "r", encoding="utf-8") as f:
            output_content = f.read()

        original_lines = original_content.split("\n")
        output_lines = output_content.split("\n")

        # Find Sensor History sections
        original_sensor_start = None
        original_data_start = None
        for i, line in enumerate(original_lines):
            if line == "Sensor History":
                original_sensor_start = i
            if line == "Data":
                original_data_start = i
                break

        output_sensor_start = None
        output_data_start = None
        for i, line in enumerate(output_lines):
            if line == "Sensor History":
                output_sensor_start = i
            if line == "Data":
                output_data_start = i
                break

        assert (
            original_sensor_start is not None
        ), "Could not find Sensor History in original file"
        assert (
            original_data_start is not None
        ), "Could not find Data section in original file"
        assert (
            output_sensor_start is not None
        ), "Could not find Sensor History in output file"
        assert (
            output_data_start is not None
        ), "Could not find Data section in output file"

        # Extract sensor history sections
        original_sensor_lines = original_lines[
            original_sensor_start:original_data_start
        ]
        output_sensor_lines = output_lines[output_sensor_start:output_data_start]

        # Count channels in each file
        original_channels = [
            i
            for i, line in enumerate(original_sensor_lines)
            if line.startswith("Channel:")
        ]
        output_channels = [
            i
            for i, line in enumerate(output_sensor_lines)
            if line.startswith("Channel:")
        ]

        assert len(original_channels) == len(
            output_channels
        ), f"Expected {len(original_channels)} channels, got {len(output_channels)}"

        # Check for blank lines between channels in output (skip first channel)
        for i in range(1, len(output_channels)):
            channel_line_idx = output_channels[i]
            previous_line = output_sensor_lines[channel_line_idx - 1]
            assert (
                previous_line.strip() == ""
            ), f"Expected blank line before Channel at line {channel_line_idx}, found: '{previous_line}'"

        os.remove(output_file)

    def test_logr_read_gzip_statistical_returns(self, test_file_directory):
        """Check that gzip compressed statistical dat files are ingested by nrgpy.logr_read"""
        filename = str(test_file_directory / "20260122_9458_00208_002233_002266_statistical.dat.gz")
        reader = LogrRead(filename)

        assert reader.site_description == "TMB_208_Screen", f"Expected site description to be 'TMB_208_Screen', got '{reader.site_description}'"
        assert reader.project == "R1.1_Hardware", f"Expected project to be 'R1.1_Hardware', got '{reader.project}'"
        assert reader.location == "Hinesburg, VT", f"Expected location to be 'Hinesburg, VT', got '{reader.location}'"
        assert len(reader.data) > 0, f"Expected data rows, got {len(reader.data)}"
        assert hasattr(reader, 'first_timestamp'), "Expected first_timestamp attribute"
        assert len(reader.ch_info) > 0, f"Expected channel info, got {len(reader.ch_info)}"

    def test_logr_read_gzip_diag_returns(self, test_file_directory):
        """Check that gzip compressed diag files are ingested by nrgpy.logr_read"""
        filename = str(test_file_directory / "20260122_9458_00208_002233_002266.diag.gz")
        reader = LogrRead(filename)

        assert reader.site_description == "TMB_208_Screen", f"Expected site description to be 'TMB_208_Screen', got '{reader.site_description}'"
        assert len(reader.data) > 0, f"Expected data rows, got {len(reader.data)}"
        assert reader.timestamp_col == "Stats_Timestamp", f"Expected timestamp column to be 'Stats_Timestamp' for diag files"

    def test_logr_read_gzip_log_returns(self, test_file_directory):
        """Check that gzip compressed log files are ingested by nrgpy.logr_read"""
        filename = str(test_file_directory / "20260122_9458_00208_002233_002266.log.gz")
        reader = LogrRead(filename)

        assert reader.site_description == "TMB_208_Screen", f"Expected site description to be 'TMB_208_Screen', got '{reader.site_description}'"
        assert len(reader.data) > 0, f"Expected data rows, got {len(reader.data)}"
        assert reader.timestamp_col == "Timestamp", f"Expected timestamp column to be 'Timestamp' for log files"

    def test_logr_concat_includes_gzip_files(self, test_file_directory):
        """Check that concat_txt includes gzip compressed files in concatenation"""
        reader = LogrRead()
        reader.concat_txt(
            dat_dir=str(test_file_directory),
            file_type="statistical", 
            file_filter="9458_00208"
        )

        # Should include both regular .dat and .dat.gz files with this filter
        gzip_files_included = any(".gz" in filename for filename in reader.dat_file_names)
        assert gzip_files_included, f"Expected gzip files to be included in concatenation. Files processed: {reader.dat_file_names}"
        assert len(reader.data) > 0, f"Expected concatenated data, got {len(reader.data)}"
        assert len(reader.dat_file_names) > 0, f"Expected files to be processed, got {reader.dat_file_names}"

    def test_logr_concat_mixed_compressed_uncompressed(self, test_file_directory):
        """Check that concat_txt can handle mix of compressed and uncompressed files"""
        reader = LogrRead()
        reader.concat_txt(
            dat_dir=str(test_file_directory),
            file_type="statistical"
        )

        # Should process both .dat and .dat.gz files
        regular_files = [f for f in reader.dat_file_names if not f.endswith('.gz')]
        gzip_files = [f for f in reader.dat_file_names if f.endswith('.gz')]
        
        assert len(regular_files) > 0, f"Expected some regular .dat files to be processed"
        assert len(gzip_files) > 0, f"Expected some .gz files to be processed"
        assert len(reader.data) > 0, f"Expected concatenated data from mixed file types"

from nrgpy import SymProTextRead


class TestSymproTxtRead:
    """Test class for SymPRO TXT reader"""

    def test_sympro_txt_read__valid_files(self, test_file_directory):
        """Check that SymPRO TXT exports are ingested by nrgpy.sympro_txt_read"""

        # Arrange
        directory = str(test_file_directory)
        file_filter = "004310"
        # Act
        reader = SymProTextRead()
        reader.concat_txt(txt_dir=directory, file_filter=file_filter)
        # Assert
        assert reader.site_number == "004310"
        assert len(reader.data) == 850

    def test_sympro_concat_cloud_concat_export_returns(self, cloud_export_concat_test_dir):
        """Check that SymPRO TXT exports are ingested by nrgpy.sympro_txt_read"""
        # Arrange
        reader = SymProTextRead()
        # Act
        reader.concat_txt(
            txt_dir=str(cloud_export_concat_test_dir),
            file_filter="671225",
            drop_duplicates=False,
        )
        # Assert
        assert reader.site_number == "671225"
        assert len(reader.data) == 11

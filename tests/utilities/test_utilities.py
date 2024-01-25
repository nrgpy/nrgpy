from nrgpy.utils.utilities import string_date_check


class TestDateCheck:
    def test_normal_sympro_format_passes(self):
        # arrange
        start_date = "2023-07-01"
        end_date = "2023-07-05"
        string = "004310_2023-07-03_00.00_000835_meas.txt"
        # act
        result = string_date_check(start_date, end_date, string)
        # assert
        assert (
            result
        ), f"expected True result from start: {start_date}, end: {end_date}, string: {string}"  # noqa: E501

    def test_normal_sympro_format_fails(self):
        # arrange
        start_date = "2023-07-01"
        end_date = "2023-07-05"
        string = "004310_2023-04-03_00.00_000835_meas.txt"
        # act
        result = string_date_check(start_date, end_date, string)
        # assert
        assert (
            not result
        ), f"expected false result from start: {start_date}, end: {end_date}, string: {string}"  # noqa: E501

    def test_normal_zx_date_format_passes(self):
        # arrange
        start_date = "2023-07-01"
        end_date = "2023-07-05"
        string = "Wind10_1225@Y2023_M07_D04.csv"
        # act
        result = string_date_check(start_date, end_date, string)
        # assert
        assert (
            result
        ), f"expected True result from start: {start_date}, end: {end_date}, string: {string}"  # noqa: E501

    def test_normal_zx_date_format_fails(self):
        # arrange
        start_date = "2023-07-01"
        end_date = "2023-07-05"
        string = "Wind10_1225@Y2023_M04_D04.csv"
        # act
        result = string_date_check(start_date, end_date, string)
        # assert
        assert (
            not result
        ), f"expected false result from start: {start_date}, end: {end_date}, string: {string}"  # noqa: E501

    def test_normal_logr_symclassic_format_passes(self):
        # arrange
        start_date = "2023-07-01"
        end_date = "2023-07-05"
        string = "20230704_0759_000000_003052_statistical.dat"
        # act
        result = string_date_check(start_date, end_date, string)
        # assert
        assert (
            result
        ), f"expected True result from start: {start_date}, end: {end_date}, string: {string}"  # noqa: E501

    def test_normal_logr_symclassic_format_fails(self):
        # arrange
        start_date = "2023-07-01"
        end_date = "2023-07-05"
        string = "20230404_0759_000000_003052_statistical.dat"
        # act
        result = string_date_check(start_date, end_date, string)
        # assert
        assert (
            not result
        ), f"expected false result from start: {start_date}, end: {end_date}, string: {string}"  # noqa: E501

    def test_custom_date_format_no_underscore(self):
        # arrange
        start_date = "2023-07-01"
        end_date = "2023-07-05"
        string = "My_MetTower123456_123456202307041134000102_0_meas.txt"
        # act
        result = string_date_check(start_date, end_date, string)
        # assert
        assert (
            result
        ), f"expected True result from start: {start_date}, end: {end_date}, string: {string}"  # noqa: E501

    def test_nrg_cloud_format_passes(self):
        # arrange
        start_date = "2024-01-01"
        end_date = "2024-01-10"
        string = "006716_SunnyDog_meas_2024.01.02-2024.01.08.txt"
        # act
        result = string_date_check(start_date, end_date, string)
        # assert
        assert (
            result
        ), f"expected True result from start: {start_date}, end: {end_date}, string: {string}"  # noqa: E501

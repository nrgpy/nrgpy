from nrgpy import SymProTextRead
import pandas as pd
from pathlib import Path
import pytest


@pytest.fixture
def test_file_directory():
    return Path(__file__).parent / "readers" / "files"


@pytest.fixture
def interval_check_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Timestamp": [
                "2023-07-01 00:00:00",
                "2023-07-01 00:05:00",
                "2023-07-01 00:10:00",
                "2023-07-01 00:15:00",
                "2023-07-01 00:20:00",
                "2023-07-01 00:25:00",
                "2023-07-01 00:30:00",
                "2023-07-01 00:35:00",
                "2023-07-01 00:40:00",
                "2023-07-01 00:45:00",
            ],
            "Value": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        }
    )


@pytest.fixture
def test_reader(test_file_directory):
    return SymProTextRead(
        test_file_directory / "004310_2022-03-17_00.00_000835_meas.txt"
    )

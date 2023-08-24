from pytest import MonkeyPatch
from nrgpy import logger
from nrgpy import CloudApi


def mock_request_session_token():
    return True

def mock_single_file(self, filename):
    pass

class TestCloudApis:
    monkeypatch = MonkeyPatch()
    
    def test_cloud_auth_invalid_creds_no_token(self):
        # Arrange
        client_id = "abc"
        client_secret = "def"
        # Act
        author = CloudApi(client_id, client_secret)
        # Assert
        assert author.resp.status_code >= 403, "expecting failure status code"

    def test_cloud_auth_expired_creds_gets_new_token(self):
        # Arrange
        TestCloudApis.monkeypatch.setattr(
            "nrgpy.CloudApi.request_session_token", mock_request_session_token
        )
        # Act
        # TODO: CloudApi.request_session_token returns bool
        TestCloudApis.monkeypatch.undo()
        # Assert
        assert True

    def test_cloud_import_filetypes_ok(self):
        # Arrange
        files = ["test.rld", "test.csv", "test.csv.zip", "test.diag", "test.statistical.dat"]
        TestCloudApis.monkeypatch.setattr(
            "nrgpy.CloudImport.single_file", 
        )
        # Act
        # Assert
        pass

    def test_cloud_import_filetypes_not_ok(self):
        # Arrange
        # Act
        # Assert
        pass

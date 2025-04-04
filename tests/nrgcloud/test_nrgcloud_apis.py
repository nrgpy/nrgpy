from pytest import MonkeyPatch
import nrgpy
from nrgpy.cloud_api import upload


def mock_maintain_session_token(arg):
    return True

def mock_request_session_token():
    return True

def mock_single_file(item, filename):
    pass 


class TestCloudApis:
    monkeypatch = MonkeyPatch()
    
    def test_cloud_auth_invalid_creds_no_token(self):
        # Arrange
        client_id = "abc"
        client_secret = "def"
        # Act
        author = nrgpy.CloudApi(client_id, client_secret)
        # Assert
        assert author.resp.status_code >= 400, "expecting failure status code"

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

    def test_cloud_import_good_filetypes_returns(self):
        # Arrange
        def return_good_files(_var):
            return ["test.rld", "test.csv", "test.csv.zip", "test.diag", "test.statistical.dat"]
        def mock_string_date_check(_var0, _var1, _var2):
            return True
        TestCloudApis.monkeypatch.setattr(
            "os.listdir", return_good_files
        )
        TestCloudApis.monkeypatch.setattr(
            "nrgpy.CloudImport.single_file", mock_single_file
        )
        TestCloudApis.monkeypatch.setattr(
            upload, "string_date_check", mock_string_date_check
        )
        # Act
        uploader = nrgpy.CloudImport(client_id="id", client_secret="secret", in_dir="dir")
        # Assert
        uploader.process()
        assert len(uploader.files) == len(return_good_files(self))
            

    def test_cloud_import_bad_filetypes_raises(self):
        # Arrange
        def return_bad_files(_var):
            return ["test.abc", "test.txt", "test.csv.7z", "test.log", "test.onesecond.dat"]
        TestCloudApis.monkeypatch.setattr(
            "os.listdir", return_bad_files
        )
        TestCloudApis.monkeypatch.setattr(
            "nrgpy.CloudImport.single_file", mock_single_file
        )
        # Act
        # Assert
        try:
            _ = nrgpy.CloudImport(client_id="id", client_secret="secret", in_dir="dir")
            assert False, "expected FileNotFoundError"
        except FileNotFoundError:
            assert True
        finally:
            TestCloudApis.monkeypatch.undo()

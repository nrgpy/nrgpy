import os
from nrgpy.common.log import NrgPythonLog


class TestNrgPythonLog:
    def test_log_initiates_without_env_variables(self):
        # arrange
        os.unsetenv("NRGPY_LOG_DIRECTORY")
        os.unsetenv("NRGPY_LOG_LEVEL")
        os.unsetenv("NRGPY_NO_LOG_FILES")

        # act
        log = NrgPythonLog()
        log.debug("test_log_initiates_without_env_variables")
        with open(log.logfile, "r") as f:
            log_contents = f.read()

        # assert
        assert log.log_directory == os.path.expanduser(
            "~/.nrgpy"
        ), "Expected default log directory ~/.nrgpy"
        assert "test_log_initiates_without_env_variables" in log_contents

    def test_log_initiates_with_env_variables(self):
        # arrange
        directory = os.path.join(os.path.expanduser("~/"), "_nrgpy_logs_test")
        os.environ["NRGPY_LOG_DIRECTORY"] = directory
        os.environ["NRGPY_LOG_LEVEL"] = "DEBUG"
        os.environ["NRGPY_NO_LOG_FILES"] = "0"

        # act
        log = NrgPythonLog()
        log.debug("test_log_initiates_with_env_variables")
        with open(log.logfile, "r") as f:
            log_contents = f.read()

        # assert
        assert log.log_directory == directory, f"Expected log directory {directory}"
        assert "test_log_initiates_with_env_variables" in log_contents

        # remove environment variables after test and remove log file and directory
        os.unsetenv("NRGPY_LOG_DIRECTORY")
        os.unsetenv("NRGPY_LOG_LEVEL")
        os.unsetenv("NRGPY_NO_LOG_FILES")
        if os.path.exists(log.logfile):
            os.remove(log.logfile)
            os.rmdir(directory)

    def test_log_initiates_no_log_file_created(self):
        # arrange
        directory = os.path.join(os.path.expanduser("~/"), "_nrgpy_logs_test")
        os.environ["NRGPY_LOG_DIRECTORY"] = directory
        os.environ["NRGPY_LOG_LEVEL"] = "DEBUG"
        os.environ["NRGPY_NO_LOG_FILES"] = "1"

        # act
        log = NrgPythonLog()
        log.debug("test_log_initiates_no_log_file_created")

        # assert
        assert not os.path.exists(log.logfile), "Expected no log file to be created"

        # cleanup
        os.unsetenv("NRGPY_NO_LOG_FILES")

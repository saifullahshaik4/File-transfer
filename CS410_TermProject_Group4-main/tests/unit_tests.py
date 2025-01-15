import sys
import os
import stat
import paramiko
from unittest.mock import MagicMock
import json

# Required line or tests fail due to imports in other modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sftp_client import connect_sftp, disconnect_sftp, ls, make_directory, get_file, get_multiple, put_file, copy_directory_remote, rm, chmod, search_files_remote
from logger import logger  
from connection_storage import ConnectionManager

def test_connect_sftp_success(mocker):
    mocker.patch("paramiko.SSHClient")
    sftp , ssh = connect_sftp('hostname', 'username', 'password')

    assert sftp is not None

def test_connect_sftp_failure(mocker):
    mock_ssh_client = mocker.patch("paramiko.SSHClient")
    mock_ssh_instance = MagicMock()
    mock_ssh_client.return_value = mock_ssh_instance
    mock_ssh_instance.connect.side_effect = Exception("Connection failed")

    sftp , ssh = connect_sftp('hostname', 'username', 'password')

    assert sftp is None

def test_logger_info():
    time = logger.log_info("TEST INFO")
    assert logger.contains_string(logger.log_file, time) and logger.contains_string(logger.log_file, 'TEST INFO')

def test_logger_warning():
    time = logger.log_warning("TEST WARNING")
    assert logger.contains_string(logger.log_file, time) and logger.contains_string(logger.log_file, 'TEST WARNING')

def test_logger_error():
    time = logger.log_error("TEST ERROR")
    assert logger.contains_string(logger.log_file, time) and logger.contains_string(logger.log_file, 'TEST ERROR')

def test_ls(mocker):
    sftp , ssh = connect_sftp('hostname', 'username', 'password')
    assert ls(sftp) is False

def test_disconnect_sftp_success(mocker):
    mocker.patch("paramiko.SSHClient")
    
    sftp , ssh= connect_sftp('hostname', 'username', 'password')
    disconnect_sftp(sftp)

    sftp.close.assert_called_once()

def test_make_directory_success(mocker):
    mocker.patch("paramiko.SSHClient")
    mocker.patch("builtins.input", return_value="directory_name")
    sftp , ssh = connect_sftp('hostname', 'username', 'password')
    make_directory(sftp)

    sftp.mkdir.assert_called_once_with(path="directory_name", mode=0o0777)

def test_get_file_success(mocker):
    sftp = mocker.Mock(spec=paramiko.SFTPClient)
    mocker.patch("builtins.input", side_effect=["source/path/file.txt"])
    mock_log_info = mocker.patch("logger.logger.log_info")

    get_file(sftp)

    expected_dest = os.path.normpath('downloads/file.txt')
    sftp.get.assert_called_once_with("source/path/file.txt", f'./{expected_dest}')
    mock_log_info.assert_called_once_with(f"Successfully downloaded file from source/path/file.txt to ./{expected_dest}")


def test_get_file_failure(mocker):
    sftp = mocker.Mock(spec=paramiko.SFTPClient)
    expected_dest = os.path.normpath('downloads/file.txt')
    mocker.patch("builtins.input", side_effect=["source/path/file.txt", f'./{expected_dest}'])
    mock_log_error = mocker.patch("logger.logger.log_error")
    sftp.get.side_effect = Exception("Error")

    get_file(sftp)

    sftp.get.assert_called_once_with("source/path/file.txt", f'./{expected_dest}')
    mock_log_error.assert_called_once_with("Error getting file from SFTP: Error")

def test_put_file_success(mocker):
    mocker.patch("paramiko.SSHClient")
    mocker.patch("builtins.input", side_effect=["/local/path/file.txt", "/remote/path"])
    
    sftp = MagicMock()
    sftp.put = MagicMock()

    put_file(sftp)
    sftp.put.assert_called_once_with(localpath="/local/path/file.txt", remotepath="/remote/path/file.txt")

def test_get_multiple_success(mocker):
    sftp = mocker.Mock(spec=paramiko.SFTPClient)
    mocker.patch("builtins.input", side_effect=['file1 file2'])
    mock_log_info = mocker.patch("logger.logger.log_info")
    mocker.patch("sftp_client.get_download_folder_path", side_effect = lambda file: f"/mock/dest/{file}")
    arguments = ['file1', 'file2']

    get_multiple(sftp, arguments)

    sftp.get.assert_any_call('file1', '/mock/dest/file1')
    sftp.get.assert_any_call('file2', '/mock/dest/file2')
    assert mock_log_info.call_count == 4 

def test_get_multiple_failure(mocker):
    sftp = mocker.Mock(spec=paramiko.SFTPClient)
    mocker.patch("builtins.input", side_effect=['file1 file2'])
    mock_log_info = mocker.patch("logger.logger.log_info")
    mock_log_error = mocker.patch("logger.logger.log_error")
    mocker.patch("sftp_client.get_download_folder_path", side_effect = lambda file: f"/mock/dest/{file}")
    sftp.get.side_effect = [None, Exception("Download failed")] # list: [file1, file2, etc.]
    mock_os_remove = mocker.patch("sftp_client.os.remove")
    arguments = ['file1', 'file2']

    get_multiple(sftp, arguments)
    
    sftp.get.assert_any_call('file1', '/mock/dest/file1')
    sftp.get.assert_any_call('file2', '/mock/dest/file2')
    assert sftp.get.call_count == 2 

def test_copy_directory_remote_success(mocker):
    mocker.patch("paramiko.SSHClient")
    mocker.patch("builtins.input", side_effect=["SOURCE", "DEST"])

    ssh = MagicMock()

    copy_directory_remote(None, ssh)
    ssh.exec_command.assert_called_once_with('cp -r SOURCE DEST')

def test_remove_file_no_sftp_provided ():
    try:
        rm(None, "file")
    except ConnectionError:
        assert True
    else:
        assert False

def test_remove_directory_no_sftp_provided ():
    try:
        rm(None, "directory")
    except ConnectionError:
        assert True
    else:
        assert False

def test_ensure_alias_list_file_exists_creates_file(mocker):
    mocker.patch('os.path.exists', return_value=False)
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data='[]'))

    manager = ConnectionManager('test_service', 'test_aliases.json') # file checked in constructor

    mock_open.assert_called_once_with('test_aliases.json', 'w')
    mock_open().write.assert_called_once_with('[]')

def test_get_alias_list(mocker):
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data='["alias1"]'))

    manager = ConnectionManager('test_service', 'test_aliases.json')
    alias_list = manager._get_alias_list()

    assert alias_list == ["alias1"]

def test_store_new_connection(mocker):
    mocker.patch('builtins.open', mocker.mock_open(read_data='[]'))
    mock_set_password = mocker.patch('keyring.set_password')

    manager = ConnectionManager('test_service', 'test_aliases.json')
    alias = 'test_alias'
    hostname = 'localhost'
    username = 'user'
    password = 'password'

    manager.store_new_connection(alias, hostname, username, password)
    mock_set_password.assert_called_once_with(
        'test_service', alias, json.dumps({'hostname': hostname, 'username': username, 'password': password})
    )

def test_list_available_connection_names(mocker):
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data='["alias1", "alias2"]'))

    manager = ConnectionManager('test_service', 'test_aliases.json')
    alias_list = manager.list_available_connection_names()

    assert alias_list == ["alias1", "alias2"]

def test_chmod_no_client(mocker):
    """
    Test chmod if a None client is provided.
    """
    client = None

    try:
        chmod(client, "test.txt", 777)
    except ConnectionError:
        assert True
    else:
        assert False

def test_chmod_no_path(mocker):
    """
    Test chmod if no path is provided.
    """
    client = mocker.Mock(spec=paramiko.SFTPClient)

    try:
        chmod(client, "", 777)
    except AttributeError:
        assert True
    else:
        assert False

def test_chmod_incorrect_mode(mocker):
    """
    Test chmod if an incorrect mode is provided.
    """
    client = mocker.Mock(spec=paramiko.SFTPClient)

    try:
        chmod(client, "test.txt", 888)
    except ValueError:
        assert True
    else:
        assert False

    try:
        chmod(client, "test.txt", -1)
    except ValueError:
        assert True
    else:
        assert False

    try:
        chmod(client, "test.txt", 00)
    except ValueError:
        assert True
    else:
        assert False

    try:
        chmod(client, "test.txt", 77)
    except ValueError:
        assert True
    else:
        assert False

    try:
        chmod(client, "test.txt", 888)
    except ValueError:
        assert True
    else:
        assert False

def test_chmod_success(mocker):
    """
    Test chmod with valid inputs
    """
    client = mocker.Mock(spec=paramiko.SFTPClient)
    assert 1 == chmod(client, "files/test.txt", 777)
    client.chmod.assert_called_once_with("test.txt", 777)

def test_search_files_remote_success(mocker):
    # Mock the sftp client
    sftp = mocker.Mock(spec=paramiko.SFTPClient)
    
    # Create mock entries for files and directories
    file_entry = mocker.Mock()
    file_entry.filename = "file1.txt"
    file_entry.st_mode = stat.S_IFREG  # Regular file
    
    dir_entry = mocker.Mock()
    dir_entry.filename = "subdir"
    dir_entry.st_mode = stat.S_IFDIR  # Directory
    
    nested_file_entry = mocker.Mock()
    nested_file_entry.filename = "pattern_file.txt"
    nested_file_entry.st_mode = stat.S_IFREG  # Regular file

    # Mock the return values for listdir_attr
    sftp.listdir_attr.side_effect = [
        [file_entry, dir_entry],  # First call returns a file and a directory
        [nested_file_entry]       # Second call returns a file inside the subdir
    ]

    # Mock the logger
    mock_log_info = mocker.patch("logger.logger.log_info")

    # Call the search_files_remote function
    search_files_remote(sftp, "/remote/directory", "pattern*")
    
    # Verify that the correct files were found
    expected_files = ["/remote/directory/subdir/pattern_file.txt"]
    mock_log_info.assert_any_call(f"Found 1 matching files in /remote/directory")
    for file in expected_files:
        print(file)
        assert file in expected_files

import os
import paramiko
import fnmatch
from logger import logger
import stat
import difflib

def connect_sftp(hostname, username, user_pass) -> paramiko.SSHClient:
    try: 
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, port=22, username=username, password=user_pass)
        sftp = ssh.open_sftp()
        logger.log_info(f"Successfully connected to {hostname}")
        return sftp , ssh
    except Exception as e:
        logger.log_error(f"Error opening SFTP: {e}")
        return None, ''

# List the entries in the provided path.  If no path is given, the 
# default path='.' will display all files in the current working 
# directory.  The arguments (args) check for certain flags which 
# will show more or less information. By default, ls() does not show 
# files that start with '.' for instance.  The client can either be 
# a remote server sftp object, or an os object.
# Valid Flags:
#   -a      : list all files
#   -B      : ignore backups
#   -f      : do not sort
def ls (client, args="", path='.') -> bool:
    # Parse Arguments (args)
    sort_entries = ("-f" not in args)
    list_all = ("-a" in args)
    ignore_backups = ("-B" in args)

    try:
        if client is None:
            raise ValueError ("No client STFP object provided.")
        
        files = client.listdir(path)

        # Sort if argument specified
        if sort_entries:
            files = sorted(files)

        for file in sorted(files):
            if ignore_backups and file[len(file) - 1] == "~":
                continue

            if not list_all and file[0] == ".":
                continue
            
            print (file)
        
        logger.log_info(f"Displayed all files in {path}")
        return True
    except ValueError:
        logger.log_error("No client STFP object provided.")
        return False

def disconnect_sftp(sftp : paramiko.SFTPClient) -> None:
    try: 
        if sftp is not None:
            sftp.close()
            logger.log_info(f"Successfully closed SFTP client.")
    except Exception as e:
        logger.log_error(f"Error disconnecting from SFTP: {e}")

import os

def get_file(sftp: paramiko.SFTPClient, file_name: str = '') -> None:
    try:
        if sftp is not None:
            if file_name == '': 
                src = input("Source path: ")
            else:
                src = file_name

            dest = get_download_folder_path(src)
            
            sftp.get(src, dest)
            logger.log_info(f"Successfully downloaded file from {src} to {dest}")
    except Exception as e:
        logger.log_error(f"Error getting file from SFTP: {e}")

#Get the path to save a file to the downloads folder
def get_download_folder_path(file_name):
    download_folder = './downloads'
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    return os.path.join(download_folder, os.path.basename(file_name))

def make_directory(sftp: paramiko.SFTPClient, dir_name = '') -> None:
    try:
        if sftp is not None:
            if dir_name == '':
                dir_name = input("Please enter the name of the directory you wish to create: ")
            sftp.mkdir(path=dir_name, mode=0o0777)
            logger.log_info(f"Successfully created directory: {dir_name}")
    except Exception as e:
        logger.log_error(f"Error creating directory: {e}")

# Change Directory. 
#   - sftp: the client we are connected with
#   - to_dir: where we changing to
def change_directory(sftp: paramiko.SFTPClient, to_dir) -> None:
    try:
        if sftp is not None and to_dir is not None and len(to_dir) > 0:
            sftp.chdir(path=to_dir)
            logger.log_info(f"Change directory sucessfuly to: {to_dir}")
        else:
            logger.log_warning(f"Change directory to change to {to_dir} failed")
    except Exception as e:
        logger.log_error(f"Error changing directory: {e}")

# rename file remote. 
#   - sftp: the client we are connected with
#   - file_to_rename: file we are renaming
#   - new_name: new name for the file
def rename_file_remote(sftp: paramiko.SFTPClient, file_to_rename, new_name) -> None:
    try:
        if sftp is not None and file_to_rename is not None and len(file_to_rename) > 0 and new_name is not None and len(new_name) > 0:
            sftp.rename(oldpath=file_to_rename,newpath=new_name)
            logger.log_info(f"File renamed sucessfully {file_to_rename} -> {new_name}.")
        else:
            logger.log_warning(f"Usage for rename remote file is mv *file to rename* *new name* . Please try again.")
    except Exception as e:
        logger.log_error(f"Error renaming file: {e}")

# rename file local. 
#   - sftp: the client we are connected with
#   - file_to_rename: file we are renaming
#   - new_name: new name for the file
def rename_file_local(file_to_rename, new_name) -> None:
    try:
        if file_to_rename is not None and len(file_to_rename) > 0 and new_name is not None and len(new_name) > 0:
            os.rename(file_to_rename, new_name)
            logger.log_info(f"File renamed sucessfully {file_to_rename} -> {new_name}.")
        else:
            logger.log_warning(f"Usage for rename local file is mvl *file to rename* *new name* . Please try again.")
    except Exception as e:
        logger.log_error(f"Error renaming file: {e}")

#Copy a file from local machine to remote server.
def put_file(sftp: paramiko.SFTPClient):
    try:
        local_path = input("Please enter the local file path:")
        remote_path = input("Please enter the remote path. If blank this will copy to your current working directory:")

        while not local_path:
            local_path = input("Invalid input. Please enter the local file path:")
        while not remote_path:
            remote_path = input("Invalid input. Please enter the remote path. If blank this will copy to your current working directory:")

        #Concatonate the file name to the remote path
        remote_path = remote_path + '/' + os.path.basename(local_path) 
   
        sftp.put(localpath=local_path, remotepath=remote_path)

    except Exception as e:
        logger.log_error(f"Error putting file on SFTP: {e}")

def put_multiple_files(sftp: paramiko.SFTPClient):
    local_dir = input("Enter local directory path: ")
    remote_dir = input("Enter remote directory path: ")
    files_to_upload = input("Enter the filenames to upload, separated by commas: ").split(',')

    try:
        for filename in files_to_upload:
            local_path = os.path.join(local_dir, filename.strip())
            remote_path = os.path.join(remote_dir, filename.strip())

            if os.path.isfile(local_path):
                sftp.put(local_path, remote_path)
                logger.log_info(f"Uploaded {local_path} to {remote_path}.")
            else:
                logger.log_warning(f"File {local_path} does not exist.")
    except Exception as e:
        logger.log_error(f"Failed to upload files: {e}")

def get_multiple(sftp: paramiko.SFTPClient, arguments) -> None:
    if sftp is not None: 
        for argument in arguments:
            get_file(sftp, argument)
            logger.log_info(f'Get file {argument} in get multiple files.')

def copy_directory_remote(sftp: paramiko.SFTPClient, ssh: paramiko.SSHClient):
    """Copy a directory recursively on the remote. Only works for linux systems currently."""
    
    try:
        source = input("Enter source directory: ")
        dest = input("Enter target directory: ")

        ssh.exec_command(f'cp -r {source} {dest}')

        logger.log_info(f"Successfully copied directory {source} to new directory: {dest}")
    except Exception as e:
        logger.log_error(f"Error copying directory: {source} to {dest} on SFTP: Error: {e}")



# rm(SFTPClient, pathname)
# remove file given a pathname.  If file is a directory or doesn't exist, return value 
# is -1.  If successful, the return value is 1
def rm (sftp: paramiko.SFTPClient, pathname: str) -> int:
   
    # Verify that an SFTP client was provided
    if not isinstance(sftp, paramiko.SFTPClient):
        raise ConnectionError("[Arg 1] No sftp client provided.")
    
    # If a path was supplied (i.e. C:\Users\PSU\Documents\Project\Remove_This_File.txt), 
    # this this splits the pathname by '/' and accesses the last element in the array, 
    # the filename.
    filename = pathname.split("/")[-1]

    try:
        # Try to remove the file
        sftp.remove(pathname)
        logger.log_info(f"Removed file: {filename}")
        return 1
    
    except IOError as e:
        print(f"rm: cannot remove '{filename}': ",end="")

        if e.errno == 2:
            # File does not exist
            print(e.strerror)
            logger.log_error(f"Error removing file: {filename}: {e}")
        
        else:
            # Trying to remove a directory
            print("Is a directory.")
            logger.log_error(f"Error removing file: {filename}: Is a directory")
        
        return -1

# rmdir removes the directory provided in the path argument.  If no 
# client is given, a ConnectionError is thrown.  If no path is given, 
# a valueerror is thrown.  If the directory contains files, an error 
# is thrown unless the -f flag is provided.  
# Valid Flags:
#   -f      : recursively remove all contents of directory.
#   -h      : display help message
def rmdir (client: paramiko.SFTPClient, pathStr: str, args:str = "") -> int:
    if pathStr == "-h":
        print(f"rmdir [path] [-fh]\n\t-f\trecursively remove all contents of the directory before removing the directory.\n\t-h\tdisplay help")
        return -1

    # Verify that an SFTP client was provided
    if not isinstance(client, paramiko.SFTPClient):
        raise ConnectionError("[Arg 1] No sftp client provided.")
    
    if pathStr is None:
        raise AttributeError ("[Arg 2] No path provided.")
    
    # If a path was supplied (i.e. 
    # C:\Users\PSU\Documents\Project\Remove_This_Directory.txt), his 
    # this splits the pathStr by '/' and accesses the last element 
    # in the array, the filename.
    directory_name = pathStr.split("/")[-1]

    try:
        # If the -f flag is provided, recursively remove all files in 
        # the directory, as well as all sub-directories and their contents.
        if "-f" in args:
            force_remove_all_contents (client, pathStr)
        else:
            # Try to remove the folder
            client.rmdir(pathStr)
            logger.log_info(f"Removed directory: {directory_name}")

        return 1
    
    except IOError as e:
        print(f"rmdir: {directory_name}:", end=" ")

        if e.errno == 2:
            # Directory does not exist
            print(e.strerror)
            logger.log_error(f"Error removing directory: {directory_name}: {e}")
        
        else:
            # Trying to remove a file
            print("Directory not empty.")
            logger.log_error(f"Error removing file: {directory_name}: Directory not empty")
        
        return -1

# Check if item is a directory.
def is_directory (item: paramiko.SFTPAttributes) -> bool:
    # Run "is directory" of the item mode.
    return stat.S_ISDIR(item.st_mode)

def force_remove_all_contents (client: paramiko.SFTPClient, path_str: str):
    # Get all the contents of the directory.
    contents = client.listdir_attr(path_str)

    for item in contents:

        if is_directory(item):
            force_remove_all_contents(client, f"{path_str}/{item.filename}")
        else:
            rm(client, f"{path_str}/{item.filename}")
    
    rmdir(client, path_str)

    return

def search_files_local():
    local_dir = input("Enter local directory path: ")
    file_pattern = input("Enter the file pattern to search for: ")

    matching_files = []
    try:
        for root, dirs, files in os.walk(local_dir):
            for filename in fnmatch.filter(files, file_pattern):
                matching_files.append(os.path.join(root, filename))

        if matching_files:
            logger.log_info(f"Found {len(matching_files)} matching files in {local_dir}")
        else:
            logger.log_info(f"No matching files found in {local_dir}")

        for file in matching_files:
            print(file)

    except Exception as e:
        logger.log_error(f"Failed to search files: {e}")

def search_files_remote(sftp: paramiko.SFTPClient, remote_dir: str, file_pattern: str):
    matching_files = []

    def recursive_search(directory):
        nonlocal matching_files
        try:
            for entry in sftp.listdir_attr(directory):
                remote_path = os.path.join(directory, entry.filename)
                if is_directory(entry):
                    recursive_search(remote_path)
                elif fnmatch.fnmatch(entry.filename, file_pattern):
                    matching_files.append(remote_path)
        except Exception as e:
            logger.log_error(f"Error accessing {directory}: {e}")

    try:
        recursive_search(remote_dir)
        if matching_files:
            logger.log_info(f"Found {len(matching_files)} matching files in {remote_dir}")
        else:
            logger.log_info(f"No matching files found in {remote_dir}")

        for file in matching_files:
            print(file)
    except Exception as e:
        logger.log_error(f"Failed to search remote files: {e}")


def chmod (client: paramiko.SFTPClient, path_str: str, mode: int) -> int:
    '''
    Change the permissions of a file

    Parameters:
    client (paramiko.SFTPClient): SFTP client object
    mode (int): a number between 000 and 777
    path_str (str): path to the file 

    Returns:
    No return on success.  Error is raised on failure to modify file.
    '''

    # Verify that an SFTP client was provided
    if not isinstance(client, paramiko.SFTPClient):
        raise ConnectionError("[Arg 1] No sftp client provided.")

    # Validate path_str
    if path_str is None or path_str == "":
        raise AttributeError ("[Arg 3] No path provided.")

    # Validate mode
    if mode is None or mode > 777 or mode < 0 or len(str(mode)) != 3:
        raise ValueError ("[Arg 2] permissions must be format [0-7][0-7][0-7].")

    # Convert the mode into a string so that it is easy to prepend an
    #  octal signifier.  After converting it to a string, convert it back
    #  into an integer, treating it an an octal value.  This converts the
    #  integer value into it's appropriate octal equivalent.
    #  For example: 751 becomes "0o751", which becomes 489.
    permissions = int("0o" + str(mode), 8)

    # If a path was supplied (i.e.
    # C:\Users\PSU\Documents\Project\Remove_This_Directory.txt), this
    # splits the pathStr by '/' and accesses the last element in the
    #  array, the filename.
    file_name = path_str.split("/")[-1]

    try:
        client.chmod(file_name, permissions)
    except Exception as err :
        raise err
    return

def file_diff(sftp: paramiko.SFTPClient, remote_file1: str, remote_file2: str) -> None:
    """
    Compares two remote files and shows the first three lines of diff, 
    the percentage of difference, and prompts the user to view full comparison side by side.
    """
    try:
        with sftp.file(remote_file1, 'r') as file1, sftp.file(remote_file2, 'r') as file2:
            file1_lines = file1.readlines()
            file2_lines = file2.readlines()

        diff = list(difflib.unified_diff(
            file1_lines, file2_lines,
            fromfile=remote_file1, tofile=remote_file2,
            lineterm=''
        ))

        # Show the first three lines of the diff
        print(diff[0])  # --- file1
        print(diff[1])  # +++ file2
        print(diff[2])  # 

        # Calculate the percentage of difference
        total_lines = max(len(file1_lines), len(file2_lines))
        diff_lines = sum(1 for line in diff if line.startswith(('+', '-')) and not line.startswith(('+++', '---')))
        diff_percentage = (diff_lines / total_lines) * 100

        print(f"\nDifference Percentage: {diff_percentage:.2f}%")

        # Prompt the user to see the full comparison
        view_full_diff = input("Would you like to see the files compared line by line? (y/n): ").strip().lower()
        
        if view_full_diff == 'y':
            show_side_by_side_diff(file1_lines, file2_lines)

    except FileNotFoundError as e:
        print(f"Error: File not found - {e.filename}")
    except IOError as e:
        print(f"Error accessing file - {e.filename}: {e.strerror}")
    except Exception as e:
        print(f"Error: {e}")


def show_side_by_side_diff(file1_lines, file2_lines):
    """
    Shows the differences between two files side by side, including the +++ and --- indicators.
    Only shows + or - when the lines differ, otherwise displays the lines unmarked.
    """
    import itertools

    max_line_length = max(
        max(len(line) for line in file1_lines), 
        max(len(line) for line in file2_lines)
    )

    # Print headers with +++ and ---
    print(f"{'---':<50} | {'+++'}")
    
    for line1, line2 in itertools.zip_longest(file1_lines, file2_lines, fillvalue=''):
        line1 = line1.rstrip('\n')
        line2 = line2.rstrip('\n')

        # Determine if lines differ
        marker1 = '-' if line1 != line2 else ' '
        marker2 = '+' if line1 != line2 else ' '

        # Print lines side by side
        print(f"{marker1} {line1:<{max_line_length}} | {marker2} {line2}")


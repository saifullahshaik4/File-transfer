from sftp_client import connect_sftp
from sftp_client import ls
from sftp_client import file_diff
from connection_storage import connection_info
from inputimeout import inputimeout, TimeoutOccurred
import sftp_client as client
import os
import getpass


def menu():
    sftp = None
    while True:
        print("\nMenu Options")
        print("0. Exit app")
        print("1. Use stored login to a server")
        print("2. Enter new login to a server")
        option = get_option("Enter a number: ")

        match option:
            case 0: 
                break
            case 1:
                existing_connection_prompts()
            case 2:
                new_connection_prompts()
            case _:
                print("Invalid option")

def existing_connection_prompts():
    print("Available connections:")
    available_names = connection_info.list_available_connection_names()
    for name in available_names:
        print(name)
    option = input("Enter an alias from the list above to connect to. ")
    connection = connection_info.get_connection_by_alias(option)
    if(connection != None):
        sftp , ssh = connect_sftp(connection['hostname'],connection['username'],connection['password'])
        logged_on_menu(sftp , connection['hostname'], ssh)
    else:
        print('Invalid Alias.\n')

def new_connection_prompts():
    print("\nEnter connection information...")
    try:
        hostname = input("Hostname: ")
        username = input("Username: ")
        user_pass = getpass.getpass("Password: ")
        sftp , ssh = connect_sftp(hostname,username,user_pass)
        if(sftp != None):
            while True:
                option = input("Would you like to store the connection information? Enter y or n. ")
                if(option == 'y'):
                    alias = input("Enter an alias for your new connection. ")
                    connection_info.store_new_connection(alias,hostname,username,user_pass)
                    break
                elif(option == 'n'):
                    break
                else:
                    print('Invalid entry, enter y or n.')
            logged_on_menu(sftp , hostname, ssh)
        else:
            print('\nConnection failed - please verify you have the correct hostname and username/password.')
    except Exception as e:
        print(f"Error: {e}")

def logged_on_menu(sftp, hostname, ssh):
    print(f'\n\nConnected to {hostname}.\n')
    while True:
        option = user_input(sftp)
        if not option:
            break

        option_split = option.split()
        if not option_split:
            continue

        command = option_split[0].lower()
        arguments = option_split[1:]

        match command:
            case 'help':
                print_help_string()
            case 'exit':
                print("\nDisconnecting from server...")
                try:
                    client.disconnect_sftp(sftp)
                except Exception as e:
                    print(f"Error: {e}")
                break
            case 'ls': 
                ls(client=sftp, args="-a", path='.')
            case 'lsl': 
                ls(client=os, args="-a", path='.')
            case 'get':
                try:
                    if len(arguments) == 1: 
                        client.get_file(sftp, arguments[0])
                    else:
                        client.get_multiple(sftp, arguments)
                except Exception as e:
                    print(f"Error: {e}")
            case 'put':
                try:
                    client.put_file(sftp)
                except Exception as e:
                    print(f"Error: {e}")
            case 'putm':
                try:
                    client.put_multiple_files(sftp)
                except Exception as e:
                    print(f"Error: {e}")
            case 'mkdir':
                try:
                    if arguments:
                        client.make_directory(sftp, arguments[0])
                    else:
                        client.make_directory(sftp)
                except Exception as e:
                    print(f"Error: {e}")
            case 'cd':
                if arguments:
                    try:
                        client.change_directory(sftp, arguments[0])
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print("Error: 'cd' command requires a directory name")
            case 'mv':
                if len(arguments) == 2:
                    try:
                        client.rename_file_remote(sftp, arguments[0], arguments[1])
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print(f"Usage for rename remote file is mv *file to rename* *new name* . Please try again.")
            case 'mvl':
                if len(arguments) == 2:
                    try:
                        client.rename_file_local(arguments[0], arguments[1])
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print(f"Usage for rename local file is mvl *file to rename* *new name* . Please try again.")
            case 'cpdir':
                try:
                    client.copy_directory_remote(sftp, ssh)
                except Exception as e:
                    print(f'Error: {e}')
            case "rm":
                if arguments:
                    try:
                        client.rm(sftp, arguments)
                    except Exception as e:
                        print(e)
                else:
                    print("Error: 'rm' command requires a file or path name")
            case "rmdir":
                if arguments:
                    try:
                        if len(arguments) > 1:
                            client.rmdir(sftp, arguments[0], arguments[1:])
                        else:
                            client.rmdir(sftp, arguments[0])
                    except Exception as e:
                        print(e)
                else:
                    print("Error: 'rmdir' command requires a directory or path name")
            case "chmod":
                if len(arguments) == 2:
                    try:
                        client.chmod(sftp, int(arguments[0]), arguments[1])
                    except Exception as err:
                        print(err)
                else:
                    print("Error: 'chmod' command requires a path and a mode")
            case "search_local":
                client.search_files_local()
            case "search_remote":
                if len(arguments) == 2:
                    remote_dir = arguments[0]
                    file_pattern = arguments[1]
                    try:
                        client.search_files_remote(sftp, remote_dir, file_pattern)
                    except Exception as e:
                        print(e)
                else:
                    print("Error: 'search_remote' command requires a directory and a pattern")
            case 'diff':
                if len(arguments) == 2:
                    try:
                        file_diff(sftp, arguments[0], arguments[1])
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print("Error: 'diff' command requires two remote file paths to compare")

            case _:
                print("Unknown command. Enter 'help' for available commands.")

def get_option(prompt: str) -> int:
    while True:
        option = input(prompt)
        try:	
            return int(option)
        except ValueError:
            print(f"{option} is not a valid integer")

def print_help_string():
    print('\n')
    print("Available commands (commands are case insensitive):")
    print("exit : Log off from server")
    print("ls : List files in remote directory")
    print("lsl : List files in local directory")
    print("get *name of file*: Copy remote file to local machine")
    print("get multiple : Copy multiple remote files to local machine")
    print("put: Copy local file to remote")
    print("mkdir *name of new directory*: Create Directory on Remote Server")
    print("putm: Copy multiple local files to remote")
    print('cd *name of directory*: Change directory')
    print('mv *file/path to rename* *new file name/new path*: rename/move  file on the remote server')
    print('mvl *file/path to rename* *new file name/new path*: rename/move  file locally')
    print("cpdir: Copy a directory on Remote server")
    print("search_local: Search for files locally. Example: enter /path/to/directory then *.txt")
    print("search_remote *directory* *pattern*: Search for files in remote server matching the pattern")
    print("diff *directory/path to/remote_file1* *directory/to/remote_file2*: Compare two files and display differences")
    print('\n')

def user_input(sftp):
    try:
        return inputimeout("Enter an option. Enter help for more information: ", timeout=30)
    except TimeoutOccurred:
        print('After 30 seconds of inactivity you are logged off of the server')
        try:
            client.disconnect_sftp(sftp)
            return None
        except Exception as e:
            print(f"Error: {e}")
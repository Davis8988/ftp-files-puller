# Contains ftp-functions to be used by other scripts
import ftplib
import socket
import os
import ntpath
from functools import wraps
from MyModules import MyGlobals


class FTPPathType:
    FILE = 1
    FOLDER = 2
    INVALID = 3
    ERROR = 4


ftp_errors_without_timeouts_errors = tuple([x for x in ftplib.all_errors if x is not socket.error and x is not OSError])


# Wrappers
def with_retry_count_decorate(action_description):
    def run_func_and_rerty_on_failure(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = MyGlobals.ftpRetriesCount
            while retry_count:
                try:
                    return func(*args, **kwargs)
                except socket.timeout:
                    print('Timeout occurred while attempting to {}. Retry count left: {}/{}'.format(action_description,
                                                                                                    retry_count,
                                                                                                    MyGlobals.ftpRetriesCount))
                    retry_count -= 1
                except OSError as errorMsg:
                    error_msg_str = str(errorMsg).lower()
                    timeout_str = 'timed out'
                    if timeout_str not in error_msg_str:
                        print('\nFailed to {}.\nError:\n{}'.format(action_description, errorMsg))
                        return None
                    print('Timeout occurred while attempting to {}. Retry count left: {}/{}'.format(action_description,
                                                                                                    retry_count,
                                                                                                    MyGlobals.ftpRetriesCount))
                    retry_count -= 1
                except BaseException as errorMsg:
                    print("\nFailed to {}.\nError:\n{}".format(action_description, errorMsg))
                    return None
                MyGlobals.sleep_for_a_while(MyGlobals.sleepBetweenRetriesSec_Default)

            print('Timeouts over - returning')
            return None

        return wrapper

    return run_func_and_rerty_on_failure

# Main download path from an FTP server
def download_path(ftp_con, src_ftp_path, dest_path):
    path_type = ftp_check_path_type(ftp_con, src_ftp_path)  # File or Folder
    if path_type == FTPPathType.FILE:
        file_parent_dir = ntpath.split(src_ftp_path)[0]
        file_name = ntpath.basename(src_ftp_path)
        if not change_ftp_dir(ftp_con, file_parent_dir):  # CD to ftp folder of the file
            return False
        return download_ftp_file(ftp_con, file_name, dest_path, create_dirs=True)  # Download the file
    elif path_type == FTPPathType.FOLDER:
        return download_ftp_dir(ftp_con, src_ftp_path, dest_path)  # Folder type: Download folder
    elif path_type == FTPPathType.INVALID:
        print('FTP Path {} is invalid'.format(src_ftp_path))  # Invalid path (or non existing)
        return None
    elif path_type == FTPPathType.ERROR:  # Failed checking path type
        print('Error while checking path {}\nCannot continue..'.format(src_ftp_path))
        return None


# Get connection to FTP server using address & port
def get_ftp_connection(ftp_addr, ftp_port, ftp_timeout):
    if MyGlobals.isVerbose:
        print("Getting ftp connection to: {}:{}".format(MyGlobals.ftpAddr, MyGlobals.ftpPort))
    ftp_obj_result = _get_ftp_connection(ftp_addr, ftp_port, ftp_timeout)
    if ftp_obj_result and MyGlobals.isVerbose:
        print("Success - got connection to: {}:{}".format(ftp_addr, ftp_port))
    return ftp_obj_result


@with_retry_count_decorate(action_description='prepare an FTP object')
def _get_ftp_connection(ftp_addr, ftp_port, ftp_timeout):
    ftp_obj = ftplib.FTP(timeout=ftp_timeout)  # prepare FTP object with a timeout setting
    ftp_obj.connect(ftp_addr, ftp_port)  # connect to host,port
    return ftp_obj

# Login to FTP server using credentials
def login_to_ftp_server(ftp_con, ftp_user, ftp_pass):
    if MyGlobals.isVerbose:
        print("Attempting to login to ftp server: {} with user: {}".format(ftp_con.host, ftp_user))
    login_result = _login_to_ftp_server(ftp_con, ftp_user, ftp_pass)
    if login_result and MyGlobals.isVerbose:
        print("Success - logged in to ftp server")
    return login_result


@with_retry_count_decorate(action_description='login to FTP server')
def _login_to_ftp_server(ftp_con, ftp_user, ftp_pass):
    try:
        ftp_con.login(ftp_user, ftp_pass)
        return True
    except ftp_errors_without_timeouts_errors as errorMsg:
        print('\nFailed to login to {} as user: {}\nError:\n'.format(ftp_con.host, ftp_user, errorMsg))
        return None


@with_retry_count_decorate(action_description='get current ftp dir')
def ftp_get_pwd(ftp_con):
    try:
        return ftp_con.pwd()
    except ftp_errors_without_timeouts_errors as errorMsg:
        print('\nFailed getting current ftp dir\nError:\n{}'.format(errorMsg))
        return None

# Check path type: File, Folder or Invalid (non exsiting?)
def ftp_check_path_type(ftp_con, ftp_path_to_check):
    if MyGlobals.isVerbose:
        print("Checking path-type of: {} ".format(ftp_path_to_check))

    if change_ftp_dir(ftp_con, ftp_path_to_check):  # Try to CD to the path
        return FTPPathType.FOLDER

    if MyGlobals.isVeryVerbose:  # Couldn't CD to it so it's not a folder
        print("{} is not a folder. Checking if it's a file".format(ftp_path_to_check))

    path_parent = ntpath.split(ftp_path_to_check)[0]  # Get parent dir of the path
    path_name = ntpath.basename(ftp_path_to_check)
    if path_name == '':  # Special case
        return FTPPathType.ERROR

    cur_loc = ftp_get_pwd(ftp_con)  # Get current location of connection in the FTP server
    if not cur_loc:
        return FTPPathType.ERROR

    if not change_ftp_dir(ftp_con, path_parent):  # ftp-cd to parent to loop on files
        return FTPPathType.ERROR

    file_list = get_file_list(ftp_con)
    if file_list is None or file_list is False:
        return FTPPathType.ERROR

    if MyGlobals.isVeryVerbose:
        print('{} Files:\n---------------\n{}\n---------------'.format(path_parent, '\n'.join(file_list)))

    path_name = str(path_name).strip().lower()
    for file_name in file_list:
        if str(file_name).strip().lower() == path_name:
            if MyGlobals.isVerbose:
                print("{} is a file".format(ftp_path_to_check))

            if not change_ftp_dir(ftp_con, cur_loc):  # Change ftp-cd back to where it was
                return FTPPathType.ERROR

            return FTPPathType.FILE

    return FTPPathType.INVALID


@with_retry_count_decorate(action_description='check if ftp-dir exists')
def ftp_check_is_dir(ftp_con, ftp_path_to_check):
    try:
        cur_loc = ftp_get_pwd(ftp_con)
        if not cur_loc:
            return None
        ftp_con.cwd(ftp_path_to_check)
        ftp_con.cwd(cur_loc)
        return True
    except ftplib.error_perm:
        if MyGlobals.isVerbose:
            print("{} is a file".format(ftp_path_to_check))
        return False


@with_retry_count_decorate(action_description='prepare ftp and os indexes')
def prepare_ftp_and_os_indexes(ftp_con, src, dest):
    if not change_ftp_dir(ftp_con, src):
        return False
    MyGlobals.mkdir_p(dest)
    if MyGlobals.isVerbose:
        print("Created dir: {}".format(dest))
    os.chdir(dest)
    return True


@with_retry_count_decorate(action_description='change local dir (cd)')
def change_local_dir(dir_path):
    os.chdir(dir_path)
    return True


@with_retry_count_decorate(action_description='delete a folder from ftp')
def ftp_delete_dir(ftp_con, dir_path):
    if MyGlobals.isVerbose:
        print('Attempting to delete ftp dir: {}'.format(dir_path))
    ftp_con.rmd(dir_path)
    if MyGlobals.isVerbose:
        print('Success - deleted ftp dir: {}'.format(dir_path))
    return True


@with_retry_count_decorate(action_description='delete a file from ftp')
def ftp_delete_file(ftp_con, file_path):
    if MyGlobals.isVerbose:
        cur_loc = ftp_get_pwd(ftp_con)
        if cur_loc:
            print('Attempting to delete ftp file: {}'.format(cur_loc + '/' + file_path))
        else:
            print('Attempting to delete ftp file: {}'.format(file_path))
    ftp_con.delete(file_path)
    if MyGlobals.isVerbose:
        print('Success - deleted ftp file: {}'.format(file_path))
    return True


def download_ftp_file(ftp_con, file_name, dest_path, create_dirs=False):
    if MyGlobals.isVerbose:
        cur_loc = ftp_get_pwd(ftp_con)
        if cur_loc:
            print('Downloading file: {} to: {}'.format(cur_loc + '/' + file_name, dest_path))
        else:
            print('Downloading file: {} to: {}'.format(file_name, dest_path))
    if create_dirs:
        if not MyGlobals.mkdir_p(dest_path):
            return None

    if not change_local_dir(dest_path):
        return False

    download_result = _download_ftp_file(ftp_con, file_name, dest_path)
    if download_result and MyGlobals.isRemoveSrc:
        return ftp_delete_file(ftp_con, file_name)

    return download_result


@with_retry_count_decorate(action_description='download a file from ftp')
def _download_ftp_file(ftp_con, file, dest):
    opened_file = open(os.path.join(dest, file), "wb")
    ftp_con.retrbinary("RETR " + file, opened_file.write)
    opened_file.close()
    if MyGlobals.isVerbose:
        print('Success - downloaded file: {} to: {}'.format(ftp_con.pwd() + '/' + file, dest))
    return True


def get_file_list(ftp_con):
    cur_loc = ''
    if MyGlobals.isVerbose:
        cur_loc = ftp_get_pwd(ftp_con)
        if cur_loc:
            print("Attempting to get file list of {}".format(cur_loc))
        else:
            print("Attempting to get file list")
    file_list = _get_file_list(ftp_con)
    if file_list and MyGlobals.isVerbose:
        if cur_loc:
            print("Success - got file list")
        else:
            print("Success - got file list of: {}".format(cur_loc))

    return file_list


@with_retry_count_decorate(action_description='get file list from ftp')
def _get_file_list(ftp_con):
    try:
        return ftp_con.nlst()
    except ftp_errors_without_timeouts_errors as errorMsg:
        print('\nFailed getting file list\nError:\n{}'.format(errorMsg))
        return None


def change_ftp_dir(ftp_con, dir_path):
    if MyGlobals.isVerbose:
        print('Attempting to change ftp-dir to {}'.format(dir_path))
    return _change_ftp_dir(ftp_con, dir_path)


@with_retry_count_decorate(action_description='change ftp dir')
def _change_ftp_dir(ftp_con, dir_path):
    try:
        ftp_con.cwd(dir_path)
        return True
    except ftp_errors_without_timeouts_errors as errorMsg:
        print('\nFailed changing ftp-dir to {}\nError:\n{}'.format(dir_path, errorMsg))
        return None


def download_ftp_dir(ftp_con, ftp_src, dest):
    dest = MyGlobals.remove_trailing_slash(dest)
    ftp_src = MyGlobals.remove_trailing_slash(ftp_src)
    src_path_dir_name = MyGlobals.get_dir_name(ftp_src)

    download_result = _download_ftp_dir(ftp_con, ftp_src, dest + '/' + src_path_dir_name)

    if download_result and MyGlobals.isRemoveSrc:
        return download_result and ftp_delete_dir(ftp_con, ftp_src)
    return download_result


def _download_ftp_dir(ftp_con, ftp_src, dest):
    print('Downloading dir: "{}" to: {}'.format(ftp_src, dest))
    if not prepare_ftp_and_os_indexes(ftp_con, ftp_src, dest):
        return False

    file_list = get_file_list(ftp_con)
    if file_list is None or file_list is False:
        return False

    ftp_src_dir_name = MyGlobals.get_dir_name(ftp_src)
    print('Dir {} Files:\n  -- {}\n'.format(ftp_src_dir_name, '\n  -- '.join(file_list)))

    cur_ind = 0
    end_ind = len(file_list)
    download_process_ok = True
    while (download_process_ok and cur_ind < end_ind):
        MyGlobals.sleep_for_a_while(MyGlobals.sleepBetweenDownloadsSec_Default)
        cur_target_name = file_list[cur_ind]

        try:
            target_path = ftp_src + "/" + cur_target_name
            # Check if a directory - if so then ftp-cd to it:
            if MyGlobals.isVerbose:
                print("Checking path-type of: {}".format(target_path))
            is_dir = ftp_check_is_dir(ftp_con, target_path)
            if is_dir is None:
                print('\nFailed checking path-type of: {}'.format(target_path))
                return False
            elif is_dir:
                if MyGlobals.isVerbose:
                    print("{} is a directory".format(target_path))
                if not change_ftp_dir(ftp_con, target_path): # If it's a directory - prepare ftp cd index
                    return False
            else:
                raise ftplib.error_perm("{} is a file".format(target_path))  # If it's a file - handle it outside of 'try' statement

            download_process_ok = download_process_ok and _download_ftp_dir(ftp_con, target_path, dest + '/' + cur_target_name)  # If it's a directory - recurse
            if download_process_ok and not change_ftp_dir(ftp_con, ftp_src):
                return False

            # If got flag: --remove_src then Attempt to remove the dir after downloading it successfully
            if download_process_ok and MyGlobals.isRemoveSrc:
                download_process_ok = download_process_ok and ftp_delete_dir(ftp_con, target_path)

        except ftplib.error_perm: # If it's a file - handle it here
            # It's a file:
            download_process_ok = download_process_ok and download_ftp_file(ftp_con, cur_target_name, dest)

        cur_ind += 1

    return download_process_ok

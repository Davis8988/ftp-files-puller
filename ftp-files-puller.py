# This script pulls FTP address for new folders and files

import sys

from MyModules import MyGlobals
from MyModules import MyFtpLib
from MyModules import MyPasswordDecipher
from MyModules import MyCrontab


# Configuration global vars can be found at MyModules/MyGlobals.py

#  _____ _____ ____    ____        _ _
# |  ___|_   _|  _ \  |  _ \ _   _| | | ___ _ __
# | |_    | | | |_) | | |_) | | | | | |/ _ \ '__|
# |  _|   | | |  __/  |  __/| |_| | | |  __/ |
# |_|     |_| |_|     |_|    \__,_|_|_|\___|_|


def remove_old_crontab_jobs():
    removed_result = MyCrontab.remove_current_ftp_puller_crontab_jobs()
    if removed_result is False:
        MyGlobals.terminate_program(2)
    return


def setup_new_crontab_job():
    if not MyCrontab.setup_script_as_crontab_job():
        MyGlobals.terminate_program(2)
    MyGlobals.terminate_program(0,
                                'Success setting-up script to run as a crontab job\nIt will run automatically by the specified timing')
    return


def pull_files_dirs_from_ftp():
    # Get connection to FTP server
    ftp_con = MyFtpLib.get_ftp_connection(MyGlobals.ftpAddr, MyGlobals.ftpPort, MyGlobals.ftpActionsTimeoutSec)
    if ftp_con is None:
        MyGlobals.terminate_program(2, msg="Failed getting ftp connection to: {}:{}".format(MyGlobals.ftpAddr, MyGlobals.ftpPort))

    ftp_password = MyGlobals.ftpPassword
    # If password is hashed - attempt to decipher it
    if MyGlobals.isHashed:
        ftp_password = MyPasswordDecipher.decipher_password_hash(ftp_password)
        if ftp_password is None:
            MyGlobals.terminate_program(2)

    # Attempt to login
    if not MyFtpLib.login_to_ftp_server(ftp_con, MyGlobals.ftpUser, ftp_password):
        MyGlobals.terminate_program(2)

    # Download src path:
    download_result = MyFtpLib.download_path(ftp_con, MyGlobals.ftpSourcePath, MyGlobals.destPath)

    # Check if successful
    if not download_result:
        MyGlobals.terminate_program(2, 'FAILED - Downloading: {} to: {}'.format(MyGlobals.ftpSourcePath, MyGlobals.destPath))

    print('SUCCESS - Downloading: {} to: {}'.format(MyGlobals.ftpSourcePath, MyGlobals.destPath))
    return


def print_crontab_jobs_with_comment():
    print_result = MyCrontab.print_current_ftp_puller_crontab_jobs()
    if print_result is False:
        MyGlobals.terminate_program(2)
    return


# -- Main function --
def main():
    received_args = MyGlobals.read_command_line_args(sys.argv[1:])
    print('FTP Puller - Started')
    print('Command Line: {} {}\n'.format(sys.argv[0], received_args))

    if not MyGlobals.check_params():  # Check that params are ok
        MyGlobals.terminate_program(1)

    if MyGlobals.isPrintCronJobs:
        print_crontab_jobs_with_comment()

    if MyGlobals.isRemoveCronJobs:  # If wants to remove old/running crontab jobs
        remove_old_crontab_jobs()

    if MyGlobals.isSetupAsCronjob and MyGlobals.receivedDownloadArgs:  # Check if wants to setup this script as a crontab job
        setup_new_crontab_job()

    elif MyGlobals.receivedDownloadArgs:  # Check if wants to run this script once
        pull_files_dirs_from_ftp()  # Start downloading

    MyGlobals.terminate_program(0, 'FTP Puller - Finished')


if __name__ == '__main__':
    main()

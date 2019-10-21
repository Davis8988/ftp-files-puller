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


def main():
    received_args = MyGlobals.read_command_line_args(sys.argv[1:])
    print('Main - Started')
    print('Command Line: {} {}\n'.format(sys.argv[0], received_args))

    # Check that params are ok
    if not MyGlobals.check_params():
        MyGlobals.terminate_program(1)

    # Check if wants to setup a crontab job:
    if MyGlobals.isRunAsCronjob:
        if not MyCrontab.setup_script_as_crontab_job():
            MyGlobals.terminate_program(1)
        print('Success setting-up script to run as a crontab job')
    # Or run this script once
    else:
        # Get connection to FTP server
        ftp_con = MyFtpLib.get_ftp_connection(MyGlobals.ftpAddr, MyGlobals.ftpPort, MyGlobals.ftpActionsTimeoutSec)
        if ftp_con is None:
            MyGlobals.terminate_program(1, msg="Failed getting ftp connection to: {}:{}".format(MyGlobals.ftpAddr,
                                                                                                MyGlobals.ftpPort))

        # If password is hashed - attempt to decipher it
        if MyGlobals.isHashed:
            ftp_password = MyPasswordDecipher.decipherPasswordHash(MyGlobals.ftpPassword)
            if ftp_password is None:
                MyGlobals.terminate_program(1)

        # Attempt to login
        if not MyFtpLib.login_to_ftp_server(ftp_con, MyGlobals.ftpUser, ftp_password):
            MyGlobals.terminate_program(1)

        # Download src path:
        download_result = MyFtpLib.download_path(ftp_con, MyGlobals.ftpSourcePath, MyGlobals.destPath)

        # Start downloading files:
        if download_result:
            print('SUCCESS - Downloading: {} to: {}'.format(MyGlobals.ftpSourcePath, MyGlobals.destPath))
        else:
            MyGlobals.terminate_program(1, 'FAILED - Downloading: {} to: {}'.format(MyGlobals.ftpSourcePath,
                                                                                    MyGlobals.destPath))

    print("Main Finished")
    MyGlobals.terminate_program(0)


if __name__ == '__main__':
    main()

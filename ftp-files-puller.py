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


def execute_crontab_jobs_now():
    execute_result = MyCrontab.execute_current_ftp_puller_crontab_jobs()
    if execute_result is False:
        MyGlobals.terminate_program(2)
    return


def setup_new_crontab_job():
    if not MyCrontab.setup_script_as_crontab_job():
        MyGlobals.terminate_program(2)
    return


def start_crontab_scheduler():
    if not MyCrontab.start_crontab_scheduler():
        MyGlobals.terminate_program(2)
    MyGlobals.terminate_program(0, 'Finished running crontab scheduler for user: {}'.format(MyGlobals.crontab_user))
    return

# Start downloading
def pull_files_dirs_from_ftp():
    # Get connection to FTP server
    ftp_con = MyFtpLib.get_ftp_connection(MyGlobals.ftpAddr, MyGlobals.ftpPort, MyGlobals.ftpActionsTimeoutSec)
    if ftp_con is None:
        MyGlobals.terminate_program(2, msg="\nFailed getting ftp connection to: {}:{}".format(MyGlobals.ftpAddr,
                                                                                              MyGlobals.ftpPort))

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
        MyGlobals.terminate_program(2, '\nFAILED - Downloading: {} to: {}'.format(MyGlobals.ftpSourcePath,
                                                                                  MyGlobals.destPath))

    print('SUCCESS - Downloading: {} to: {}'.format(MyGlobals.ftpSourcePath, MyGlobals.destPath))
    return


# Prints all installed crontab jobs with given job-comment
#   If no job-comment given - then default one(defined in MyGlobals) is used
def print_crontab_jobs_with_comment():
    print_result = MyCrontab.print_current_ftp_puller_crontab_jobs()
    if print_result is False:
        MyGlobals.terminate_program(2)
    return


# Prints starting info
def print_start_info():
    received_args = MyGlobals.read_command_line_args(sys.argv[1:])
    print('{}  - FTP Puller - Started'.format(MyGlobals.get_current_date_and_time_str()))

    if MyGlobals.isVerbose:
        print('Command Line: {} {}\n'.format(sys.argv[0], received_args))

    if MyGlobals.isVeryVerbose:
        print('Configuration:\n{}'.format(MyGlobals.get_cur_configuration_str()))


# Checks if user wants to launch following tasks (independently):
# - print current defined crontab jobs
# - remove crontab jobs
# - test crontab jobs  [without setting up new ones. If do wants to setup new jobs,
#                        then first set them up, then check again if watns to test
#                        the newly defined jobs]
# - setup new crontab jobs
def check_crontab_helper_tasks():
    if MyGlobals.isPrintCronJobs:
        print_crontab_jobs_with_comment()

    if MyGlobals.isRemoveCronJobs:  # If wants to remove old/running crontab jobs
        remove_old_crontab_jobs()

    if MyGlobals.isTestJobsNow and not MyGlobals.isSetupAsCronjob:  # If wants to test crontab jobs, without setting new jobs - then execute current defined jobs now
        execute_crontab_jobs_now()

    if MyGlobals.isSetupAsCronjob and MyGlobals.receivedDownloadArgs:  # Check if wants to setup this script as a crontab job
        setup_new_crontab_job()
        if MyGlobals.isTestJobsNow:  # If wants to test new defined jobs now - then execute them
            execute_crontab_jobs_now()

        start_crontab_scheduler()  # After setup crontab job - start the scheduler and remain here [doesn't return from this function]


def check_params():
    if not MyGlobals.check_params():  # Check that params are ok
        MyGlobals.terminate_program(1)


# -- Main function --
def main():
    print_start_info()
    check_params()

    if MyGlobals.isSetupAsCronjob:
        check_crontab_helper_tasks()  # if '--setup_as_crontab_job' flag received - then main doesn't continue further from here. The download part occurs inside.
    elif MyGlobals.receivedDownloadArgs:
        pull_files_dirs_from_ftp()  # if just wants to downoad without using crontab helper-tasks - then just go ahead and download now

    # If got here - Finish successful:
    MyGlobals.terminate_program(0)


main()

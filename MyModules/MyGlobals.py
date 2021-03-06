# Contains global functions to be used in other scripts
import time
import errno
import os
import sys
import ntpath
import re
import getopt
import getpass

from pyfiglet import Figlet

scriptName = ntpath.basename(sys.argv[0])
scriptPath = sys.path[0]

# Defaults
ftpPort_Default = 21
ftpActionsTimeoutSec_Default = 8
ftpRetriesCount_Default = 10
sleepForBetweenActions_Default = 3
sleepBetweenDownloads_Default = 0.05
crontabJobComment_Default = 'ftp-files-puller crontab job'

ftpAddr = os.getenv('FTP_ADDRESS', '')
ftpPort = os.getenv('FTP_PORT', ftpPort_Default)
ftpUser = os.getenv('FTP_USER', '')
ftpPassword = os.getenv('FTP_PASSWORD', '')
ftpRetriesCount = os.getenv('FTP_RETRIES_COUNT', ftpRetriesCount_Default)
ftpSourcePath = os.getenv('FTP_SOURCE_PATH', '')
destPath = os.getenv('FTP_DEST_PATH', '')
ftpEncryptKey = os.getenv('FTP_ENCRYPT_KEY', '')
passwordEncrypterExe = os.getenv('FTP_ENCRYPTER_PATH', '')
ftpActionsTimeoutSec = os.getenv('FTP_ACTIONS_TIMEOUT', ftpActionsTimeoutSec_Default)
isRemoveSrc = False
isHashed = False
isSilent = False
isVerbose = False
isVeryVerbose = False

# Python-Crontab
crontab_user = os.getenv('CRONTAB_USER', getpass.getuser())
crontab_time = os.getenv('CRONTAB_TIME', '')
crontab_comment = os.getenv('CRONTAB_COMMENT', crontabJobComment_Default)
isSetupAsCronjob = False
isEveryReboot = False
isRemoveCronJobs = False
isPrintCronJobs = False

# For check if got args for downloading
receivedDownloadArgs = False


def read_command_line_args(argv):
    # Attempt to prepare a reading params object
    try:
        opts, args = getopt.getopt(argv, "ha:o:u:p:t:r:s:d:k:e:", ["ftp_addr=",
                                                                   "ftp_port=",
                                                                   "ftp_user=",
                                                                   "ftp_password=",
                                                                   "ftp_timeout=",
                                                                   "ftp_retries=",
                                                                   "src=",
                                                                   "dest=",
                                                                   "key=",
                                                                   "encrypter_path=",
                                                                   "remove_src",
                                                                   "hashed",
                                                                   "silent",
                                                                   "verbose",
                                                                   "very_verbose",
                                                                   "crontab_user=",
                                                                   "crontab_time=",
                                                                   "crontab_comment=",
                                                                   "setup_as_crontab_job",
                                                                   "every_reboot",
                                                                   "remove_crontab_jobs",
                                                                   "print_crontab_jobs",
                                                                   "help"])
    except getopt.GetoptError as error_msg:
        terminate_program(1, "\nError preparing 'getopt' object:\n" + str(error_msg))

    #  Args to be populated:
    global ftpAddr
    global ftpPort
    global ftpUser
    global ftpPassword
    global ftpActionsTimeoutSec
    global ftpRetriesCount
    global ftpSourcePath
    global destPath
    global ftpEncryptKey
    global passwordEncrypterExe
    global isRemoveSrc
    global isHashed
    global isSilent
    global isVerbose
    global isVeryVerbose
    global crontab_user
    global crontab_time
    global crontab_comment
    global isSetupAsCronjob
    global isEveryReboot
    global isRemoveCronJobs
    global isPrintCronJobs

    received_args = ''

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            help_str = get_help_string()
            terminate_program(0, msg=help_str)
        elif opt in ("-a", "--ftp_addr"):
            ftpAddr = arg
        elif opt in ("-o", "--ftp_port"):
            ftpPort = arg
        elif opt in ("-u", "--ftp_user"):
            ftpUser = arg
        elif opt in ("-p", "--ftp_password"):
            ftpPassword = arg
            received_args += '{} {} '.format("-p", re.sub(".", "*", arg))
            continue
        elif opt in ("-t", "--ftp_timeout"):
            ftpActionsTimeoutSec = arg
        elif opt in ("-r", "--ftp_retries"):
            ftpRetriesCount = arg
        elif opt in ("-s", "--src"):
            ftpSourcePath = arg
        elif opt in ("-d", "--dest"):
            destPath = arg
        elif opt in ("-k", "--encrypt_key"):
            received_args += '{} {} '.format("-k", re.sub(".", "*", arg))
            ftpEncryptKey = arg
        elif opt in ("-e", "--encrypter_path"):
            passwordEncrypterExe = arg
        elif opt in ["--remove_src"]:
            isRemoveSrc = True
        elif opt in ["--hashed"]:
            isHashed = True
        elif opt in ["--silent"]:
            isSilent = True
        elif opt in ["--verbose"]:
            isVerbose = True
        elif opt in ["--very_verbose"]:
            isVerbose = True
            isVeryVerbose = True
        elif opt in ("--crontab_user"):
            crontab_user = arg
        elif opt in ("--crontab_time"):
            crontab_time = arg
        elif opt in ("--crontab_comment"):
            crontab_comment = arg
        elif opt in ["--setup_as_crontab_job"]:
            isSetupAsCronjob = True
        elif opt in ["--every_reboot"]:
            isEveryReboot = True
        elif opt in ["--remove_crontab_jobs"]:
            isRemoveCronJobs = True
        elif opt in ["--print_crontab_jobs"]:
            isPrintCronJobs = True
        else:
            error_msg = "Error - unexpected arg: '{}'".format(arg)
            terminate_program(1, error_msg)

        # Check if long arg with a value (e.g --ftp_addr=www.google.com)
        if '--' in opt and arg:
            received_args += '{}={} '.format(opt, arg)
        else:
            received_args += '{} {} '.format(opt, arg)

    return received_args


def check_params():
    global ftpAddr
    global ftpPort
    global ftpUser
    global ftpPassword
    global ftpActionsTimeoutSec
    global ftpRetriesCount
    global ftpSourcePath
    global destPath
    global ftpEncryptKey
    global passwordEncrypterExe
    global crontab_user
    global crontab_time
    global crontab_comment
    global isSetupAsCronjob
    global isRemoveCronJobs
    global isPrintCronJobs
    global receivedDownloadArgs

    if isVerbose:
        print("Validating params")

    # If at least one is not empty - then True
    receivedDownloadArgs = bool(ftpAddr or ftpUser or ftpPassword or ftpSourcePath or destPath)

    # Check what user wants to do and validate params accordingly
    if receivedDownloadArgs:
        if not (ftpAddr and ftpUser and ftpPassword and ftpSourcePath and destPath):  # Needs to provide all the downloading args
            print("Please provide the following:\n-a ftp-address -u user -p pass -s src path -d dest path")
            return False

        # If provided hashed password - then needs to provide a key or the passwords-encrypter.exe application file path
        if isHashed and not (ftpEncryptKey or passwordEncrypterExe):
            print("--hashed flag detected but missing encryption key arg: [-k]  OR  password-encrypter.exe arg: [-e] path")
            return False

        # If wants to setup a crontab job - then needs to provide crontab time arg too
        if isSetupAsCronjob and not crontab_time:
            print("--setup_as_crontab_job flag detected but missing arg --crontab_time= ")
            return False

        # Convert params types:
        try:
            ftpPort = int(ftpPort)
            ftpActionsTimeoutSec = int(ftpActionsTimeoutSec)
            ftpRetriesCount = int(ftpRetriesCount)
            ftpAddr = str(ftpAddr)
            ftpUser = str(ftpUser)
            ftpPassword = str(ftpPassword)
            ftpSourcePath = str(ftpSourcePath)
            destPath = str(destPath)
            ftpEncryptKey = str(ftpEncryptKey)
            passwordEncrypterExe = str(passwordEncrypterExe)
            crontab_user = str(crontab_user)
            crontab_time = str(crontab_time)
            crontab_comment = str(crontab_comment)
        except BaseException as errorMsg:
            print('Failed validating params.\nError:\n{}'.format(errorMsg))
            return False

    elif isRemoveCronJobs:
        pass
    elif isPrintCronJobs:
        pass
    else:  # If didn't receive download args AND didn't receive remove-crontab-job arg AND didn't receive print-crontab-jobs arg  -  then nothing to do. Missing args.
        print("No args were given, and no env vars set.\nPlease provide the following:\n-a ftp-address -u user -p pass -s src path -d dest path")
        return False

    if isVeryVerbose:
        print("Success - params are ok")

    return True


def get_dir_name(dir_path):
    return os.path.basename(os.path.normpath(dir_path))


def sleep_for_a_while(sleep_sec):
    try:
        if isVeryVerbose:
            print('Sleeping for {} seconds'.format(sleep_sec))
        time.sleep(sleep_sec)
        return True
    except BaseException as errorMsg:
        print('Failed sleeping for {} seconds\nError:\n{}'.format(sleep_sec, errorMsg))
        return False


def remove_trailing_slash(path):
    if (path[len(path) - 1] == '/') or (path[len(path) - 1] == '\\'):
        return path[:len(path) - 1]
    return path


def terminate_program(exit_code, msg=''):
    if msg:
        print(msg)
    if exit_code == 1:
        print('Aborting with error..\n{}'.format(get_help_string()))
    elif exit_code == 2:
        print('Aborting with error..')
    sys.exit(exit_code)


def mkdir_p(path):
    try:
        os.makedirs(path)
        return True
    except OSError as errorMsg:
        if errorMsg.errno == errno.EEXIST and os.path.isdir(path):
            return True
        else:
            print('Failed creating dir: {}\nError:\n{}'.format(path, errorMsg))
            return None


def get_title_string(font, title):
    custom_fig = Figlet(font=font)
    return custom_fig.renderText(title)


def get_help_string():
    global scriptName

    # Prepare title:
    font = 'small'
    title = 'FTP Puller'
    help_str = get_title_string(font, title)

    # Prepare help string
    help_str += "\n"
    help_str += "This tool pulls files/dirs from an FTP server to given path.\n\n"
    help_str += "Usage:\n"
    help_str += scriptName + " -a <server> -u <user> -p <pass> -s <src file/dir path> -d <dest dir path> [flags] \n\n"

    help_str += "FTP:\n"
    help_str += " -a, --ftp_addr=          : FTP-Server name or ip.\n"
    help_str += " -o, --ftp_port=          : FTP-Port to connect to. Default is {}\n".format(ftpPort_Default)
    help_str += " -u, --ftp_user=          : FTP-User to connect with.\n"
    help_str += " -p, --ftp_password=      : FTP-Password to connect. If hashed add flag --hash.\n"
    help_str += " -t, --ftp_timeout=       : FTP actions timeout in seconds. Default is: {}\n".format(ftpActionsTimeoutSec_Default)
    help_str += " -r, --ftp_retries=       : FTP actions retries count when timeout expires. Default is: {}\n\n".format(ftpRetriesCount_Default)

    help_str += "Paths:\n"
    help_str += " -s, --src=               : Source FTP path of file or dir to pull.\n"
    help_str += " -d, --dest=              : Local/network destination dir path.\n\n"

    help_str += "Encryption:\n"
    help_str += " -k, --encrypt_key=       : When using hashed password, use this key to interpret it.\n"
    help_str += " -e, --encrypter_path=    : Passwords-encrypter.exe path to interpret hashed password instead of key.\n\n"

    help_str += "Flags:\n"
    help_str += " --remove_src             : Remove pulled source file/dir if successful.\n"
    help_str += " --hashed                 : Indicate that password is hashed and it needs to be deciphered (using a key[-k] or encrypter[-e]).\n"
    help_str += " --silent                 : Silent mode - no user interaction.\n"
    help_str += " --verbose                : More output on each action.\n"
    help_str += " --very_verbose           : A lot more output on each action.\n\n"

    help_str += "Crontab:\n"
    help_str += " --setup_as_crontab_job   : Setup script execution as a crontab job.\n"
    help_str += " --crontab_user=          : Crontab job user. Default is current logged on user.\n"
    help_str += " --crontab_time=          : Crontab time.\n"
    help_str += " --crontab_comment=       : Crontab job comment. Default is '{}'.\n".format(crontabJobComment_Default)
    help_str += " --every_reboot           : Enable job start on every reboot.\n"
    help_str += " --print_crontab_jobs     : Print all crontab jobs with comment provided by '--crontab_comment=' for provided user.\n"
    help_str += " --remove_crontab_jobs    : Remove all crontab jobs with comment provided by '--crontab_comment=' for provided user. Used for cancelling old/running jobs.\n\n"

    help_str += "Help:\n"
    help_str += " -h, --help               : print this help message and exit\n\n"

    help_str += "Default values read from environment variables on startup:\n"
    help_str += "  -a, --ftp_addr=         :  [FTP_ADDRESS]\n"
    help_str += "  -o, --ftp_port=         :  [FTP_PORT]\n"
    help_str += "  -u, --ftp_user=         :  [FTP_USER]\n"
    help_str += "  -p, --ftp_password=     :  [FTP_PASSWORD]\n"
    help_str += "  -t, --ftp_timeout=      :  [FTP_ACTIONS_TIMEOUT]\n"
    help_str += "  -r, --ftp_retries=      :  [FTP_RETRIES_COUNT]\n"
    help_str += "  -s, --src=              :  [FTP_SOURCE_PATH]\n"
    help_str += "  -d, --dest=             :  [FTP_DEST_PATH]\n"
    help_str += "  -k, --key=              :  [FTP_ENCRYPT_KEY]\n"
    help_str += "  -e, --encrypter_path=   :  [FTP_ENCRYPTER_PATH]\n"
    help_str += "  --crontab_user=         :  [CRONTAB_USER]\n"
    help_str += "  --crontab_time=         :  [CRONTAB_TIME]\n"
    help_str += "  --crontab_comment=      :  [CRONTAB_COMMENT]\n\n"

    help_str += "Examples\n"
    help_str += " Pull dir:         " + scriptName + " -a 192.168.12.56 -u myUser -p myPass123 -s /david_files/bash_scripts -d /usr/scripts --silent \n"
    help_str += " Pull file:        " + scriptName + " -a 192.168.12.56 -u myUser -p myPass123 -s /docs/usernames.txt -d /usr/docs --silent \n"
    help_str += " Pull dir [WIN]:   " + scriptName + " -a 192.168.12.56 -u myUser -p myPass123 -s /docs/usernames.txt -d C:\\Users\\david\\Desktop --silent \n"
    help_str += " Hashed Passwd:    " + scriptName + " -a 192.168.12.56 -u myUser -p 21f8j9f8jw9sdui -k 2u3r9dewfjf -s /docs/usernames.txt -d C:\\Users\\david\\Desktop --hashed --silent \n"
    help_str += " Hashed Passwd 2:  " + scriptName + " -a 192.168.12.56 -u myUser -p 21f8j9f8jw9sdui -e D:\\PasswordsEncrypter\\passwords-encrypter.exe -s /docs/usernames.txt -d C:\\Users\\david\\Desktop --hashed --silent \n"

    return help_str

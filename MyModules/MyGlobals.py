# Contains global functions to be used in other scripts
import time
import errno
import os
import sys
import ntpath
import re
import getopt

from pyfiglet import Figlet

scriptName = ntpath.basename(sys.argv[0])

# Defaults
ftpPort_Default = 21
ftpActionsTimeoutSec_Default = 8
ftpRetriesCount_Default = 10
sleepForBetweenActions_Default = 3
sleepBetweenDownloads_Default = 0.05

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
crontab_user = os.getenv('CRONTAB_USER', '')
crontab_time = os.getenv('CRONTAB_TIME', '')
crontab_comment = os.getenv('CRONTAB_COMMENT', '')
isRunAsCronjob = False
isEveryReboot = False


def get_dir_name(dirPath):
    return os.path.basename(os.path.normpath(dirPath))


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
    help_str += " -a, --ftp_addr=         : FTP-Server name or ip.\n"
    help_str += " -o, --ftp_port=         : FTP-Port to connect to. Default is {}\n".format(ftpPort_Default)
    help_str += " -u, --ftp_user=         : FTP-User to connect with.\n"
    help_str += " -p, --ftp_password=     : FTP-Password to connect. If hashed add flag --hash.\n"
    help_str += " -t, --ftp_timeout=      : FTP actions timeout in seconds. Default is: {}\n".format(ftpActionsTimeoutSec_Default)
    help_str += " -r, --ftp_retries=      : FTP actions retries count when timeout expires. Default is: {}\n\n".format(ftpRetriesCount_Default)

    help_str += "Paths:\n"
    help_str += " -s, --src=              : Source FTP path of file or dir to pull.\n"
    help_str += " -d, --dest=             : Local/network destination dir path.\n\n"

    help_str += "Encryption:\n"
    help_str += " -k, --encrypt_key=      : When using hashed password, use this key to interpret it.\n"
    help_str += " -e, --encrypter_path=   : Passwords-encrypter.exe path to interpret hashed password instead of key.\n\n"

    help_str += "Flags:\n"
    help_str += " --remove_src            : Remove pulled source file/dir if successful.\n"
    help_str += " --hashed                : Indicate that password is hashed and it needs to be deciphered (using a key[-k] or encrypter[-e]).\n"
    help_str += " --silent                : Silent mode - no user interaction.\n"
    help_str += " --verbose               : More output on each action.\n"
    help_str += " --very_verbose          : A lot more output on each action.\n\n"

    help_str += "Crontab:\n"
    help_str += " --run_as_cronjob        : Add run of this script as a cronjob.\n"
    help_str += " --every_reboot          : Enable job to start on every reboot.\n"
    help_str += " --crontab_user=         : Crontab job user.\n"
    help_str += " --crontab_time=         : Crontab time.\n"
    help_str += " --crontab_comment=      : Crontab job comment.\n\n"

    help_str += "Help:\n"
    help_str += " -h, --help              : print this help message and exit\n\n"

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
    global isRunAsCronjob

    if isVerbose:
        print("Validating params")

    # Must have at least address, user, pass, src and dest paths
    if not (ftpAddr and ftpUser and ftpPassword and ftpSourcePath and destPath):
        error_msg = "Please provide the following:\n-a ftp-address -u user -p pass -s src path -d dest path"
        terminate_program(1, error_msg)

    # If hashed - then needs a key or the passwords-encrypter.exe file path
    if isHashed and not (ftpEncryptKey or passwordEncrypterExe):
        error_msg = "--hashed flag detected but missing encryption key [-k] OR password-encrypter.exe [-e] path"
        terminate_program(1, error_msg)

    if isRunAsCronjob and not (crontab_user or crontab_time):
        error_msg = "--run_as_cronjob flag detected but missing --crontab_user= OR --crontab_time="
        terminate_program(1, error_msg)

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


    if isVeryVerbose:
        print("Success - params are ok")
    return True


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
                                                                   "run_as_cronjob",
                                                                   "every_reboot",
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
    global isRunAsCronjob
    global isEveryReboot

    received_args = ''

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            helpStr = get_help_string()
            terminate_program(0, msg=helpStr)
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
        elif opt in ["--run_as_cronjob"]:
            isRunAsCronjob = True
        elif opt in ["--every_reboot"]:
            isEveryReboot = True
        else:
            error_msg = "Error - unexpected arg: '{}'".format(arg)
            terminate_program(1, error_msg)

        received_args += '{} {} '.format(opt, arg)

    return received_args


def terminate_program(exit_code, msg=''):
    print(msg)
    if exit_code != 0:
        print('Aborting..\n{}'.format(get_help_string()))
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

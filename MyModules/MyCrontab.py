# Contains functions for creating new crontab job for python scripts

from crontab import CronTab
from MyModules import MyGlobals


# Fields are: Minute Hour Day Month Day_of_the_Week
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday; 7 is also Sunday on some systems)
# │ │ │ │ │
# │ │ │ │ │
# │ │ │ │ │
# * * * * *  command to execute


def setup_script_as_crontab_job():
    command_str = create_crontab_command()
    time_str = MyGlobals.crontab_time
    user_to_use = MyGlobals.crontab_user
    comment_str = MyGlobals.crontab_comment
    is_every_reboot = MyGlobals.isEveryReboot

    crontab_job = prepare_crontab_job(user_to_use, time_str, command_str, comment_str, is_every_reboot)
    if not create_crontab_job(crontab_job):
        return False


def create_crontab_job(crontab_job):
    try:
        crontab_job.write()
        return True
    except BaseException as errorMsg:
        print('Failed creating crontab job\nError:\n{}'.format(errorMsg) )
        return False


def prepare_crontab_job(user_to_use, time_str, command_str, comment_str='', is_every_reboot=False):
    try:
        cron = CronTab(user=user_to_use)
        crontab_job = cron.new(command=command_str, comment=comment_str)
        crontab_job.setall(time_str)
        if is_every_reboot:
            crontab_job.every_reboot()
        return crontab_job
    except BaseException as errorMsg:
        print('Failed creating crontab job to run:\n - Command: {}'
                                                 '\n - Time: {}'
                                                 '\n - User: {}'
                                                 '\nError:\n{}'.format(command_str, time_str, user_to_use, errorMsg))
        return None


def create_crontab_command():
    script_name = MyGlobals.scriptName

    # FTP:
    args = '-a {} '.format(MyGlobals.ftpAddr)
    args += '-o {} '.format(MyGlobals.ftpPort)
    args += '-u {} '.format(MyGlobals.ftpUser)
    args += '-p {} '.format(MyGlobals.ftpPassword)
    args += '-t {} '.format(MyGlobals.ftpActionsTimeoutSec)
    args += '-r {} '.format(MyGlobals.ftpRetriesCount)

    # Paths:
    args += '-s {} '.format(MyGlobals.ftpSourcePath)
    args += '-d {} '.format(MyGlobals.destPath)

    # Encryption:
    if MyGlobals.ftpEncryptKey:
        args += '-k {} '.format(MyGlobals.ftpEncryptKey)
    if MyGlobals.passwordEncrypterExe:
        args += '-e {} '.format(MyGlobals.passwordEncrypterExe)

    # Flags:
    if MyGlobals.isRemoveSrc:
        args += '--remove_src '
    if MyGlobals.isHashed:
        args += '--hashed '
    if MyGlobals.isSilent:
        args += '--silent '
    if MyGlobals.isVerbose:
        args += '--verbose '
    if MyGlobals.isVeryVerbose:
        args += '--very_verbose '

    full_command = script_name + ' ' + args
    return full_command

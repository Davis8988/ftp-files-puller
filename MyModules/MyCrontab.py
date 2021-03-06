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


def remove_current_ftp_puller_crontab_jobs():
    comment_str = MyGlobals.crontab_comment
    user_to_use = MyGlobals.crontab_user

    if MyGlobals.isVerbose:
        print("Removing all crontab jobs with comment: '{}' for user: '{}'".format(comment_str, user_to_use))

    cron = connect_cron_for_user(user_to_use)
    if cron is None:
        return False

    if len(cron) == 0:
        print('No crontab jobs found')
        return True

    removed_count = remove_jobs_with_comment(cron, comment_str)
    if removed_count is False:
        return False

    if not write_crontab_jobs(cron):
        return False

    print('Success removing {} crontab jobs'.format(removed_count))
    return True


def print_current_ftp_puller_crontab_jobs():
    comment_str = MyGlobals.crontab_comment
    user_to_use = MyGlobals.crontab_user

    if MyGlobals.isVerbose:
        print("Printing all crontab jobs with comment: '{}' for user: '{}'".format(comment_str, user_to_use))

    cron = connect_cron_for_user(user_to_use)
    if cron is None:
        return False

    if len(cron) == 0:
        print('No crontab jobs found')
        return True

    return print_jobs_with_comment(cron, comment_str)


def setup_script_as_crontab_job():
    command_str = create_crontab_command()
    comment_str = MyGlobals.crontab_comment
    time_str = MyGlobals.crontab_time
    user_to_use = MyGlobals.crontab_user
    is_every_reboot = MyGlobals.isEveryReboot

    cron = connect_cron_for_user(user_to_use)
    if cron is None:
        return False

    if not add_crontab_job(cron, user_to_use, time_str, command_str, comment_str, is_every_reboot):
        return False

    if not write_crontab_jobs(cron):
        return False

    return True


def print_jobs_with_comment(cron, comment_str):

    try:
        for job in cron:
            print('{}\n'.format(job))

        if MyGlobals.isVeryVerbose:
            print('Finished printing all crontab jobs with comment: {}')

        return True
    except BaseException as errorMsg:
        print('Failed to print all crontab jobs with comment: {}\nError:\n{}'.format(comment_str, errorMsg))
        return False


def remove_jobs_with_comment(cron, comment_str):

    before_jobs_count = len(cron)
    try:
        if MyGlobals.isVeryVerbose:
            print('Jobs count before removing: {}'.format(before_jobs_count))
        cron.remove_all(comment=comment_str)
        after_jobs_count = len(cron)
        if MyGlobals.isVeryVerbose:
            print('Jobs count after removing: {}'.format(after_jobs_count))
        total_jobs_removed = before_jobs_count - after_jobs_count
        return total_jobs_removed
    except BaseException as errorMsg:
        print('Failed to remove all crontab jobs with comment: {}\nError:\n{}'.format(comment_str, errorMsg))
        return False


def write_crontab_jobs(cron):
    if MyGlobals.isVerbose:
        print('Writing crontab settings to the system')
    try:
        cron.write()
        return True
    except BaseException as errorMsg:
        print('Failed creating crontab job\nError:\n{}'.format(errorMsg))
        return False


def connect_cron_for_user(user_to_use):
    if MyGlobals.isVerbose:
        print('Connecting to crontab of user: {}'.format(user_to_use))
    try:
        return CronTab(user=user_to_use)
    except BaseException as errorMsg:
        print('Failed to connect to crontab for user: {}\nError:\n{}'.format(user_to_use, errorMsg))
        return None


def add_crontab_job(cron, user_to_use, time_str, command_str, comment_str='', is_every_reboot=False):
    if MyGlobals.isVerbose:
        print('Adding new crontab job:'
              '\n - Command: {}'
              '\n - Time: {}'
              '\n - User: {}'.format(command_str, time_str, user_to_use))
    try:
        crontab_job = cron.new(command=command_str, comment=comment_str)
        crontab_job.setall(time_str)
        if is_every_reboot:
            crontab_job.every_reboot()

        if MyGlobals.isVerbose:
            print('Success adding new crontab job')
        return True
    except BaseException as errorMsg:
        print('Failed adding new crontab job:'
              '\n - Command: {}'
              '\n - Time: {}'
              '\n - User: {}'
              '\nError:\n{}'.format(command_str, time_str, user_to_use, errorMsg))
        return False


def create_crontab_command():
    full_script_path = MyGlobals.scriptPath + '/' + MyGlobals.scriptName

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

    full_command = 'python3 "' + full_script_path + '" ' + args
    return full_command

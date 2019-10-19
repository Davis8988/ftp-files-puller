# Contains functions for creating new crontab job for python scripts

from crontab import CronTab

# Fields are: Minute Hour Day Month Day_of_the_Week
# ┌───────────── minute (0 - 59)
# │ ┌───────────── hour (0 - 23)
# │ │ ┌───────────── day of month (1 - 31)
# │ │ │ ┌───────────── month (1 - 12)
# │ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday;
# │ │ │ │ │                                       7 is also Sunday on some systems)
# │ │ │ │ │
# │ │ │ │ │
# * * * * *  command to execute

def create_crontab_job(user_to_use, time_str, command_str, comment_str='', is_every_reboot=False):
    try:
        cron = CronTab(user=user_to_use)
        crontab_job = cron.new(command=command_str, comment=comment_str)
        crontab_job.setall(time_str)
        if is_every_reboot:
            crontab_job.every_reboot()
        crontab_job.write()
        return True
    except BaseException as errorMsg:
        print('Failed creating crontab job to run:\n - Command: {}\n - Time: {}\nError:\n{}'.format(command_str, time_str, errorMsg))
        return False



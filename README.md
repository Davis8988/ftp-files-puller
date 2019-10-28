# FTP-Files-Puller
Python script for pulling files/dirs from an FTP server to local/remote path

<pre>

This tool pulls files/dirs from an FTP server to given path.

Usage:
ftp-files-puller.py -a <server> -u <user> -p <pass> -s <src file/dir path> -d <dest dir path> [flags]

FTP:
 -a, --ftp_addr=          : FTP-Server name or ip.
 -o, --ftp_port=          : FTP-Port to connect to. Default is 21
 -u, --ftp_user=          : FTP-User to connect with.
 -p, --ftp_password=      : FTP-Password to connect. If hashed add flag --hash.
 -t, --ftp_timeout=       : FTP actions timeout in seconds. Default is: 8
 -r, --ftp_retries=       : FTP actions retries count when timeout expires. Default is: 10

Paths:
 -s, --src=               : Source FTP path of file or dir to pull.
 -d, --dest=              : Local/network destination dir path.

Encryption:
 -k, --encrypt_key=       : When using hashed password, use this key to interpret it.
 -e, --encrypter_path=    : Passwords-encrypter.exe path to interpret hashed password instead of key.

Flags:
 --remove_src             : Remove pulled source file/dir if successful.
 --hashed                 : Indicate that password is hashed and it needs to be deciphered (using a key[-k] or encrypter[-e]).
 --silent                 : Silent mode - no user interaction.
 --verbose                : More output on each action.
 --very_verbose           : A lot more output on each action.

Crontab:
 --setup_as_crontab_job   : Setup script execution as a crontab job.
 --crontab_user=          : Crontab job user. Default is current logged on user.
 --crontab_time=          : Crontab time.
 --crontab_comment=       : Crontab job comment. Default is 'ftp-files-puller crontab job'.
 --every_reboot           : Enable job start on every reboot.
 --print_crontab_jobs     : Print all crontab jobs with comment provided by '--crontab_comment=' for provided user.
 --remove_crontab_jobs    : Remove all crontab jobs with comment provided by '--crontab_comment=' for provided user. Used for cancelling old/running jobs.

Help:
 -h, --help               : print this help message and exit

Default values read from environment variables on startup:
  -a, --ftp_addr=         :  [FTP_ADDRESS]
  -o, --ftp_port=         :  [FTP_PORT]
  -u, --ftp_user=         :  [FTP_USER]
  -p, --ftp_password=     :  [FTP_PASSWORD]
  -t, --ftp_timeout=      :  [FTP_ACTIONS_TIMEOUT]
  -r, --ftp_retries=      :  [FTP_RETRIES_COUNT]
  -s, --src=              :  [FTP_SOURCE_PATH]
  -d, --dest=             :  [FTP_DEST_PATH]
  -k, --key=              :  [FTP_ENCRYPT_KEY]
  -e, --encrypter_path=   :  [FTP_ENCRYPTER_PATH]
  --crontab_user=         :  [CRONTAB_USER]
  --crontab_time=         :  [CRONTAB_TIME]
  --crontab_comment=      :  [CRONTAB_COMMENT]

Examples
 Pull dir:         ftp-files-puller.py -a 192.168.12.56 -u myUser -p myPass123 -s /david_files/bash_scripts -d /usr/scripts --silent
 Pull file:        ftp-files-puller.py -a 192.168.12.56 -u myUser -p myPass123 -s /docs/usernames.txt -d /usr/docs --silent
 Pull dir [WIN]:   ftp-files-puller.py -a 192.168.12.56 -u myUser -p myPass123 -s /docs/usernames.txt -d C:\Users\david\Desktop --silent
 Hashed Passwd:    ftp-files-puller.py -a 192.168.12.56 -u myUser -p 21f8j9f8jw9sdui -k 2u3r9dewfjf -s /docs/usernames.txt -d C:\Users\david\Desktop --hashed --silent
 Hashed Passwd 2:  ftp-files-puller.py -a 192.168.12.56 -u myUser -p 21f8j9f8jw9sdui -e D:\PasswordsEncrypter\passwords-encrypter.exe -s /docs/usernames.txt -d C:\Users\david\Desktop --hashed --silent

</pre>
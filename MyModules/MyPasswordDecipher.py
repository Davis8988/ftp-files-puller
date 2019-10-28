# Contains functions for deciphering passwords hashes to be used by other scripts
import subprocess
import os

from MyModules import MyGlobals as MyGlobals
from cryptography.fernet import Fernet

encodingType = 'utf-8'


def get_password_from_password_encrypter_exe(password_encrypter_exe, password_hash):
    if MyGlobals.isVerbose:
        print("Deciphering password hash using encrypter-exe: {}".format(password_encrypter_exe))
    # noinspection PyBroadException
    try:
        result = subprocess.run("{} -i {} -d -s -r".format(password_encrypter_exe, password_hash), capture_output=True)
    except BaseException as errorMsg:
        print("Failed excuting subprocess of encrypter-exe: {}\nto decipher password from given hash: {}\nError:\n{}".format(password_encrypter_exe, password_hash, errorMsg))
        return None
    if not result.returncode == 0:
        return None

    if MyGlobals.isVeryVerbose:
        print("Success - deciphered password hash using encrypter-exe")

    global encodingType
    sub_proc_output = result.stdout
    if type(sub_proc_output) == bytes:
        sub_proc_output = bytes.decode(sub_proc_output, encodingType)
    return sub_proc_output.strip()


def decrypt_password(password_to_decrypt, key):

    cipher_suite = Fernet(key)
    try:
        if not type(password_to_decrypt) == bytes:
            password_to_decrypt = str(password_to_decrypt).encode()
        uncipher_text = (cipher_suite.decrypt(password_to_decrypt))
        plain_text = bytes(uncipher_text).decode("utf-8")
        if MyGlobals.isVeryVerbose:
            print("Success - deciphered password hash")
        return plain_text
    except BaseException as errorMsg:
        print("Failed deciphering password hash\nError:\n{}".format(errorMsg))
        return None


def decipher_password_hash(password):
    if MyGlobals.isVerbose:
        print("Attempting to decipher password hash")

    # Use password-encrypter.exe
    if MyGlobals.passwordEncrypterExe and os.path.isfile(MyGlobals.passwordEncrypterExe):
        return get_password_from_password_encrypter_exe(MyGlobals.passwordEncrypterExe, password)

    # passwordEncrypterExe doesn't exist (None or wrong path doesn't matter.)
    #  so use the key and lib cryptography
    return decrypt_password(password, MyGlobals.ftpEncryptKey)

# Contains functions for deciphering passwords hashes to be used by other scripts
import subprocess
import os

from MyModules import MyGlobals as MyGlobals
from cryptography.fernet import Fernet

encodingType = 'utf-8'

def getPasswordFromPasswordEncrypterExe(passwordEncrypterExe, passwordHash):
    if MyGlobals.isVerbose:
        print("Deciphering password hash using encrypter-exe: {}".format(passwordEncrypterExe))
    try:
        result = subprocess.run("{} -i {} -d -s -r".format(passwordEncrypterExe, passwordHash), capture_output=True)
    except BaseException as errorMsg:
        print("Failed excuting subprocess of encrypter-exe:\n{}\nto decipher password from given hash: \n{}".format(passwordEncrypterExe, passwordHash))
        return None
    if not result.returncode == 0:
        return None

    if MyGlobals.isVeryVerbose:
        print("Success - deciphered password hash using encrypter-exe")

    global encodingType
    subProcOutput = result.stdout
    if type(subProcOutput) == bytes:
        subProcOutput = bytes.decode(subProcOutput, encodingType)
    return subProcOutput.strip()

def decryptPassword(passwordToDecrypt, key):

    cipher_suite = Fernet(key)
    try:
        if not type(passwordToDecrypt) == bytes:
            passwordToDecrypt = str(passwordToDecrypt).encode()
        uncipher_text = (cipher_suite.decrypt(passwordToDecrypt))
        plain_text = bytes(uncipher_text).decode("utf-8")
        if MyGlobals.isVeryVerbose:
            print("Success - deciphered password hash")
        return plain_text
    except BaseException as errorMsg:
        print("Failed deciphering password hash\nError:\n{}".format(errorMsg))
        return None



def decipherPasswordHash(password):
    if MyGlobals.isVerbose:
        print("Attempting to decipher password hash")

    # Use password-encrypter.exe
    if MyGlobals.passwordEncrypterExe and os.path.isfile(MyGlobals.passwordEncrypterExe):
        return getPasswordFromPasswordEncrypterExe(MyGlobals.passwordEncrypterExe, password)

    # passwordEncrypterExe doesn't exist (None or wrong path doesn't matter.)
    #  so use the key and lib cryptography
    return decryptPassword(password, MyGlobals.ftpEncryptKey)

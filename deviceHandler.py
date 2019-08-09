import paramiko
from paramiko.ssh_exception import AuthenticationException
import time
import sys
import os
import ipdb
import serial

# THIS SCRIPT HANDLES THE DEVICE SPECIFIC IMPLEMENTATION

# FETCHES DATA FOR DEVICE LINKED TO IP AND RUNS THE DEVICE
# SPECIFIC TASK FUNCTION AND RETURNS WHETHER IT WAS COMPLETED
def ipDeviceHandler(ip):
    # CHECKS TO SEE IF THE ADDRESS IS IN THE FILE
    infoHolder = ipdb.ipdb()
    if infoHolder.isIPv4(ip):
        device = infoHolder.getipdb()[ip]
        brand = device['brand']
        # RUNS THE SPECIFIC FUNCTION FOR THE DEVICE
        if brand == 'MRV OS-904':
            print(f'Running task on {brand}')
            isUpdated, newver = mrv_os_904(ip, infoHolder)
            # UPDATES DATABASE IF DEVICE WAS UPDATED
            if isUpdated:
                device['version'] = newver
                infoHolder.setInfo(ip, device)
                return True
        # IF THE BRAND OF DEVICE WAS NOT FOUND
        else:
            print(f'{brand} not found!')
    else:
        print(f'{ip} is not a valid IPv4 address!')
    return False

# COMPLETES A DEVICE SPECIFIC TASK FROM THE SERIAL PORT
def serialDeviceHandler(com, device):
    if device == 'alcatel_6850':
        print(f'Running task on alcatel_6850')
        # WARNING WILL DEFAULT
        # TODO add a try again
        result = default_alcatel_6850(com)
        return result
    # IF THE DEVICE WAS NOT FOUND
    else:
        print(f'{device} not found!')
    return False

# FUNCTION FOR DEFAULTING alcatel_6850
# INPUT IS THE COM TO CONNECT TO THE DEVICE
# RETURNS WHETHER THE TASK WAS COMPLETED
def default_alcatel_6850(com):
    result = False
    try:
        # LOGIN INFO
        login = b'redacted'
        password = ['redacted']

        # OPENS SERIAL CONNECTION
        ser = serial.Serial()
        ser.port = com
        ser.timeout = 10
        ser.write_timeout = 10
        ser.open()

        flag = 0
        output = ''
        while ser.is_open:
            if ser.in_waiting > 0:
                output += '\n' + str(ser.read(9999).decode("utf-8"))
            elif flag == 0:
                for passwd in password:
                    ser.write(login + b'\n')
                    ser.write(passwd + b'\n')
                    time.sleep(2)
                    output += '\n' + str(ser.read(9999).decode("utf-8"))
                    time.sleep(2)
                    if ('->' in output):
                        print('Logged in')
                        break
                time.sleep(2)
                flag = 1
            elif flag == 1:
                if not('->' in output):
                    print('Could not login in!')
                    break
                else:
                    flag = 2
            elif flag == 2:
                output = ''
                ser.write(b'ls\n')
                time.sleep(2)
                flag = 3
            elif flag == 3:
                if 'boot.slot.cfg' in output:
                    ser.write(b'rm boot.slot.cfg\n')
                    print('boot.slot')
                ser.write(b'cd working\n')
                output = ''
                ser.write(b'ls\n')
                time.sleep(2)
                flag = 4
            elif flag == 4:
                if 'boot.cfg' in output:
                    ser.write(b'rm boot.cfg\n')
                    print('work boot')
                ser.write(b'cd ..\n')
                ser.write(b'cd certified\n')
                output = ''
                ser.write(b'ls\n')
                time.sleep(2)
                flag = 5
            elif flag == 5:
                if 'boot.cfg' in output:
                    ser.write(b'rm boot.cfg\n')
                    print('cert boot')
                flag = 6
            elif flag == 6:
                ser.write(b'reload\n')
                time.sleep(1)
                ser.write(b'y\n')
                print('Rebooting')
                result = True
                flag = 7
            elif flag ==7:
                if 'NIs are ready' in output:
                    # flag = 8
                    break
    # TODO add exception handling
    except Exception as e:
        print(e)
    finally:
        ser.close()
    return result


# FUNCTION TO RUN UPDATER ON SPECIFIC DEVICE
# RETURNS A TUPLE OF (isUpdated, newver) WHERE
# isUpdated IS A BOOL OF WHETHER THE DEVICE WAS UPDATED
# newver IS THE NEW VERSION, None IS NO UPDATE WAS APPLIED
def mrv_os_904(ip, infoHolder):
    result = (False, None)
    curver = ''

    # GETS ALL THE INFO FROM THE INFOHOLDER
    device = infoHolder.getipdb()[ip]
    deviceport = device['port']
    devicelogin = device['login']
    devicepass = device['password']
    serverIP = infoHolder.getServer()['ip']
    serverLogin = infoHolder.getServer()['login']
    serverPassword = infoHolder.getServer()['password']
    newver = infoHolder.getConfig()[device['brand']]['version']
    verfile = infoHolder.getConfig()[device['brand']]['file']
    verFilePath = infoHolder.getConfig()[device['brand']]['path']

    # DECLARES SSH OBJECT
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # CONNECTS TO DEVICE AND INVOKES A SHELL
        # TODO handle multiple passwords and logins
        ssh.connect(
            ip,
            port=deviceport,
            username=devicelogin,
            password=devicepass)
        channel = ssh.invoke_shell()
        channel.settimeout(30)

        # GRABS CURRENT VERSION OFF OF DEVICE
        channelData = ''
        while True:
            channelData += '\n' + str(channel.recv(9999)) #.decode("utf-8")
            if channelData.endswith('OS904> \''):
                strlen = len(channelData)
                channel.send('show version | include MasterOS\n')
                time.sleep(1)
                channelData += '\n' + str(channel.recv(9999))
                time.sleep(1)
                strStart = channelData.find('MasterOS version:', strlen)
                curver = str(channelData[strStart+18:len(channelData)-14])
                # print(f'curver: {curver}')
                time.sleep(5)
                break

        # DEBUG
        # if curver != newver:
        #     print(f'Updating!\ncurver: {curver}\nnewver: {newver}')
        # else:
        #     print('They were the same!')

        # IF NOT UPDATED, UPDATE DEVICE
        if curver != newver:
            print(f'Updating!\ncurver: {curver}\nnewver: {newver}')
            channel.send('en\n')
            time.sleep(1)
            channel.send(f'upgrade ftp {serverIP} {verFilePath} ' +
                f'{verfile} {serverLogin} {serverPassword}\n')
            channel.send(f'{devicepass}\n')
            time.sleep(5)
            while True:
                channelData += str(channel.recv(9999))
                # print(channelData)
                if '(y|n)' in channelData[len(channelData) - 20:]:
                    time.sleep(1)
                    channel.send('y\n')
                    time.sleep(5)
                    channelData += str(channel.recv(9999))
                    result = (True, newver)
                    break

    # HANDLES ERRORS AND EXCEPTIONS
    except socket.error as e:
        print(f'A errror has occurred while connecting to {ip}!')
    except socket.timeout as e:
        print(f'A time-out has occurred on {ip}!')
    except AuthenticationException as e:
        print(f'Bad Login on {ip}!')
    except Exception as e:
        print(f'This error happened on {ip}:\n{e}')
    finally:
        ssh.close()
    return result

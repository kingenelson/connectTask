import sys
import os
import io
import deviceHandler

# WILL COMPLETE AN ACTION BASED ON COMMAND-LINE INPUT

###########################################################################
# VARIABLES
# NAME OF TXT FILE TO GET ADDRESSES FROM
IP_FILE = 'ip_address.txt'

# OUTPUT LIST OF ADRESSES THAT HAD THEIR DEVICE ACTION COMPLETED
iplist = []

# WHETHER A SERIAL DEVICE HAD ITS ACTION COMPLETED
serialUp = False

###########################################################################
# FETCHES LIST OF IP'S TO CHECK
# CAN INPUT A SPECIFIC IP OR LEAVE ARG BLANK TO RUN ON FULL LIST

# NO OTHER ARGS WERE ENTERED ON THE COMMAND LINE
if len(sys.argv) == 1:
    # TODO add comfirmation
    try:
        # OPENS TEXT FILE WITH IPS AND SENDS THEM TO THE DEVICE HANDLER
        with open(IP_FILE, 'r', encoding='utf-8') as ipfile:
        # ipfile = open(IP_FILE, 'r', encoding='utf-8')
            for ip in ipfile:
                if deviceHandler.ipDeviceHandler(ip):
                    # IF TASK COMPLETE ADD TO LIST
                    iplist.append(ip)
    except FileNotFoundError:
        # MAKE SURE (IP_FILE) EXISTS IN THE SAME DIR
        print(f'Cannot find {IP_FILE} in {os.getcwd()}')

# IF THERE IS ADDITIONAL COMMAND-LINE ARGS
elif len(sys.argv) >= 2:
    # CHECK WHICH TYPE OF CONNECTION TO TRY
    connectType = str(sys.argv[1])
    # IF ip [address]
    if connectType == 'ip':
        ip = str(sys.argv[2])
        # PASSES INFO TO DEVICE HANDLER
        if deviceHandler.ipDeviceHandler(ip):
            iplist.append(ip)
    # IF serial [com] [device]
    elif connectType == 'serial':
        # PASSES INFO TO DEVICE HANDLER
        if deviceHandler.serialDeviceHandler(sys.argv[2], sys.argv[3]):
            serialUp = True
    else:
        print('Invalid args!')

else:
    # IF TOO MANY ARGS ARE ENTERED
    print('Too many args!')

# PRINTS THE LIST OF ADDRESSES THAT HAD THEIR DEVICE ACTION COMPLETE
# TODO note: may change to print to file instead
if len(iplist) > 0:
    print('The following devices had there action complete:')
    for ip in iplist:
        print(ip)
# IF A SERIAL DEVICE ACTION WAS COMPLETE
elif serialUp:
    print(f'Serial device on {sys.argv[2]} tasks complete!')
else:
    print('No devices had there action complete')
print('Done!')

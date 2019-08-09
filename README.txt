################################################################################
# ABOUT

Scipt that will complete a task via ip and ssh connection or by serial connection. See deviceHandler.py for exact device specific implementation

################################################################################
# INSTRUCTIONS TO USE

- For single IP
1. Make sure the ipdb.yml has the correct device, server, and config info.
2. run in cmd in the connectTask dir:
    venv\Scripts\activate.bat
    python inputHandler.py {ip} {ipv4 address}

- For multiple IP's
1. Make sure the ipdb.yml has the correct device, server, and config info.
2. Input IPv4 Addreses in ip_address.txt
2. run in cmd in the connectTask dir:
    venv\Scripts\activate.bat
    python inputHandler.py

- For serial connection
1. run in cmd in the connectTask dir:
    venv\Scripts\activate.bat
    python inputHandler.py {serial} {com} {device}

- To get venv dependencies
1. run in cmd in the connectTask dir:
    pip install -r requiremnets.txt

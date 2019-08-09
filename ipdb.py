import yaml

# THIS IS THE HANDLER CLASS FOR THE SERVER INFO, DEVICE CONFIG, AND IP DATABASE

# THE FILE TO READ FROM
YAMLFILE = 'ipdb.yml'

class ipdb:
    # OPENS (YAMLFILE) AND GETS INFO OFF OF IT
    def __init__(self):
        try:
            with open(YAMLFILE, 'r') as file:
                data = list(yaml.load_all(file))
                self.server = data[0]
                self.config = data[1]
                self.ipdb = data[2]
        except FileNotFoundError:
            # MAKE SURE (YAMLFILE) EXISTS IN THE SAME DIR
            print(f'Cannot find {YAMLFILE} in {os.getcwd()}')

    # RETURNS SERVER INFO
    def getServer(self):
        return self.server

    # RETURNS DEVICE CONFIG
    def getConfig(self):
        return self.config

    # RETURNS IP DATABASE
    def getipdb(self):
        return self.ipdb

    # RETURNS IF ip IS IN DATABASE
    def isIPv4(self, ip):
        return ip in self.ipdb

    # WRITES NEW CONFIG
    def setInfo(self, ip, device):
        # TODO may be a more effiecent way
        self.ipdb[ip] = device
        with open(YAMLFILE, 'w') as file:
            yaml.dump_all([self.server, self.config, self.ipdb], file)

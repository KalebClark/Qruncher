import re
import sys
import json


""" =================================== QCConfig Class  =======================
=========================================================================== """
class QCConfig:
    config = {"builders": [], "maps": []}

    def __init__(self, config_files):
        """ QCConfig Init ======================= """
        self.config_files = config_files
        self.readFiles()
        self.saveFiles()

    def scaffoldNew(self, pType, name):
        """ Scaffold New profile ================ """
        if pType == 'builders':
            scaffold = {
                "name": name,
                "tools": [
                    {"name": "qbsp", "path": False, "args": []},
                    {"name": "light", "path": False, "args": []},
                    {"name": "vis", "path": False, "args": []}   
                ]
            }
        elif pType == 'maps':
            scaffold = {
                "name": name,
                "game": "",
                "source": "",
                "dest": ""
            }

        if not self.profileExists(pType, name):
            print("Creating new " + pType + ": " + name)
            self.config[pType].append(scaffold)
            print(self.config[pType])
        
        #self.saveFiles()

    def profileExists(self, pType, name):
        """ Check if profile already exists ===== """
        for profile in self.config[pType]:
            if profile['name'] == name:
                return True
        
        return False

    def readFiles(self):
        """ Read Files ========================== """
        for cfg in self.config_files:
            try:
                config_json = open(cfg['file'])
                self.config[cfg['name']] = json.load(config_json)
            except FileNotFoundError as e:
                print("Failed to open Config file: " + str(e))
                print("Creating new file: " + cfg['file'])
                self.scaffoldNew(cfg['name'], 'default')

    def saveFiles(self):
        """ Save Files ========================== """
        for cfg in self.config_files:
            try:
                config_json = open(cfg['file'], 'w+')
                json.dump(self.config[cfg['name']],config_json, indent=2, separators=(',', ': '))
            except FileNotFoundError as e:
                print("Failed to open file for writing")

""" =================================== QCompile Class  =======================
=========================================================================== """
class QCompile:

    def __init__(self, config_files):
        self.config = QCConfig(config_files)


""" =================================== MAIN ==================================
=========================================================================== """
def main():
    config_files = [
        {"name": "builders", "file": 'qcompile_builders.json'},
        {"name": "maps", "file": 'qcompile_maps.json'}
    ]
    app = QCompile(config_files)

if __name__ == '__main__':
    sys.exit(main())


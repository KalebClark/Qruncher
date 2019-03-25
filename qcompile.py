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
            print("Creating new " + pType + " profile: " + name)
            self.config[pType].append(scaffold)
        else:
            print("Profile already exists. Not creating")
        
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

    def listBuilders(self):
        """ List all build profiles """
        for profile in self.config['builders']:
            print("Name: " + profile['name'])
            for tool in profile['tools']:
                tool_path = tool['path']
                if not tool['path']:
                    tool_path = 'default'       # UPDATE THIS WITH DEFAULT TOOL PATH
                print("---------------------------")
                print("  Tool: " + tool['name'])
                print("  Path: " + tool_path)
                print("  Opts: " + " ".join(tool['args']))
                print("  Command: " + tool_path + " " + " ".join(tool['args']))

    def listMaps(self):
        """ List all map profiles """
        for mmap in self.config['maps']:
            print("Name:   " + mmap['name'])
            print("-------------------------")
            print("  Game:   " + mmap['game'])
            print("  Source: " + mmap['source'])
            print("  Dest:   " + mmap['dest']+"\n")

""" =================================== QCompile Class  =======================
=========================================================================== """
class QCompile:
    command = ''
    command_opt = ''
    option = ''

    def __init__(self, config_files):
        self.config = QCConfig(config_files)
        self.compiler = Compiler()
        self.parseArgs()

    def parseArgs(self):
        print("# of args: "+str(len(sys.argv)))
        # Check to se if there are ANY args.
        if len(sys.argv) <= 1:
            self.help()
            sys.exit(0)

        # Check to see if argv[1] is a split (should alwyas be...)
        if re.match(".*:.*", sys.argv[1]):
            self.command = sys.argv[1].split(':')[0]
            self.command_opt = sys.argv[1].split(':')[1]
        else:
            print("unrecognized command...")
            self.help()

        # Parse options
        if len(sys.argv) >= 3:
            self.option = sys.argv[2]

    def help(self):
        print("Usage:")
        print("  qcompile.py <command> <options>\n")
        print("Examples:")
        print("  (build mode) qcompile.py build:fast myFavoriteMap")
        print("  (conf mode)  qcompile.py build:new buildProfileName\n")
        print("Available Commands:")
        print(" build")
        print("  build:<profile>\tBuild with specified profile")
        print("  build:new\t\tCreate new build profile")
        print("  build:list\t\tList build profiles")
        print(" map")
        print("  map:new\t\tCreate new Map Profile")
        print("  map:list\t\tList map profiles")

    def isOptProfile(self, opt):
        if self.config.profileExists('builders', opt):
            return True
        elif self.config.profileExists('maps', opt):
            return True

        return False

""" =================================== COMPILER ==============================
=========================================================================== """        
class Compiler:

    def __init__(self):
        pass

        


""" =================================== MAIN ==================================
=========================================================================== """
def main():
    config_files = [
        {"name": "builders", "file": 'qcompile_builders.json'},
        {"name": "maps", "file": 'qcompile_maps.json'}
    ]
    app = QCompile(config_files)

    if app.command == 'build':
        if app.command_opt == 'new':
            app.config.scaffoldNew('builders', app.option)
            print("Open the builders json file to configure new profile")
            app.config.saveFiles()
            sys.exit(0)
        elif app.command_opt == 'list':
            print("Listing all BUILD profiles")
            app.config.listBuilders()
            sys.exit(0)

        if app.isOptProfile(app.command_opt):
            print("Right on, Lets build it!")
        else:
            print("Build profile does not exist!")


    if app.command == 'map':
        if app.command_opt == 'new':
            app.config.scaffoldNew('maps', app.option)
            print("Open the maps json file to configure new profile")
            app.config.saveFiles()
            sys.exit(0)
        elif app.command_opt == 'list':
            print("Listing all MAP profiles")
            app.config.listMaps()
            sys.exit(0)

if __name__ == '__main__':
    sys.exit(main())


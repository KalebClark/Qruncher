import re
import os
import sys
import json
import subprocess

""" =================================== QCConfig Class  =======================
=========================================================================== """
class QCConfig:
    #config = {"config": {"toolpath": '', "engines": []}, "builders": [], "maps": []}
    config = {"config": {}, "builders": [], "maps": [],  "engines": [], "mods": []}

    def __init__(self, config_file):
        """ QCConfig Init ======================= """
        self.config_file = config_file
        self.readFiles()
        self.saveFiles()

    def scaffoldNew(self, pType, name):
        """ Scaffold New profile ================ """
        if pType == 'builders':
            scaffold = {
                "name": name,
                "default": False,
                "tools": [
                    {"name": "qbsp", "path": False, "args": []},
                    {"name": "light", "path": False, "args": []},
                    {"name": "vis", "path": False, "args": []}   
                ]
            }
        elif pType == 'maps':
            scaffold = {
                "name": name,
                "source": "",
                "dest": ""
            }
        elif pType == 'engines':
            scaffold = {"name": name, "default": False, "path":'',"base_dir":'', "args": []}
        elif pType == 'mods':
            scaffold = {"name": name, "default": False, "subdir": ''}

        if not self.profileExists(pType, name):
            print("Creating new " + pType + " profile: " + name)
            self.config[pType].append(scaffold)
        else:
            print("Profile already exists. Not creating")

    def indexOfTool(self, build_profile, tool):
        """ Get index of tool =================== """
        profile = self.getProfile('builders', build_profile)
        for idx, t in enumerate(profile['tools']):
            if tool == t['name']:
                return idx
        return False

    def profileExists(self, pType, profile_name):
        """ Check if profile already exists ===== """
        for idx, profile in enumerate(self.config[pType]):
            if profile['name'] == profile_name:
                return idx
        
        return False

    def getProfile(self, pType, profile_name):
        """ Get profile ========================= """
        idx = self.profileExists(pType, profile_name)
        if not idx:
            print(pType.capitalize() + " profile ("+profile_name+") does not exist")
            return False
        
        return self.config[pType][idx]

    def getDefaultProfile(self, pType):
        for profile in self.config[pType]:
            if profile['default']:
                return profile

        return False

    def readFiles(self):
        """ Read Files ========================== """
        try:
            config_json = open(self.config_file)
            self.config = json.load(config_json)
        except FileNotFoundError as fnfe:
            print("Failed to open Config file:" + str(fnfe))
            self.createConfig()


    def createConfig(self):
        print("Creating default config file. Open " + self.config_file + " to configure")
        base_path = input("Enter the base path to your quake install: ")
        tool_path = input("Enter the tool path for qbsp,light,vis etc: ")
        self.config['config']['base_path'] = base_path
        self.config['config']['tool_path'] = tool_path

        self.scaffoldNew('engines', 'default')
        self.scaffoldNew('builders', 'default')
        self.scaffoldNew('maps', 'default')
        self.scaffoldNew('mods', 'default')

    def saveFiles(self):
        """ Save Files ========================== """
        try:
            config_json = open(self.config_file, 'w+')
            json.dump(self.config, config_json, indent=2, separators=(',', ': '))
        except FileNotFoundError as fnfe:
            print("Failed to open for writing: " + str(fnfe))

    def deleteProfile(self, pType, profile_name):
        """ Delete Profile ====================== """
        del_idx = self.profileExists(pType, profile_name)
        if del_idx is not False:
            print("Deleting " + pType + " profile " + profile_name)
            self.config[pType].pop(del_idx)
        elif del_idx is False:
            print("Profile not found: " + profile_name)

    def listBuilders(self):
        """ List all build profiles ============= """
        print("Build Profiles:")
        print("-----------------------------------")
        for profile in self.config['builders']:
            if profile['default']:
                default = "\t(default)"
            else:
                default = ''
            print("Name: " + profile['name'] + default)
            
    def showBuilders(self, profile_name):
        """ Show detailed build profile ========= """
        idx = self.profileExists('builders', profile_name)
        profile = self.config['builders'][idx]
        print("Build Profile: " + profile['name'])
        for tool in profile['tools']:
            tool_path = tool['path']
            if not tool['path']:
                tool_path = 'default'
            print("-----------------------------------")
            print("  Tool: " + tool['name'])
            print("  Path: " + tool_path)
            print("  Opts: " + " ".join(tool['args']))
            print("  Command: " + tool_path + " " + " ".join(tool['args']))


    def listMaps(self):
        """ List all map profiles =============== """
        print("Map Profiles:")
        print("-----------------------------------")
        for mmap in self.config['maps']:
            if mmap['default']:
                default = "\t(default)"
            else:
                default = ''
            print("Name: " + mmap['name'] + default)
    
    def showMaps(self, profile_name):
        """ Show map detail ===================== """
        idx = self.profileExists('maps', profile_name)
        mmap = self.config['maps'][idx]
        print("Map profile: " + mmap['name'])
        print("---------------------------------------")
        print("  Source: " + mmap['source'])
        print("  Dest:   " + mmap['dest']+"\n")

    def listEngines(self):
        """ List all engine profiles ============ """
        print("Engine Profiles:")
        print("----------------------------------------")
        for engine in self.config['engines']:
            if engine['default']:
                default = "\t(default)"
            else:
                default = ''
            print("Name: " + engine['name'] + default)

    def showEngines(self, profile_name):
        """ Show engine detail ================== """
        idx = self.profileExists('engines', profile_name)
        engine = self.config['engines'][idx]
        print("Engine Profile: " + engine['name'])
        print("---------------------------------------")
        print("  Path: " + engine['path'])
        print("  base_dir: " + engine['base_dir'])
        print("  args: " + " ".join(engine['args']))

    def listMods(self):
        """ List all mods ======================= """
        print("Mod Profiles")
        print("----------------------------------------")
        for mod in self.config['mods']:
            print(mod)
            if mod['default']:
                default = "\t(default)"
            else:
                default = ''
            print("Name: " + mod['name'] + default)

    def showMods(self, profile_name):
        """ Show mod detail ===================== """
        idx = self.profileExists('mods', profile_name)
        mod = self.config['mods'][idx]
        print("Mod profile: " + mod['name'])
        print("-----------------------------------------")
        print("  subdir: " + mod['subdir'])


""" =================================== QCompile Class  =======================
=========================================================================== """
class QCompile:
    command = ''
    command_opt = ''
    option = ''
    opts = {}

    def __init__(self, config_files):
        self.config = QCConfig(config_files)
        self.compiler = Compiler()
        self.parseArgs()

    def parseArgs(self):
        """ Parse Agruments into something more confusing. You are welcome """
        del sys.argv[0]
        print("# of args: "+str(len(sys.argv)))
        
        # Check to see if there are any args.
        if len(sys.argv) == 0:
            self.help()
            sys.exit(0)

        for arg in sys.argv:
            if self.isSplit(arg):
                splt = self.splitArg(arg)
                self.opts[splt['cmd']] = splt['opt']
            else:
                self.opts['profile_name'] = arg

    def splitArg(self, arg):
        return {
            "cmd": arg.split(':')[0],
            "opt": arg.split(':')[1]
        }

    def isSplit(self, arg):
        if re.match("^[A-z]+:[A-z]+$", arg):
            return True
        else:
            return False

    def help(self):
        print("Usage:")
        print("  qcompile.py <command> <options>\n")
        print("Examples:")
        print("  (build mode) qcompile.py build:fast myFavoriteMap")
        print("  (conf mode)  qcompile.py build:new buildProfileName\n")
        print("Available Commands:")

        print(" build")
        print("  build:<name>\t\tBuild with specified profile")
        print("  build:list\t\tList build profiles")
        print("  build:show <name>\tShow specified build profile")
        print("  build:new <name>\tCreate new build profile")
        print("  build:del <name>\tRemove specified build profile")
        
        print(" map")
        print("  map:list\t\tList map profiles")
        print("  map:show <name>\tShow map profile")
        print("  map:new <name> \tCreate new map Profile")
        print("  map:del <name>\tRemove specified map profile")
        
        print(" engine")
        print("  engine:list\t\tList engine profiles")
        print("  engine:show <name>\tShow engine profile")
        print("  engine:new <name> \tCreate new engine profile")
        print("  engine:del <name> \tRemove specified engine profile")
        
        print(" mod")
        print("  mod:list\t\tList mod profiles")
        print("  mod:show <name>\tShow specified mod profile")
        print("  mod:new <name>\tCreate new mod profile")
        print("  mod:del <name>\tRemove specified profile")

        print(" play")
        print("  play <name>\tPlay map profile without compilation")

    def isProfile(self, profile_name):
        if self.config.profileExists('builders', profile_name):
            return True
        elif self.config.profileExists('maps', profile_name):
            return True
        elif self.config.profileExists('engines', profile_name):
            return True
        elif self.config.profileExists('mods', profile_name):
            return True

        return False

""" =================================== COMPILER ==============================
=========================================================================== """        
class Compiler:
    cfg = {}
    def __init__(self):
        self.cfg = QCConfig('qcompile.json')


    def runBuild(self, opts):
        tool_path = self.cfg.config['config']['tool_path']
        base_path = self.cfg.config['config']['base_path']

        # Get Build Profile
        try:
            builder = self.cfg.getProfile('builders', opts['build'])
        except KeyError:
            print("Must specify valid build profile")
            sys.exit(0)

        # Get Map Profile
        try:
            mmap = self.cfg.getProfile('maps', opts['map'])
        except KeyError:
            mmap = self.cfg.getDefaultProfile('maps')

        # Get engine Profile
        try:
            engine = self.cfg.getProfile('engines', opts['engine'])
        except KeyError:
            engine = self.cfg.getDefaultProfile('engines')

        # Get Mod Profile
        try:
            mod = self.cfg.getProfile('mods', opts['mod'])
        except KeyError:
            mod = self.cfg.getDefaultProfile('mods')

        print("BUILD: " + str(builder))
        print("MAP: " + str(mmap))
        print("ENGINE: " + str(engine))
        print("MOD: " + str(mod))

        source = mmap['source']
        map_filename = os.path.basename(source)
        map_basename = os.path.splitext(map_filename)[0]
        print(map_filename)
        print(map_basename)
        dest = mmap['dest'] + map_basename + ".bsp"
        map_dest_path = mmap['dest']
        print(map_dest_path)

        # for idx, tool in enumerate(builder['tools']):
        #     cmd = [
        #         tool_path + tool['name']
        #     ] + tool['args']
        #     if tool['name'] == 'qbsp':
        #         cmd = cmd + [source, dest]
        #     elif tool['name'] == 'light': 
        #         cmd = cmd + [dest]
        #     print(cmd)

        qbsp_idx = self.cfg.indexOfTool(opts['build'], 'qbsp')
        qbsp_cmd = [
            tool_path + builder['tools'][qbsp_idx]['name']
        ] + builder['tools'][qbsp_idx]['args'] + [source, dest]

        light_idx = self.cfg.indexOfTool(opts['build'], 'light')
        light_cmd = [
            tool_path + builder['tools'][light_idx]['name']
        ] + builder['tools'][light_idx]['args'] + [dest]

        vis_idx = self.cfg.indexOfTool(opts['build'], 'vis')
        vis_cmd = [
            tool_path + builder['tools'][vis_idx]['name']
        ] + [dest]
        
        subprocess.call(qbsp_cmd)
        subprocess.call(light_cmd)
        subprocess.call(vis_cmd)

        sys.exit(0)
        tool_path = self.cfg.config['config']['tool_path']
        base_path = self.cfg.config['config']['base_path']

        # Build Profile
        idx = self.cfg.profileExists('builders', build_name)
        builder = self.cfg.config['builders'][idx]

        # Map Profile
        idx = self.cfg.profileExists('maps', map_name)
        mmap = self.cfg.config['maps'][idx]

        # Run QBSP
        qbsp_cmd = [
            tool_path + builder['tools'][0]['name']
        ]
        qbsp_cmd = qbsp_cmd + builder['tools'][0]['args']

        source = mmap['source']
        dest = mmap['dest']

        qbsp_cmd = qbsp_cmd + [source, dest]

        print(qbsp_cmd)
        subprocess.call(qbsp_cmd)
        # Run LIGHT

        # Run VIS

        # Copy map 

        # Run Game

        


""" =================================== MAIN ==================================
=========================================================================== """
def main():
    config_file = 'qcompile.json'
    app = QCompile(config_file)
    detail = False

    print(len(app.opts))
    print(app.opts)

    if len(app.opts) <= 2: # Config Mode
        # print("Config Mode")
        try:
            profile_name = app.opts['profile_name']
            del app.opts['profile_name']
        except KeyError:
            pass
        cmd = list(app.opts.keys())[0]
        opt = list(app.opts.values())[0]

        # Check to see if it is BUILD
        # and the option IS a profile. This means that we are going 
        # to use ALL defaults on everything except the build.
        if cmd == 'build' and app.isProfile(opt):
            app.compiler.runBuild(app.opts)

        # Handle builds
        if cmd == 'build':
            if opt == 'list':
                app.config.listBuilders()
                sys.exit(0)
            if opt == 'show':
                app.config.showBuilders(profile_name)
                sys.exit(0)
            if opt == 'new':
                app.config.scaffoldNew('builders', profile_name)
                app.config.saveFiles()
                sys.exit(0)
            if opt == 'del':
                if query_yes_no("Confirm"):
                    app.config.deleteProfile('builders', profile_name)
                    app.config.saveFiles()
                sys.exit(0)
        # Handle Maps
        elif cmd == 'map':
            if opt == 'list':
                app.config.listMaps()
                sys.exit(0)
            if opt == 'show':
                app.config.showMaps(profile_name)
                sys.exit(0)
            if opt == 'new':
                app.config.scaffoldNew('maps', profile_name)
                app.config.saveFiles()
                sys.exit(0)
            if opt == 'del':
                if query_yes_no("Confirm"):
                    app.config.deleteProfile('maps', profile_name)
                    app.config.saveFiles()
                sys.exit(0)

        # Handle Engine
        elif cmd == 'engine':
            if opt == 'list':
                app.config.listEngines()
                sys.exit(0)
            if opt == 'show':
                app.config.showEngines(profile_name)
                sys.exit(0)
            if opt == 'new':
                app.config.scaffoldNew('engines', profile_name)
                app.config.saveFiles()
                sys.exit(0)
            if opt == 'del':
                if query_yes_no("Confirm"):
                    app.config.deleteProfile('engines', profile_name)
                    app.config.saveFiles()
                sys.exit(0)

        # Handle Mods
        elif cmd == 'mod':
            if opt == 'list':
                app.config.listMods()
                sys.exit(0)
            if opt == 'show':
                app.config.showMods(profile_name)
                sys.exit(0)
            if opt == 'new':
                app.config.scaffoldNew('mods', profile_name)
                app.config.saveFiles()
                sys.exit(0)
            if opt == 'del':
                if query_yes_no("Confirm"):
                    app.config.deleteProfile('mods', profile_name)
                    app.config.saveFiles()
                sys.exit(0)
        elif cmd == 'play':
            pass
        else:
            app.help()

    if len(app.opts) > 2: # Build Mode
        print("Build Mode")
        del app.opts['profile_name']
        app.compiler.runBuild(app.opts)

    sys.exit(0)

def query_yes_no(question):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    prompt = " [Y/n]: "

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("please respond with yes or no")

if __name__ == '__main__':
    sys.exit(main())


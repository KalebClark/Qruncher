import re
import os
import sys
import json
import time
from datetime import datetime, timedelta
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
        for profile in self.config[pType]:
            if profile['name'] == profile_name:
                return True
        
        return False

    def getProfile(self, pType, profile_name, ret_index=False):
        """ Get profile ========================= """
        profile_index = None
        for idx, profile in enumerate(self.config[pType]):
            if profile['name'] == profile_name:
                profile_index = idx
        
        if profile_index == None:
            raise Exception("Profile " + profile_name +" does not exist...")
        
        if ret_index:
            return profile_index
        else:
            return self.config[pType][profile_index]

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
        del_idx = self.getProfile(pType, profile_name, True)
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
        profile = self.getProfile('builders', profile_name)
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
        mmap = self.getProfile('maps', profile_name)
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
        engine = self.getProfile('engines', profile_name)
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
        mod = self.getProfile('mods', profile_name)
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
        if self.config.profileExists('builders', profile_name) is not False:
            return True
        elif self.config.profileExists('maps', profile_name) is not False:
            return True
        elif self.config.profileExists('engines', profile_name) is not False:
            return True
        elif self.config.profileExists('mods', profile_name) is not False:
            return True

        return False

""" =================================== COMPILER ==============================
=========================================================================== """        
class Compiler:
    cfg = {}
    def __init__(self):
        self.cfg = QCConfig('qcompile.json')

    def timeSubProcess(self, args):
        sdt = datetime.now()
        start_time = sdt.microsecond
        subprocess.run(args)
        edt = datetime.now()
        end_time = edt.microsecond

        duration = edt - sdt
        duration_s = duration.total_seconds()

        splt = str(duration).split(':')
        
        return {
            'h': splt[0],
            'm': splt[1],
            's': str(round(float(splt[2]),3))
        }

    def getFileStats(self, file_path):
        try:
            fs = os.stat(file_path)
            fs_time = datetime.fromtimestamp(fs.st_mtime)
            return {
                "exists": str(True),
                "size": str(round(fs.st_size / 1024))+"k",
                "time": str(fs_time)
            }
        except FileNotFoundError as fnfe:
            return {"exists": str(False), "size": '', "time": ''}

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

        # Setup Paths
        map_full_path = mmap['source']
        map_file_name = os.path.basename(map_full_path)
        map_basename  = os.path.splitext(map_file_name)[0]
        map_directory = os.path.dirname(map_full_path)+os.sep
        bsp_full_path = map_directory + map_basename + ".bsp"
        prt_full_path = map_directory + map_basename + ".prt"
        lit_full_path = map_directory + map_basename + ".lit"

        # Handle output. If specified in MAP profile, override. Otherwise
        # use MOD profile as output.
        if not mmap['dest']:
            bsp_destination = base_path + os.sep + mod['subdir'] + os.sep + "maps" + os.sep + map_basename + ".bsp"
        else:
            bsp_destination = mmap['dest'] + os.sep + map_basename + ".bsp"    

        # Change into map_directory for generation of log files in build dir.
        os.chdir(map_directory)

        # Create QBSP Command
        qbsp_idx = self.cfg.indexOfTool(opts['build'], 'qbsp')
        qbsp_args = builder['tools'][qbsp_idx]['args']
        qbsp_cmd = [
            tool_path + os.sep + builder['tools'][qbsp_idx]['name']
        ] + qbsp_args + [map_full_path]

        # Create VIS Command
        vis_idx = self.cfg.indexOfTool(opts['build'], 'vis')
        vis_args = builder['tools'][vis_idx]['args']
        vis_cmd = [
            tool_path + os.sep + builder['tools'][vis_idx]['name']
        ] + vis_args + [bsp_full_path]

        # Create LIGHT Command
        light_idx = self.cfg.indexOfTool(opts['build'], 'light')
        light_args = builder['tools'][light_idx]['args']
        light_cmd = [
            tool_path + os.sep + builder['tools'][light_idx]['name']
        ] + light_args + [bsp_full_path]

        # Run QBSP, VIS, LIGHT
        qbsp_time = self.timeSubProcess(qbsp_cmd)

        vis_time = self.timeSubProcess(vis_cmd)

        light_time = self.timeSubProcess(light_cmd)

        # Move bsp file to final destination
        try:
            os.remove(bsp_destination)
        except OSError:
            pass

        os.rename(bsp_full_path, bsp_destination)

        # Done Compiling. Check stats on files generated
        map_fs = self.getFileStats(map_full_path)
        bsp_fs = self.getFileStats(bsp_full_path)
        prt_fs = self.getFileStats(prt_full_path)
        lit_fs = self.getFileStats(lit_full_path)

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("\nQCruncher File Report @\t"+current_time)
        print("-----------------------------------------------")
        print("File\tExists\t\tSize\tCreate Date/time")
        print("-----------------------------------------------")
        print(".map\t"+map_fs['exists']+"\t\t"+map_fs['size']+"\t"+map_fs['time'])
        print(".bsp\t"+bsp_fs['exists']+"\t\t"+bsp_fs['size']+"\t"+bsp_fs['time'])
        print(".prt\t"+prt_fs['exists']+"\t\t"+prt_fs['size']+"\t"+prt_fs['time'])
        print(".lit\t"+lit_fs['exists']+"\t\t"+lit_fs['size']+"\t"+lit_fs['time'])

        print("\nQCruncher Tools Report")
        print("-----------------------------------------------")
        print("Tool\tHrs\tMin\tSeconds\tArguments")
        print("-----------------------------------------------")
        print("QBSP:\t"+qbsp_time['h']+"\t"+qbsp_time['m']+"\t"+qbsp_time['s']+"\t"+" ".join(qbsp_args))
        print("VIS :\t"+vis_time['h']+"\t"+vis_time['m']+"\t"+vis_time['s']+"\t"+" ".join(vis_args))
        print("LIGHT:\t"+light_time['h']+"\t"+light_time['m']+"\t"+light_time['s']+"\t"+" ".join(light_args))

        print("\nFinal Destination of bsp file: ")
        print(bsp_destination)

        # Run QUAKE!!!

        # Check OS. If its 'darwin'(MacOS), some executables are in mac format,
        # which is inside a folder. Need to use the "open" command on mac os to
        # fire this off. Linux & windows are straight paths.
        platform = sys.platform
        engine_exe = None
        engine_path = None
        if platform == 'darwin':
            # Does path exist?
            if os.path.exists(engine['path']):
                # Yes. full path or directory?
                if os.path.isfile(engine['path']):
                    # Full Path
                    engine_path = engine['path']
                    engine_exe = [engine['path']]
                elif os.path.isdir(engine['path']):
                    # Directory. Must have the .app already
                    engine_path = engine['path']
                    engine_exe = ['open'] + [engine_path, '--args']

            else:
                # Does not exist. Add .app and check again
                if os.path.exists(engine['path']+".app"):
                    # found it with .app
                    engine_path = engine['path']+".app"
                    engine_exe = ['open'] + [engine_path+".app", '--args']
                else:
                    # Just does not exist. Bail.
                    print("Engine Executable does not exist. Exiting")
                    sys.exit(0)
        else:
            # Onward to other OS's
            if not os.path.exists(engine['path']):
                print("Engine executable does not exist. Exiting")
                sys.exit(0)
            engine_path = engine['path']
            engine_exe = engine['path']

        engine_exe = engine_exe + engine['args'] + ['-basedir', base_path]

        # Add mod
        engine_exe = engine_exe + ['-game', mod['subdir']]

        # Add Map
        engine_exe = engine_exe + ['+map', map_basename+".bsp"]
        print(engine_exe)
        subprocess.run(engine_exe)
        sys.exit(0)

        


""" =================================== MAIN ==================================
=========================================================================== """
def main():
    config_file = 'qcompile.json'
    app = QCompile(config_file)

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
            print("Proceed to building")

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
        if 'profile_name' in app.opts:
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


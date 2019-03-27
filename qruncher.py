#!/usr/bin/env python3
import re
import os
import sys
import json
import time
from datetime import datetime, timedelta
import subprocess

""" =================================== QConfig Class  =======================
=========================================================================== """
class QConfig:
    """
    Configuration class for Qruncher
    ...
    Attributes
    ----------
    config : dict
        Main configuration read in from json file. Instantiated here for
        preload of json.
    config_file : str
        Name of the json config file specified in the instantiaion of app.

    Methods
    -------
    scaffoldNew(pType, name)
        Scaffolds new configurations into the main config dict
    """
    config = {"config": {}, "builders": [], "maps": [],  "engines": [], "mods": []}

    def __init__(self, config_file):
        """ QConfig Init ======================= """
        self.config_file = config_file
        self.readFiles()
        self.saveFiles()

    def scaffoldNew(self, pType, profile_name):
        """ ===============================================
        Scaffold a new profile. Used mainly by the 'new' 
        command. Also used on first time run

        Parameters
        ----------
        pType : str
            Type of config to scaffold.
        profile_name : str
            name of the profile to scaffold
        =============================================== """
        if pType == 'builders':
            # BUILD Scaffold
            scaffold = {
                "name": profile_name,
                "default": False,
                "tools": [
                    {"name": "qbsp", "path": False, "args": []},
                    {"name": "light", "path": False, "args": []},
                    {"name": "vis", "path": False, "args": []}   
                ]
            }
        elif pType == 'maps':
            # MAP Scaffold
            scaffold = {
                "name": profile_name,
                "source": "",
                "dest": False
            }
        elif pType == 'engines':
            # ENGINE Scaffold
            scaffold = {"name": profile_name, "default": False, "path":'', "args": []}
        elif pType == 'mods':
            # MOD Scaffold
            scaffold = {"name": profile_name, "default": False, "subdir": ''}

        # Check to see if default profile already exists.
        if not self.profileExists(pType, profile_name):
            print("Creating new " + pType + " profile: " + profile_name)
            self.config[pType].append(scaffold)
        else:
            print("Profile already exists. Not creating")

    def indexOfTool(self, build_profile, tool):
        """ ===============================================
        Returns the index of specified tool in BUILD profile

        Parameters
        ----------
        build_profile : str
            Name of the build profile
        tool : str
            Name of the tool

        Returns
        -------
        int
            List index of the specified tool.
        =============================================== """
        profile = self.getProfile('builders', build_profile)
        for idx, t in enumerate(profile['tools']):
            if tool == t['name']:
                return idx
        return False

    def profileExists(self, pType, profile_name):
        """ ===============================================
        Check to see if a profile already exists.

        Parameters
        ----------
        pType : str
            Type of configuration to look in
        profile_name : str
            Name of the profile to check

        Returns
        -------
        bool
            True if the profile was found
            False if the profile was not found
        =============================================== """
        for profile in self.config[pType]:
            if profile['name'] == profile_name:
                return True
        
        return False

    def getProfile(self, pType, profile_name):
        """ ===============================================
        Get the full configuration of the specified profile
        or just return the index.

        Parameters
        ----------
        pType : str
            Type of configuration to look in
        profile_name : str
            Name of the configuration to get

        Returns
        -------
        dict (ret_index=True)
            A dict of the full profile configuration
        =============================================== """
        profile_index = None
        for idx, profile in enumerate(self.config[pType]):
            if profile['name'] == profile_name:
                profile_index = idx
        
        if profile_index == None:
            raise ProfileNotFoundException(pType, profile_name)
        
        return self.config[pType][profile_index]

    def getProfileIndex(self, pType, profile_name):
        """ ===============================================
        Get the index of the specified profile

        Parameters
        ----------
        pType : str
            Type of configuration to look in
        profile_name : str
            Name of the configuration to find

        Returns
        -------
        int
            Index of the profile in config list
        =============================================== """
        profile_index = None
        for idx, profile in enumerate(self.config[pType]):
            if profile['name'] == profile_name:
                profile_index = idx

        if profile_index == None:
            raise ProfileNotFoundException(pType, profile_name)
        
        return profile_index

    def getDefaultProfile(self, pType):
        """ ===============================================
        Get the default profile for specified type

        Parameters
        ----------
        pType : str
            Type of configuration to look in for default

        Returns
        -------
        dict
            Dict of default configuration for type
        =============================================== """
        profile = None
        for p in self.config[pType]:
            if p['default']:
                profile = p
        
        if profile is None:
            raise NoDefaultProfileException(pType)

        return profile

    def readFiles(self):
        """ ===============================================
        Read the json configration file and load it into 
        self.config dict

        TODO: Clean up exception. 
        =============================================== """
        try:
            config_json = open(self.config_file)
            self.config = json.load(config_json)
        except FileNotFoundError as fnfe:
            print("Failed to open Config file:" + str(fnfe))
            self.createConfig()

    def createConfig(self):
        """ ===============================================
        Create configuration file when there is no config
        file found. Walks the user through static portions
        of the config. The rest will need to be edited in file
        TODO: Ask more questions??
        =============================================== """
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
        """ ===============================================
        Save self.config dict to json file.
        TODO: Clean up exception.
        =============================================== """
        try:
            config_json = open(self.config_file, 'w+')
            json.dump(self.config, config_json, indent=2, separators=(',', ': '))
        except FileNotFoundError as fnfe:
            print("Failed to open for writing: " + str(fnfe))

    def deleteProfile(self, pType, profile_name):
        """ ===============================================
        Delete specified profile

        Parameters
        ----------
        pType : str
            Type of configuration to delete
        profile_name : str
            Name of the profile to delete
        
        Returns
        -------
        bool
            Success of deletion. True=worked, false=failed

        TODO: Return success of delete. 
        =============================================== """
        del_idx = self.getProfileIndex(pType, profile_name)
        print("Deleting " + pType + " profile " + profile_name)
        self.config[pType].pop(del_idx)

    def listBuilders(self):
        """ ===============================================
        Print list of BULIDER profiles for the user
        TODO: Better formatting?
        =============================================== """
        print("Build Profiles:")
        print("-----------------------------------")
        for profile in self.config['builders']:
            if profile['default']:
                default = "\t(default)"
            else:
                default = ''
            print("Name: " + profile['name'] + default)
            
    def showBuilders(self, profile_name):
        """ ===============================================
        Print detail view of specified profile for the user
        TODO: Better formatting?
        =============================================== """
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
        """ ===============================================
        Print list of MAP profiles for the user
        TODO: Better Formatting?
        =============================================== """
        print("Map Profiles:")
        print("-----------------------------------")
        for mmap in self.config['maps']:
            if mmap['default']:
                default = "\t(default)"
            else:
                default = ''
            print("Name: " + mmap['name'] + default)
    
    def showMaps(self, profile_name):
        """ ===============================================
        Print detailed view of MAP profile for the user
        TODO: Better formatting?
        =============================================== """
        mmap = self.getProfile('maps', profile_name)
        print("Map profile: " + mmap['name'])
        print("---------------------------------------")
        print("  Source: " + mmap['source'])
        print("  Dest:   " + mmap['dest']+"\n")

    def listEngines(self):
        """ ===============================================
        Print list of ENGINE profiles for the user
        TODO: Better Formatting?
        =============================================== """
        print("Engine Profiles:")
        print("----------------------------------------")
        for engine in self.config['engines']:
            if engine['default']:
                default = "\t(default)"
            else:
                default = ''
            print("Name: " + engine['name'] + default)

    def showEngines(self, profile_name):
        """ ===============================================
        Print detailed view of ENGINE profile for user
        TODO: Better Formatting
        =============================================== """
        engine = self.getProfile('engines', profile_name)
        print("Engine Profile: " + engine['name'])
        print("---------------------------------------")
        print("  Path: " + engine['path'])
        print("  base_dir: " + engine['base_dir'])
        print("  args: " + " ".join(engine['args']))

    def listMods(self):
        """ ===============================================
        Print list of MOD profiles for the user
        TODO: Better formatting
        =============================================== """
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
        """ ===============================================
        Print detailed view of MOD profile for user
        TODO: Better formatting
        =============================================== """
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
        self.config = QConfig(config_files)
        self.compiler = QCompiler()
        self.parseArgs()

    def parseArgs(self):
        """ ===============================================
        Parse arguments into something more confusing than
        sys.argv

        Arguments are complicated here because they all
        use a : split. 

        Parsed arguments are prepared as class variables
        =============================================== """
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
        """ ===============================================
        Split the : joined argument into two parts reliably.

        Parameters
        ----------
        arg : str
            Argument string from sys.argv

        Returns
        -------
        dict
            Dictionary of both parts with keys
        =============================================== """
        return {
            "cmd": arg.split(':')[0],
            "opt": arg.split(':')[1]
        }

    def isSplit(self, arg):
        """ ===============================================
        Test to see if argument is a : joined pair.

        Parameters
        ----------
        arg : str
            Argument string from sys.argv

        Returns
        -------
        bool
            True if splitable, False if not. 
        =============================================== """
        if re.match("^[A-z]+:[A-z]+$", arg):
            return True
        else:
            return False

    def help(self):
        """ ===============================================
        Print helpful information for user!
        =============================================== """
        print("Usage:")
        print("  qruncher.py <command> <options>\n")
        print("Examples:")
        print("  (build mode) qruncher.py build:fast myFavoriteMap")
        print("  (conf mode)  qruncher.py build:new buildProfileName\n")
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
        """ ===============================================
        Check to see if a string is a profile name.

        Parameters
        ----------
        profile_name : str
            Name of the profile to check on.

        Returns
        -------
        bool
            True if profile exists anywhere. False if not.
        
        TODO: Loop keys on config dict to search instead 
        of checking each manually. 
        =============================================== """
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
class QCompiler:
    cfg = {}
    def __init__(self):
        self.cfg = QConfig('qruncher.json')

    def runTool(self, args):
        """ ===============================================
        Run a tool and time the duration of the execution.

        Parameters
        ----------
        args : list
            List of executable & arguments for subprocess.run()

        Returns
        -------
        dict
            Dictionary of hours, minutes and seconds
            it took to complete the execution of the tool
        =============================================== """
        sdt = datetime.now()
        try:
            subprocess.run(args)
        except FileNotFoundError as fnfe:
            print(str(fnfe))
            print(args)
            sys.exit(1)

        edt = datetime.now()

        duration = edt - sdt

        splt = str(duration).split(':')
        
        return {
            'h': splt[0],
            'm': splt[1],
            's': str(round(float(splt[2]),3))
        }

    def getFileStats(self, file_path):
        """ ===============================================
        Get file stats and return the data. Also handles 
        FileNotFound exception. 

        Parameters
        ----------
        file_path : str
            Path to a file

        Returns
        -------
        dict
            Dictionary containing data about the file.
        ================================================ """
        try:
            fs = os.stat(file_path)
            fs_time = datetime.fromtimestamp(fs.st_mtime)
            return {
                "exists": str(True),
                "size": str(round(fs.st_size / 1024))+"k",
                "time": str(fs_time)
            }
        except FileNotFoundError:
            return {"exists": str(False), "size": '', "time": ''}

    def getTool(self, build_profile, tool):
        """ ===============================================
        Get tool profile and prepare for use

        Parameters
        ----------
        tool : str
            Name of the tool

        Returns
        -------
        list
            List of data
        =============================================== """
        #      qbsp_idx = self.cfg.indexOfTool(opts['build'], 'qbsp')
        # qbsp = builder['tools'][qbsp_idx]
        tool = build_profile['tools'][
            self.cfg.indexOfTool(build_profile['name'], tool)
        ]
        tool_path = None
        if tool['path']:
            tool_path = tool['path']
        else:
            tool_path = self.cfg.config['config']['tool_path'] + os.sep + tool['name']

        # Get tool Arguments
        tool_args = tool['args']

        return {"path": tool_path, "args": tool_args}
        # return [tool_path, tool_args]


    def runBuild(self, opts):
        """ ===============================================
        Run the build process. This is it!

        Parameters
        ----------
        opts : dict
            All command line options
        =============================================== """
        # Get system paths
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

        """ Setup Paths =============================== """
        # full path to .map file
        map_full_path = mmap['source']
        
        # name of the map with ext (awesomemap.map)
        map_filename = os.path.basename(map_full_path)
        
        # name of map without ext (awesomemap)
        map_basename  = os.path.splitext(map_filename)[0]

        # name of map with .bsp ext (awesomemap.bsp)
        map_bspname = map_basename+".bsp"

        # Directory where the map lives (/path/to/)
        map_directory = os.path.dirname(map_full_path)+os.sep

        # Full path to .bsp file (/path/to/awesomemap.bsp)
        bsp_full_path = map_directory + map_basename + ".bsp"

        # Full path to .prt file (/path/to/awesomemap.prt)
        prt_full_path = map_directory + map_basename + ".prt"

        # Full path to .lit file (/path/to/awesomemap.lit)
        lit_full_path = map_directory + map_basename + ".lit"
        """ End Setup Paths =========================== """

        """ Handle output destination. If dest is specified in MAP profile
        use that. If not specified in MAP profile, use MOD profile as output
        =============================================== """
        if not mmap['dest']:
            bsp_destination = base_path + os.sep + mod['subdir'] + os.sep + "maps" + os.sep + map_basename + ".bsp"
        else:
            bsp_destination = mmap['dest'] + os.sep + map_basename + ".bsp"    

        # Change into map_directory for generation of log files in build dir.
        os.chdir(map_directory)

        """ Create QBSP Command """
        qbsp = self.getTool(builder, 'qbsp')
        # Build command list for subprocess.run()
        # executable + args + path_to_.map_fie
        qbsp_cmd = [qbsp['path']] + qbsp['args'] + [map_full_path]

        """ Create VIS Command """
        vis = self.getTool(builder, 'vis')
        # Build command list for subprocess.run()
        # executable + args + path_to_.bsp_file
        vis_cmd = [vis['path']] + vis['args'] + [bsp_full_path]

        """ Create LIGHT Command """
        light = self.getTool(builder, 'light')
        # Build command list for subprocess.run()
        # executable + args + path_to_.bsp_file
        light_cmd = [light['path']] + light['args'] + [bsp_full_path]

        # Run QBSP, VIS, LIGHT
        qbsp_time = self.runTool(qbsp_cmd)

        vis_time = self.runTool(vis_cmd)

        light_time = self.runTool(light_cmd)

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
        print("QBSP:\t"+qbsp_time['h']+"\t"+qbsp_time['m']+"\t"+qbsp_time['s']+"\t"+" ".join(qbsp['args']))
        print("VIS :\t"+vis_time['h']+"\t"+vis_time['m']+"\t"+vis_time['s']+"\t"+" ".join(vis['args']))
        print("LIGHT:\t"+light_time['h']+"\t"+light_time['m']+"\t"+light_time['s']+"\t"+" ".join(light['args']))

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
                    engine_exe = ['open'] + [engine_path, '--args']
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

""" =================================== EXCEPTIONS ============================
=========================================================================== """
class ProfileNotFoundException(Exception):
    def __init__(self, pType, profile_name):
        print("ERROR: Profile Not Found: Type="+pType+" Name="+profile_name)
        print("")

class NoDefaultProfileException(Exception):
    def __init__(self, pType):
        print("ERROR: No default profile for: "+pType)
        


""" =================================== MAIN ==================================
=========================================================================== """
def main():
    config_file = 'qruncher.json'
    app = QCompile(config_file)

    if len(app.opts) <= 2: # Config Mode
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


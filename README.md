# Qruncher
Profile based task manager for compiling quake style maps.

Qruncher manages the entire task of compiling your map. All the components of the build process are saved as profiles so you can reuse these profiles on different maps, engines etc. Profiles are saved in a json file so its easy to read and modify.

## What is managed as a profile?
### Overview
- **Build:** The build profile saves all the options for qbsp, vis and light. Useful for having a different set of options for debugging, testing, release.
- **Map:** The map profile saves the map source and destination paths.
- **Engine:** The engine profile saves different engines so you can test your map with multiple engines easily.
- **Mod:** The mod profile saves information about the mod. Useful for managing multiple 'mods' along with vanilla.

### Build Profile
The build profile manages the three basic tools for compiling a map. QBSP, VIS and LIGHT. It stores the executable path so you can have different executables in different profiles. It also stores all of the command line options for each of the three tools.

This can be very useful for having a profile for debugging, testing and release. In debugging you may have options that are NOT for release such as -dirtdebug.  Your release compile might have everything cranked up and you dont want to do that every time you squonk a brush over 16 units. 
##### Structure
- **name**: (String) The name of the profile. Must be unique.
- **default**: (Boolean) Only one can be True, and it will be default. All others false.
- **tools**: (Array)
-**name**: (String) The name of the tool. Must be unique.
-**path**: (String) Path to the tool. If this is set as a full path to executable, it will be used. If it is set to 'false', then 'name' will be appended to 'tool_path' and used in the compiler. This of 'false' as the default.
-**args**: (Array) Each argument for the tool should have its own entry in this array. Even for arguments that have multiple entries such as '-threads 6'
##### Example BUILD Profile:
```json
{
      "name": "default",
      "default": true,
      "tools": [
        {
          "name": "qbsp",
          "path": "c:\quake\tools\ericw\qbsp.exe",
          "args": [
            "-noverbose",
            "-bsp2"
          ]
        },
        {
          "name": "light",
          "path": "/opt/games/quake/tools/qbsp",
          "args": [
            "-extra4",
            "-bouncedebug"
          ]
        },
        {
          "name": "vis",
          "path": false,
          "args": [
            "-noambient",
            "-level 3"
          ]
        }
      ]
    }
```

### Map Profile
The map profile manages the locations of the .map file your editor produces. It stores the 'source' and 'destination'.

Many people work on multiple maps, and not just one till its done. The map profile saves you the time of having to either select the .map file from a file selector window, or typing out the full path when you want to switch between maps you are working on.

##### Structure
- **name**: (String) The name of the profile. Must be unique.
- **default**: (Boolean) Only one can be True, and it will be default. All others false.
- **source**: (String) Full path to the .map file. 
- **dest**: (String/False): If this is NOT 'false', the compiler will use this as the destination of where it copies the .bsp file to when everything is done. If it is set to 'false' the compiler will copy the .bsp to the correctly location as specified by the 'base_path' and **mod** profile.

##### Example MAP profile
```json
{
      "name": "default",
      "default": false,
      "source": "c:\quake\map-dev\radical.map",
      "dest": false
}
```

### Engine Profile
The engine profile manages the path to the executable and the OPTIONAL command line arguments. The MANDATORY command line arguments for loading a map directly such as -basedir +map (and -game if using a mod) are all handled by qruncher. 

Having multiple engine profiles allows you to easily test your map with different engines by a single command line switch.

##### Structure
- **name**: (String) Name of the profile. Must be unique.
- **default**: (Boolean) Only one can be True, and it will be default. All others false.
- **path**: (String) The full path to the engine executable.
- **args**: (Array) Each argument for the tool should have its own entry in this array. **NOTE:** +map, -basedir, -game will all be added by qruncher. You only need to specify optional arguments such as windowed, resolution etc. 

##### Example ENGINE Profile
```json
    {
      "name": "quakespasm",
      "default": true,
      "path": "/opt/games/quake/QuakeSpasm-SDL2",
      "args": [
        "-noipx"
      ]
    }

```

### Mod Profile



## Why did you make this? 
This is the basic workflow for compiling/testing maps:
1. Save .map file in editor
2. Run qbsp against .map file
3. Run vis against .bsp file
4. Run light against .bsp file
5. Copy file to the correct folder for your engine
6. Launch quake engine with appropriate flags to run your map.

This can be accomplished in many ways. There are GUI's, tools built into the editor, batch files, scripts etc. I find many of these methods to be cumbersome to my workflow. I just want to ALT-TAB up arrow and Enter. For that, I started creating batch files and scripts to compile maps. Then I found that I was copying these scripts for debugging, different mods, different engines etc. I wanted a way to compile my maps with a simple command line that allowed for all of those options.

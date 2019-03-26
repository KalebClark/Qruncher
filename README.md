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
##### Example profile:
```json
{
      "name": "default",
      "default": true,
      "tools": [
        {
          "name": "qbsp",
          "path": false,
          "args": [
            "-noverbose",
            "-bsp2"
          ]
        },
        {
          "name": "light",
          "path": false,
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

### Engine Profile

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

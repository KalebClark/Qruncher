# QCruncher
Profile based task manager for compiling quake style maps.

QCruncher manages the entire task of compiling your map. All the components of the build process are saved as profiles so you can reuse these profiles on different maps, engines etc.

What is managed as a profile?
- **Build:** The build profile saves all the options for qbsp, vis and light. Useful for having a different set of options for debugging, testing, release.
- **Map:** The map profile saves the map path, as well as a destination.
- **Engine:** The engine profile saves different engines so you can test your map with multiple engines easily.
- **Mod:** The mod profile saves information about the mod. Useful for managing multiple 'mods' along with vanilla.

Here is the basic workflow for compiling/testing maps:
1. Save .map file in editor
2. Run qbsp against .map file
3. Run vis against .bsp file
4. Run light against .bsp file
5. Copy file to the correct folder for your engine
6. Launch quake engine with appropriate flags to run your map.

This can be accomplished in many ways. There are GUI's, tools built into the editor, batch files, scripts etc. I find many of these methods to be cumbersome to my workflow. I just want to ALT-TAB up arrow and Enter.

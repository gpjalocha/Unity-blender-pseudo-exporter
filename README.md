# Unity-blender-pseudo-exporter

## INFO
This repo contains python blender script to migrate mesh by scanning input FBX file and ingesting blender mesh data into FBX mesh data.

It's a workaround for blender FBX exporter which doesn't work 100% correctly and messes some armaure data. Mainly tested on shredders assets

## Features

Script migrates following mesh data:

* Vertices data
* Normals, binormals and tangents
* UV data
* Vertices bone weights

## Prerequisites

Script was tested on blender 4 and on FBX models exported from Unity 2021.3.17f1 so it's recommended to have exact same versions. It's also necessary to either have some tool for FBX binary<->ascii conversion, or to export in unity the same model twice, in binary and in ascii.

## Usage

* Import exported unity asset to blender. Use the default import options + autmatic armature orientation.
* Prepare ascii version of imported FBX. Either convert it to some other file, or export in unity the same model but in ASCII.
* Modify the mesh as you like.
* In the `scripting` tab in blender open the `fbxreplacer.py` file.
* Replace the `fbxAsciiPathIn` to path to your ASCII fbx and `fbxAsciiPathOut` as the path to the file you want the model to be _exported_ to.
* Run the script.
* File should be exported correctly. Check in unity if model looks fine.

In case of any bugs raise incident or dm me.

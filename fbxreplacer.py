import bpy
import re
import numpy as np
import os


fbxAsciiPathIn="D:/shredders_mods/rider/Assets/fbxAscii/coat8Untitled.fbx"
fbxAsciiPathOut="D:/shredders_mods/rider/Assets/fbxAscii/coat8_testBlender.fbx"

# Get the active object
obj = bpy.context.active_object

def retreive_uv():
    if obj and obj.type == 'MESH':
        mesh = obj.data
        if mesh.uv_layers:
            uv_coordinates_dict = {}
            uv_indices_per_face = []
            for face in mesh.polygons:
                uv_indices_for_face = []
                for loop_index in face.loop_indices:
                    loop = mesh.loops[loop_index]
                    uv_coordinates = mesh.uv_layers.active.data[loop.index].uv
                    uv_coordinates_tuple = (uv_coordinates.x, uv_coordinates.y)
                    if uv_coordinates_tuple not in uv_coordinates_dict:
                        uv_coordinates_dict[uv_coordinates_tuple] = len(uv_coordinates_dict)
                    uv_indices_for_face.append(uv_coordinates_dict[uv_coordinates_tuple])
                uv_indices_per_face.append(uv_indices_for_face)
            deduplicated_uv_coordinates = list(uv_coordinates_dict.keys())
            return str(len(deduplicated_uv_coordinates)*2),str(len(uv_indices_per_face)*3),','.join([','.join([str(a),str(b)]) for a,b in deduplicated_uv_coordinates]) , ','.join([','.join([str(a),str(b),str(c)]) for a,b,c in uv_indices_per_face]) , 
        else:
            print("No UV data found for the mesh.")
    else:
        print("No active mesh object found.")


def add_vertex_weights_to_data(boneName,boneId,data):
    vertex_group = obj.vertex_groups[boneName]
    vertex_weights = [(v.index, g.weight) for v in obj.data.vertices for g in v.groups if g.group == vertex_group.index]
    data[boneId]={
        'Indexes':{
            'length': str(len(vertex_weights)),
            'data'  : ','.join([str(a) for a,b in vertex_weights])
            },
        'Weights':{
            'length': str(len(vertex_weights)),
            'data'  : ','.join([str(b) for a,b in vertex_weights])}}
    return data
    


def replace_mesh_fbx_data(file_in,file_out,overwrite=True):
    obj = bpy.context.active_object
    #Mesh exported from unity should be named Scene, extract this model ID first
    #line modes:
    #  read=1 looking for the mesh to write (write lines by default, write=1)
    #  read=0 found the mesh to overwrite  (write lines by default, write=1)
    #  read=-1 found data block type to be replaced, write mesh data and set write=-1 to avoid writing, read=0
    #  read=0, write=1 - found line with end bracket. Continue finding other data blocks to replace
    #fetch object ID first
    #Prepare data
    obj.data.calc_tangents()
    uvCoordsLen,uvIndLen,uvCoords,uvInd=retreive_uv()
    id=''
    id_bone=''
    dataObj={}
    with open(file_in,'r') as in_fbx:
        read=1
        for line in in_fbx:
            if re.match(pattern=(".+;Geometry::Scene, Model::%s" % re.search('^(.+?)(\.\d\d\d)?$',obj.name)[1]),string=line):
                read=0
                #print(line)
                continue
            if read==0:
                id=re.search('C: "OO",([0-9]+),',line)[1]
                dataObj={
                    id:{
                        "Vertices":{
                            "length":str(len(getattr(obj.data,'vertices'))*3),
                            "data":','.join([','.join([str(x) for x in a.co]) for a in getattr(obj.data,'vertices')])
                        },
                        "PolygonVertexIndex":{
                            "length":str(len(getattr(obj.data,'polygons'))*3),
                            "data":','.join([','.join([str(x if i%3!=2 else -x-1) for i,x in enumerate(a.vertices)]) for a in getattr(obj.data,'polygons')])
                            },
                        "Normals":{
                            "length":str(len(obj.data.loops)*3),
                            "data":','.join([','.join([str(a) for a in np.cross(a.tangent,a.bitangent)]) for a in obj.data.loops])
                        },
                        "Binormals":{
                            "length":str(len(obj.data.loops)*3),
                            "data":','.join([','.join([str(x) for x in a.bitangent]) for a in obj.data.loops])
                        },
                        "Tangents":{
                            "length":str(len(obj.data.loops)*3),
                            "data":','.join([','.join([str(x) for x in a.tangent]) for a in obj.data.loops])
                        },
                        "UV":{
                            "length":uvCoordsLen,
                            "data":uvCoords
                        },
                        "UVIndex":{
                            "length":uvIndLen,
                            "data":uvInd
                        }}}
                read=-1
            if read==-1:
                break
    #fetch bones IDs. Scan existing vertex groups first from mesh in blender and then scan
    #the file for the corresponding names to fetch IDs
    boneNames=[a.name for a in obj.vertex_groups]
    with open(file_in,'r') as in_fbx:
        read=1
        for line in in_fbx:
            if re.match(pattern=r'.+;Model::Bip01.+?, SubDeformer::BoneWeightCluster',string=line):
                #check if bone in fbx file have corresponding vertex group here in blender
                #there is Bip01 that doesn't have weights even in fbx
                #and there might be some other stuff
                #print('some bone line matches')
                boneNameFbx=re.search(pattern=r".+;Model::(Bip01.+?), SubDeformer::BoneWeightCluster",string=line)[1]
                if boneNameFbx in boneNames:
                    print('found matching bone %s' % boneNameFbx)
                    read=0
                    print(line)
                else:
                    print('not matching bone weigh: %s' % boneNameFbx)
                continue
            if read==0:
                id_bone=re.search('C: "OO",[0-9]+,([0-9]+)',line)[1]
                vertex_group = obj.vertex_groups[boneNameFbx]
                vertex_weights = [(v.index, g.weight) for v in obj.data.vertices for g in v.groups if g.group == vertex_group.index]
                dataObj[id_bone]={
                    'Indexes':{
                        'length': str(len(vertex_weights)),
                        'data'  : ','.join([str(a) for a,b in vertex_weights])
                        },
                    'Weights':{
                        'length': str(len(vertex_weights)),
                        'data'  : ','.join([str(b) for a,b in vertex_weights])}}
                read=-1
    print('going to replace obj %s' % id)
    read=1
    write=1
    objAttr=''
    type_replace=''
    currentObjId=''
    if os.path.exists(file_out):
        # If overwrite is True, clear out the file
        if overwrite:
            with open(file_out, 'w') as f:
                pass  # Clears the file
        else:
            raise Exception("File already exists. Use overwrite=True to overwrite.")
    with open(file_in,'r') as in_fbx:
        #print('going to with open %s' % id)
        for line in in_fbx:   
            with open(file_out, 'a') as out_fbx:
                regexReplPattern='\s+Geometry: %s, "Geometry::Scene", "Mesh"' % id
                boneReplPattern='\s+Deformer: ('+ '|'.join(dataObj.keys()) +'), "SubDeformer::BoneWeightCluster", "Cluster" {'
                regexReplPattern+='|'+boneReplPattern
                if re.match(pattern=regexReplPattern, string=line):
                    read=0
                    #print('Found geometry or bone')
                    #print(line)
                    currentObjId=re.search(r'.+: ([0-9]+),',line)[1]
                    print(currentObjId)
                    out_fbx.write(line)
                    continue
                #UNIVERSAL READ ATTR OBJ
                regexObjAttr=r"\s+("+'|'.join(dataObj[id].keys())+"|Weights|Indexes):"
                if read==0 and re.match(regexObjAttr,line):
                    #print(line)
                    objAttr=re.search(regexObjAttr,line)[1]
                    #print(currentObjId,objAttr)
                    data_to_write=dataObj[currentObjId][objAttr]
                    #type_replace='vertices'
                    print('replacing %s data' % objAttr )
                    write=0
                    read=-1
                    out_fbx.write(re.sub(r'[0-9]+',data_to_write['length'],line))
                    continue
                if write==1:
                    out_fbx.write(line)
                if write==-1 and re.match('\s*}',line):
                    out_fbx.write('\n'+line)
                    #print('end bracket, wrote %s' % line)
                    write=1
                    read=0
                    if objAttr in ['Weights','UVIndex']: read=1; write=1
                    #if type_replace=='polygons': debugLine=True
                    continue
                if write==0 and objAttr!='':
                    write=-1
                    read=0
                    stringPrefix=re.match(r'\s+a: ',line)[0]
                    out_fbx.write(stringPrefix+data_to_write['data'])
                        
                

replace_mesh_fbx_data(fbxAsciiPathIn,fbxAsciiPathOut,overwrite=True)
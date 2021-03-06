import maya.cmds as cmds
import maya.mel as mel

import os


def get_op_context():
    """
    Gets openPipeline optionVars and returns them as a python dict
    """
    op_context = {
        'level1': cmds.optionVar(q='op_currOpenLevel1'),
        'level2': cmds.optionVar(q='op_currOpenLevel2'),
        'level3': cmds.optionVar(q='op_currOpenLevel3'),
        'tab': cmds.optionVar(q='op_currOpenTab'),
        'category': cmds.optionVar(q='op_currOpenCategory'),
        'version': cmds.optionVar(q='op_currOpenVersion'),
        'proj_name': cmds.optionVar(q='op_currProjectName'),
        'proj_path': cmds.optionVar(q='op_currProjectPath'),
        'lib_path': cmds.optionVar(q='op_libPath'),
        'shot_path': cmds.optionVar(q='op_shotPath'),
    }
    return op_context


def create_workspaces(asset_type, asset_name):
    """
    Creates default asset workspaces
    """
    workspaces = {
        'texturing': {
            'photoshop': ['textures', 'sourceimages'],
            'substancePainter': ['sourceimages', 'meshes', 'projects'],
            'mari': ['projects', 'sourceimages', 'meshes']
        },
        'modeling': {
            'zbrush': ['obj', 'ztools'],
        }
    }
    asset_root = mel.eval(
        'openPipelineGetFileName 2 "{asset_type}" "{asset_name}" "" "folder" 0 0'
        .format(asset_type=asset_type, asset_name=asset_name))
    work_root = os.path.join(asset_root, 'work')
    for workspace in workspaces:
        workspace_root = os.path.join(work_root, workspace)
        for dir in workspaces[workspace]:
            os.makedirs(os.path.join(workspace_root, dir))
            for subdir in workspaces[workspace][dir]:
                os.makedirs(os.path.join(workspace_root, dir, subdir))


def collect_bake_sets():
    """
    returns a list of dicts of bake sets in the scene
    """
    set_name = 'bake_SET' # this is the name we're looking for!!
    obj_sets = cmds.ls(type='objectSet')
    bake_sets = []

    for obj_set in obj_sets:
        if set_name in obj_set:
            bake_sets.append(obj_set)

    bake_set_dicts = []

    for bake_set in bake_sets:
        members = cmds.sets(bake_set,q=True)
        [x.encode('UTF8') for x in members]

        # check for cache attrs
        step = 1
        if cmds.attributeQuery('step', node=bake_set, exists=1):
            step = cmds.getAttr(bake_set+'.step')
        static = 0
        if cmds.attributeQuery('static', node=bake_set, exists=1):
            static = cmds.getAttr(bake_set+'.static')

        bake_dict = {
            'name': bake_set,
            'members': members,
            'step': step,
            'static': static,
        }

        bake_set_dicts.append(bake_dict)

    return bake_set_dicts


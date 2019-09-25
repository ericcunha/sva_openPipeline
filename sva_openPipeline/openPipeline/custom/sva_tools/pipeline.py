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

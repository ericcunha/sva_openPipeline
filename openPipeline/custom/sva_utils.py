import maya.cmds as cmds
import maya.mel as mel

import os


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

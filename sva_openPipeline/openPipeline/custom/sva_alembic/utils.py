import maya.cmds as cmds
import os


def get_op_file_info():
    """
            queries openPipeline optionVars for the currently open file

            return:
            op_file_info = a dictionary with the following keys:values:
                                    tab = currently open tab
                                    cat = whether it's a shot, asset type, or component
                                    level1 = currently open level1
                                    level2 = currently open level2
                                    level3 = currently open level3
                                    version = currently open version
    """
    op_file_info = {
        "tab": cmds.optionVar(q='op_currOpenTab'),
        "cat": cmds.optionVar(q='op_currOpenCategory'),
        "level1": cmds.optionVar(q='op_currOpenLevel1'),
        "level2": cmds.optionVar(q='op_currOpenLevel2'),
        "level3": cmds.optionVar(q='op_currOpenLevel3'),
        "version": cmds.optionVar(q='op_currOpenVersion'),
    }
    return op_file_info


def get_op_proj_info():
    """
            queries openPipeline project related optionVars

            return:
            op_proj_info = a dictionary with the following keys & values:
                                    proj_name = current project name
                                    proj_path = current project path
                                    lib_path = current project lib path
                                    shot_path = current project shot path
                                    asset_types = all asset types in current project
    """
    op_proj_info = {
        "proj_name": cmds.optionVar(q='op_currProjectName'),
        "proj_path": cmds.optionVar(q='op_currProjectPath'),
        "lib_path": cmds.optionVar(q='op_libPath'),
        "shot_path": cmds.optionVar(q='op_shotPath'),
        "asset_types": cmds.optionVar(q='op_assetTypes'),
    }
    return op_proj_info


def get_cache_dir():
    """
            gets the cache dir for the currently open shot in openPipeline

            return:
            cache_dir = the cache directory
    """
    proj_context = get_op_proj_info()
    shot_path = proj_context['shot_path']

    shot_context = get_op_file_info()
    level1 = shot_context['level1']
    level2 = shot_context['level2']
    level3 = shot_context['level3']

    cache_dir = os.path.join(
        shot_path, level1, level2, 'cache', 'alembic', level3
    ).replace('/', '\\')

    return cache_dir

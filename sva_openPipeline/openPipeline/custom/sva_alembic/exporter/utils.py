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
		"tab" : cmds.optionVar(q='op_currOpenTab'),
		"cat" : cmds.optionVar(q='op_currOpenCategory'),
		"level1" : cmds.optionVar(q='op_currOpenLevel1'),
		"level2" : cmds.optionVar(q='op_currOpenLevel2'),
		"level3" : cmds.optionVar(q='op_currOpenLevel3'),
		"version" : cmds.optionVar(q='op_currOpenVersion'),
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
		"proj_name" : cmds.optionVar(q='op_currProjectName'),
		"proj_path" : cmds.optionVar(q='op_currProjectPath'),
		"lib_path" : cmds.optionVar(q='op_libPath'),
		"shot_path" : cmds.optionVar(q='op_shotPath'),
		"asset_types" : cmds.optionVar(q='op_assetTypes'),
	}
	return op_proj_info


def get_cache_dir(proj_path, tab, level1, level2, level3):
	"""
		gets the cache dir for the currently open shot in openPipeline

		args:
		proj_path = path to the current project
		tab = the currently open tab in openPipeline
		level1 = currently open level1 in openPipeline
		level2 = currently open level2 in openPipeline

		return:
		cache_dir = the cache directory
	"""
	cache_dir = os.path.join(proj_path, 'cache', 'alembic', level1, level2, level3).replace('/', '\\')
	return cache_dir


def get_bake_sets():
    """
        gets all the bakeSets in the scene along with some useful info for each

        return:
        bake_sets = a nested dictionary where the keys are all of the bakeSets and the nested dict is:
                    namespace = the namespace of the bake sets (if not a reference, grabs the prefix of the bakeSet)
					asset_type = the asset type from openPipeline (if not an op asset, will return 'custom')
					path = the path of the referenced file (returns none as a string if not a reference)
    """
    sets = cmds.ls('::*bake_SET')
    bake_sets = {}
    for bake_set in sets:
        namespace = ''
        asset_type = ''
        path = ''

        # if it's referenced, get the namespace and file path
        if cmds.referenceQuery(bake_set, inr=1):
            namespace = bake_set.rpartition(':')[0]
            path =  cmds.referenceQuery(bake_set, filename=True, wcn=1)
            if '/lib/' in path:
                asset_type = path.split('/lib/')[1].split('/')[0]
            else:
                asset_type = 'custom'

        # if not, just store the prefix of the bakeSet
        else:
            namespace = bake_set.rpartition('_')[0]
            asset_type = 'custom'
            path = 'none'

        bake_sets[bake_set] = {
            'namespace' : namespace,
            'asset_type' : asset_type,
            'path' : path,
        }

    return bake_sets

def get_shot_assets():
    """
        gets the asset types for all bake sets in the currently open shot
    """

    assets = []
    refs = cmds.file(q=1, r=1)
    for ref in refs:
        if '/lib/' in ref:
            assets.append(ref.split('/lib/')[1].split('/')[0])
    return sorted(set(assets))

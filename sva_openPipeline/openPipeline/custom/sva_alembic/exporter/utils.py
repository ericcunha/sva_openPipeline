from bakeset import Bakeset
import maya.cmds as cmds
import maya.mel as mel
import os
import traceback

import sva_alembic.utils
import bakeset
reload(bakeset)


def get_bake_sets():
    """
        gets all the bakeSets in the scene and creates a Bakeset object for them

        return:
        bake_sets = a list of Bakeset objects
    """
    sets = cmds.ls('::*bake_SET')
    bake_sets = []
    for bake_set in sets:
        bake_sets.append(bakeset.Bakeset(bake_set))
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


def get_cache_file(namespace, cache_path):
    # get cache version
    cache_files = []
    for file in os.listdir(cache_path):
        if file.endswith('.abc'):
            cache_files.append(file)

    # build filename
    version = str(len(cache_files)+1).zfill(3)
    filename = (namespace + '_cache_v' + version + ".abc")
    cache_file = os.path.join(cache_path, filename)

    return cache_file


# def get_frame_range(static=0):
#     start = cmds.playbackOptions(q=True, min=True)
#     end = cmds.playbackOptions(q=True, max=True)
#     current = cmds.currentTime(q=True)
#     if static:
#         start = current
#         end = current
#     frange = [start, end]
#     return frange


def get_abc_job(bake_set, frame_range):
    # reload our bake_set
    bake_set.reload()

    # make the cache dir
    cache_dir = sva_alembic.utils.get_cache_dir()
    cache_path = os.path.join(cache_dir, bake_set.category, bake_set.namespace)
    if not os.path.isdir(cache_path):
        os.makedirs(cache_path)

    # get the cache file name
    cache_file = get_cache_file(bake_set.namespace, cache_path)

    # build the roots command string
    root_cmd = '-root {}'.format(' -root '.join(bake_set.members))

    # build the alembic command string
    step = bake_set.step
    static = bake_set.static
    # frame_range = get_frame_range(static)

    job = ("-frameRange " + str(frame_range[0]) + " " + str(frame_range[1]) + " -step " + str(
        step) + " -wuvs -uvWrite -worldSpace -writeVisibility -dataFormat ogawa " + root_cmd + " -file \\\"" + cache_file.replace('\\', '/') + "\\\"")
    return job


def export_abc(job):
    if not cmds.pluginInfo('AbcExport.mll', q=True, loaded=True):
        cmds.loadPlugin('AbcExport.mll')
    try:
        cmd = "AbcExport -j \"" + job + "\";"
        mel.eval(cmd)
    except:
        print(traceback.format_exc())

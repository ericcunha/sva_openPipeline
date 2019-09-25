import maya.cmds as cmds
import maya.mel as mel
import os
from shutil import copyfile

import sva_tools.abc
reload(sva_tools.abc)
import sva_tools.sets
reload(sva_tools.sets)


def export_abc_model():
    """
    Exports a static alembic cache of the model for SHD
    """
    file, version = sva_tools.abc.get_static_model_path()

    bake_set = sva_tools.sets.collect_bake_sets()
    if bake_set:
        if len(bake_set) > 1:
            raise Exception("Can't have more than 1 bake_SET on the asset level!")

        models = bake_set[0]['members']
        frame = str(cmds.currentTime(q=True))

        # export alembic
        if not cmds.pluginInfo('AbcExport.mll',q=True,loaded=True):
            cmds.loadPlugin('AbcExport.mll')

        root_cmd = ""
        if len(models) > 1:
            for model in models:
                root_cmd += "-root " + model + " "
        else:
            root_cmd = "-root " + models[0] + " "

        job = ("-frameRange " + frame + " " + frame + " -stripNamespaces -wuvs -uvWrite -worldSpace -writeVisibility -dataFormat ogawa " + root_cmd + " -file " + file.replace('\\','/'))
        mel.eval("AbcExport -j \"" + job + "\";")

        copyfile(file, version)

import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds


def namespacer(cache, namespaces):
    cmds.file(f=1, new=1)
    if not cmds.pluginInfo('AbcExport', q=1, l=1):
        cmds.loadPlugin('AbcExport')
    # create the namespaces
    for namespace in namespaces:
        cmds.namespace(add=namespace)
    # import the alembic
    command = "AbcImport -mode import {}".format(cache)
    mel.eval(command)
    # save scene
    scene_name = os.path.basename(cache).rstrip('.abc')+'.mb'
    scene_path = os.path.join(os.path.dirname(cache), scene_name)
    file = cmds.file(scene_path, f=1, s=1)
    return file

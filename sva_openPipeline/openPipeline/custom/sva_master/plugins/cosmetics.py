import maya.cmds as cmds


def delete_display_layers():
    """
    Deletes all the display layers in the scene
    """
    layers = cmds.ls(type='displayLayer')
    for layer in layers:
        if layer != 'defaultLayer':
            cmds.delete(layer)
            print('Deleted {}'.format(layer))


def delete_junk_grp():
    """
    Deletes objects in a group named JUNK
    """
    junk = 'JUNK'
    if cmds.objExists(junk):
        cmds.delete(junk)
        if cmds.objExists(junk):
            raise Exception(
                '{junk} group could not be deleted, check contents'.format(
                    junk=junk))
        else:
            print('Deleted {junk} group'.format(junk=junk))

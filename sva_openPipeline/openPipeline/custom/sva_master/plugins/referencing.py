import maya.cmds as cmds


def import_refs():
    """
    Imports all references in the scene
    Unloaded references will be removed
    """
    refs = cmds.file(reference=1, q=1)
    if refs:
        while refs:
            for ref in refs:
                # if it's unloaded, remove it
                if cmds.file(ref, dr=1, q=1):
                    cmds.file(ref, removeReference=1)
                    print('Removing reference to {} since it was unloaded.'.
                          format(ref))
                # else, import it
                else:
                    cmds.file(ref, importReference=1)
                    print('Imported reference to {}.'.format(ref))
            newRefs = cmds.file(reference=1, q=1)
            refs = newRefs


def remove_namespaces():
    """
    Removes all namespaces in the scene
    """
    allNS = cmds.namespaceInfo(listOnlyNamespaces=True)
    for ns in allNS:
        if ns != 'UI' and ns != 'shared':
            cmds.namespace(removeNamespace=ns, mergeNamespaceWithParent=True)
            print('Removed namespace: {}'.format(ns))

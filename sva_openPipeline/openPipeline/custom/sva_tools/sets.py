import maya.cmds as cmds


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


def create_bakeSet():
    """
        Creates a new bakeSet. If in a shot, prompts the user for a name.
    """
    bakeSet = 'bake_SET'
    tab = cmds.optionVar(q='op_currOpenTab')
    name = ''
    # check if we're in a shot
    if tab == 3:
        # ask the user for a set name so it's not the default
        result = cmds.promptDialog(title='Name bakeSet',
                                   message='Enter name for bakeSet:',
                                   button=['OK', 'Cancel'],
                                   defaultButton='OK',
                                   cancelButton='Cancel',
                                   dismissString='Cancel')

        if result == 'OK':
            name = cmds.promptDialog(query=True, text=True) + '_' + bakeSet
    # if we're in an asset, just use the default name
    else:
        name = bakeSet

    # create the set
    if not cmds.objExists(bakeSet):
        bakeSet = cmds.sets(name=name)

    # add cache options to bake set
    # static - whether or not we cache for the whole duration of the shot
    cmds.addAttr(bakeSet, ln='static', at='long', min=0, max=1, dv=0)
    cmds.setAttr(bakeSet + '.static', e=1, keyable=1)
    # step - the cache step size (sample every n'th frame)
    cmds.addAttr(bakeSet, ln='step', at='double', min=0, dv=1)
    cmds.setAttr(bakeSet + '.step', e=1, keyable=1)

    return bakeSet

import maya.cmds as cmds
import os
import maya.app.renderSetup.model.renderSetup as renderSetup
import maya.cmds as cmds
import mtoa.aovs as aovs


def set_fnp():
    """
        set the file name prefix for the current shot in openPipeline
    """
    seq = cmds.optionVar(q='op_currOpenLevel1')
    shot = cmds.optionVar(q='op_currOpenLevel2')

    path = os.path.join(seq, shot, '<Scene>', '<RenderLayer>', '<Scene>.<RenderLayer>').replace('\\', '/')
    cmds.setAttr('defaultRenderGlobals.imageFilePrefix', path, type='string')


def make_aov(aov, type='rgb'):
    """
        Creates an AOV if it doesn't already exist.

        Args:
        aov = The name of the AOV to make.
        type = The data type of the new aov. Valid values are:
            int
            bool
            float
            rgb
            rgba
            vector
            vector2
            pointer
    """
    allowed_types = ['int', 'bool', 'float', 'rgb', 'rgba', 'vector', 'vector2', 'pointer']
    if type not in allowed_types:
        raise Exception('Type {} is not allowed!'.format(type))

    all_aovs = aovs.AOVInterface().getAOVNodes(names=True)
    exists = 0
    for sublist in all_aovs:
        if aov in sublist:
            exists = 1
            print '{} AOV already exits!'.format(aov)
            break
    if not exists:
        aovs.AOVInterface().addAOV(aov, aovType=type)
        print 'created {}!'.format(aov)

def set_globals(renderer):
    """
        Sets the render globals for the current lighting scene.

        Args:
        renderer = the renderer you want to use (currently only support Arnold)

        Return:
        none
    """
    if renderer == 'arnold':
        # set arnold as the current renderer
        if not cmds.pluginInfo('mtoa', q=1, l=1):
            cmds.loadPlugin('mtoa')
        cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")

        # file name prefix
        set_fnp()

        # change EXR options
        cmds.setAttr("defaultArnoldDriver.ai_translator", 'exr', type='string')
        cmds.setAttr('defaultArnoldDriver.exrCompression', 2)
        cmds.setAttr('defaultArnoldDriver.halfPrecision', 1)
        cmds.setAttr('defaultArnoldDriver.mergeAOVs', 1)

        # animation settings
        cmds.setAttr('defaultRenderGlobals.outFormatControl', 0)
        cmds.setAttr('defaultRenderGlobals.animation', 1)
        cmds.setAttr('defaultRenderGlobals.putFrameBeforeExt', 1)
        cmds.setAttr('defaultRenderGlobals.extensionPadding', 4)

        # change resolution
        cmds.setAttr("defaultResolution.width", 1280)
        cmds.setAttr("defaultResolution.height", 720)

        # set verbosity level to output progress and render path
        cmds.setAttr('defaultArnoldRenderOptions.log_verbosity', 2)

        # disable auto tx conversion
        cmds.setAttr('defaultArnoldRenderOptions.autotx', 0)

        # make AOVs
        aov_list = {
            'N':'vector',
            'P':'vector',
            'RGBA':'rgba',
            'Z':'float',
            'coat_direct':'rgb',
            'coat_indirect':'rgb',
            'diffuse_direct':'rgb',
            'diffuse_indirect':'rgb',
            'emission':'rgb',
            'shadow_matte':'rgba',
            'specular_direct':'rgb',
            'specular_indirect':'rgb',
            'sss_direct':'rgb',
            'sss_indirect':'rgb',
            'transmission_direct':'rgb',
            'transmission_indirect':'rgb',
            'crypto_asset':'rgb',
            'crypto_material':'rgb',
            'crypto_object':'rgb',
            }

        for aov in aov_list:
            try:
                make_aov(aov, aov_list[aov])
            except:
                print 'could not set up {}'.format(aov)
            # if making a cryptomatte aov, create the shader and connect it!
            if 'crypto' in aov:
                crypto_shader = '_aov_cryptomatte'
                if not cmds.objExists(crypto_shader):
                    crypto_shader = cmds.createNode('cryptomatte', n=crypto_shader, ss=True)
                cmds.connectAttr(crypto_shader+'.outColor', 'aiAOV_'+aov+'.defaultValue', f=1)
                print 'connected cryptomatte shader to {}'.format(aov)

            # if making the RGBA light aov, check option for all light groups
            if 'RGBA' in aov:
                cmds.setAttr('aiAOV_'+aov+'.lightGroups', 1)

        print 'Arnold render globals set up succesfully!'


def remove_shading_edits():
    """
        removes shading reference edits on selected objects
    """
    sel = cmds.ls(sl=1, long=1)
    shapes = []
    ref_nodes = set()

    for obj in sel:
        if cmds.referenceQuery(obj, inr=1):
            obj_shapes = cmds.listRelatives(obj, f=1, s=1)
            if obj_shapes:
                shapes.extend(obj_shapes)
            else:
                shapes.extend(obj)
            ref_node = cmds.referenceQuery(obj, referenceNode=1)
            ref_nodes.add(ref_node)

    if ref_nodes:
        for ref_node in ref_nodes:
            cmds.file(unloadReference=ref_node)

        for shape in shapes:
            cmds.referenceEdit(shape+'.instObjGroups', removeEdits=1, failedEdits=1, successfulEdits=1, editCommand='connectAttr')
            cmds.referenceEdit(shape+'.instObjGroups', removeEdits=1, failedEdits=1, successfulEdits=1, editCommand='disconnectAttr')

        for ref_node in ref_nodes:
            cmds.file(loadReference=ref_node)

        print 'Done remove shading edits!'

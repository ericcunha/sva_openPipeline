import maya.cmds as cmds
import os
from . import pipeline

def get_static_model_path():
    """
    Returns the paths to the master model file and the version model file
    for exporting the static alembic for SHD
    """
    context = pipeline.get_op_context()
    proj_path = context['proj_path']
    level1 = context['level1']
    level2 = context['level2']
    tab = context['tab']
    if str(tab) == '2':
        tab = 'lib'
    if str(tab) == '3':
        tab = 'scenes'

    level3 = context['level3']
    cache_dir = os.path.join(proj_path,tab,level1,level2,'cache')
    cache_version_dir = os.path.join(cache_dir,'versions')

    # make the cache dirs
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)
    if not os.path.isdir(cache_version_dir):
        os.makedirs(cache_version_dir)

    # get cache version
    cache_files = []
    for file in os.listdir(cache_version_dir):
        if file.endswith('.abc'):
            cache_files.append(file)

    # build version filename
    version = str(len(cache_files)+1).zfill(3)
    version_filename = (level2 + '_cache_v' + version + ".abc")
    version_cache_file = os.path.join(cache_version_dir,version_filename)

    # build master filename
    filename = (level2 + "_cache.abc")

    model_file = os.path.join(cache_dir, filename)
    version_model_file = os.path.join(cache_version_dir, version_filename)
    return model_file, version_model_file

def reference_asset_abc():
    """
        References the asset cache into the current scene.
    """
    print '\n##################################\n\nReferencing asset cache...\n'

    # load the alembic plugin
    if not cmds.pluginInfo('AbcImport', q=1, l=1):
        cmds.loadPlugin('AbcImport')

    # make sure we're in an asset
    if cmds.optionVar(q='op_currOpenTab') != 2:
        raise Exception('Not in an asset!')

    # get the asset cache
    abc_cache = get_static_model_path()[0]
    asset_cache = ''
    if os.path.isfile(abc_cache):
        asset_cache = abc_cache
    else:
        raise Exception('There is no asset cache exported!')

    # make sure it isn't already referenced
    refs = cmds.file(q=1, r=1, wcn=1)
    if asset_cache not in refs:
        level2 = cmds.optionVar(q='op_currOpenLevel2')
        namespace = '{}_cache'.format(level2)
        # check if namespace exists already
        if cmds.namespace(exists=namespace):
            raise Exception(
                'The namespace {} already exists!'.format(namespace))
        # reference it!
        cmds.file(asset_cache, r=True, namespace=namespace)
        print 'Successfully referenced asset cache:\n{}'.format(asset_cache)
        print '\nUsing namespace:\n{}\n\n##################################'.format(
            namespace)

    else:
        print 'Asset cache already referenced, aborting...\n\n##################################'

import maya.cmds as cmds
import sva_alembic.utils

import os
import cask

import cache
# reload(cache)

# reload(sva_alembic.utils)


def get_assets(lib_path):
    """
        returns a dictionary where the keys are all of the assets in a project and the values are their asset types
    """
    asset_types = [x for x in os.listdir(lib_path) if os.path.isdir(os.path.join(lib_path, x))]
    asset_dict = {}
    for asset_type in asset_types:
        assets = [x for x in os.listdir(os.path.join(lib_path, asset_type)) if os.path.isdir(os.path.join(lib_path, asset_type, x))]
        for asset in assets:
            asset_dict[asset] = asset_type
    return asset_dict


def get_subdirs(path):
    subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return subdirs


def get_shot_caches(cache_dir):
    """
        Creates a cache object for every cache found for the scene
    """
    cache_scenes = [os.path.join(cache_dir, c) for c in os.listdir(cache_dir) if os.path.isdir(os.path.join(cache_dir, c))]
    # we need the namespaces to make the cache object so we don't look it up for eeevery cache
    proj_context = sva_alembic.utils.get_op_proj_info()
    refs = get_refs()
    assets = get_assets(proj_context['lib_path'])
    caches = []
    for cache_scene in cache_scenes:
        categories = get_subdirs(cache_scene)
        for category in categories:
            cat_caches = get_subdirs(os.path.join(cache_scene, category))
            for cat_cache in cat_caches:
                caches.append(cache.Cache(os.path.join(cache_scene, category, cat_cache), refs, assets))
    return caches


def get_refs():
    """
            returns a dict where the keys are namespaces in the scene
            and the values are the references that correspond
    """
    refs = cmds.file(q=1, r=1)
    ref_dict = {}

    for ref in refs:
        ref_node = cmds.referenceQuery(ref, rfn=True)
        namespace = cmds.referenceQuery(ref_node, namespace=True).lstrip(':')
        ref_dict[namespace] = {
            'path': ref.replace('/', os.sep),
            'clean_path': ref.split('{')[0].replace('/', os.sep),
            'ref_node': ref_node,
        }
    return ref_dict


def get_namespaces():
    cmds.namespace(setNamespace=':')
    default_namespaces = ['UI', 'shared']
    all_namespaces = cmds.namespaceInfo(listOnlyNamespaces=True, recurse=True)
    namespaces = [n for n in all_namespaces if n not in default_namespaces]
    return namespaces


def get_scene_alembics(shot):
    """
        returns a dict where the keys are namespaces in the scene
        and the values are the alembic node that corresponds to it
        followed by the file path of the alembic
    """
    if not cmds.pluginInfo('AbcImport.mll', q=1, loaded=1):
        cmds.loadPlugin('AbcImport.mll')

    alembic_nodes = cmds.ls(type='AlembicNode')
    alembic_dict = {}
    for node in alembic_nodes:
        file = cmds.getAttr(node+'.fn')
        if file:
            if shot in file:  # make sure the alembics correspond to this shot
                version = file.rpartition('.')[0].rpartition('v')[-1]
                namespace = file.split('/')[-2]

                existing_version = 0
                if namespace in alembic_dict:  # if this namespace is already stored, get it's version to compare
                    existing_file = alembic_dict[namespace]
                    existing_version = existing_file.rpartition('.')[0].rpartition('v')[-1]

                if version >= existing_version:  # if the current version is greater than the previously stored one, store the new one!
                    if namespace in alembic_dict:
                        pass
                        # cmds.delete(alembic_dict[namespace]) # delete the old one!
                        # THIS ISN'T DELETING SHIT! WE NEVER STORED THE FILE NODE
                    alembic_dict[namespace] = file.rpartition('/')[-1]
                else:
                    cmds.delete(node)  # delete the current one!

    return alembic_dict


def objs_from_abc(abc, children):
    """
            returns a list of objects from an alembic file

            args:
            abc = path to alembic file
            children = bool, whether or not to include the children, otherwise it will just return root objects

            return:
            abc_objs = the list of objects from the alembic file
    """
    abc_objs = []
    archive = cask.Archive(abc)

    def get_objs(obj):
        for child in obj.children.values():
            abc_objs.append((child.name).split(':')[-1])
            if children:
                get_objs(child)

    get_objs(archive.top)
    return abc_objs


def namespace_from_abc(abc):
    archive = cask.Archive(abc)

    for child in archive.top.children.values():
        if ':' in child.name:
            namespace = (child.name).split(':')[0]
            return namespace


def vis_from_abc(abc):
    """
            returns a list of objects from an alembic file

            args:
            abc = path to alembic file
            children = bool, whether or not to include the children, otherwise it will just return root objects

            return:
            abc_objs = the list of objects from the alembic file
    """
    abc_objs = []
    archive = cask.Archive(abc)

    def set_vis(obj):
        for child in obj.children.values():
            try:
                abc_objs.append(child.name)
                vis = 1
                if 'visible' in child.properties:
                    vis = child.properties['visible'].values[0]
                    if vis == -1:
                        vis = 1

                if cmds.objExists(child.name):
                    if cmds.attributeQuery('visibility', node=child.name, ex=1):
                        if not cmds.listConnections(child.name+'.visibility'):
                            cmds.setAttr(child.name+'.visibility', vis)
            except:
                print 'Could not update alembic vis on {}'.format(child.name)

            set_vis(child)
    set_vis(archive.top)


def swap_namespace(from_ns, to_ns):
    # temporarily swap the to_ns if it already exists
    tmp_ns_dict = []
    if cmds.namespace(exists=to_ns):
        tmp_ns = to_ns+str(1)
        while cmds.namespace(exists=tmp_ns):
            tmp_ns = tmp_ns+str(1)
        tmp_ns_dict.append({
            tmp_ns: to_ns,
        })
        swap_namespace(to_ns, tmp_ns)

    cmds.namespace(set=':')
    cmds.namespace(force=True, moveNamespace=(from_ns, to_ns))

    return tmp_ns_dict


def remove_namespace(namespace):
    if cmds.namespace(exists=namespace):
        cmds.namespace(set=':')
        cmds.namespace(force=True, moveNamespace=(namespace, ':'))
        cmds.namespace(removeNamespace=namespace)

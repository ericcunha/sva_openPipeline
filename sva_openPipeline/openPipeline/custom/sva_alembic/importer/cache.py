import maya.cmds as cmds
import maya.mel as mel
import os

import sva_alembic.utils
import utils


class Cache():
    def __init__(self, path, refs, assets):
        self.path = path
        self.refs = refs
        self.assets = assets
        self.asset_name = self.path.split(os.sep)[-1].split('_')[0]
        self.namespace = self.get_namespace()

        self.proj_context = sva_alembic.utils.get_op_proj_info()

        self.category = ''
        self.scene = ''
        self.abcs = []

        self.status = ''  # unloaded, current, old
        self.mode = None  # reference, attach
        self.loaded_abc = None
        self.shds = []
        self.loaded_shd = None
        self.abc_node = None
        self.latest_abc = None
        self.ref_node = None

        self.gui = None

        self.refresh()

    def refresh(self):
        self.category = self.get_category()
        self.scene = self.get_scene()
        self.abcs = self.get_abcs()
        self.latest_abc = self.get_latest_abc()
        self.shds = self.get_shds()

        self.get_loaded_abc()

        self.status = self.get_status()

    def get_category(self):
        category = self.path.split(os.sep)[-1]
        return category

    def get_scene(self):
        scene = self.path.split(os.sep)[-3]
        return scene

    def get_abcs(self):
        caches = [os.path.join(self.path, x) for x in os.listdir(self.path) if x.endswith('.abc')]
        return caches

    def get_namespace(self):
        path_split = self.path.split(os.sep)
        namespace = '{cache_scene}_{cache_namespace}'.format(
            cache_scene=path_split[-3],
            cache_namespace=path_split[-1]
        )
        return namespace

    def get_shds(self):
        shds = []

        components = self.get_components()
        shd_components = [c for c in components if 'SHD' in os.path.basename(c)]
        for shd in shd_components:
            publishes = [f for f in os.listdir(shd) if os.path.isfile(os.path.join(shd, f))]
            if publishes:
                shds.append({
                    'name': os.path.basename(shd),
                    'path': os.path.join(shd, publishes[0]),
                })
        return shds

    def get_components(self):
        components = []
        if self.path.split(os.sep)[-2] == 'asset':
            if self.asset_name in self.assets:
                category = self.assets[self.asset_name]
                component_path = os.path.join(
                    self.proj_context['lib_path'].replace('/', os.sep),
                    category,
                    self.asset_name,
                    'components',
                )
                components = [os.path.join(component_path, d) for d in os.listdir(component_path) if os.path.isdir(os.path.join(component_path, d))]
        return components

    def get_loaded_abc(self):
        # check if the namespace we're looking for is already in the scene
        if self.namespace in self.refs:
            # if it is, check to see what the reference is
            path = self.refs[self.namespace]['clean_path']
            # if the namespace match and the reference matches, it's reffed!
            if self.path in path:
                self.loaded_abc = path.replace('/', os.sep)
                self.ref_node = self.refs[self.namespace]['ref_node']
                self.mode = 'reference'
            # if it's not reffed, lets see if a shd is reffed
            else:
                for shd in self.shds:
                    if shd['path'] in path:
                        abc_node = cmds.ls(self.namespace+':*', type='AlembicNode')
                        if abc_node:
                            if not cmds.referenceQuery(abc_node[0], inr=True):
                                self.mode = 'attach'
                                self.loaded_shd = shd
                                self.loaded_abc = cmds.getAttr(abc_node[0]+'.abc_File').replace('/', os.sep)
                                self.abc_node = abc_node[0]

    def get_latest_abc(self):
        if self.abcs:
            latest = sorted(self.abcs)[-1]
            return latest
        else:
            return None

    def get_status(self):
        status = ''
        if not self.loaded_abc:
            status = 'unloaded'

        elif self.loaded_abc == self.latest_abc:
            status = 'current'
        else:
            status = 'old'

        return status

    def load(self, mode, shd, version):
        cache = [v for v in self.abcs if version in v]
        if not cache:
            raise Exception('Could not find a {version} in caches.'.format(version=version))

        if mode == 'attach':
            # if the current mode is ref, get rid of the ref first
            if self.mode and mode != self.mode:
                self.remove()

            # delete the existing abc node
            if self.abc_node:
                if cmds.objExists(self.abc_node):
                    cmds.delete(self.abc_node)

            # see if the shade is loaded
            if not self.loaded_shd or self.loaded_shd['name'] != shd:
                for current_shd in self.shds:
                    if current_shd['name'] == shd:
                        # reference it
                        # TODO add check to make sure namespace isnt taken

                        # if we don't have a loaded shade, make a new reference
                        if not self.loaded_shd:
                            cmds.file(current_shd['path'], r=True, namespace=self.namespace)
                        # if there is a loaded shade, just switch the ref path
                        else:
                            # cmd = 'cmds.file({}, lr={})'.format(current_shd['path'], self.refs[self.namespace]['ref_node'])
                            # print cmd
                            cmds.file(unloadReference=self.refs[self.namespace]['ref_node'])
                            cmds.file(current_shd['path'].replace('\\', '/'), lr=self.refs[self.namespace]['ref_node'])
                        self.loaded_shd = current_shd
                        self.refs = utils.get_refs()

            # attach to shd!
            self.attach(cache[0])
            self.mode = 'attach'

        if mode == 'reference':
            # if the current mode is attach, get rid of the shd first
            if self.mode and mode != self.mode:
                self.remove()

            # delete the existing abc node
            if self.abc_node:
                if cmds.objExists(self.abc_node):
                    cmds.delete(self.abc_node)
                    self.abc_node = None

            if self.mode == mode and self.ref_node:
                cmds.file(cache[0], lr=self.ref_node)
            else:
                cmds.file(cache[0], r=True, namespace=self.namespace)
                self.refs = utils.get_refs()  # update the reference list

            if self.namespace in self.refs:
                self.ref_node = self.refs[self.namespace]['ref_node']

            self.loaded_abc = cache[0]
            self.mode = 'reference'

        # refresh the status
        self.status = self.get_status()

    def attach(self, cache):
        # attach
        cache = str(cache)
        all_objs = cmds.ls(self.namespace+':*', r=1, dag=1, long=1)
        all_abcs_old = cmds.ls(type='AlembicNode')
        alembic_geo = utils.objs_from_abc(cache, 1)

        # temporarily switch the namespace while attaching to match alembic geo
        alembic_root_namespace = utils.namespace_from_abc(cache)
        # cmds.namespace(force=True, moveNamespace=(self.namespace, alembic_root_namespace))
        cmds.file(self.refs[self.namespace]['path'], e=1, namespace=alembic_root_namespace)

        roots = []
        bad_objs = []
        exclusions = ['Constraint', 'constraint', 'ffd']

        for geo in alembic_geo:
            # TODO: just make the obs_from_abc function return the abc names
            # with their namespaces in tact and gt rid of namespace from abc function
            if cmds.objExists(alembic_root_namespace+':'+geo):
                roots.append(alembic_root_namespace+':'+geo)
            else:
                for exclusion in exclusions:
                    if exclusion not in geo:
                        bad_objs.append(geo)

        # warn user about cache object mismatches
        if len(bad_objs):
            problems = 1
            border_space = 10
            control_space = 5

            bad_string = '\n'.join(bad_objs)
            bad_obj_win = 'bcImp_badObjWin'
            bad_obj_win = cmds.window(t='{} - Bad cache objects!'.format(self.namespace), rtf=1)

            bad_obj_form = cmds.formLayout(nd=100)
            heading = cmds.text(
                w=400, l='The following geometry is in the cache, but not in the SHD asset:')
            bad_scroll = cmds.textScrollList()
            for obj in bad_objs:
                cmds.textScrollList(bad_scroll, e=1, append=obj)
            footing = cmds.text(
                l='You should probably publish the SHD asset.')
            yes_btn = cmds.button(
                l='Ok!', c='import maya.cmds as cmds; cmds.deleteUI("{}")'.format(bad_obj_win))

            cmds.formLayout(bad_obj_form, e=1,
                            attachForm=(
                                (heading, 'top', border_space),
                                (heading, 'left', border_space),
                                (heading, 'right', border_space),
                                (bad_scroll, 'left', border_space),
                                (bad_scroll, 'right', border_space),
                                (footing, 'left', border_space),
                                (footing, 'right', border_space),
                                (yes_btn, 'left', border_space),
                                (yes_btn, 'right', border_space),
                                (yes_btn, 'bottom', border_space),
                            ),
                            attachControl=(
                                (bad_scroll, 'top', control_space, heading),
                                (bad_scroll, 'bottom', control_space, footing),
                                (footing, 'bottom', control_space, yes_btn),
                            ))

            cmds.showWindow(bad_obj_win)

        # connect the alembic to the shade file!
        alembic_cmd = 'AbcImport -mode "import" -connect "{}" "{}";'.format(
            ' '.join(roots), cache.replace('\\', '/'))
        mel.eval(alembic_cmd)

        # change the namespace back!
        if cmds.namespace(exists=self.namespace):
            utils.remove_namespace(self.namespace)
        cmds.file(self.refs[self.namespace]['path'], e=1, namespace=self.namespace)

        if cmds.namespace(exists=alembic_root_namespace):
            cmds.namespace(set=':')
            cmds.namespace(force=True, moveNamespace=(alembic_root_namespace, self.namespace))
            utils.remove_namespace(alembic_root_namespace)

        all_abcs_new = cmds.ls(type='AlembicNode')
        all_abcs_diff = list(set(all_abcs_new) - set(all_abcs_old))
        alembic_node = ''
        if all_abcs_diff:
            alembic_node = cmds.rename(all_abcs_diff[0], self.namespace+':AlembicNode')

        if not alembic_node:
            alembic_node = cmds.createNode('AlembicNode', n=self.namespace+':AlembicNode')
            cmds.setAttr(alembic_node+'.fn', cache, type='string')

        self.abc_node = alembic_node
        self.loaded_abc = cache

    def remove(self):
        if self.abc_node:
            if cmds.objExists(self.abc_node):
                cmds.delete(self.abc_node)
        if self.namespace in self.refs:
            cmds.file(self.refs[self.namespace]['path'], removeReference=True, mergeNamespaceWithRoot=True)
            utils.remove_namespace(self.namespace)

        self.status = 'unloaded'
        self.mode = None
        self.loaded_abc = None
        self.loaded_shd = None
        self.abc_node = None
        self.ref_node = None

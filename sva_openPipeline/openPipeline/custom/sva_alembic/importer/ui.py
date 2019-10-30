import maya.cmds as cmds
from functools import partial
import os
import utils
import traceback

import sva_alembic.utils


class Show():
    """
        Creates the Abc Importer UI
    """

    def __init__(self):
        self.win_name = 'abcImporterWin'
        if cmds.window(self.win_name, ex=1):
            cmds.deleteUI(self.win_name)

        self.createWin()
        self.refresh()

    def createWin(self):
        field_height = 20
        border_space = 10
        line_space = 5
        icon_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons')

        self.win = cmds.window(self.win_name, w=400, h=400, rtf=1, s=1, t='ABC Importer')

        self.main_form = cmds.formLayout(nd=100)  # main form for the entire window

        # header
        self.title_logo = cmds.image(i=os.path.join(icon_dir, 'abcExp_logo.png'))
        self.title = cmds.text(fn='boldLabelFont', l=' ABC Importer', h=25, al='left')

        # all check icons
        self.check_all = cmds.iconTextButton(l='', w=20, h=20, ann='Check all caches', c=self.checkAll, i=os.path.join(icon_dir, 'abcExp_check.png'))
        self.check_none = cmds.iconTextButton(l='', w=20, h=20, ann='Uncheck all caches', c=self.checkNone, i=os.path.join(icon_dir, 'abcExp_unCheck.png'))
        self.refresh_btn = cmds.iconTextButton(l='', w=20, h=20, ann='Refresh caches', c=self.refresh, i=os.path.join(icon_dir, 'abcImp_refresh.png'))

        # bake set tab layout (cause scroll layouts won't expand child form to full size for some reason)
        self.cache_tab = cmds.tabLayout(bs='none', w=300, cr=1, tabsVisible=0, scrollable=1, bgc=[.2, .2, .2])
        cmds.setParent(self.main_form)

        # action buttons
        self.remove_btn = cmds.button(l='REMOVE', ann='Remove selected caches/SHD assets from the scene', h=30, c=self.remove_callback)
        self.upgrade_btn = cmds.button(l='UPGRADE', ann='Switch all versions to the latest', h=30, c=self.upgrade)
        self.import_btn = cmds.button(l='LOAD', ann='Load selected caches into the scene', h=30, bgc=[.2, .4, .2], c=self.import_callback)

        cmds.formLayout(self.main_form, e=True,
                        attachForm=(
                            (self.title_logo, 'top', border_space),
                            (self.title_logo, 'left', border_space),
                            (self.title, 'top', border_space),
                            (self.title, 'right', border_space),
                            (self.check_all, 'right', border_space),
                            (self.cache_tab, 'left', border_space),
                            (self.cache_tab, 'right', border_space),
                            (self.remove_btn, 'left', border_space),
                            (self.upgrade_btn, 'right', border_space),
                            (self.import_btn, 'left', border_space),
                            (self.import_btn, 'right', border_space),
                            (self.import_btn, 'bottom', border_space),
                        ),
                        attachPosition=(
                            (self.upgrade_btn, 'left', border_space/2, 50),
                        ),
                        attachControl=(
                            (self.title, 'left', 5, self.title_logo),
                            (self.check_all, 'top', 0, self.title),
                            (self.check_none, 'top', 0, self.title),
                            (self.check_none, 'right', border_space/2, self.check_all),
                            (self.refresh_btn, 'top', 0, self.title),
                            (self.refresh_btn, 'right', border_space/2, self.check_none),
                            (self.cache_tab, 'top', border_space, self.check_all),
                            (self.cache_tab, 'bottom', border_space, self.upgrade_btn),
                            (self.upgrade_btn, 'bottom', border_space, self.import_btn),
                            (self.remove_btn, 'bottom', border_space, self.import_btn),
                            (self.remove_btn, 'right', border_space, self.upgrade_btn),
                        ))

        cmds.showWindow(self.win)
        cmds.window(self.win, e=1, w=400, h=400)

    def populate_cache_tab(self):
        """
            populates self.cache_tab layout with all of the bake sets for the shot
        """
        cache_tab_form_name = 'cache_tab_form'
        if cmds.formLayout(cache_tab_form_name, ex=1):
            cmds.deleteUI(cache_tab_form_name)
        self.cache_tab_form = cmds.formLayout(cache_tab_form_name, nd=100, p=self.cache_tab)
        self.caches = utils.get_shot_caches(self.cache_dir)
        self.cache_scene_layouts = []

        # create the subUIs for each cache scene and cache
        for cache_scene in set([c.scene for c in self.caches]):
            # make a frame layout for the cache scene
            frame = cmds.frameLayout(cache_scene+'_FRL', p=self.cache_tab_form, cll=1, l=cache_scene)
            self.cache_scene_layouts.append(frame)

            # loop through all of the caches for the current cache scene
            for cache in [c for c in self.caches if c.scene == cache_scene]:
                # check if the cache folder actually has anything in it
                if cache.abcs:
                    # create the UI for the current cache
                    cache.gui = Cache_GUI(cache, frame)

        # get all of the frame layouts in alphabetical order without duplicates
        frame_layouts = sorted(list(set(self.cache_scene_layouts)))
        # edit the form layout
        for x, frame_layout in enumerate(frame_layouts):
            cmds.formLayout(self.cache_tab_form, e=True,
                            attachForm=(
                                (str(frame_layout), 'right', 0),
                                (str(frame_layout), 'left', 0),
                            ))
            # if it's the first element, attach to the top of the form
            if x == 0:
                cmds.formLayout(self.cache_tab_form, e=True,
                                attachForm=(
                                    (str(frame_layout), 'top', 0),
                                ))
            # if not, attach to the previous element
            else:
                cmds.formLayout(self.cache_tab_form, e=True,
                                attachControl=(
                                    (str(frame_layout), 'top', 0, str(frame_layouts[x-1])),
                                ))

    def buildSceneLayouts(self, name):
        """
            creates the frame and column layouts for a given asset type

            Args:
            name = the name of the asset type to make the frame layout for
                    this name appears in the label of the resulting frame

            Return:
            frame = the frame layout
        """
        frame = cmds.frameLayout(name+'_FRL', p=self.cache_tab_form, cll=1, cl=0, l=name)
        return frame

    def checkAll(self, *args):
        """
            checks all of the caches in the UI
        """
        for cache in self.caches:
            cmds.checkBox(cache.gui.check, e=1, v=1)

    def checkNone(self, *args):
        """
            unchecks all of the caches in the UI
        """
        for cache in self.caches:
            cmds.checkBox(cache.gui.check, e=1, v=0)

    def import_callback(self, *args):
        # loop through the caches to access their checkboxes
        for cache in self.caches:
            # if they are enabled, import!
            if cmds.checkBox(cache.gui.check, q=1, v=1):
                try:
                    # # import!
                    cache.gui.load()
                except Exception:
                    traceback.print_exc()
        self.refresh()

    def remove_callback(self, *args):
        response = cmds.confirmDialog(title='You sure?', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No',
                                      dismissString='No', message='You sure you want to remove the selected cache(s) from your scene?')
        if response == 'Yes':
            # loop through the caches to access their checkboxes
            for cache in self.caches:
                # if they are enabled, import!
                if cmds.checkBox(cache.gui.check, q=1, v=1):
                    try:
                        # remove!
                        cache.gui.remove()
                    except Exception:
                        traceback.print_exc()
            self.refresh()

    def upgrade(self, *args):
        for cache in self.caches:
            # if they are enabled, upgrade!!
            if cmds.checkBox(cache.gui.check, q=1, v=1):
                versions = cmds.optionMenu(cache.gui.v_om, q=1, ni=1)
                cmds.optionMenu(cache.gui.v_om, e=1, sl=versions)

    def refresh(self, *args):
        """
            refreshes the UI
        """
        self.op_file_info = sva_alembic.utils.get_op_file_info()
        self.op_proj_info = sva_alembic.utils.get_op_proj_info()
        self.cache_dir = os.path.dirname(sva_alembic.utils.get_cache_dir())

        self.assets = utils.get_assets(self.op_proj_info['lib_path'])
        self.alembics = utils.get_scene_alembics(self.op_file_info['level2'])
        self.refs = utils.get_refs()
        self.caches = []
        # self.caches.clear()
        if os.path.isdir(self.cache_dir):
            self.populate_cache_tab()


class Cache_GUI():
    def __init__(self, cache, parent):
        self.cache = cache
        self.parent = parent
        self.control_height = 20

        self.row = cmds.rowLayout(
            p=self.parent,
            numberOfColumns=6,
            columnWidth6=(20, 100, 2, 60, 80, 60),
            adjustableColumn=2,
            columnAlign=(1, 'right'),
            columnAttach=[
                (1, 'both', 0),
                (2, 'both', 0),
                (3, 'both', 0),
                (4, 'both', 0),
                (5, 'both', 0),
                (6, 'both', 0),
            ]
        )
        self.check = cmds.checkBox(l='', h=self.control_height, v=1)
        self.field = cmds.textField(
            h=self.control_height,
            ed=False,
            bgc=[.4, .4, .4],
            text=self.cache.namespace,
            ann='GREEN = the latest version of the cache is in your scene\nORANGE = there is a newer version of the cache available\nYELLOW = there were problems loading the cache\nRED = the cache is not in your shot'
        )
        self.space = cmds.text(l='')
        self.v_om = cmds.optionMenu(h=self.control_height, bgc=[.3, .3, .3], w=40, cc=lambda x: cmds.checkBox(self.check, e=1, v=1))
        self.mode_om = cmds.optionMenu(h=self.control_height, bgc=[.3, .3, .3], w=60, cc=self.mode_toggle_callback)
        self.shd_om = cmds.optionMenu(h=self.control_height, bgc=[.3, .3, .3], w=40, cc=self.shd_toggle_callback)

        self.refresh()

    def refresh(self):
        self.populate_versions()
        self.populate_shds()
        self.populate_modes()
        self.mode_toggle_callback()
        self.display_status()

    def populate_versions(self):
        self.clear_om(self.v_om)

        menu_items = cmds.optionMenu(self.v_om, q=True, itemListLong=True)
        if menu_items:
            cmds.deleteUI(menu_items)
        for abc in self.cache.abcs:
            version = abc.split('_cache_')[-1].rstrip('.abc')
            cmds.menuItem(p=self.v_om, label=version)

        # select the correct version
        option_version = self.cache.latest_abc
        if self.cache.loaded_abc:
            option_version = self.cache.loaded_abc

        cmds.optionMenu(self.v_om, e=1, v=option_version.split('_cache_')[-1].rstrip('.abc'))

    def populate_shds(self):
        self.clear_om(self.shd_om)

        if self.cache.shds:
            for shd in self.cache.shds:
                cmds.menuItem(p=self.shd_om, label=shd['name'])
        else:
            cmds.optionMenu(self.shd_om, e=True, en=False)

        if self.cache.loaded_shd:
            cmds.optionMenu(self.shd_om, e=True, v=self.cache.loaded_shd['name'])

    def populate_modes(self):
        # clear the menu first
        self.clear_om(self.mode_om)

        modes = ['reference', 'attach']
        for mode in modes:
            cmds.menuItem(p=self.mode_om, label=mode)

        # if there are shades, default to attach
        if self.cache.shds:
            cmds.optionMenu(self.mode_om, e=True, v=modes[1])
        # if not, select reference and disable option menu
        else:
            cmds.optionMenu(self.mode_om, e=True, v=modes[0], en=False)

        # if the cache is already in the scene, set it to the existing mode
        if self.cache.mode:
            cmds.optionMenu(self.mode_om, e=True, v=self.cache.mode)

    def mode_toggle_callback(self, *args):
        mode = cmds.optionMenu(self.mode_om, q=True, v=True)
        if mode == 'reference':
            cmds.optionMenu(self.shd_om, e=True, en=False)
        if mode == 'attach':
            cmds.optionMenu(self.shd_om, e=True, en=True)

        cmds.checkBox(self.check, e=True, v=1)

    def shd_toggle_callback(self, *args):
        cmds.checkBox(self.check, e=True, v=1)

    def display_status(self):
        # edit field colors to reflect status of cache
        red = [.5, .2, .2]
        green = [.2, .5, .2]
        orange = [.5, .4, .2]
        yellow = [.6, .6, .2]

        color_dict = {
            'unloaded': red,
            'old': orange,
            'current': green,
        }

        cmds.textField(self.field, e=1, bgc=color_dict[self.cache.status])

        if self.cache.status == 'current':
            cmds.checkBox(self.check, e=1, v=0)

    def load(self):
        mode = cmds.optionMenu(self.mode_om, q=True, v=True)
        version = cmds.optionMenu(self.v_om, q=True, v=True)
        if cmds.optionMenu(self.shd_om, q=True, ni=True):
            shd = cmds.optionMenu(self.shd_om, q=True, v=True)
        else:
            shd = None

        self.cache.load(mode, shd, version)
        self.refresh()

    def remove(self):
        self.cache.remove()
        self.refresh()

    def clear_om(self, om):
        menu_items = cmds.optionMenu(om, q=True, itemListLong=True)
        if menu_items:
            cmds.deleteUI(menu_items)

    def upgrade(self):
        pass

import maya.cmds as cmds
import os
import utils
reload(utils)

class Show():
    """
        Creates the Abc Exporter UI
    """
    def __init__(self):
        self.win_name = 'abcExporterWin'
        if cmds.window(self.win_name, ex=1):
            cmds.deleteUI(self.win_name)

        self.create_win()
        self.op_file_info = utils.get_op_file_info()
        self.op_proj_info = utils.get_op_proj_info()
        self._populate_bake_tab()

    def create_win(self):
        field_height = 20
        border_space = 10
        line_space = 5
        icon_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons')

        self.win = cmds.window(self.win_name, w=100, h=400, rtf=1, s=1, t='ABC Exporter')

        self.main_form = cmds.formLayout(nd=100) # main form for the entire window

        # header
        self.title_logo = cmds.image(i=os.path.join(icon_dir, 'abcExp_logo.png'))
        self.title = cmds.text(fn='boldLabelFont', l=' ABC Exporter', h=25, al='left')

        # all check icons
        self.check_all = cmds.iconTextButton(l='', w=20, h=20, c=self.check_all, i=os.path.join(icon_dir, 'abcExp_check.png'))
        self.check_none = cmds.iconTextButton(l='', w=20, h=20, c=self.check_none, i=os.path.join(icon_dir, 'abcExp_unCheck.png'))

        # bake set tab layout (cause scroll layouts won't expand child form to full size for some reason)
        self.bake_tab = cmds.tabLayout(bs='none', cr=1, tabsVisible=0, scrollable=1, bgc=[.2,.2,.2])
        cmds.setParent(self.main_form)

        # frame range options
        self.range_txt = cmds.text(l='Frame Range:')
        self.range_coll = cmds.radioCollection()
        self.range_rb = cmds.radioButton(label='', sl=1)
        self.static_rb = cmds.radioButton(label='static')

        self.range_start_field = cmds.floatField(h=field_height, w=50, pre=2, v=cmds.playbackOptions(q=1, minTime=1))
        self.range_split_txt = cmds.text(l='-')
        self.range_end_field = cmds.floatField(h=field_height, w=50, pre=2, v=cmds.playbackOptions(q=1, maxTime=1))

        self.step_txt = cmds.text(l='Step:')
        self.step_field = cmds.floatField(h=field_height, w=50, pre=2, v=1.0)

        # action buttons
        self.refresh_btn = cmds.button(l='REFRESH', h=30)
        self.export_btn = cmds.button(l='EXPORT', h=30)

        cmds.formLayout(self.main_form, e=True,
                        attachForm=(
                            (self.title_logo, 'top', border_space),
                            (self.title_logo, 'left', border_space),
                            (self.title, 'top', border_space),
                            (self.title, 'right', border_space),
                            (self.check_all, 'right', border_space),
                            (self.bake_tab, 'left', border_space),
                            (self.bake_tab, 'right', border_space),
                            (self.range_txt, 'left', border_space),
                            (self.range_rb, 'left', border_space*3),
                            (self.static_rb, 'left', border_space*3),
                            (self.step_txt, 'left', border_space),
                            (self.refresh_btn, 'left', border_space),
                            (self.refresh_btn, 'bottom', border_space),
                            (self.export_btn, 'right', border_space),
                            (self.export_btn, 'bottom', border_space),
                        ),
                        attachPosition=(
                            (self.refresh_btn, 'right', border_space/2, 50),
                            (self.export_btn, 'left', border_space/2, 50),
                        ),
                        attachControl=(
                            (self.title, 'left', 5, self.title_logo),
                            (self.check_all, 'top', 0, self.title),
                            (self.check_none, 'top', 0, self.title),
                            (self.check_none, 'right', border_space/2, self.check_all),
                            (self.bake_tab, 'top', border_space, self.check_all),
                            (self.bake_tab, 'bottom', border_space, self.range_txt),
                            (self.range_txt, 'bottom', border_space+5, self.range_rb),
                            (self.range_rb, 'bottom', border_space/2, self.static_rb),
                            (self.range_start_field, 'left', 5, self.range_rb),
                            (self.range_start_field, 'bottom', border_space/2.5, self.static_rb),
                            (self.range_split_txt, 'bottom', border_space, self.static_rb),
                            (self.range_split_txt, 'left', border_space, self.range_start_field),
                            (self.range_end_field, 'bottom', border_space/2.5, self.static_rb),
                            (self.range_end_field, 'left', border_space, self.range_split_txt),
                            (self.static_rb, 'bottom', border_space, self.step_txt),
                            (self.step_txt, 'bottom', border_space*2, self.refresh_btn),
                            (self.step_field, 'left', border_space, self.step_txt),
                            (self.step_field, 'bottom', border_space*1.5, self.refresh_btn),
                        ))

        cmds.showWindow(self.win)
        cmds.window(self.win, e=1, w=250, h=400)

    def _populate_bake_tab(self):
        """
            populates self.bake_tab layout with all of the bake sets for the shot
        """
        self.bake_tab_form = cmds.formLayout(nd=100, p=self.bake_tab)
        bake_sets = utils.get_bake_sets()
        self.asset_type_layouts = {} # a dict where the keys are asset_types and the values are the frame layout[0] and the column layout[1]
        self.bake_column_layouts = [] # the column layouts created for each bakeset
        self.checkBoxes = [] # all of the bakeSet checkboxes

        # create the subUIs for each asset type and bake set
        for bake_set in bake_sets:
            asset_type = bake_sets[bake_set]['asset_type']
            # if there isn't a frame layout for this asset type, make one
            if asset_type not in self.asset_type_layouts:
                self.asset_type_layouts[asset_type] = self._build_asset_type_layouts(asset_type)

            # get the column layout for the current asset type's frame layout to house the checkbox
            column_layout = self.asset_type_layouts[asset_type][1]
            # create the checkbox for the current bake set
            self.checkBoxes.append(cmds.checkBox(bake_set+'_CHK', p=column_layout, l=bake_set, v=1))

        # get all of the frame layouts in alphabetical order without duplicates
        frame_layouts = sorted(list(set([x[0] for x in self.asset_type_layouts.values()])))
        # edit the form layout
        for x, frame_layout in enumerate(frame_layouts):
            cmds.formLayout(self.bake_tab_form, e=True,
                    attachForm=(
                        (str(frame_layout), 'right', 0),
                        (str(frame_layout), 'left', 0),
                    ))
            # if it's the first element, attach to the top of the form
            if x == 0:
                cmds.formLayout(self.bake_tab_form, e=True,
                    attachForm=(
                        (str(frame_layout), 'top', 0),
                    ))
            # if not, attach to the previous element
            else:
                cmds.formLayout(self.bake_tab_form, e=True,
                    attachControl=(
                        (str(frame_layout), 'top', 0, str(frame_layouts[x-1])),
                    ))

    def _build_asset_type_layouts(self, name):
        """
            creates the frame and column layouts for a given asset type

            Args:
            name = the name of the asset type to make the frame layout for
                    this name appears in the label of the resulting frame

            Return:
            frame = the frame layout
            column = the column layout
        """
        frame = cmds.frameLayout(name+'_FRL', p=self.bake_tab_form, cll=1, l=name)
        column = cmds.columnLayout(name+'_CML')
        return frame, column

    def check_all(self, *args):
        """
            checks all of the caches in the UI
        """
        for box in self.checkBoxes:
            cmds.checkBox(box, e=1, v=1)

    def check_none(self, *args):
        """
            unchecks all of the caches in the UI
        """
        for box in self.checkBoxes:
            cmds.checkBox(box, e=1, v=0)

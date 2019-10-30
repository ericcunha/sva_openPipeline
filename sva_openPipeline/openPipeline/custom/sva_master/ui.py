from .processors import *
import maya.cmds as cmds
import maya.mel as mel
import os
import traceback

from . import plugins
reload(plugins)


class UI():
    """
    Builds the master file UI
    """

    def __init__(self):
        """
        Constructor
        """
        self.win_name = 'op_secondaryUI'
        self.win_title = 'Master File'
        self.m_name = cmds.optionVar(q='op_masterName').upper()
        self.tab = cmds.optionVar(q='op_currOpenTab')
        self.level1 = cmds.optionVar(q='op_currOpenLevel1')
        self.level2 = cmds.optionVar(q='op_currOpenLevel2')
        self.level3 = cmds.optionVar(q='op_currOpenLevel3')
        self.delete_win()

        type = ''
        if cmds.optionVar(ex='op_currOpenType'):
            type = cmds.optionVar(q='op_currOpenType')

        if type == 'workshop':
            self.create_win()
            self.populate_processors()

            cmds.showWindow(self.win)

        elif type == 'master':
            cmds.confirmDialog(
                m="You're currently viewing a {} file. Action not possible.".
                format(self.m_name),
                button="OK",
                title="openPipeline message")
        else:
            cmds.confirmDialog(
                message="Nothing is currently open for editing. Action not possible.",
                button="OK",
                title="openPipeline message")

    def delete_win(self, *args):
        """
        Deletes the window if it exists
        """
        if cmds.window(self.win_name, ex=1):
            cmds.deleteUI(self.win_name)

    def create_win(self):
        """
        Builds the window
        """
        border_space = 10
        line_space = border_space / 2
        section_space = 15
        field_height = 25

        self.win = cmds.window(self.win_name, title=self.win_title)
        self.main_form = cmds.formLayout(nd=100)

        self.process_txt = cmds.text(l='Process:')

        self.after_rbg = cmds.radioButtonGrp(
            numberOfRadioButtons=3,
            label="After Master Open:",
            labelArray3=["Workshop", "Master", "New"],
            columnWidth4=[100, 80, 60, 60],
            columnAlign4=["left", "left", "left", "left"],
            sl=1)

        self.custom_master_txt = cmds.text(l="Custom " + self.m_name +
                                           " Command:")
        self.custom_master_cmd_field = cmds.textField(w=240)

        self.comment_txt = cmds.text(l="comment: ", w=60, h=20)
        self.comment_field = cmds.scrollField(w=190, h=40, ww=1)

        self.master_btn = cmds.button(l=self.m_name,
                                      c=self.save_master,
                                      bgc=[.9, .7, .4])
        self.cancel_btn = cmds.button(l="cancel",
                                      c=self.delete_win,
                                      bgc=[.8, .4, .4])

        self.process_scroll = cmds.scrollLayout(h=50)
        cmds.setParent(self.main_form)

        cmds.formLayout(
            self.main_form,
            e=True,
            attachForm=(
                (self.process_txt, 'top', border_space),
                (self.process_txt, 'left', border_space),
                (self.process_scroll, 'right', border_space),
                (self.process_scroll, 'left', border_space),
                (self.after_rbg, 'left', border_space),
                (self.after_rbg, 'right', border_space),
                (self.custom_master_txt, 'left', border_space),
                (self.custom_master_cmd_field, 'left', border_space),
                (self.custom_master_cmd_field, 'right', border_space),
                (self.comment_txt, 'left', border_space),
                (self.comment_field, 'left', border_space),
                (self.comment_field, 'right', border_space),
                (self.master_btn, 'left', border_space),
                (self.master_btn, 'bottom', border_space),
                (self.cancel_btn, 'right', border_space),
                (self.cancel_btn, 'bottom', border_space),
            ),
            attachControl=(
                (self.process_scroll, 'top', line_space, self.process_txt),
                (self.process_scroll, 'bottom', line_space, self.after_rbg),
                (self.after_rbg, 'bottom', line_space, self.custom_master_txt),
                (self.custom_master_txt, 'bottom', line_space,
                 self.custom_master_cmd_field),
                (self.custom_master_cmd_field, 'bottom', line_space,
                 self.comment_txt),
                (self.comment_txt, 'bottom', line_space, self.comment_field),
                (self.comment_field, 'bottom', border_space, self.master_btn),
            ),
            attachPosition=(
                (self.master_btn, 'right', line_space, 50),
                (self.cancel_btn, 'left', line_space, 50),
            ))

    def populate_processors(self):
        cmds.setParent(self.process_scroll)
        self.processor_uis = []
        sorted_processors = sorted(PROCESSORS, key=lambda k: k['order'])
        for processor in sorted_processors:
            processorUI = ProcessorUI(processor)
            enabled = self.load_processor_state(processor)
            if enabled:
                processorUI.enable()
            self.processor_uis.append(processorUI)

    def run_processors(self):
        self.failed_processors = []
        for processor in self.processor_uis:
            if processor.is_enabled():
                passed = processor.run()
                if not passed:
                    self.failed_processors.append(
                        processor.processor_dict['name'])

    def load_processor_state(self, processor):
        enabled = 0
        # get the default level of enabledness
        if 'asset' in processor['task'] and self.tab == 2:
            enabled = 1
        if 'shot' in processor['task'] and self.tab == 3:
            enabled = 1
        for task in processor['task']:
            if task in self.level3:
                enabled = 1
        # is there component level enabledness?
        # is there project level enabledness?
        return enabled

    def save_master(self, *args):
        comment = cmds.scrollField(self.comment_field, q=1, tx=1)
        after = cmds.radioButtonGrp(self.after_rbg, q=1, sl=1)
        custom_cmd = cmds.textField(self.custom_master_cmd_field, q=1, tx=1)
        # save a workshop first
        mel.eval(
            'openPipelineSaveWorkshop("{comment}");'.format(comment=comment))
        # if any processors fail, prompt user to let them know and either
        # reopen workshop or continue mastering with errors (dangerous!)
        self.run_processors()
        if self.failed_processors:
            failed_processors_str = '\n'.join(self.failed_processors)
            prompt = cmds.confirmDialog(
                title='Failed Processors',
                message='The following processors have failed:\n\n{failed}\n\nDo you want to continue Mastering (dangerous!) or reopen the workshop?'
                .format(failed=failed_processors_str),
                button=['Continue Mastering', 'Reopen Workshop'],
                defaultButton='Reopen Workshop',
                cancelButton='Continue Mastering',
                dismissString='Continue Mastering')
            if prompt == 'Reopen Workshop':
                mel.eval(
                    'openPipelineForceOpenItem("workshop", "{tab}", "{level1}", "{level2}", "{level3}", 0)'
                    .format(tab=self.tab,
                            level1=self.level1,
                            level2=self.level2,
                            level3=self.level3))
                self.delete_win()
                return

        mel.eval(
            'openPipelineSaveMaster("{comment}", "{after}", "{custom_cmd}")'.
            format(comment=comment, after=after, custom_cmd=custom_cmd))
        self.delete_win()


class ProcessorUI():
    def __init__(self, processor_dict):
        self.processor_dict = processor_dict
        self.checkbox = cmds.checkBox(l=self.processor_dict['name'],
                                      ann=self.processor_dict['description'],
                                      v=0)

    def run(self):
        try:
            exec(self.processor_dict['cmd'])
            self.update_status('pass')
            return 1
        except Exception:
            cmds.warning(
                '{plugin} failed with the following error:\n {error}'.format(
                    plugin=self.processor_dict['name'], error=traceback.print_exc()))
            self.update_status('fail')
            return 0

    def update_status(self, status):
        if status == 'pass':
            cmds.checkBox(self.checkbox, e=1, bgc=[0, 1, 0])

        if status == 'fail':
            cmds.checkBox(self.checkbox, e=1, bgc=[1, 0, 0])

    def is_enabled(self):
        enabled = cmds.checkBox(self.checkbox, q=1, v=1)
        return enabled

    def enable(self):
        cmds.checkBox(self.checkbox, e=1, v=1)

    def disable(self):
        cmds.checkBox(self.checkbox, e=1, v=0)

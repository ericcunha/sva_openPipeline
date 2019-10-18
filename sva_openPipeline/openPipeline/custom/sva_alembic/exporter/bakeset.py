import maya.cmds as cmds


class Bakeset():
    def __init__(self, bake_set):
        self.set = bake_set
        self.extension = '_bake_SET'
        self.namespace = self.get_namespace()
        self.path = self.get_path()

        # these can change
        self.members = ''
        self.static = ''
        self.step = ''
        self.reload()

        self.asset_type = self.get_asset_type()
        self.category = self.get_category()

        # this is used by the UI to tell if we should cache
        self.checkbox = ''

    def reload(self):
        self.members = self.get_members()
        self.static = self.is_static()
        self.step = self.get_step()

    def is_static(self):
        static = 0
        try:
            static = cmds.getAttr(self.set+'.static')
        except:
            pass
        return static

    def get_step(self):
        step = 1
        try:
            step = cmds.getAttr(self.set+'.step')
        except:
            pass
        return step

    def get_members(self):
        members = [x for x in cmds.sets(
            self.set, q=1) if cmds.objectType(x) == 'transform']
        return members

    def is_camera(self):
        is_camera = 0
        if len(self.members) == 1:
            shape = ''
            if cmds.objectType(self.members[0]) == 'transform':
                shape = cmds.listRelatives(self.members[0], shapes=True)
            else:
                shape = self.members[0]
            if shape:
                if cmds.objectType(shape) == 'camera':
                    is_camera = 1
        return is_camera

    def get_namespace(self):
        namespace = ''
        if ':' in self.set:
            namespace = self.set.split(':')[0]
        # if there's no namespace, get the name before publish set extension
        elif self.extension in self.set:
            namespace = self.set.replace(self.extension, "")
        else:
            namespace = self.set
        return namespace

    def get_path(self):
        path = None
        if cmds.referenceQuery(self.set, inr=1):
            path = cmds.referenceQuery(self.set, filename=True, wcn=True)
        return path

    def get_asset_type(self):
        asset_type = 'custom'
        if self.path:
            if '/lib/' in self.path:
                asset_type = self.path.split('/lib/')[1].split('/')[0]
        if self.is_camera():
            asset_type = 'camera'
        return asset_type

    def get_category(self):
        category = self.asset_type
        if category not in ['custom', 'camera']:
            category = 'asset'
        return category

    def is_enabled(self):
        enabled = 0
        if self.checkbox:
            enabled = cmds.checkBox(self.checkbox, q=1, v=1)
        return enabled

# task can either be component name or 'shot' or 'asset'
PROCESSORS = [
    {
        'name': 'import references',
        'description':
        'imports all of the references in the scene. Unloaded references will be removed',
        'order': 1,
        'cmd': 'import plugins.referencing; plugins.referencing.import_refs()',
        'task': ['asset']
    },
    {
        'name': 'remove namespaces',
        'description': 'removes all namespaces in the scene',
        'order': 2,
        'cmd': 'import plugins.referencing; plugins.referencing.remove_namespaces()',
        'task': ['MDL', 'SHD']  # we want to CONVERT in the rig for our ABC
    },
    {
        'name': 'convert namespaces',
        'description': 'converts all : to _ for each namespace in the scene',
        'order': 2,
        'cmd': 'import plugins.referencing; reload(plugins.referencing); plugins.referencing.convert_namespaces()',
        'task': ['RIG']  # we want to CONVERT in the rig for our ABC
    },
    {
        'name': 'delete display layers',
        'description': 'removes all display layers in the scene',
        'order': 2,
        'cmd': 'import plugins.cosmetics; plugins.cosmetics.delete_display_layers()',
        'task': ['asset']
    },
    {
        'name': 'delete JUNK group',
        'description': 'deletes all objects in a group named JUNK',
        'order': 2,
        'cmd': 'import plugins.cosmetics; plugins.cosmetics.delete_junk_grp()',
        'task': ['asset']
    },
    {
        'name': 'export static ABC',
        'description': 'exports a static cache of the bake_SET for SHD',
        'order': 3,
        'cmd': 'import plugins.modeling; reload(plugins.modeling); plugins.modeling.export_abc_model()',
        'task': ['RIG']
    },
]

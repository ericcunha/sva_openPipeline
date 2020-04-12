import os
import maya.mel as mel


def start():
    # get the directory the script is running from
    op_path = os.path.dirname(os.path.realpath(__file__)).replace('\\', '/')
    mel.eval('source "{op_path}/openPipeline.mel"'.format(op_path=op_path))
    # tell openPipeline where to find the openPipeline script folder
    mel.eval('openPipeline("{}","{}")'.format(op_path, op_path))
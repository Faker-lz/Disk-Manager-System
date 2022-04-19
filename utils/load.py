"""
:
@author: lingzhi
* @date 2022/4/14 11:44
"""

# coding=utf-8
import os


# 返回icon中文件的系统文件路径
def load_image(file):
    relative_path = os.getcwd()
    filePath = relative_path + file
        # os.path.join(relative_path, 'icon', file)
    print(filePath)
    return filePath


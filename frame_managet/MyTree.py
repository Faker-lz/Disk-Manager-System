"""
:
@author: lingzhi
* @date 2022/4/15 17:45
"""

import wx
import glob
import os
import psutil
import shutil
import wx.lib.agw.aui as aui

from utils import Images
from utils.IconMap import Ext2IconDict


class MyTreeCtrl(wx.TreeCtrl):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

    def OnCompareItems(self, item1, item2):
        """ OnCompareItems
        data = [0, directory_name] /
        data = [1, file_name]
        """
        data1 = self.GetItemData(item1)
        data2 = self.GetItemData(item2)
        if data1[0] > data2[0]:
            return 1
        elif data1[0] < data2[0]:
            return -1
        else:
            if data1[1].lower() > data2[1].lower():
                return 1
            elif data1[1].lower() < data2[1].lower():
                return -1
            else:
                return 0


class DirectoryTree(wx.Window):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        # 记录电脑路径
        self.work_path = os.getcwd() # os.path.abspath('.')[:3] # os.getcwd()  # 默认为当前的工作区目录

        # 创建树
        self.tree = MyTreeCtrl(self, -1,
                               style=wx.TR_DEFAULT_STYLE  # 默认样式
                                     | wx.TR_TWIST_BUTTONS  # 结点使用 >/v 而不是 +/-
                                     | wx.TR_NO_LINES  # 不绘制结点之间的连线
                               )

        # 初始化图像列表
        self.InitImageList()

        # 初始化树
        self.InitTree()

        # self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnRename, self.tree)


        # 布局
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.tree, 1, wx.EXPAND | wx.LEFT | wx.BOTTOM, 2)
        self.SetSizer(sizer)


    def InitImageList(self):
        """初始化图像列表"""
        # 创建一个图像列表
        il = wx.ImageList(16, 16)
        # 扩展名到图标 ID 的字典
        self.ext_map_imageId = {}
        for ext in Ext2IconDict:
            # 文件扩展名 to imageID
            bmp = getattr(Images, Ext2IconDict[ext]).GetBitmap()
            self.ext_map_imageId[ext] = il.Add(bmp)
        # 单独添加几种特殊情况
        self.ext_map_imageId['default_file'] = il.Add(getattr(Images, 'default_file').GetBitmap())
        self.ext_map_imageId['default_folder'] = il.Add(getattr(Images, 'default_folder').GetBitmap())
        self.ext_map_imageId['default_folder_opened'] = il.Add(getattr(Images, 'default_folder_opened').GetBitmap())
        # 将图像分配给树
        self.tree.AssignImageList(il)

    def InitTree(self):
        """初始化树"""
        # 获取工作目录所有子文件和子目录
        self.all_files = self.GetChildrenFile()
        # self.GetAllFileFrom(self.work_path)
        # self.GetChildrenFile()
        # 设置根目录
        if self.tree.GetCount() < 1:
            self.root_id = self.tree.AddRoot(self.all_files[0], data=[0, self.all_files[0]])
        else:
            self.root_id = self.tree.GetRootItem()
        # 清楚所有子结点
        self.tree.DeleteChildren(self.root_id)
        # 递归添加子节点
        self.AddTreeNodes(self.root_id, self.all_files[1])
        # 根结点展开
        self.tree.Expand(self.root_id)
        # 对子结点排序
        self.tree.SortChildren(self.root_id)

    def GetDiskInfo(self):
        """
        获取电脑盘符
        """
        return psutil.disk_partitions()

    def GetChildrenFile(self):
        """
        获取当前路径下的子文件,并更新树
        """
        sub_list = []
        for file_name in glob.iglob(os.path.join(self.work_path, "*")):
            if os.path.isfile(file_name):
                sub_list.append(
                    [file_name.split('\\')[-1]]
                )
            else:
                file_name_without_root = file_name.split('\\')[-1]
                sub_list.append(file_name_without_root)
        root = self.work_path.split('\\')[-1]
        return [root, sub_list]


    def GetAllFileFrom(self, path):
        """递归获取包括该目录及其子文件、子目录所有文件，
           生成一个“树状列表”，如: [root, [sub-list]]
            [root, [
                    item1,
                    [item2, [
                        item21, item22, item23
                    ],
                    item3,
                ]
            ]
        """
        sub_list = []
        for file_name in glob.iglob(os.path.join(path, "*")):
            if os.path.isdir(file_name):
                sub_list.append(self.GetAllFileFrom(file_name))
            else:
                file_name_without_root = file_name.split('\\')[-1]
                sub_list.append(file_name_without_root)
        root = path.split('\\')[-1]
        return [root, sub_list]

    def CompareTreeList(self, plist, qlist):
        """比较两个树状列表"""
        if len(plist) != len(qlist):
            return False

        res = True
        for p, q in zip(plist, qlist):
            if type(p) == str and type(q) == str:
                if p != q:
                    return False
            elif type(p) == list and type(q) == list:
                res = self.CompareTreeList(p, q)
            else:
                return False
        return res

    def AddTreeNodes(self, parentItem, items):
        """递归添加树结点

        Args:
            parentItem ([treeItemID]): [description]
            items ([list]): [description]
        """
        self.tree.SetItemImage(parentItem, self.ext_map_imageId['default_folder'])
        for item in items:
            if type(item) == str:
                newItem = self.tree.AppendItem(parentItem, item, data=[0, item])
                # 设置结点的图像（文件夹）
                self.tree.SetItemImage(newItem, self.ext_map_imageId['default_folder'], which=wx.TreeItemIcon_Normal)
                self.tree.SetItemImage(newItem, self.ext_map_imageId['default_folder_opened'],
                                       which=wx.TreeItemIcon_Expanded)
            else:
                # TODO 上下反转过
                newItem = self.tree.AppendItem(parentItem, item[0], data=[1, item[0]])
                # 设置数据图像
                ext = item[0].split('.')[-1]  # 扩展名
                if ext in self.ext_map_imageId:
                    self.tree.SetItemImage(newItem, self.ext_map_imageId[ext], which=wx.TreeItemIcon_Normal)
                else:
                    self.tree.SetItemImage(newItem, self.ext_map_imageId['default_file'], which=wx.TreeItemIcon_Normal)
            # 递归调用
                # TODO understand
                # self.AddTreeNodes(newItem, item[1])

    def IsDirChange(self):
        """判断当前工作区目录是否修改"""
        tmp_list = self.GetAllFileFrom(self.work_path)
        return not self.CompareTreeList(tmp_list, self.all_files)

    def GetSelectionItem(self):
        """返回被选中的结点"""
        return self.tree.GetFocusedItem()

    def Unselect(self):
        """取消选中的结点"""
        self.tree.Unselect()

    def GetItemData(self, id):
        """返回指定结点的data"""
        return self.tree.GetItemData(id)

    def CreateDirectory(self):
        """
        创建文件夹
        """
        file = os.path.join(self.work_path, "新建文件夹")
        if not os.path.exists(file):
            os.makedirs(file)

    def CreateFile(self):
        """
        创建文件
        """
        file = os.path.join(self.work_path, "新建文件")
        if not os.path.exists(file):
            f = open(file, 'w')
            f.close()

    def DeleteDirectory(self, id):
        """
        删除文件夹
        """
        item = self.tree.GetItemText(id)
        file = os.path.join(self.work_path, item)
        if os.path.isdir(file):
            shutil.rmtree(file)
            # os.rmdir(file)

    def DeleteFile(self, id):
        """
        删除文件
        """
        item = self.tree.GetItemText(id)
        os.remove(os.path.join(self.work_path, item))

    def GetItemText(self, item):
        if item:
            return self.tree.GetItemText(item)
        else:
            return ""

    def OnRename(self):
        item = self.tree.GetSelection()
        old_name = os.path.join(self.work_path, self.GetItemText(item))
        text = wx.GetTextFromUser(message="new name", caption="Please type new name", default_value=self.GetItemText(item),
                                                parent=None)
        if text:
            new_name = os.path.join(self.work_path, text)
            os.rename(old_name, new_name)





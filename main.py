"""
:
@author: lingzhi
* @date 2022/4/14 18:55
"""
import os
import wx
from frame_managet.MyTree import DirectoryTree
import wx.lib.agw.aui as aui


class TestFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetTitle("DiskManager")
        self.SetSize(800, 600)

        self.dir_tree = DirectoryTree(self, size=(200, 600))
        self.txt = wx.TextCtrl(self, -1, value="Welcome to Disk Manager System", style=wx.TE_MULTILINE)

        # aui manager It can realize the biggest/small window, drag
        self._mgr = aui.AuiManager(agwFlags=aui.AUI_MGR_LIVE_RESIZE)    #agwFlags=aui.AUI_MGR_LIVE_RESIZE
        self._mgr.SetManagedWindow(self)
        self._mgr.AddPane(self.dir_tree, aui.AuiPaneInfo().Caption("workspace").
                          Left().Layer(1).Position(1).CloseButton(True).MaximizeButton(True).MinimizeButton(True))
        self._mgr.AddPane(self.txt, aui.AuiPaneInfo().CenterPane())

        # 记得要 Update
        self._mgr.Update()

        # 绑定事件
        self.Bind(wx.EVT_ACTIVATE, self.OnActive)  # Whenever the mouse to click the window, check the updated directory
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnTreeRightUp)  # Right-click popup menu
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.EnterFile, self.dir_tree.tree)

    def OnActive(self, event):
        if event.GetActive():
            print("On Active!")
            if self.dir_tree.IsDirChange():
                print("Refresh dir-tree!")
                self.dir_tree.InitTree()

    def OnTreeRightUp(self, event):
        id = self.dir_tree.GetSelectionItem()
        self.msg = ""
        if id.IsOk():
            self.msg = self.dir_tree.GetItemData(id)
            print(self.msg)

        menu = wx.Menu()

        menu_refresh = menu.Append(-1, "refresh")
        self.Bind(wx.EVT_MENU, self.ReFresh, menu_refresh)

        menu_open_file = menu.Append(-1, "open file")
        self.Bind(wx.EVT_MENU, self.OpenFile, menu_open_file)

        menu_create_file = menu.Append(-1, "new file")
        self.Bind(wx.EVT_MENU, self.OnCreateFile, menu_create_file)

        menu_create_directory = menu.Append(-1, "new directory")
        self.Bind(wx.EVT_MENU, self.OnCreateDirectory, menu_create_directory)

        menu_delete_directory = menu.Append(-1, "delete directory")
        self.Bind(wx.EVT_MENU, self.OnDeleteDirectory, menu_delete_directory)

        menu_delete_file = menu.Append(-1, "delete file")
        self.Bind(wx.EVT_MENU, self.OnDeleteFile, menu_delete_file)

        menu_rename = menu.Append(-1, "rename")
        self.Bind(wx.EVT_MENU, self.OnRename, menu_rename)

        menu_close_file = menu.Append(-1, "close file")
        self.Bind(wx.EVT_MENU, self.CloseFile, menu_close_file)

        menu_return = menu.Append(-1, "return")
        self.Bind(wx.EVT_MENU, self.OnReturn, menu_return)

        self.PopupMenu(menu)
        menu.Destroy()

        # Remember to cancel the current selection
        self.dir_tree.Unselect()

    def OnSend(self, event):
        self.txt.AppendText("\nClick: " + self.msg)

    def ReFresh(self, event):
        """
        Refresh Tree and Detail Prototypes
        """
        self.dir_tree.InitTree()

    def OnCreateFile(self, event):
        """
        Create a new file
        """
        self.dir_tree.CreateFile()
        self.dir_tree.InitTree()

    def OnCreateDirectory(self, event):
        """
        Create a new folder
        """
        self.dir_tree.CreateDirectory()
        self.dir_tree.InitTree()

    def OnDeleteDirectory(self, event):
        id = self.dir_tree.GetSelectionItem()
        self.dir_tree.DeleteDirectory(id)
        self.dir_tree.InitTree()

    def OnDeleteFile(self, event):
        id = self.dir_tree.GetSelectionItem()
        self.dir_tree.DeleteFile(id)
        self.dir_tree.InitTree()

    def OnRename(self, event):
        item = self.dir_tree.tree.GetSelection()
        self.dir_tree.OnRename()
        self.dir_tree.InitTree()

    def EnterFile(self, event):
        id = self.dir_tree.GetSelectionItem()
        self.msg = self.dir_tree.GetItemData(id)
        select_file_path = os.path.join(self.dir_tree.work_path, self.msg[1])
        print(select_file_path)
        if os.path.isdir(select_file_path):
            self.dir_tree.work_path = select_file_path
            self.dir_tree.tree.DeleteAllItems()
            self.dir_tree.InitTree()
        else:
            self.ReadFile(select_file_path)
        print("Enter:"+self.msg[1])

    def CloseFile(self, event):
        self.txt.Clear()

    def ReadFile(self, file_path):
        self.txt.Clear()
        with open(file_path, 'r', encoding='utf-8') as file:
            file_data = file.readlines()
            for row in file_data:
                self.txt.AppendText(row)

    def OpenFile(self, event):
        id = self.dir_tree.GetSelectionItem()
        self.msg = self.dir_tree.GetItemData(id)
        select_file_path = os.path.join(self.dir_tree.work_path, self.msg[1])
        os.startfile(select_file_path)

    def OnReturn(self, event):
        """
        Back at the next higher level
        """
        self.dir_tree.work_path = os.path.split(self.dir_tree.work_path)[0]
        self.dir_tree.tree.DeleteAllItems()
        self.dir_tree.InitTree()



if __name__ == '__main__':
    app = wx.App()
    frm = TestFrame(None)
    frm.Show()
    app.MainLoop()



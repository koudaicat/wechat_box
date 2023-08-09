import uiautomation as uia
import time


class WxParam:
    SYS_TEXT_HEIGHT = 33
    TIME_TEXT_HEIGHT = 34
    RECALL_TEXT_HEIGHT = 45
    CHAT_TEXT_HEIGHT = 52
    CHAT_IMG_HEIGHT = 117
    SpecialTypes = ['[文件]', '[图片]', '[视频]', '[音乐]', '[链接]']


class WxUtils:
    def SplitMessage(MsgItem):
        uia.SetGlobalSearchTimeout(0)
        MsgItemName = MsgItem.Name
        if MsgItem.BoundingRectangle.height() == WxParam.SYS_TEXT_HEIGHT:
            Msg = ('SYS', MsgItemName, ''.join([str(i) for i in MsgItem.GetRuntimeId()]))
        elif MsgItem.BoundingRectangle.height() == WxParam.TIME_TEXT_HEIGHT:
            Msg = ('Time', MsgItemName, ''.join([str(i) for i in MsgItem.GetRuntimeId()]))
        elif MsgItem.BoundingRectangle.height() == WxParam.RECALL_TEXT_HEIGHT:
            if '撤回' in MsgItemName:
                Msg = ('Recall', MsgItemName, ''.join([str(i) for i in MsgItem.GetRuntimeId()]))
            else:
                Msg = ('SYS', MsgItemName, ''.join([str(i) for i in MsgItem.GetRuntimeId()]))
        else:
            Index = 1
            User = MsgItem.ButtonControl(foundIndex=Index)
            try:
                while True:
                    if User.Name == '':
                        Index += 1
                        User = MsgItem.ButtonControl(foundIndex=Index)
                    else:
                        break
                Msg = (User.Name, MsgItemName, ''.join([str(i) for i in MsgItem.GetRuntimeId()]))
            except Exception as e:
                Msg = ('SYS', MsgItemName, ''.join([str(i) for i in MsgItem.GetRuntimeId()]))
        uia.SetGlobalSearchTimeout(10.0)
        return Msg


    def ControlSize(control):
        locate = control.BoundingRectangle
        size = (locate.width(), locate.height())
        return size


class WeChat:
    def __init__(self):
        self.UiaAPI = uia.WindowControl(ClassName='WeChatMainWndForPC')
        self.SessionList = self.UiaAPI.ListControl(Name='会话')
        # self.hello = self.UiaAPI.ButtonControl(Name="聊天")
        self.EditMsg = self.UiaAPI.EditControl(Name='输入')
        self.SearchBox = self.UiaAPI.EditControl(Name='搜索')
        self.MsgList = self.UiaAPI.ListControl(Name='消息')
        self.SessionItemList = []
        self.begin_time = None


    def GetSessionList(self, reset=False):
        '''获取当前会话列表，更新会话列表'''
        self.SessionItem = self.SessionList.ListItemControl()
        SessionList = []  # 会话人员列表
        lastname = ''
        num = 0
        while True:
            try:
                name = self.SessionItem.Name
                SessionList.append(name)
            except:
                self.SessionList.WheelDown(wheelTimes=3, waitTime=0.1 * 3)
                self.SessionItem = self.SessionList.ListItemControl()
                if num != 0:
                    if lastname.Name == self.SessionItem.Name:
                        print(lastname, self.SessionItem)
                        break
                lastname = self.SessionItem
                num += 1
            self.SessionItem = self.SessionItem.GetNextSiblingControl()

        return list(set(SessionList))

    def Search(self, keyword):
        '''
        查找微信好友或关键词
        keywords: 要查找的关键词，str   * 最好完整匹配，不完全匹配只会选取搜索框第一个
        '''
        # self.hello.Click()
        self.UiaAPI.SetFocus()
        time.sleep(0.2)
        # self.UiaAPI.click()
        self.UiaAPI.SendKeys('{Ctrl}f', waitTime=1)
        self.SearchBox.SendKeys(keyword, waitTime=1.5)
        self.SearchBox.SendKeys('{Enter}')
        self.SearchBox.SendKeys('{Enter}')

    def LoadMoreMessage(self, n=0.1):
        '''定位到当前聊天页面，并往上滚动鼠标滚轮，加载更多聊天记录到内存'''
        n = 0.1 if n < 0.1 else 1 if n > 1 else n
        self.MsgList.WheelUp(wheelTimes=int(500 * n), waitTime=0.1)

    def get_who(self, who, RollTimes=1):
        self.UiaAPI.SwitchToThisWindow()
        RollTimes = 10 if not RollTimes else RollTimes

        def roll_to(who=who, RollTimes=RollTimes):
            for i in range(RollTimes):
                if who not in self.GetSessionList()[:-1]:
                    self.SessionList.WheelDown(wheelTimes=3, waitTime=0.1 * i)
                else:
                    time.sleep(0.5)
                    self.SessionList.ListItemControl(Name=who).Click(simulateMove=False)
                    return 1
            return 0

        rollresult = roll_to()
        if rollresult:
            return 1
        else:
            self.Search(who)
            return roll_to(RollTimes=1)

    def GetAllMessage(self):
        '''获取当前窗口中加载的所有聊天记录'''
        MsgDocker = []
        SYS = 0
        while True:
            MsgItems = self.MsgList.GetChildren()
            for MsgItem in MsgItems:
                s = WxUtils.SplitMessage(MsgItem)
                if s[0] == 'SYS':
                    SYS = s[1]
                MsgDocker.append(s)
            if SYS:
                break
            # print(MsgItems, len(MsgItems))
            if len(MsgItems) != 0:
                self.LoadMoreMessage(n=0.1)
            if len(MsgItems) == 0:
                break
        res = [(x[0], x[1], x[2], SYS) for x in MsgDocker]
        return res





if __name__ == '__main__':
    action = WeChat()
    # 获取微信聊天界面里面的所有好友或群聊
    people_list = action.GetSessionList()
    for man in people_list:
        action.Search(man)
        s = action.GetAllMessage() # 依次获取与每个好友或群聊的聊天记录
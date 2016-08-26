# -*- coding: utf-8 -*-

import wx
import os
import sqlite3
import random
import wx.grid as gridlib


def twoZeroPoint(dataFloat):
    return str("{0:.2f}".format(dataFloat))


class DBwork():
    def __init__(self, dbFileName):
        try:
            self.connect = sqlite3.connect(dbFileName)
            self.cursor = self.connect.cursor()
            self.cursor.execute('CREATE TABLE if not exists receipt (id INTEGER PRIMARY KEY AUTOINCREMENT,'
                                ' name TEXT,'
                                ' receipt TEXT)')
            self.cursor.execute('CREATE TABLE if not exists ingredients (id INTEGER PRIMARY KEY AUTOINCREMENT,'
                                ' nameRec TEXT,'
                                ' name TEXT,'
                                ' type TEXT,'
                                ' nomVolType REAL,'
                                ' priceNomVolType REAL,'
                                ' count INT,'
                                ' sum REAL)')
            self.connect.commit()
        except:
            pass

    def getListReceipt(self):
        self.cursor.execute('select name from receipt')
        return self.cursor.fetchall()

    def getListName(self, name):
        req = u'select name from ingredients where name like "{name}%"'.format(name=name)
        self.cursor.execute(req)
        data = self.cursor.fetchall()
        return data

    def saveReceipt(self, nameRec, textRec, dataRec):
        self.cursor.execute('''
            delete from receipt where name = :name''', {"name": nameRec})
        self.cursor.execute('''
            delete from ingredients where nameRec = :name''', {"name": nameRec})
        self.cursor.execute('''
            insert into receipt (name, receipt) values (?, ?);''', [nameRec, textRec])
        for i in dataRec:
            self.cursor.execute('''
            insert into ingredients (nameRec,
             name,
             type,
             nomVolType,
             priceNomVolType,
             count,
             sum)
             values (?, ?, ?, ?, ?, ?, ?)''', [nameRec, i[0], i[1], i[2], i[3], i[4], i[5]])
        self.connect.commit()

    def deleteReceipt(self, nameRec):
        self.cursor.execute('''
            delete from receipt where name = :name''', {"name": nameRec})
        self.cursor.execute('''
            delete from ingredients where nameRec = :name''', {"name": nameRec})
        self.connect.commit()

    def getReceiptData(self, receipt):
        receiptData = []
        self.cursor.execute('''
        select name, type, nomVolType, priceNomVolType, count, sum from ingredients where nameRec = :receipt''',
                            {"receipt": receipt})
        data = self.cursor.fetchall()
        if len(data) == 0:
            return [{'name': '',
                    'type': '',
                    'nomVolType': '',
                    'priceNomVolType': '',
                    'count': '',
                    'sum': ''}]
        for i in data:
            receiptData.append({'name': i[0],
                                'type': i[1],
                                'nomVolType': i[2],
                                'priceNomVolType': i[3],
                                'count': i[4],
                                'sum': i[5]})
        return receiptData

    def getText(self, receipt):
        self.cursor.execute('''
        select receipt from receipt where name = :receipt''', {"receipt": receipt})
        data = self.cursor.fetchone()
        if data == None:
            return u'Пусто'
        return data[0]

    def Close(self):
        self.connect.close()

DB = DBwork('test.db')


class ReceiptChoice (wx.Frame):
    def __init__(self, parent, ID, title, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, ID, title, pos, size, style)
        sizer=wx.BoxSizer(wx.VERTICAL)
        self.box = MainListBox(self, -1, choices=self.loadDataToListBox())
        self.OK = wx.Button(self, -1, 'OK')
        sizer.Add(self.box, 1, wx.EXPAND)
        sizer.Add(self.OK, 0, wx.EXPAND)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_BUTTON, self.setData, self.OK)

    def loadDataToListBox(self):
        keys = []
        for i in DB.getListReceipt():
            keys.append(i[0])
        return keys

    def setData(self, evt):
        name = self.box.GetString(self.box.GetSelection())
        i.mainPanel.nameReceipt.SetLabel(name)
        i.loadReceipt()
        self.Destroy()

class Main(wx.Frame):
    def __init__(self):
        # self.DB = DBwork('test.db')
        wx.Frame.__init__(self, None, title='Cooci!', size=(1000, 700), style=wx.MINIMIZE_BOX
                                                                              | wx.MAXIMIZE_BOX
                                                                              | wx.RESIZE_BORDER
                                                                              | wx.SYSTEM_MENU
                                                                              | wx.CAPTION
                                                                              | wx.CLOSE_BOX
                                                                              | wx.CLIP_CHILDREN)
        self.mainMenu = wx.MenuBar()
        self.menuFile = wx.Menu()
        self.menuFile.Append(1011, u'Открыть')
        self.mainMenu.Append(self.menuFile, u'База')
        self.menuReceipt = wx.Menu()
        self.menuReceipt.Append(1021, u'Выбрать')
        self.menuReceipt.Append(1022, u'Сохранить')
        self.menuReceipt.Append(1023, u'Новый')
        self.menuReceipt.Append(1024, u'Удалить')
        self.mainMenu.Append(self.menuReceipt, u'Рецепты')
        self.SetMenuBar(self.mainMenu)

        self.Bind(wx.EVT_MENU, self.openBase, id=1011)
        self.Bind(wx.EVT_MENU, self.openReceipt, id=1021)
        self.Bind(wx.EVT_MENU, self.saveReceipt, id=1022)
        self.Bind(wx.EVT_MENU, self.newReceipt, id=1023)
        self.Bind(wx.EVT_MENU, self.deleteReceipt, id=1024)

        mainSizerHor = wx.BoxSizer(wx.HORIZONTAL)
        self.mainPanel = MainPanel(self, -1)

        mainSizerHor.Add(self.mainPanel, 1, wx.EXPAND)

        self.SetSizer(mainSizerHor)
        self.Show()
        self.Layout()

    def openReceipt(self, evt):
        choiceReceipt = ReceiptChoice(self, -1, u'Выбери рецепт')
        choiceReceipt.Show(True)

    def loadReceipt(self):
        self.mainPanel.listPanel.clean()
        selection = self.mainPanel.nameReceipt.GetLabel()
        data = DB.getReceiptData(selection)
        text = DB.getText(selection)
        self.mainPanel.addText(text)
        self.mainPanel.listPanel.genLines(data)
        self.mainPanel.Layout()

    def openBase(self, evt):
        wildcard = "Sqlite3 file (*.db)|*.db|" \
                   "All files (*.*)|*.*"
        dlg = wx.FileDialog(
            self, message=u"Выберите файл",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
            )

        if dlg.ShowModal() == wx.ID_OK:
            paths = dlg.GetPaths()

    def saveReceipt(self, evt):
        name = self.mainPanel.nameReceipt.GetLabel()
        data = self.mainPanel.listPanel.getLines()
        # print data
        text = self.mainPanel.mainText.GetValue()
        DB.saveReceipt(name, text, data)

    def updateDataListBox(self):
        pass
        # self.mainListBox.update(self.loadDataToListBox())

    def loadDataToListBox(self):
        keys = []
        for i in DB.getListReceipt():
            keys.append(i[0])
        return keys

    def onSelectItem(self, event):
        self.mainPanel.listPanel.clean()
        selection = self.mainPanel.nameReceipt.GetValue()
        data = DB.getReceiptData(selection)
        text = DB.getText(selection)
        self.mainPanel.addText(text)
        self.mainPanel.listPanel.genLines(data)
        self.mainPanel.setCost(event)

    def newReceipt(self, event):
        self.mainPanel.clean()
        while 1:
            dialog = wx.TextEntryDialog(self, u'Имя блюда', '')
            answer = dialog.ShowModal()
            if answer == wx.ID_OK:
                if dialog.GetValue() == '' or dialog.GetValue() == None:
                    dlg = wx.MessageDialog(self,
                                           u'Нельзя пустое имя'.format(self.mainPanel.nameReceipt.GetLabel()),
                                           u'Предупреждение',
                                           wx.ID_OK | wx.ICON_WARNING
                                           )
                    dlg.ShowModal()
                    dlg.Destroy()
                    continue
                self.mainPanel.setName([dialog.GetValue()])
                return
            elif answer == wx.ID_CANCEL:
                print 'tss'
                break

    def deleteReceipt(self, event):
        name = self.mainPanel.nameReceipt.GetLabel()
        if name == '' or name == None:
            dlg = wx.MessageDialog(self, u'Нельзя удалить пустое имя'.format(self.mainPanel.nameReceipt.GetLabel()),
                                   u'Предупреждение',
                                   wx.ID_OK | wx.ICON_WARNING
                                   )
            dlg.ShowModal()
            dlg.Destroy()
            return

        dlg = wx.MessageDialog(self, u'Точно удалить {}?'.format(self.mainPanel.nameReceipt.GetLabel()),
                               u'Подтверждение удаления',
                               wx.YES_NO | wx.ICON_WARNING
                               )

        if dlg.ShowModal() == wx.ID_YES:
            DB.deleteReceipt(name)
            self.mainPanel.nameReceipt.SetLabel('')
            self.mainPanel.listPanel.clean()

        dlg.Destroy()



class MainPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizerButtons = wx.BoxSizer(wx.HORIZONTAL)
        panelSizerCaptionSave = wx.FlexGridSizer(1, 4, 1, 4)
        self.addButton = wx.Button(self, -1, u"Добавить строку", size=(-1, 30))
        self.delButton = wx.Button(self, -1, u"Удалить строку", size=(-1, 30))

        self.nameReceipt = wx.StaticText(self, -1, label=u'Рецепт')
        self.mainText = wx.TextCtrl(self, -1, style=wx.MULTIPLE)

        self.costText = wx.StaticText(self, -1, label=u'Итого=')

        self.count = wx.TextCtrl(self, -1, value='1', size=(50, 25))

        self.countText = wx.StaticText(self, -1, label=u'Шт.=')


        self.gridPanel = wx.Panel(self)
        sizer2 = wx.BoxSizer()
        self.listPanel = GridPanel(self.gridPanel)
        sizer2.Add(self.listPanel, 1, wx.EXPAND|wx.ALL)
        self.gridPanel.SetSizer(sizer2)

        panelSizerCaptionSave.Add((10, 10))
        panelSizerCaptionSave.Add(self.costText, 0, wx.ALIGN_RIGHT)
        panelSizerCaptionSave.Add(self.count, 0, wx.ALIGN_RIGHT)
        panelSizerCaptionSave.Add(self.countText, 0, wx.ALIGN_RIGHT)
        panelSizerCaptionSave.AddGrowableCol(1)

        panelSizerButtons.Add(self.addButton, 0)
        panelSizerButtons.Add(self.delButton, 0)

        panelSizer.Add((0, 10))
        panelSizer.Add(self.nameReceipt,1 ,wx.EXPAND, 0)
        panelSizer.Add(panelSizerButtons, 1)
        panelSizer.Add(self.gridPanel, 10, wx.EXPAND|wx.ALL)
        panelSizer.Add(self.mainText, 10, wx.EXPAND)
        panelSizer.Add(panelSizerCaptionSave, 1, wx.EXPAND)

        self.SetSizer(panelSizer)
        self.Bind(wx.EVT_BUTTON, self.clickAdd, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.clickDel, self.delButton)
        self.listPanel.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.setCost)
        self.Bind(gridlib.EVT_GRID_SELECT_CELL, self.setCellChoice)
        self.count.Bind(wx.EVT_KEY_UP, self.setCost, self.count)
        self.Bind(wx.EVT_KEY_DOWN, self.test, self.listPanel)
        self.Bind(gridlib.EVT_GRID_EDITOR_CREATED, self.test)

    def setName(self, name):
        self.nameReceipt.SetLabel(u''.join(name))

    def clean(self):
        #TODO add remind to save
        self.mainText.Clear()
        self.listPanel.clean()
        self.Layout()

    def clickAdd(self, event):
        self.listPanel.addLine()
        self.Layout()

    def clickDel(self, event):
        self.listPanel.delLine()
        self.Layout()

    def addText(self, text):
        self.mainText.Clear()
        self.mainText.SetValue(text)


    def test(self, evt):
        self.x = self.listPanel.GetGridCursorCol()
        self.y = self.listPanel.GetGridCursorRow()
        self.tt = evt.Control
        self.tt.Bind(wx.EVT_TEXT, self.test2)
    def test2(self, evt):
        data = DB.getListName(evt.GetString())
        short_list=[]
        for i in data:
            short_list.append(i[0])
        self.tt.Clear()
        self.tt.Append(short_list)
        evt.Skip()


    def setCost(self, evt):
        # print self.listPanel.GetGridCursorCol()
        # print self.listPanel.GetGridCursorRow()
        summ = self.listPanel.calcSum(evt)
        self.costText.SetLabel(u"Итого= {} р.".format(summ))
        try:
            count = float(self.count.GetValue())
        except:
            count = 1
        price = float(summ)/count
        self.countText.SetLabel(u"Шт= {} р.".format(twoZeroPoint(price)))
        self.Layout()

    def setCellChoice(self, event):
        txt = self.listPanel.GetCellValue(event.GetRow(),
                                event.GetCol())
        data = DB.getListName(txt)
        short_list=[]
        for i in data:
            short_list.append(i[0])
        self.listPanel.SetCellEditor(event.GetRow(),
                                event.GetCol(), gridlib.GridCellChoiceEditor(short_list, allowOthers=True))
        event.Skip()

    def setCellChoice2(self, (x, y), text):
        data = DB.getListName(text)
        print data
        short_list = []
        for i in data:
            short_list.append(i[0])
        self.listPanel.SetCellEditor(x, y, gridlib.GridCellChoiceEditor(short_list, allowOthers=True))


class MainListBox(wx.ListBox):
    def __init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 choices=[], style=0, validator=wx.DefaultValidator):
        wx.ListBox.__init__(self, parent, id, pos=wx.DefaultPosition, size=wx.DefaultSize,
                            choices=choices, style=0, validator=wx.DefaultValidator)

    def update(self, choices):
        self.Clear()
        for i in choices:
            self.Append(i)


class GridPanel(gridlib.Grid):
    def __init__(self,parent):
        self. values = {'name': 0,
               'type': 1,
               'nomVolType': 2,
               'priceNomVolType': 3,
               'count': 4,
               'sum': 5,
               }
        gridlib.Grid.__init__(self, parent, -1)
        self.CreateGrid(1, 6)
        self.SetColLabelValue(0, u'Наименование')
        self.SetColLabelSize(60)
        self.SetColSize(0, 200)
        self.SetColLabelValue(1, u'Единицы')
        self.SetColSize(1, 110)
        self.SetColLabelValue(2, u'Количество в\n упаковке')
        self.SetColSize(2, 110)
        self.SetColLabelValue(3, u'Стоимость\n упаковки')
        self.SetColSize(3, 110)
        self.SetColLabelValue(4, u'Количество\n используемое')
        self.SetColSize(4, 110)
        self.SetColLabelValue(5, u'Сумма')
        self.SetColSize(5, 100)


    def clean(self):
        self.DeleteRows(numRows=self.GetNumberRows())
        self.ClearGrid()

    def genLines(self, receipt):
        self.AppendRows(len(receipt))
        for i in range(0, len(receipt)):
            for data in receipt[i]:
                self.SetCellValue(i, self.values[data], u'{}'.format(receipt[i][data]))
            self.SetCellEditor(i, 2, gridlib.GridCellFloatEditor())
            self.SetCellEditor(i, 3, gridlib.GridCellFloatEditor())
            self.SetCellEditor(i, 4, gridlib.GridCellFloatEditor())
            self.SetCellEditor(i, 5, gridlib.GridCellFloatEditor())

    def addLine(self):
        self.AppendRows(numRows=1)

    def delLine(self):
        dialog = wx.TextEntryDialog(self, u'Номер строки', '')
        if dialog.ShowModal() == wx.ID_OK:
            try:
                self.DeleteRows(pos=int(dialog.GetValue())-1)
            except:
                pass
        else:
            pass

    def getLines(self):
        data = []
        for i in range(0, self.GetNumberRows()):
            data.append([])
            for j in range(0, self.GetNumberCols()):
                data[i].append(self.GetCellValue(i, j))
        return data

    def calcSum(self, evt):
        summ = 0
        for i in range(0, self.GetNumberRows()):
            packVolume = self.GetCellValue(i, 2)
            price = self.GetCellValue(i, 3)
            count = self.GetCellValue(i, 4)
            if packVolume == None: packVolume = 0
            if price == None: price = 0
            if count == None: count = 0
            x = (float(price) / float(packVolume)) * float(count)
            summ += x
            self.SetCellValue(i, 5, twoZeroPoint(x))
        return twoZeroPoint(summ)




app = wx.App()
i = Main()
app.MainLoop()

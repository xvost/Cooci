# -*- coding: utf-8 -*-

import wx
import sys
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
        select name, type, nomVolType, priceNomVolType, count, sum from ingredients where nameRec = :receipt''', {"receipt": receipt})
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


class Main(wx.Frame):
    def __init__(self):
        self.DB = DBwork('test.db')
        wx.Frame.__init__(self, None, title='Cooci!', size=(1000, 700), style=wx.MINIMIZE_BOX
                                                                              # | wx.MAXIMIZE_BOX
                                                                              | wx.RESIZE_BORDER
                                                                              | wx.SYSTEM_MENU
                                                                              | wx.CAPTION
                                                                              | wx.CLOSE_BOX
                                                                              | wx.CLIP_CHILDREN)
        mainSizerHor = wx.BoxSizer(wx.HORIZONTAL)
        mainSizerVert = wx.BoxSizer(wx.VERTICAL)
        self.mainPanel = MainPanel(self, -1)
        self.mainListBox = MainListBox(self, -1, choices=self.loadDataToListBox())
        self.addButton = wx.Button(self, -1, u'Новый')
        self.delButton = wx.Button(self, -1, u'Удалить')
        self.saveButton = wx.Button(self, -1, u'Сохранить')
        mainSizerVert.Add(self.mainListBox, 1, wx.EXPAND)
        mainSizerVert.Add(self.addButton, 0, wx.EXPAND)
        mainSizerVert.Add(self.delButton, 0, wx.EXPAND)
        mainSizerVert.Add(self.saveButton, 0, wx.EXPAND)
        mainSizerHor.Add(mainSizerVert, 3, wx.EXPAND)
        mainSizerHor.Add(self.mainPanel, 3, wx.EXPAND)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.onSelectItem, self.mainListBox)
        self.Bind(wx.EVT_LISTBOX, self.onSelectItem, self.mainListBox)
        self.Bind(wx.EVT_BUTTON, self.onClickButtonAdd, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.onClickButtonSave, self.saveButton)
        self.Bind(wx.EVT_BUTTON, self.onClickButtonDelete, self.delButton)
        self.Bind(wx.EVT_BUTTON, self.updateDataListBox())
        self.SetSizeHints(400, 500, 1000, 700)

        self.SetSizer(mainSizerHor)
        self.Show()
        self.Layout()

    def updateDataListBox(self):
        self.mainListBox.update(self.loadDataToListBox())

    def loadDataToListBox(self):
        keys = []
        for i in self.DB.getListReceipt():
            keys.append(i[0])
        return keys

    def onSelectItem(self, event):
        self.mainPanel.listPanel.clean()
        selection = self.mainListBox.GetStringSelection()
        data = self.DB.getReceiptData(selection)
        text = self.DB.getText(selection)
        self.mainPanel.addText(text)
        self.mainPanel.listPanel.genLines(data)
        self.mainPanel.setCost(event)

    def onClickButtonAdd(self, event):
        dialog = wx.TextEntryDialog(self, u'Имя блюда', '')
        if dialog.ShowModal() == wx.ID_OK:
            self.mainListBox.InsertItems([dialog.GetValue()], 0)
        else:
            print 'tss'

    def onClickButtonSave(self, event):
        name = self.mainListBox.GetString(self.mainListBox.GetSelection())
        data = self.mainPanel.listPanel.getLines()
        # print data
        text = self.mainPanel.mainText.GetValue()
        self.DB.saveReceipt(name, text, data)

    def onClickButtonDelete(self, event):
        name = self.mainListBox.GetString(self.mainListBox.GetSelection())
        self.DB.deleteReceipt(name)
        self.mainListBox.Delete(self.mainListBox.GetSelection())


class MainPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id)
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        panelSizerButtons = wx.BoxSizer(wx.HORIZONTAL)
        panelSizerCaptionSave = wx.FlexGridSizer(1, 3, 1, 3)
        self.addButton = wx.Button(self, -1, u"Добавить", size=(100, 30))
        self.delButton = wx.Button(self, -1, u"Удалить", size=(100, 30))

        self.mainText = wx.TextCtrl(self, -1, style=wx.MULTIPLE)

        self.costText = wx.StaticText(self, -1, label=u'Итого=')

        self.captionTextSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.gridPanel = wx.Panel(self)
        sizer2 = wx.BoxSizer()
        self.listPanel = GridPanel(self.gridPanel)
        sizer2.Add(self.listPanel, 1, wx.EXPAND|wx.ALL)
        self.gridPanel.SetSizer(sizer2)

        panelSizerCaptionSave.Add((10, 10))
        panelSizerCaptionSave.Add(self.costText, 0, wx.ALIGN_RIGHT)
        panelSizerCaptionSave.AddGrowableCol(1)

        panelSizerButtons.Add(self.addButton, 0)
        panelSizerButtons.Add(self.delButton, 0)


        panelSizer.Add(panelSizerButtons, 1)
        panelSizer.Add(self.captionTextSizer,1 ,wx.EXPAND, 0)
        panelSizer.Add(self.gridPanel, 10, wx.EXPAND|wx.ALL)
        panelSizer.Add(self.mainText, 10, wx.EXPAND)
        panelSizer.Add(panelSizerCaptionSave, 1, wx.EXPAND)

        self.SetSizer(panelSizer)
        self.Bind(wx.EVT_BUTTON, self.clickAdd, self.addButton)
        self.Bind(wx.EVT_BUTTON, self.clickDel, self.delButton)
        self.listPanel.Bind(wx.grid.EVT_GRID_CELL_CHANGE, self.setCost)


    def clickAdd(self, event):
        self.listPanel.addLine()
        self.Layout()

    def clickDel(self, event):
        self.listPanel.delLine()
        self.Layout()

    def addText(self, text):
        self.mainText.Clear()
        self.mainText.SetValue(text)

    def setCost(self, evt):
        summ = self.listPanel.calcSum(evt)
        self.costText.SetLabel(u"Итого= {} р.".format(summ))
        self.Layout()


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
            x = (float(price) / float(packVolume)) * float(count)
            summ += x
            self.SetCellValue(i, 5, twoZeroPoint(x))
        return twoZeroPoint(summ)


app = wx.App()
i = Main()
app.MainLoop()

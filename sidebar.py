#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4 import QtGui

from widget import Button, Viewer
from colorPicker import ColorDialog


class PaletteCanvas(QtGui.QWidget):
    """ Canvas where the palette is draw """
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.background = QtGui.QBrush(self.parent.project.bgColor)
        self.black = QtGui.QColor(0, 0, 0)
        self.white = QtGui.QColor(255, 255, 255)
        self.parent.project.updateBackgroundSign.connect(self.updateBackground)
        self.rowLength = 8
        self.swatchWidth = self.swatchHeight = 16
        self.swatchHorizontalPadding = self.swatchVerticalPadding = 2
        self.swatchOffsetX = self.swatchWidth + 2 * self.swatchHorizontalPadding
        self.swatchOffsetY = self.swatchHeight + 2 * self.swatchVerticalPadding
        self.setFixedSize(self.rowLength * self.swatchOffsetX + self.swatchHorizontalPadding,
                          self.rowLength * self.swatchOffsetY + self.swatchVerticalPadding)
        
    def updateBackground(self):
         self.background = QtGui.QBrush(self.parent.project.bgColor)
         self.update()

    def swatchIndexToGridCoord(self, index):
        return (index % self.rowLength, index // self.rowLength)
    
    def swatchGridCoordToIndex(self, x, y):
        return y * self.rowLength + x
    
    def swatchRect(self, x, y):
        return QtCore.QRect(x * self.swatchOffsetX + self.swatchHorizontalPadding,
                            y * self.swatchOffsetY + self.swatchVerticalPadding,
                            self.swatchWidth, self.swatchHeight)
    
    def paintEvent(self, ev=''):
        p = QtGui.QPainter(self)
        p.fillRect (0, 0, self.width(), self.height(), self.background)
        for n, i in enumerate(self.parent.project.colorTable):
            rect = self.swatchRect(*(self.swatchIndexToGridCoord(n)))
            color = QtGui.QColor().fromRgba(i)
            if n == 0:
                p.fillRect(rect.adjusted(0, 0, -rect.width() // 2, -rect.height() // 2), QtGui.QBrush(color))
                p.fillRect(rect.adjusted(rect.width() // 2, rect.height() // 2, 0, 0), QtGui.QBrush(color))
            else:
                p.fillRect(rect, QtGui.QBrush(color))

        rect = self.swatchRect(*(self.swatchIndexToGridCoord(self.parent.project.color)))
        p.setPen(self.black)
        p.drawRect (rect.adjusted(-2, -2, 1, 1))
        p.setPen(self.white)
        p.drawRect (rect.adjusted(-1, -1, 0, 0))

    def event(self, event):
        if (event.type() == QtCore.QEvent.MouseButtonPress and
                       event.button()==QtCore.Qt.LeftButton):
            item = self.getItem(event.x(), event.y())
            if item is not None:
                self.parent.project.setColor(item)
        elif (event.type() == QtCore.QEvent.MouseButtonDblClick and
                       event.button()==QtCore.Qt.LeftButton):
            item = self.getItem(event.x(), event.y())
            if item is not None:
                self.parent.editColor(item)
        return QtGui.QWidget.event(self, event)
        
    def getItem(self, x, y):
        x, y = (x - self.swatchHorizontalPadding) // self.swatchOffsetX, (y - self.swatchVerticalPadding) // self.swatchOffsetY
        s = self.swatchGridCoordToIndex(x, y)
        if s >= 0 and s < len(self.parent.project.colorTable):
            return s
        return None

class AlphaCanvas(QtGui.QWidget):
    """ Canvas where the palette is drawn """
    def __init__(self, parent):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.setFixedSize(26, 26)
        self.background = QtGui.QBrush(self.parent.project.bgColor)
        self.alpha = QtGui.QPixmap("icons/color_alpha.png")
        self.parent.project.updateBackgroundSign.connect(self.updateBackground)
        
    def updateBackground(self):
         self.background = QtGui.QBrush(self.parent.project.bgColor)
         self.update()

    def event(self, event):
        if (event.type() == QtCore.QEvent.MouseButtonPress and
                       event.button()==QtCore.Qt.LeftButton):
            self.parent.project.setColor(0)
        elif event.type() == QtCore.QEvent.Paint:
            p = QtGui.QPainter(self)
            p.fillRect (0, 0, self.width(), self.height(), 
                    QtGui.QBrush(QtGui.QColor(70, 70, 70)))
            p.fillRect (1, 1, self.width()-2, self.height()-2, self.background)
            if self.parent.project.color == 0:
                p.fillRect (3, 3, 20, 20, QtGui.QBrush(QtGui.QColor(0, 0, 0)))
                p.fillRect (4, 4, 18, 18, QtGui.QBrush(QtGui.QColor(255, 255, 255)))
            p.drawPixmap(5, 5, self.alpha)
            # just to be sure alpha is the first color
            p.fillRect(5, 5, 16, 16, QtGui.QBrush(
                QtGui.QColor().fromRgba(self.parent.project.colorTable[0])))
        return QtGui.QWidget.event(self, event)

    
class PenWidget(QtGui.QWidget):
    def __init__(self, parent, project):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.project = project
        self.setToolTip("pen")
        self.setFixedSize(26, 26)
        self.project.updateBackgroundSign.connect(self.update)
        self.penMenu = QtGui.QMenu(self)
        self.currentAction = None
        self.loadPen()
        self.project.customPenSign.connect(self.setCustomPen)

    def loadPen(self):
        self.penMenu.clear()
        for name, icon in self.project.penList:
            action = QtGui.QAction(QtGui.QIcon(icon), name, self)
            action.pixmap = icon
            action.setIconVisibleInMenu(True)
            self.penMenu.addAction(action)
            if not self.currentAction:
                self.currentAction = action

    def event(self, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            self.changePen()
        elif event.type() == QtCore.QEvent.Paint:
            p = QtGui.QPainter(self)
            p.fillRect (0, 0, self.width(), self.height(), 
                    QtGui.QBrush(QtGui.QColor(70, 70, 70)))
            p.fillRect (1, 1, self.width()-2, self.height()-2, 
                    QtGui.QBrush(self.project.bgColor))
            if self.currentAction.pixmap:
                p.drawPixmap(5, 5, self.currentAction.pixmap)
        return QtGui.QWidget.event(self, event)
        
    def changePen(self):
        self.penMenu.setActiveAction(self.currentAction)
        action = self.penMenu.exec(self.mapToGlobal(QtCore.QPoint(26, 2)), self.currentAction)
        if action:
            self.currentAction = action
            self.project.pen = self.project.penDict[action.text()]
            self.project.penChangedSign.emit()
            self.update()
        
    def setCustomPen(self, li):
        nLi = []
        mY = len(li)//2
        mX = len(li[0])//2
        for y in range(len(li)):
            py = y - mY
            for x in range(len(li[y])):
                col = li[y][x]
                if col:
                    px = x - mX
                    nLi.append((px, py, col))
        if nLi:
            self.project.penDict["custom"] = nLi
            self.project.pen = self.project.penDict["custom"]
            self.icon = None
            self.update()
            self.project.penChangedSign.emit()
            self.parent.penClicked()


class BrushWidget(QtGui.QWidget):
    def __init__(self, parent, project):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.project = project
        self.setToolTip("brush")
        self.setFixedSize(26, 26)
        self.project.updateBackgroundSign.connect(self.update)
        self.brushMenu = QtGui.QMenu(self)
        self.currentAction = None
        self.loadBrush()

    def loadBrush(self):
        self.brushMenu.clear()
        for name, icon in self.project.brushList:
            action = QtGui.QAction(QtGui.QIcon(icon), name, self)
            action.pixmap = icon
            action.setIconVisibleInMenu(True)
            self.brushMenu.addAction(action)
            if name == "solid":
                self.currentAction = action

    def event(self, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            self.changeBrush()
        elif event.type() == QtCore.QEvent.Paint:
            p = QtGui.QPainter(self)
            p.fillRect (0, 0, self.width(), self.height(), 
                    QtGui.QBrush(QtGui.QColor(70, 70, 70)))
            p.fillRect (1, 1, self.width()-2, self.height()-2, 
                    QtGui.QBrush(self.project.bgColor))
            if self.currentAction.pixmap:
                p.drawPixmap(5, 5, self.currentAction.pixmap)
        return QtGui.QWidget.event(self, event)
        
    def changeBrush(self):
        self.brushMenu.setActiveAction(self.currentAction)
        action = self.brushMenu.exec(self.mapToGlobal(QtCore.QPoint(26, 2)), self.currentAction)
        if action:
            self.currentAction = action
            self.project.brush = self.project.brushDict[action.text()]
            self.update()

            
class OptionFill(QtGui.QWidget):
    """ contextual option for the fill tool """
    def __init__(self, parent, project):
        QtGui.QVBoxLayout .__init__(self)
        self.project = project
        self.parent = parent
        
        self.adjacentFillRadio = QtGui.QRadioButton("adjacent colors", self)
        self.adjacentFillRadio.pressed.connect(self.adjacentPressed)
        self.adjacentFillRadio.setChecked(True)
        self.similarFillRadio = QtGui.QRadioButton("similar colors", self)
        self.similarFillRadio.pressed.connect(self.similarPressed)
        
        ### Layout ###
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.adjacentFillRadio)
        layout.addWidget(self.similarFillRadio)
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
    def adjacentPressed(self):
        self.project.fillMode = "adjacent"
        
    def similarPressed(self):
        self.project.fillMode = "similar"
        
        
class OptionSelect(QtGui.QWidget):
    """ contextual option for the select tool """
    def __init__(self, parent, project):
        QtGui.QVBoxLayout .__init__(self)
        self.project = project
        
        self.cutFillRadio = QtGui.QRadioButton("cut", self)
        self.cutFillRadio.pressed.connect(self.cutPressed)
        self.cutFillRadio.setChecked(True)
        self.copyFillRadio = QtGui.QRadioButton("copy", self)
        self.copyFillRadio.pressed.connect(self.copyPressed)
        
        ### Layout ###
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.cutFillRadio)
        layout.addWidget(self.copyFillRadio)
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
    def cutPressed(self):
        self.project.selectMode = "cut"
    
    def copyPressed(self):
        self.project.selectMode = "copy"
        
class PaletteWidget(QtGui.QWidget):
    """ side widget containing palette """
    def __init__(self, project):
        QtGui.QWidget.__init__(self)
        self.project = project

        self.alphaCanvas = AlphaCanvas(self)

        ### palette ###
        self.paletteCanvas = PaletteCanvas(self)
        self.paletteV = Viewer()
        self.paletteV.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.paletteV.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.paletteV.setWidget(self.paletteCanvas)
        
        self.project.updatePaletteSign.connect(self.paletteCanvas.update)
        self.project.updatePaletteSign.connect(self.alphaCanvas.update)
        addColorB = Button("add color",
            "icons/color_add.png", self.addColor)
        delColorB = Button("delete color",
            "icons/color_del.png", self.delColor)
        moveLeftColorB = Button("move color left",
            "icons/color_move_left.png", self.moveColorLeft)
        moveRightColorB = Button("move color right",
            "icons/color_move_right.png", self.moveColorRight)

        ### Layout ###
        colorButtons = QtGui.QHBoxLayout()
        colorButtons.setSpacing(0)
        colorButtons.addWidget(addColorB)
        colorButtons.addWidget(delColorB)
        colorButtons.addWidget(moveLeftColorB)
        colorButtons.addWidget(moveRightColorB)
        paintOption = QtGui.QHBoxLayout()
        paintOption.setSpacing(0)
        paintOption.addWidget(self.alphaCanvas)
        paintOption.addStretch()
        self.layout = QtGui.QGridLayout()
        self.layout.setSpacing(0)
        self.layout.addLayout(paintOption, 1, 1)
        self.layout.addWidget(self.paletteV, 2, 1)
        self.layout.addLayout(colorButtons, 3, 1)
        self.layout.setContentsMargins(6, 0, 6, 0)
        self.setLayout(self.layout)

    def showEvent(self, event):
        self.paletteV.setFixedWidth(self.paletteCanvas.width() + 
                    self.paletteV.verticalScrollBar().width() + 2)

    ######## Color #####################################################
    def editColor(self, n):
        col = self.project.colorTable[self.project.color]
        ok, color = ColorDialog(False, col).getRgba()
        if not ok:
            return
        self.project.saveToUndo("colorTable")
        self.project.colorTable[n] = color
        for i in self.project.timeline.getAllCanvas():
            i.setColorTable(self.project.colorTable)
        self.project.updateViewSign.emit()
        self.paletteCanvas.update()
        self.project.colorChangedSign.emit()

    def addColor(self):
        """ select a color and add it to the palette"""
        if not len(self.project.colorTable) >= 256:
            col = self.project.colorTable[self.project.color]
            ok, color = ColorDialog(False, col).getRgba()
            if not ok:
                return
            self.project.saveToUndo("colorTable_frames")
            self.project.colorTable.append(color)
            self.project.setColor(len(self.project.colorTable)-1)
            for i in self.project.timeline.getAllCanvas():
                i.setColorTable(self.project.colorTable)
            self.project.updateViewSign.emit()

    def delColor(self):
        col, table = self.project.color, self.project.colorTable
        if col != 0:
            self.project.saveToUndo("colorTable_frames")
            table.pop(col)
            for i in self.project.timeline.getAllCanvas():
                i.delColor(col)
                i.setColorTable(table)
            self.project.setColor(col-1)
            self.project.updateViewSign.emit()

    def moveColorLeft(self):
        col, table = self.project.color, self.project.colorTable
        if col != 0:
            self.project.saveToUndo("colorTable_frames")
            table[col], table[col-1] = table[col-1], table[col]
            for i in self.project.timeline.getAllCanvas():
                i.swapColor(col, col-1)
                i.setColorTable(table)
            self.project.setColor(col-1)

    def moveColorRight(self):
        col, table = self.project.color, self.project.colorTable
        if col != len(table)-1:
            self.project.saveToUndo("colorTable_frames")
            table[col], table[col+1] = table[col+1], table[col]
            for i in self.project.timeline.getAllCanvas():
                i.swapColor(col, col+1)
                i.setColorTable(table)
            self.project.setColor(col+1)

class ContextWidget(QtGui.QWidget):
    """ side widget cantaining painting context """
    def __init__(self, project):
        QtGui.QWidget.__init__(self)
        self.project = project

        self.penWidget = PenWidget(self, self.project)
        self.brushWidget = BrushWidget(self, self.project)

        ### Layout ###
        self.layout = QtGui.QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.addWidget(self.penWidget)
        self.layout.addWidget(self.brushWidget)
        self.layout.addStretch()
        self.layout.setContentsMargins(6, 0, 6, 0)
        self.setLayout(self.layout)
                
class OptionsWidget(QtGui.QWidget):
    """ side widget cantaining options """
    def __init__(self, project):
        QtGui.QWidget.__init__(self)
        self.project = project
        
        self.optionFill = OptionFill(self, self.project)
        self.optionSelect = OptionSelect(self, self.project)

        ### Layout ###
        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.addWidget(self.optionFill)
        self.optionFill.hide()
        self.layout.addWidget(self.optionSelect)
        self.optionSelect.hide()
        self.layout.addStretch()
        self.setLayout(self.layout)        

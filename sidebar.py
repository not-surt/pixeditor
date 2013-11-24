#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import math
import random

from widget import Button, Viewer
from colorPicker import ColorDialog
from FlowLayout import FlowLayout


class ToolWidget(QWidget):
    def __init__(self, parent=None):
        super(ToolWidget, self).__init__(parent)
        layout = FlowLayout()
        #layout = QHBoxLayout()
        #layout.setSizeConstraint(QLayout.SetFixedSize)
        #layout.setSpacing(0)
        #layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        pass

    def addAction(self, action):
        self.parent().addAction(action)
        button = QToolButton(self)
        button.setDefaultAction(action)
        button.setAutoRaise(True)
        iconSize = QApplication.style().pixelMetric(QStyle.PM_ToolBarIconSize)
        size = QApplication.style().sizeFromContents(QStyle.CT_ToolButton, QStyleOptionToolButton(), QSize(iconSize, iconSize))
        button.setIconSize(QSize(iconSize, iconSize))
        button.setFixedSize(size)
        self.layout().addWidget(button)
        pass

class ColorComponentSlider(QSlider):
    def __init__(self, component, orientation=Qt.Horizontal, parent=None):
        super(ColorComponentSlider, self).__init__(orientation, parent)
        self.component = component
        pass


class ColorComponentPlane(QSlider):
    def __init__(self, componentX, componentY, parent=None):
        pass


class ColorSlidersWidget(QWidget):
    colorChanged = pyqtSignal(QColor)
    colorComponentChanged = pyqtSignal(str, int)

    def color(self):
        return self.__color

    def setColor(self, value):
        if value.isValid() and self.__color != value:
            self.__color = value
            self.colorChanged.emit(self.__color)

    pyqtProperty(QColor, color, setColor)

    def setColorComponent(self, component, componentValue):
        color = QColor(self.__color)
        if component == "hue" or component == "saturation" or component == "value" or component == "lightness":
            hue, saturation, value, _ = color.getHsv()
        if component == "cyan" or component == "magenta" or component == "yellow" or component == "black":
           cyan, magenta, yellow, black, _ = color.getCmyk()
        if component == "red":
            color.setRed(componentValue)
        elif component == "green":
            color.setGreen(componentValue)
        elif component == "blue":
            color.setBlue(componentValue)
        elif component == "hue":
            color.setHsv(componentValue, saturation, value)
        elif component == "saturation":
            color.setHsv(hue, componentValue, value)
        elif component == "value":
            color.setHsv(hue, saturation, componentValue)
        elif component == "lightness":
            color.setHsl(hue, saturation, componentValue)
        elif component == "cyan":
            color.setCmyk(componentValue, magenta, yellow, black)
        elif component == "magenta":
            color.setCmyk(cyan, componentValue, yellow, black)
        elif component == "yellow":
            color.setCmyk(cyan, magenta, componentValue, black)
        elif component == "black":
            color.setCmyk(cyan, magenta, yellow, componentValue)
        self.setColor(color)

    def getColorComponent(color, component):
        if component == "red":
            return color.red()
        elif component == "green":
            return color.green()
        elif component == "blue":
            return color.blue()
        elif component == "hue":
            return color.getHsv()[0]
        elif component == "saturation":
            return color.getHsv()[1]
        elif component == "value":
            return color.getHsv()[2]
        elif component == "lightness":
            return color.getHsl()[2]
        elif component == "cyan":
            return color.getCmyk()[0]
        elif component == "magenta":
            return color.getCmyk()[1]
        elif component == "yellow":
            return color.getCmyk()[2]
        elif component == "black":
            return color.getCmyk()[3]

    def __init__(self, components, parent=None):
        super(ColorSlidersWidget, self).__init__(parent)

        self.__color = QColor()

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        for i in range(0, len(components)):
            if components[i] is None:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                layout.addWidget(separator, i, 0, 1, 3)
            else:
                slider = QSlider(Qt.Horizontal, self)
                # Range
                componentRange = (0, 255) if components[i][2] is None else components[i][2]
                slider.setRange(*componentRange)
                slider.setTickInterval((componentRange[1] - componentRange[0]) // 8)
                # Step
                if components[i][3] is None:
                    slider.setSingleStep(1)
                    slider.setPageStep(8)
                else:
                    slider.setSingleStep(components[i][3][0])
                    slider.setPageStep(components[i][3][1])
                slider.setTracking(True)

                spin = QSpinBox(self)
                spin.setRange(slider.minimum(), slider.maximum())

                def setColorComponentWrapper(value, widget=self, component=components[i][0]):
                    componentValue = ColorSlidersWidget.getColorComponent(widget.color(), component)
                    if componentValue != value:
                        widget.setColorComponent(component, value)

                def setSliderValueWrapper(color, widget=slider, component=components[i][0]):
                    componentValue = ColorSlidersWidget.getColorComponent(color, component)
                    if widget.value() != componentValue:
                        widget.setValue(componentValue)

                def setSpinValueWrapper(color, widget=spin, component=components[i][0]):
                    componentValue = ColorSlidersWidget.getColorComponent(color, component)
                    if widget.value() != componentValue:
                        widget.setValue(componentValue)

                slider.valueChanged.connect(setColorComponentWrapper)
                self.colorChanged.connect(setSliderValueWrapper)
                spin.valueChanged.connect(setColorComponentWrapper)
                self.colorChanged.connect(setSpinValueWrapper)
                #slider.valueChanged.connect(lambda value, widget=self, i=i, components=components, component=components[i][0]: widget.setColorComponent(component, value))
                #self.colorChanged.connect(lambda color, widget=slider, i=i, components=components, component=components[i][0]: widget.setValue(ColorSlidersWidget.getColorComponent(color, component)))
                #spin.valueChanged.connect(lambda value, widget=self, i=i, components=components, component=components[i][0]: widget.setColorComponent(component, value))
                #self.colorChanged.connect(lambda color, widget=spin, i=i, components=components, component=components[i][0]: widget.setValue(ColorSlidersWidget.getColorComponent(color, component)))

                label = QLabel(components[i][1], self)
                label.setAlignment(Qt.AlignRight)
                label.setBuddy(slider)

                layout.addWidget(label, i, 0)
                layout.addWidget(slider, i, 1)
                layout.addWidget(spin, i, 2)


class RgbSlidersWidget(ColorSlidersWidget):
    components = [("red", "R", None, None),
                  ("green", "G", None, None),
                  ("blue", "B", None, None)]
    def __init__(self, parent=None):
        super(RgbSlidersWidget, self).__init__(RgbSlidersWidget.components, parent)


class HsvSlidersWidget(ColorSlidersWidget):
    components = [("hue", "H", (0, 359), None),
                  ("saturation", "S", None, None),
                  ("value", "V", None, None)]
    def __init__(self, parent=None):
        super(HsvSlidersWidget, self).__init__(HsvSlidersWidget.components, parent)


class HslSlidersWidget(ColorSlidersWidget):
    components = [("hue", "H", (0, 359), None),
                  ("saturation", "S", None, None),
                  ("lightness", "L", None, None)]
    def __init__(self, parent=None):
        super(HslSlidersWidget, self).__init__(HslSlidersWidget.components, parent)


class CmykSlidersWidget(ColorSlidersWidget):
    components = [("cyan", "C", None, None),
                  ("magenta", "M", None, None),
                  ("yellow", "Y", None, None),
                  ("black", "K", None, None)]
    def __init__(self, parent=None):
        super(CmykSlidersWidget, self).__init__(CmykSlidersWidget.components, parent)


class PaletteCanvas(QWidget):
    """ Canvas where the palette is draw """

    def __init__(self, parent):
        QWidget.__init__(self)
        self.parent = parent
        self.background = QBrush(self.parent.project.bgColor)
        self.black = QColor(0, 0, 0)
        self.white = QColor(255, 255, 255)
        self.parent.project.updateBackgroundSign.connect(self.updateBackground)
        self.swatches = 256
        self.columns = 8
        self.rows = (self.swatches + self.swatches % self.columns) // self.columns
        self.swatchWidth = 24
        self.swatchHeight = 24
        self.swatchHorizontalPadding = self.swatchVerticalPadding = 1
        self.swatchOffsetX = self.swatchWidth + 2 * self.swatchHorizontalPadding
        self.swatchOffsetY = self.swatchHeight + 2 * self.swatchVerticalPadding
        self.setFixedSize(self.columns * self.swatchOffsetX + self.swatchHorizontalPadding,
                          (
                          self.swatches + self.swatches % self.columns) // self.columns * self.swatchOffsetY + self.swatchVerticalPadding)
        self.setAcceptDrops(True)

    def updateBackground(self):
        self.background = QBrush(self.parent.project.bgColor)
        self.update()

    def swatchIndexToGrid(self, index):
        return (index % self.columns, index // self.columns)

    def swatchGridToIndex(self, x, y):
        if x < 0 or x >= self.columns:
            return None
        index = y * self.columns + x
        if index < 0 or index > self.swatches:
            return None
        return index

    def swatchPointToGrid(self, x, y):
        return ((x - self.swatchHorizontalPadding / 2) / self.swatchOffsetX,
                (y - self.swatchVerticalPadding / 2) / self.swatchOffsetY)

    def swatchRect(self, x, y):
        return QRect(x * self.swatchOffsetX + self.swatchHorizontalPadding,
                     y * self.swatchOffsetY + self.swatchVerticalPadding,
                     self.swatchWidth, self.swatchHeight)

    def paintEvent(self, ev=''):
        p = QPainter(self)
        p.fillRect(0, 0, self.width(), self.height(), self.background)
        for n, i in enumerate(self.parent.project.colorTable):
            rect = self.swatchRect(*(self.swatchIndexToGrid(n)))
            color = QColor().fromRgba(i)
            if n == 0:
                p.fillRect(rect.adjusted(0, 0, -rect.width() // 2, -rect.height() // 2), QBrush(color))
                p.fillRect(rect.adjusted(rect.width() // 2, rect.height() // 2, 0, 0), QBrush(color))
            else:
                p.fillRect(rect, QBrush(color))

        rect = self.swatchRect(*(self.swatchIndexToGrid(self.parent.project.color)))
        p.setPen(self.black)
        p.drawRect(rect.adjusted(-1, -1, 0, 0))
        p.setPen(self.white)
        p.drawRect(rect.adjusted(0, 0, -1, -1))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragStartPosition = event.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if (event.pos() - self.dragStartPosition).manhattanLength() >= QApplication.startDragDistance():
                ### initiate drag and drop ###
                gridX, gridY = self.swatchPointToGrid(self.dragStartPosition.x(), self.dragStartPosition.y())
                self.dragIndex = self.swatchGridToIndex(math.floor(gridX), math.floor(gridY))
                if self.dragIndex is not None and self.dragIndex < len(self.parent.project.colorTable):
                    drag = QDrag(self)
                    mimeData = QMimeData()
                    mimeData.setColorData(QColor.fromRgba(self.parent.project.colorTable[self.dragIndex]))
                    drag.setMimeData(mimeData)
                    image = QImage(self.swatchWidth, self.swatchHeight, QImage.Format_ARGB32)
                    image.fill(mimeData.colorData())
                    drag.setPixmap(QPixmap.fromImage(image))
                    drag.setHotSpot(QPoint(image.width() // 2, image.height() // 2))
                    dropAction = drag.exec(Qt.CopyAction | Qt.MoveAction)

    def mouseReleaseEvent(self, event):
        item = self.getItem(event.x(), event.y())
        if item is not None:
            self.parent.project.setColorIndex(item)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            item = self.getItem(event.x(), event.y())
            if item is not None:
                self.parent.editColor(item)
            event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-color"):
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self

    def dragMoveEvent(self, event):
        self

    def dropEvent(self, event):
        event.mimeData().formats()
        gridX, gridY = self.swatchPointToGrid(event.pos().x(), event.pos().y())
        dropIndex = self.swatchGridToIndex(math.floor(gridX), math.floor(gridY))
        if dropIndex is not None and dropIndex < len(self.parent.project.colorTable):
            # Insert colour
            if event.keyboardModifiers() & Qt.ControlModifier and event.keyboardModifiers() & Qt.ShiftModifier:
                pos = dropIndex + (0 if gridX - math.floor(gridX) < 0.5 else 1)
                colorTable = self.parent.project.colorTable
                self.parent.project.colorTable = colorTable[:pos] + colorTable[
                                                                    self.dragIndex:self.dragIndex + 1] + colorTable[
                                                                                                         pos:]
                self.parent.updateColorTable()
            # Replace colour
            elif event.keyboardModifiers() & Qt.ShiftModifier:
                self.parent.project.colorTable[dropIndex] = event.mimeData().colorData().rgba()
                #self.parent.project.updatePaletteSign.emit()
                self.parent.updateColorTable()
            # Move colour
            elif event.keyboardModifiers() & Qt.ControlModifier:
                pos = dropIndex + (0 if gridX - math.floor(gridX) < 0.5 else 1)
                colorTable = self.parent.project.colorTable
                if pos < self.dragIndex:
                    self.parent.project.colorTable = colorTable[:pos] + colorTable[
                                                                        self.dragIndex:self.dragIndex + 1] + colorTable[
                                                                                                             pos:self.dragIndex] + colorTable[
                                                                                                                                   self.dragIndex + 1:]
                    self.parent.updateColorTable()
                elif pos > self.dragIndex:
                    self.parent.project.colorTable = colorTable[:self.dragIndex] + colorTable[
                                                                                   self.dragIndex + 1:pos] + colorTable[
                                                                                                             self.dragIndex:self.dragIndex + 1] + colorTable[
                                                                                                                                                  pos:]
                    self.parent.updateColorTable()
            # Swap colours
            else:
                temp = self.parent.project.colorTable[dropIndex]
                self.parent.project.colorTable[dropIndex] = event.mimeData().colorData().rgba()
                self.parent.project.colorTable[self.dragIndex] = temp
                #self.parent.project.updatePaletteSign.emit()
                self.parent.updateColorTable()
        event.acceptProposedAction()

    def getItem(self, x, y):
        x, y = (x - self.swatchHorizontalPadding) // self.swatchOffsetX, (
                                                                         y - self.swatchVerticalPadding) // self.swatchOffsetY
        s = self.swatchGridToIndex(x, y)
        if s != None and s >= 0 and s < len(self.parent.project.colorTable):
            return s
        return None


class PenWidget(QWidget):
    def __init__(self, parent, project):
        QWidget.__init__(self)
        self.parent = parent
        self.project = project
        self.setToolTip("pen")
        self.setFixedSize(26, 26)
        self.project.updateBackgroundSign.connect(self.update)
        self.penMenu = QMenu(self)
        self.currentAction = None
        self.loadPen()
        self.project.customPenSign.connect(self.setCustomPen)

    def loadPen(self):
        self.penMenu.clear()
        for name, icon in self.project.penList:
            action = QAction(QIcon(icon), name, self)
            action.pixmap = icon
            action.setIconVisibleInMenu(True)
            self.penMenu.addAction(action)
            if not self.currentAction:
                self.currentAction = action

    def event(self, event):
        if event.type() == QEvent.MouseButtonPress:
            self.changePen()
        elif event.type() == QEvent.Paint:
            p = QPainter(self)
            p.fillRect(0, 0, self.width(), self.height(),
                       QBrush(QColor(70, 70, 70)))
            p.fillRect(1, 1, self.width() - 2, self.height() - 2,
                       QBrush(self.project.bgColor))
            if self.currentAction.pixmap:
                p.drawPixmap(5, 5, self.currentAction.pixmap)
        return QWidget.event(self, event)

    def changePen(self):
        self.penMenu.setActiveAction(self.currentAction)
        action = self.penMenu.exec(self.mapToGlobal(QPoint(26, 2)), self.currentAction)
        if action:
            self.currentAction = action
            self.project.pen = self.project.penDict[action.text()]
            self.project.penChangedSign.emit()
            self.update()

    def setCustomPen(self, li):
        nLi = []
        mY = len(li) // 2
        mX = len(li[0]) // 2
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
            #self.parent.penClicked()
            #self.parent.penToolAction.trigger()


class BrushWidget(QWidget):
    def __init__(self, parent, project):
        QWidget.__init__(self)
        self.parent = parent
        self.project = project
        self.setToolTip("brush")
        self.setFixedSize(26, 26)
        self.project.updateBackgroundSign.connect(self.update)
        self.brushMenu = QMenu(self)
        self.currentAction = None
        self.loadBrush()

    def loadBrush(self):
        self.brushMenu.clear()
        for name, icon in self.project.brushList:
            action = QAction(QIcon(icon), name, self)
            action.pixmap = icon
            action.setIconVisibleInMenu(True)
            self.brushMenu.addAction(action)
            if name == "solid":
                self.currentAction = action

    def event(self, event):
        if event.type() == QEvent.MouseButtonPress:
            self.changeBrush()
        elif event.type() == QEvent.Paint:
            p = QPainter(self)
            p.fillRect(0, 0, self.width(), self.height(),
                       QBrush(QColor(70, 70, 70)))
            p.fillRect(1, 1, self.width() - 2, self.height() - 2,
                       QBrush(self.project.bgColor))
            if self.currentAction.pixmap:
                p.drawPixmap(5, 5, self.currentAction.pixmap)
        return QWidget.event(self, event)

    def changeBrush(self):
        self.brushMenu.setActiveAction(self.currentAction)
        action = self.brushMenu.exec(self.mapToGlobal(QPoint(26, 2)), self.currentAction)
        if action:
            self.currentAction = action
            self.project.brush = self.project.brushDict[action.text()]
            self.update()


class OptionFill(QWidget):
    """ contextual option for the fill tool """

    def __init__(self, parent, project):
        QVBoxLayout.__init__(self)
        self.project = project
        self.parent = parent

        self.adjacentFillRadio = QRadioButton("Adjacent colors", self)
        self.adjacentFillRadio.pressed.connect(self.adjacentPressed)
        self.adjacentFillRadio.setChecked(True)
        self.similarFillRadio = QRadioButton("Similar colors", self)
        self.similarFillRadio.pressed.connect(self.similarPressed)

        ### Layout ###
        layout = QVBoxLayout()
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


class OptionSelect(QWidget):
    """ contextual option for the select tool """

    def __init__(self, parent, project):
        QVBoxLayout.__init__(self)
        self.project = project

        self.cutFillRadio = QRadioButton("Cut", self)
        self.cutFillRadio.pressed.connect(self.cutPressed)
        self.cutFillRadio.setChecked(True)
        self.copyFillRadio = QRadioButton("Copy", self)
        self.copyFillRadio.pressed.connect(self.copyPressed)

        ### Layout ###
        layout = QVBoxLayout()
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


class OptionMove(QWidget):
    """ contextual option for the select tool """

    def __init__(self, parent, project):
        QVBoxLayout.__init__(self)
        self.project = project

        self.clipRadio = QRadioButton("Clip", self)
        self.clipRadio.pressed.connect(self.clipPressed)
        self.clipRadio.setChecked(True)
        self.wrapRadio = QRadioButton("Wrap", self)
        self.wrapRadio.pressed.connect(self.wrapPressed)

        ### Layout ###
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.addWidget(self.clipRadio)
        layout.addWidget(self.wrapRadio)
        layout.addStretch()
        layout.setContentsMargins(0, 0, 0, 0)
        #self.setLayout(layout)

    def clipPressed(self):
        self.project.moveMode = "clip"

    def wrapPressed(self):
        self.project.moveMode = "wrap"


class PaletteWidget(QWidget):
    """ side widget containing palette """

    def __init__(self, project):
        QWidget.__init__(self)
        self.project = project

        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        ### context menu ###
        newAction = QAction("New", self)
        self.addAction(newAction)
        mergeAction = QAction("Merge", self)
        self.addAction(mergeAction)
        deleteAction = QAction("Delete", self)
        self.addAction(deleteAction)
        cutAction = QAction("Cut", self)
        self.addAction(cutAction)
        copyAction = QAction("Copy", self)
        self.addAction(copyAction)
        pasteAction = QAction("Paste", self)
        self.addAction(pasteAction)

        ### palette ###
        self.paletteCanvas = PaletteCanvas(self)
        self.paletteV = Viewer()
        self.paletteV.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.paletteV.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.paletteV.setWidget(self.paletteCanvas)

        self.project.updatePaletteSign.connect(self.paletteCanvas.update)
        addColorB = Button("add color",
                           "icons/color_add.png", self.addColor)
        delColorB = Button("delete color",
                           "icons/color_del.png", self.delColor)

        ### Layout ###
        colorButtons = QHBoxLayout()
        colorButtons.setSpacing(0)
        colorButtons.addWidget(addColorB)
        colorButtons.addWidget(delColorB)
        paintOption = QHBoxLayout()
        paintOption.setSpacing(0)
        paintOption.addStretch()
        layout = QGridLayout()
        layout.setSpacing(0)
        layout.addLayout(paintOption, 1, 1)
        layout.addWidget(self.paletteV, 2, 1)
        layout.addLayout(colorButtons, 3, 1)
        layout.setContentsMargins(6, 0, 6, 0)
        self.setLayout(layout)

    def showEvent(self, event):
        self.paletteV.setFixedWidth(self.paletteCanvas.width() +
                                    self.paletteV.verticalScrollBar().width() + 2)

    ######## Color #####################################################
    def updateColorTable(self):
        for i in self.project.timeline.getAllCanvas():
            i.setColorTable(self.project.colorTable)
        self.project.updateViewSign.emit()
        self.paletteCanvas.update()
        self.project.colorChangedSign.emit()

    def editColor(self, n):
        current = self.project.colorTable[self.project.color]
        color = QColorDialog.getColor(QColor(current), self, None, QColorDialog.ShowAlphaChannel)
        if not color.isValid():
            return
        self.project.saveToUndo("colorTable")
        self.project.colorTable[n] = color.rgba()
        self.updateColorTable()

    def addColor(self):
        """ select a color and add it to the palette"""
        if not len(self.project.colorTable) >= 256:
            col = self.project.colorTable[self.project.color]
            ok, color = ColorDialog(False, col).getRgba()
            if not ok:
                return
            self.project.saveToUndo("colorTable_frames")
            self.project.colorTable.append(color)
            self.project.setColorIndex(len(self.project.colorTable) - 1)
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
            self.project.setColorIndex(col - 1)
            self.project.updateViewSign.emit()


class ContextWidget(QWidget):
    """ side widget containing painting context """

    def __init__(self, project):
        QWidget.__init__(self)
        self.project = project
        #self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.penWidget = PenWidget(self, self.project)
        self.brushWidget = BrushWidget(self, self.project)

        ### Layout ###
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.addWidget(self.penWidget)
        layout.addWidget(self.brushWidget)
        layout.addStretch()
        layout.setContentsMargins(6, 0, 6, 0)
        self.setLayout(layout)


class OptionsWidget(QWidget):
    """ side widget containing options """

    def __init__(self, project):
        QWidget.__init__(self)
        self.project = project

        self.optionFill = OptionFill(self, self.project)
        self.optionSelect = OptionSelect(self, self.project)
        self.optionMove = OptionMove(self, self.project)

        ### Layout ###
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.addWidget(self.optionFill)
        self.optionFill.hide()
        layout.addWidget(self.optionSelect)
        self.optionSelect.hide()
        layout.addWidget(self.optionMove)
        self.optionMove.hide()
        layout.addStretch()
        self.setLayout(layout)

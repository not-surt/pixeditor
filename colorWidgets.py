from PyQt4.QtCore import *
from PyQt4.QtGui import *

import math
import random

from widget import Button, Viewer
from colorPicker import ColorDialog
from FlowLayout import FlowLayout


def setColorComponent(__color, component, componentValue):
    color = QColor(__color)
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
    return color

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


class ToolWidget(QWidget):
    def __init__(self, parent=None):
        super(ToolWidget, self).__init__(parent)
        layout = FlowLayout()
        #layout = QHBoxLayout()
        #layout.setSizeConstraint(QLayout.SetFixedSize)
        #layout.setSpacing(0)
        #layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        pass

    def addAction(self, action):
        self.parent().addAction(action)
        button = QToolButton(self)
        button.setDefaultAction(action)
        button.setAutoRaise(True)
        iconSize = self.style().pixelMetric(QStyle.PM_ToolBarIconSize)
        size = self.style().sizeFromContents(QStyle.CT_ToolButton, QStyleOptionToolButton(), QSize(iconSize, iconSize))
        button.setIconSize(QSize(iconSize, iconSize))
        button.setFixedSize(size)
        self.layout().addWidget(button)
        pass

class ColorComponentSlider(QSlider):
    colorChanged = pyqtSignal(QColor)
    colorComponentChanged = pyqtSignal(str, int)

    def color(self):
        return self.__color

    def setColor(self, color):
        if color.isValid() and self.__color != color:
            self.startColor = color
            self.__color = color
            self.colorChanged.emit(self.__color)
            self.setValue(getColorComponent(self.__color, self.__component))

    pyqtProperty(QColor, color, setColor)

    def __init__(self, component, orientation=Qt.Horizontal, parent=None):
        super(ColorComponentSlider, self).__init__(orientation, parent)
        self.__component = component
        self.__color = QColor()
        self.startColor = QColor()
        self.colorChanged.connect(self.update)
        pass

    def component(self):
        return self.__component

    def unitValue(self):
        return (self.value() - self.minimum()) / (self.maximum() - self.minimum())

    def paintEvent(self, event):
        painter = QPainter(self)
        for i in range(0, self.width() - 1):
            color = setColorComponent(self.__color, self.__component, (i / (self.width() - 1)) * (self.maximum() - self.minimum()))
            painter.fillRect(i, 0, 1, self.height(), color)
            pass
        i = (self.value() - self.minimum()) / (self.maximum() - self.minimum()) * (self.width() - 1)
        handleSize = 2
        halfHeight = self.height() // 2
        painter.fillRect(i - handleSize, 0, handleSize, halfHeight, QColor(Qt.black))
        painter.fillRect(i, 0, handleSize, halfHeight, QColor(Qt.white))
        painter.fillRect(i - handleSize, halfHeight, handleSize, self.height() - halfHeight, QColor(Qt.white))
        painter.fillRect(i, halfHeight, handleSize, self.height() - halfHeight, QColor(Qt.black))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setValue(self.minimum() + (event.pos().x() / self.width()) * (self.maximum() - self.minimum()))
            self.startColor = self.__color
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.setValue(self.minimum() + (event.pos().x() / self.width()) * (self.maximum() - self.minimum()))
            event.accept()

    def mouseReleaseEvent(self, event):
        self.setColor(self.startColor)
        event.accept()


class ColorSpaceSlidersWidget(QWidget):
    colorChanged = pyqtSignal(QColor)
    colorComponentChanged = pyqtSignal(str, int)

    def color(self):
        return self.__color

    def setColor(self, color):
        if color.isValid() and self.__color != color:
            self.__color = color
            self.colorChanged.emit(self.__color)

    pyqtProperty(QColor, color, setColor)


    def __init__(self, components, parent=None):
        super(ColorSpaceSlidersWidget, self).__init__(parent)

        self.__color = QColor()

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        for i in range(0, len(components)):
            if components[i] is None:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setFrameShadow(QFrame.Sunken)
                layout.addWidget(separator, i, 0, 1, 3)
            else:
                slider = ColorComponentSlider(components[i][0], Qt.Horizontal, self)
                # Range
                componentRange = (0, 255) if components[i][2] is None else components[i][2]
                slider.setRange(*componentRange)
                # Step
                if components[i][3] is None:
                    slider.setSingleStep(1)
                    slider.setPageStep(8)
                else:
                    slider.setSingleStep(components[i][3][0])
                    slider.setPageStep(components[i][3][1])
                slider.setTracking(True)
                slider.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

                spin = QSpinBox(self)
                spin.setRange(slider.minimum(), slider.maximum())
                spin.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

                def setColorComponentWrapper(value, widget=self, component=components[i][0]):
                    componentValue = getColorComponent(widget.color(), component)
                    if componentValue != value:
                        widget.setColor(setColorComponent(widget.color(), component, value))

                def setSliderValueWrapper(color, widget=slider, component=components[i][0]):
                    componentValue = getColorComponent(color, component)
                    if widget.value() != componentValue:
                        widget.setValue(componentValue)

                def setSpinValueWrapper(color, widget=spin, component=components[i][0]):
                    componentValue = getColorComponent(color, component)
                    if widget.value() != componentValue:
                        widget.setValue(componentValue)

                slider.valueChanged.connect(setColorComponentWrapper)
                #self.colorChanged.connect(setSliderValueWrapper)
                self.colorChanged.connect(slider.setColor)
                spin.valueChanged.connect(setColorComponentWrapper)
                self.colorChanged.connect(setSpinValueWrapper)

                label = QLabel(components[i][1], self)
                label.setAlignment(Qt.AlignRight)
                label.setBuddy(slider)
                label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

                layout.addWidget(label, i, 0)
                layout.addWidget(slider, i, 1)
                layout.addWidget(spin, i, 2)


class RgbSlidersWidget(ColorSpaceSlidersWidget):
    components = [("red", "R", None, None),
                  ("green", "G", None, None),
                  ("blue", "B", None, None)]
    def __init__(self, parent=None):
        super(RgbSlidersWidget, self).__init__(RgbSlidersWidget.components, parent)


class HsvSlidersWidget(ColorSpaceSlidersWidget):
    components = [("hue", "H", (0, 359), None),
                  ("saturation", "S", None, None),
                  ("value", "V", None, None)]
    def __init__(self, parent=None):
        super(HsvSlidersWidget, self).__init__(HsvSlidersWidget.components, parent)


class HslSlidersWidget(ColorSpaceSlidersWidget):
    components = [("hue", "H", (0, 359), None),
                  ("saturation", "S", None, None),
                  ("lightness", "L", None, None)]
    def __init__(self, parent=None):
        super(HslSlidersWidget, self).__init__(HslSlidersWidget.components, parent)


class CmykSlidersWidget(ColorSpaceSlidersWidget):
    components = [("cyan", "C", None, None),
                  ("magenta", "M", None, None),
                  ("yellow", "Y", None, None),
                  ("black", "K", None, None)]
    def __init__(self, parent=None):
        super(CmykSlidersWidget, self).__init__(CmykSlidersWidget.components, parent)


class PaletteCanvas(QWidget):
    """ Canvas where the palette is drawn. """

    colorTableChanged = pyqtSignal(list)
    indexChanged = pyqtSignal(int)
    colorChanged = pyqtSignal(int, QColor)

    def colorTable(self):
        return self.__colorTable

    def setColorTable(self, colorTable):
        self.__colorTable = colorTable

    pyqtProperty(list, colorTable, setColorTable)

    def index(self):
        return self.__currentIndex

    def setIndex(self, index):
        self.__index = index

    def color(self, index):
        return self.__colorTable[self.index]

    def setColor(self, index, color):
        self.__colorTable[index] = color

    pyqtProperty(list, colorTable, setColorTable)

    def __init__(self, parent, index=None, colorTable=[]):
        QWidget.__init__(self)
        self.__colorTable = colorTable
        self.__index = index

        self.parent = parent
        self.swatches = 256
        self.columns = 8
        self.rows = (self.swatches + self.swatches % self.columns) // self.columns
        self.swatchWidth = 24
        self.swatchHeight = 24
        self.swatchHorizontalPadding = self.swatchVerticalPadding = 0
        self.swatchOffsetX = self.swatchWidth + 2 * self.swatchHorizontalPadding
        self.swatchOffsetY = self.swatchHeight + 2 * self.swatchVerticalPadding
        self.setFixedSize(self.columns * self.swatchOffsetX + self.swatchHorizontalPadding,
                          (
                          self.swatches + self.swatches % self.columns) // self.columns * self.swatchOffsetY + self.swatchVerticalPadding)
        self.setAcceptDrops(True)

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
        for n, i in enumerate(self.parent.project.colorTable):
            rect = self.swatchRect(*(self.swatchIndexToGrid(n)))
            color = QColor().fromRgba(i)
            if n == 0:
                p.fillRect(rect.adjusted(0, 0, -rect.width() // 2, -rect.height() // 2), QBrush(color))
                p.fillRect(rect.adjusted(rect.width() // 2, rect.height() // 2, 0, 0), QBrush(color))
            else:
                p.fillRect(rect, QBrush(color))

        rect = self.swatchRect(*(self.swatchIndexToGrid(self.parent.project.color)))
        p.setPen(QColor(0, 0, 0))
        p.drawRect(rect.adjusted(1, 1, -2, -2))
        p.setPen(QColor(255, 255, 255))
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
        gridX, gridY = self.swatchPointToGrid(event.pos().x(), event.pos().y())
        index = self.swatchGridToIndex(math.floor(gridX), math.floor(gridY))
        if index is not None:
            self.parent.project.setColorIndex(index)
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
        if dropIndex is not None:
            # Insert colour
            if dropIndex < self.swatches and event.keyboardModifiers() & Qt.ControlModifier and event.keyboardModifiers() & Qt.ShiftModifier:
                dropIndex = dropIndex if dropIndex < len(self.parent.project.colorTable) else len(self.parent.project.colorTable)
                pos = dropIndex + (0 if gridX - math.floor(gridX) < 0.5 else 1)
                colorTable = self.parent.project.colorTable
                self.parent.project.colorTable = colorTable[:pos] + colorTable[
                                                                    self.dragIndex:self.dragIndex + 1] + colorTable[
                                                                                                         pos:]
                self.parent.updateColorTable()
            if dropIndex < len(self.parent.project.colorTable):
                # Replace colour
                if event.keyboardModifiers() & Qt.ShiftModifier:
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
        lockAction = QAction("Lock", self)
        lockAction.setCheckable(True)
        self.addAction(lockAction)

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
        self.project.colorChanged.emit()

    def colorDialog(self):
        current = self.project.colorTable[self.project.color]
        return QColorDialog.getColor(QColor(current), self)

    def editColor(self, n):
        color = self.colorDialog()
        if not color.isValid():
            return
        self.project.saveToUndo("colorTable")
        self.project.colorTable[n] = color.rgba()
        self.updateColorTable()

    def addColor(self):
        """ select a color and add it to the palette"""
        if not len(self.project.colorTable) >= 256:
            color = self.colorDialog()
            if not color.isValid():
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

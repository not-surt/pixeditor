#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# Copyright Nicolas Bougère (nicolas.bougere@z-uo.com), 2012-2013
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# export spritesheet
# export all canvas
# watch copy paste

# add camera layer
# add rough layer with higher resolution

import sys
import os

from data import Project
from timeline import TimelineWidget
from sidebar import *
from dialogs import *
from widget import Dock
from import_export import *
from widget import Background

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class SelectionRect(QGraphicsRectItem):
    """ Rect item used in scene to display a selection """

    def __init__(self, pos):
        QGraphicsRectItem.__init__(self, pos.x(), pos.y(), 1, 1)
        self.startX = pos.x()
        self.startY = pos.y()

        self.setPen(QPen(QColor("black"), 0))
        dashPen = QPen(QColor("white"), 0, Qt.DashLine)
        dashPen.setDashPattern([6, 6])
        self.dash = QGraphicsRectItem(self.rect(), self)
        self.dash.setPen(dashPen)

    def scale(self, pos):
        rect = QRectF(self.startX, self.startY, pos.x() - self.startX, pos.y() - self.startY)
        self.setRect(rect)
        self.dash.setRect(rect)

    def getRect(self):
        """ return a QRect with positive width and height """
        w = int(self.rect().width())
        h = int(self.rect().height())
        if w < 0:
            x = int(self.rect().x()) + w
            w = int(self.rect().x()) - x
        else:
            x = int(self.rect().x())
        if h < 0:
            y = int(self.rect().y()) + h
            h = int(self.rect().y()) - y
        else:
            y = int(self.rect().y())
        return QRect(x, y, w, h)


class Scene(QGraphicsView):
    """ widget used to display the layers, onionskin, pen, background
        it can zoom with mouseWheel, pan with mouseMiddleClic
        it send mouseRightClic info to the current Canvas"""

    def __init__(self, project):
        QGraphicsView.__init__(self)
        self.project = project
        self.zoomN = 1
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # scene
        self.scene = QGraphicsScene(self)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.setScene(self.scene)
        self.setTransformationAnchor(
            QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setMinimumSize(256, 256)
        self.scene.setSceneRect(0, 0,
                                self.project.size.width(), self.project.size.height())
        # background
        self.setBackgroundBrush(QBrush(self.project.bgColor))
        self.bg = self.scene.addPixmap(
            Background(self.project.size, self.project.bgPattern))
        # frames
        self.itemList = []
        self.canvasList = []
        # OnionSkin
        p = QPixmap(self.project.size)
        self.onionPrevItem = self.scene.addPixmap(p)
        self.onionPrevItem.setZValue(101)
        self.onionPrevItem.setOpacity(0.5)
        self.onionPrevItem.hide()
        p = QPixmap(self.project.size)
        self.onionNextItem = self.scene.addPixmap(p)
        self.onionNextItem.setZValue(102)
        self.onionNextItem.setOpacity(0.5)
        self.onionNextItem.hide()
        # pen
        self.penItem = QGraphicsRectItem(0, 0, 1, 1)
        self.penItem.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self.penItem.setPen(QPen(Qt.NoPen))
        self.scene.addItem(self.penItem)
        self.penItem.setZValue(103)
        self.penItem.hide()
        self.project.penChanged.connect(self.changePen)
        self.project.toolChanged.connect(self.changePen)
        self.project.colorChanged.connect(self.changePen)
        self.changePen()

        self.project.updateViewSign.connect(self.changeFrame)
        self.project.updateBackgroundSign.connect(self.updateBackground)
        self.changeFrame()

    def changePen(self):
        for i in self.penItem.childItems():
            self.scene.removeItem(i)
        if self.project.tool == "pen" and self.project.pen:
            pen = QPen(Qt.NoPen)
            if len(self.project.pen[0]) == 3:
                for i in self.project.pen:
                    brush = QColor(self.project.colorTable[i[2]])
                    p = QGraphicsRectItem(i[0], i[1], 1, 1, self.penItem)
                    p.setPen(pen)
                    p.setBrush(brush)
            else:
                brush = QColor(self.project.colorTable[self.project.color])
                for i in self.project.pen:
                    p = QGraphicsRectItem(i[0], i[1], 1, 1, self.penItem)
                    p.setPen(pen)
                    p.setBrush(brush)

    def updateBackground(self):
        self.setBackgroundBrush(QBrush(self.project.bgColor))
        self.bg.setPixmap(Background(self.project.size,
                                     self.project.bgPattern))

    def changeFrame(self):
        self.canvasList = self.project.timeline.getCanvasList(self.project.curFrame)
        # resize scene if needed
        if self.scene.sceneRect().size().toSize() != self.project.size:
            self.scene.setSceneRect(0, 0,
                                    self.project.size.width(), self.project.size.height())
            self.updateBackground()
            # add item for layer if needed
        for i in range(len(self.itemList), len(self.canvasList)):
            self.itemList.append(self.scene.addPixmap(QPixmap(1, 1)))
            self.itemList[i].setZValue(100 - i)
            # remove item for layer if needed
        for i in range(len(self.canvasList), len(self.itemList)):
            self.scene.removeItem(self.itemList[i])
            del self.itemList[i]
            # updates canvas
        for n, i in enumerate(self.canvasList):
            if i and self.project.timeline[n].visible:
                self.itemList[n].setVisible(True)
                self.itemList[n].pixmap().convertFromImage(i)
                self.itemList[n].update()
            else:
                self.itemList[n].setVisible(False)
                # onionskin
        layer = self.project.timeline[self.project.curLayer]
        if (not self.project.playing and self.project.onionSkinPrev and
                self.project.timeline[self.project.curLayer].visible):
            frame = self.project.curFrame
            prev = False
            while 0 <= frame < len(layer):
                if layer[frame]:
                    if frame == 0 and self.project.loop:
                        prev = layer.getCanvas(len(layer) - 1)
                    else:
                        prev = layer.getCanvas(frame - 1)
                    if prev and prev != layer.getCanvas(self.project.curFrame):
                        self.onionPrevItem.pixmap().convertFromImage(prev)
                        self.onionPrevItem.show()
                    else:
                        self.onionPrevItem.hide()
                    break
                frame -= 1
            else:
                self.onionPrevItem.hide()
        else:
            self.onionPrevItem.hide()
        if (not self.project.playing and self.project.onionSkinNext and
                self.project.timeline[self.project.curLayer].visible):
            frame = self.project.curFrame + 1
            nex = False
            while 0 <= frame < len(layer):
                if layer[frame]:
                    self.onionNextItem.pixmap().convertFromImage(layer[frame])
                    self.onionNextItem.show()
                    break
                frame += 1
            else:
                if (frame == len(layer) and self.project.loop and
                            layer[0] != layer.getCanvas(self.project.curFrame)):
                    self.onionNextItem.pixmap().convertFromImage(layer[0])
                    self.onionNextItem.show()
                else:
                    self.onionNextItem.hide()
        else:
            self.onionNextItem.hide()

    def wheelEvent(self, event):
        if event.delta() > 0:
            self.scaleView(2)
        elif event.delta() < 0:
            self.scaleView(0.5)

    def scaleView(self, factor):
        n = self.zoomN * factor
        if n < 1 or n > 128:
            return
        self.zoomN = n
        self.penItem.hide()
        self.scale(factor, factor)

    def pointToInt(self, point):
        return QPoint(int(point.x()), int(point.y()))

    def pointToFloat(self, point):
        return QPointF(int(point.x()), int(point.y()))

    def mousePressEvent(self, event):
        l = self.project.curLayer
        # pan
        if event.buttons() == Qt.MidButton:
            self.startScroll = (self.horizontalScrollBar().value(),
                                self.verticalScrollBar().value())
            self.lastPos = QPoint(QCursor.pos())
            self.setDragMode(QGraphicsView.NoDrag)
        # draw on canvas
        elif (self.project.timeline[l].visible
              and (event.buttons() == Qt.LeftButton
                   or event.buttons() == Qt.RightButton)
              and self.project.tool == "pen"
              or self.project.tool == "pipette"
              or self.project.tool == "fill"):
            pos = self.pointToInt(self.mapToScene(event.pos()))
            if not self.canvasList[l] and self.project.tool == "pen":
                self.project.timeline[self.project.curLayer].insertCanvas(
                    self.project.curFrame, self.project.makeCanvas())
                self.project.updateTimelineSign.emit()
                self.project.updateViewSign.emit()
            self.canvasList[l].click(pos, event.buttons())
            self.itemList[l].pixmap().convertFromImage(self.canvasList[l])
            self.itemList[l].update()
        # move or select
        elif (self.project.timeline[l].visible and self.canvasList[l]
              and event.buttons() == Qt.LeftButton):
            pos = self.pointToInt(self.mapToScene(event.pos()))
            if self.project.tool == "move":
                self.lastPos = pos
            elif self.project.tool == "select":
                self.selRect = SelectionRect(pos)
                self.selRect.setZValue(103)
                self.scene.addItem(self.selRect)
        else:
            return QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        self.penItem.show()
        self.penItem.setPos(self.pointToFloat(self.mapToScene(event.pos())))
        l = self.project.curLayer
        # pan
        if event.buttons() == Qt.MidButton:
            globalPos = QCursor.pos()
            self.horizontalScrollBar().setValue(self.startScroll[0] -
                                                globalPos.x() + self.lastPos.x())
            self.verticalScrollBar().setValue(self.startScroll[1] -
                                              globalPos.y() + self.lastPos.y())
        # draw on canvas
        elif (self.project.timeline[l].visible and self.canvasList[l]
              and (event.buttons() == Qt.LeftButton
                   or event.buttons() == Qt.RightButton)
              and self.project.tool == "pen"
              or self.project.tool == "pipette"
              or self.project.tool == "fill"):
            pos = self.pointToInt(self.mapToScene(event.pos()))
            self.canvasList[l].move(pos, event.buttons())
            self.itemList[l].pixmap().convertFromImage(self.canvasList[l])
            self.itemList[l].update()
        # move or select
        elif (self.project.timeline[l].visible and self.canvasList[l]
              and event.buttons() == Qt.LeftButton):
            pos = self.pointToInt(self.mapToScene(event.pos()))
            if self.project.tool == "move":
                dif = pos - self.lastPos
                intPos = self.pointToInt(self.itemList[l].pos())
                self.itemList[l].setPos(QPointF(intPos + dif))
                self.lastPos = pos
            elif self.project.tool == "select":
                self.selRect.scale(pos)
        else:
            return QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            l = self.project.curLayer
            if self.project.tool == "move" and self.canvasList[l] and self.itemList[l].pos():
                self.project.saveToUndo("canvas")
                offset = (int(self.itemList[l].pos().x()),
                          int(self.itemList[l].pos().y()))
                self.canvasList[l].loadFromList(
                    self.canvasList[l].returnAsList(),
                    self.canvasList[l].width(), offset)
                self.itemList[l].setPos(QPointF(0, 0))
                self.changeFrame()
            elif self.project.tool == "select":
                rect = self.selRect.getRect()
                if rect.isValid():
                    sel = self.canvasList[l].returnAsMatrix(rect)
                    if self.project.selectMode == "cut":
                        self.project.saveToUndo("canvas")
                        self.canvasList[l].delRect(rect)
                    self.project.customPenSign.emit(sel)
                    self.changeFrame()
                self.scene.removeItem(self.selRect)
                del self.selRect
        else:
            return QGraphicsView.mouseReleaseEvent(self, event)

    def enterEvent(self, event):
        self.penItem.show()

    def leaveEvent(self, event):
        self.penItem.hide()


class MainWindow(QMainWindow):
    """ Main windows of the application """

    def __init__(self):
        QMainWindow.__init__(self)

        QApplication.setOrganizationName("z-uo")
        QApplication.setApplicationName("pixeditor")

        self.colorDialog = QColorDialog()
        self.colorDialog.setOptions(QColorDialog.NoButtons)
        #self.colorDialog.hide()

        self.project = Project(self)

        self.rgbWidget = RgbSlidersWidget(self)
        self.rgbWidget.colorChanged.connect(self.project.setColor)
        self.project.colorChanged.connect(lambda widget=self: widget.rgbWidget.setColor(QColor(widget.project.colorTable[widget.project.color])))

        self.hsvWidget = HsvSlidersWidget(self)
        self.hsvWidget.colorChanged.connect(self.project.setColor)
        self.project.colorChanged.connect(lambda widget=self: widget.hsvWidget.setColor(QColor(widget.project.colorTable[widget.project.color])))

        self.hslWidget = HslSlidersWidget(self)
        self.hslWidget.colorChanged.connect(self.project.setColor)
        self.project.colorChanged.connect(lambda widget=self: widget.hslWidget.setColor(QColor(widget.project.colorTable[widget.project.color])))

        self.cmykWidget = CmykSlidersWidget(self)
        self.cmykWidget.colorChanged.connect(self.project.setColor)
        self.project.colorChanged.connect(lambda widget=self: widget.cmykWidget.setColor(QColor(widget.project.colorTable[widget.project.color])))

        self.contextWidget = ContextWidget(self.project)
        self.optionsWidget = OptionsWidget(self.project)
        self.paletteWidget = PaletteWidget(self.project)
        self.timelineWidget = TimelineWidget(self.project)
        self.scene = Scene(self.project)
        self.toolsWidget = ToolWidget(self)

        self.updateTitle()
        self.project.updateTitleSign.connect(self.updateTitle)

        self.setCentralWidget(self.scene)
        self.setDockNestingEnabled(True)

        toolsDock = QDockWidget("Tools")
        toolsDock.setWidget(self.toolsWidget)
        toolsDock.setObjectName("toolsDock")
        self.addDockWidget(Qt.LeftDockWidgetArea, toolsDock)

        contextDock = QDockWidget("Context")
        contextDock.setWidget(self.contextWidget)
        contextDock.setObjectName("contextDock")
        self.addDockWidget(Qt.LeftDockWidgetArea, contextDock)

        optionsDock = QDockWidget("Options")
        optionsDock.setWidget(self.optionsWidget)
        optionsDock.setObjectName("optionsDock")
        self.addDockWidget(Qt.LeftDockWidgetArea, optionsDock)

        paletteDock = QDockWidget("Palette")
        paletteDock.setWidget(self.paletteWidget)
        paletteDock.setObjectName("paletteDock")
        self.addDockWidget(Qt.LeftDockWidgetArea, paletteDock)

        #colorDialogDock = QDockWidget("Color Dialog")
        #colorDialogDock.setWidget(self.colorDialog)
        #colorDialogDock.setObjectName("colorDialog")
        #self.addDockWidget(Qt.LeftDockWidgetArea, colorDialogDock)

        rgbDock = QDockWidget("RGB")
        rgbDock.setWidget(self.rgbWidget)
        rgbDock.setObjectName("rgbDock")
        self.addDockWidget(Qt.LeftDockWidgetArea, rgbDock)

        hsvDock = QDockWidget("HSV")
        hsvDock.setWidget(self.hsvWidget)
        hsvDock.setObjectName("hsvDock")
        self.addDockWidget(Qt.LeftDockWidgetArea, hsvDock)

        hslDock = QDockWidget("HSL")
        hslDock.setWidget(self.hslWidget)
        hslDock.setObjectName("hslDock")
        self.addDockWidget(Qt.LeftDockWidgetArea, hslDock)

        cmykDock = QDockWidget("CMYK")
        cmykDock.setWidget(self.cmykWidget)
        cmykDock.setObjectName("cmykDock")
        self.addDockWidget(Qt.LeftDockWidgetArea, cmykDock)

        self.tabifyDockWidget(rgbDock, hsvDock)
        self.tabifyDockWidget(hsvDock, hslDock)
        self.tabifyDockWidget(hslDock, cmykDock)
        rgbDock.raise_()

        timelineDock = Dock("Timeline")
        timelineDock.setWidget(self.timelineWidget)
        timelineDock.setObjectName("timelineDock")
        timelineDock.setFeatures(QDockWidget.DockWidgetVerticalTitleBar | QDockWidget.AllDockWidgetFeatures)
        self.addDockWidget(Qt.BottomDockWidgetArea, timelineDock)

        ### Toolbar ###
        toolActions = QActionGroup(self)
        toolActions.setExclusive(True)
        penToolAction = QAction(QIcon("icons/tool_pen.png"), "&Pen", toolActions)
        penToolAction.setCheckable(True)
        penToolAction.setChecked(True)
        penToolAction.triggered.connect(self.penToolAction)
        pipetteToolAction = QAction(QIcon("icons/tool_pipette.png"), "P&ipette", toolActions)
        pipetteToolAction.setCheckable(True)
        pipetteToolAction.triggered.connect(self.pipetteToolAction)
        fillToolAction = QAction(QIcon("icons/tool_fill.png"), "&Fill", toolActions)
        fillToolAction.setCheckable(True)
        fillToolAction.triggered.connect(self.fillToolAction)
        moveToolAction = QAction(QIcon("icons/tool_move.png"), "&Move", toolActions)
        moveToolAction.setCheckable(True)
        moveToolAction.triggered.connect(self.moveToolAction)
        selectToolAction = QAction(QIcon("icons/tool_select.png"), "&Select", toolActions)
        selectToolAction.setCheckable(True)
        selectToolAction.triggered.connect(self.selectToolAction)
        toolbar = QToolBar("Tools")
        toolbar.addAction(penToolAction)
        toolbar.addAction(pipetteToolAction)
        toolbar.addAction(fillToolAction)
        toolbar.addAction(moveToolAction)
        toolbar.addAction(selectToolAction)
        toolbar.setObjectName("toolsToolbar")
        #self.addToolBar(toolbar)
        penToolAction.setShortcut('1')
        pipetteToolAction.setShortcut('2')
        fillToolAction.setShortcut('3')
        moveToolAction.setShortcut('4')
        selectToolAction.setShortcut('5')

        self.toolsWidget.addAction(penToolAction)
        self.toolsWidget.addAction(pipetteToolAction)
        self.toolsWidget.addAction(fillToolAction)
        self.toolsWidget.addAction(moveToolAction)
        self.toolsWidget.addAction(selectToolAction)

        ### File menu ###
        menubar = self.menuBar()
        openAction = QAction('&Open', self)
        openAction.triggered.connect(self.openAction)
        openAction.setShortcut(QKeySequence.Open)
        saveAsAction = QAction('Save &as', self)
        saveAsAction.triggered.connect(self.saveAsAction)
        saveAsAction.setShortcut(QKeySequence.SaveAs)
        saveAction = QAction('&Save', self)
        saveAction.triggered.connect(self.saveAction)
        saveAction.setShortcut(QKeySequence.Save)

        importNewAction = QAction('&Import as new', self)
        importNewAction.triggered.connect(self.importAsNewAction)
        importLayerAction = QAction('I&mport as layer', self)
        importLayerAction.triggered.connect(self.importAsLayerAction)
        exportAction = QAction('&Export', self)
        exportAction.triggered.connect(self.exportAction)
        exportAction.setShortcut('Ctrl+E')

        exitAction = QAction('E&xit', self)
        exitAction.triggered.connect(self.exitAction)
        exitAction.setShortcut(QKeySequence.Quit)

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAsAction)
        fileMenu.addAction(saveAction)
        fileMenu.addSeparator()
        fileMenu.addAction(importNewAction)
        fileMenu.addAction(importLayerAction)
        fileMenu.addAction(exportAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        ### Edit menu ###
        undoAction = QAction('&Undo', self)
        undoAction.triggered.connect(self.project.undo)
        undoAction.setShortcut(QKeySequence.Undo)
        redoAction = QAction('&Redo', self)
        redoAction.triggered.connect(self.project.redo)
        redoAction.setShortcut(QKeySequence.Redo)

        cutAction = QAction('&Cut', self)
        cutAction.triggered.connect(self.timelineWidget.cut)
        cutAction.setShortcut(QKeySequence.Cut)
        copyAction = QAction('C&opy', self)
        copyAction.triggered.connect(self.timelineWidget.copy)
        copyAction.setShortcut(QKeySequence.Copy)
        pasteAction = QAction('&Paste', self)
        pasteAction.triggered.connect(self.timelineWidget.paste)
        pasteAction.setShortcut(QKeySequence.Paste)

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(undoAction)
        editMenu.addAction(redoAction)
        editMenu.addSeparator()
        editMenu.addAction(cutAction)
        editMenu.addAction(copyAction)
        editMenu.addAction(pasteAction)

        ### tools menu ###
        toolsMenu = menubar.addMenu('&Tools')
        toolsMenu.addAction(penToolAction)
        toolsMenu.addAction(pipetteToolAction)
        toolsMenu.addAction(fillToolAction)
        toolsMenu.addAction(moveToolAction)
        toolsMenu.addAction(selectToolAction)

        ### view menu ###
        viewMenu = menubar.addMenu('&View')
        toolbars = self.findChildren(QToolBar)
        for toolbar in toolbars:
            viewMenu.addAction(toolbar.toggleViewAction())
        viewMenu.addSeparator()
        dockWidgets = self.findChildren(QDockWidget)
        for dock in dockWidgets:
            viewMenu.addAction(dock.toggleViewAction())
        viewMenu.addSeparator()
        lockLayoutAction = QAction('&Lock Layout', self)
        lockLayoutAction.setCheckable(True)
        lockLayoutAction.triggered.connect(lambda: self.lockLayoutAction(lockLayoutAction))
        viewMenu.addAction(lockLayoutAction)

        ### project menu ###
        newAction = QAction('&New', self)
        newAction.triggered.connect(self.newAction)
        cropAction = QAction('&Crop', self)
        cropAction.triggered.connect(self.cropAction)
        resizeAction = QAction('&Resize', self)
        resizeAction.triggered.connect(self.resizeAction)
        replacePaletteAction = QAction('Replace &palette', self)
        replacePaletteAction.triggered.connect(self.replacePaletteAction)
        prefAction = QAction('&Background', self)
        prefAction.triggered.connect(self.backgroundAction)

        projectMenu = menubar.addMenu('&Project')
        projectMenu.addAction(newAction)
        projectMenu.addAction(cropAction)
        projectMenu.addAction(resizeAction)
        projectMenu.addSeparator()
        projectMenu.addAction(replacePaletteAction)
        projectMenu.addSeparator()
        projectMenu.addAction(prefAction)

        ### resources menu ###
        savePaletteAction = QAction('Save current &palette', self)
        savePaletteAction.triggered.connect(self.savePaletteAction)
        savePenAction = QAction('Save &custom pen', self)
        savePenAction.triggered.connect(self.savePenAction)
        reloadResourcesAction = QAction('&Reload resources', self)
        reloadResourcesAction.triggered.connect(self.reloadResourcesAction)

        resourcesMenu = menubar.addMenu('&Resources')
        resourcesMenu.addAction(savePaletteAction)
        resourcesMenu.addAction(savePenAction)
        resourcesMenu.addSeparator()
        resourcesMenu.addAction(reloadResourcesAction)

        ### shortcuts ###
        shortcut = QShortcut(self)
        shortcut.setKey(Qt.Key_Left)
        shortcut.activated.connect(lambda: self.selectFrame(-1))
        shortcut2 = QShortcut(self)
        shortcut2.setKey(Qt.Key_Right)
        shortcut2.activated.connect(lambda: self.selectFrame(1))
        shortcut3 = QShortcut(self)
        shortcut3.setKey(Qt.Key_Up)
        shortcut3.activated.connect(lambda: self.selectLayer(-1))
        shortcut4 = QShortcut(self)
        shortcut4.setKey(Qt.Key_Down)
        shortcut4.activated.connect(lambda: self.selectLayer(1))
        shortcut5 = QShortcut(self)
        shortcut5.setKey(Qt.Key_Space)
        shortcut5.activated.connect(self.timelineWidget.playPauseClicked)

        ### settings ###
        self.readSettings()

        self.show()

    def writeSettings(self):
        settings = QSettings()
        settings.beginGroup("mainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.endGroup()

    def readSettings(self):
        settings = QSettings()
        settings.beginGroup("mainWindow")
        try:
            self.restoreGeometry(settings.value("geometry"))
        except TypeError:
            pass # no geometry to restore so leave as is
        try:
            self.restoreState(settings.value("windowState"))
        except TypeError:
            pass # no state to restore so leave as is
        settings.endGroup()

    ######## Toolbar #####################################################
    def penToolAction(self):
        self.project.tool = "pen"
        self.project.toolChanged.emit()
        self.optionsWidget.optionFill.hide()
        self.optionsWidget.optionSelect.hide()
        self.optionsWidget.optionMove.hide()

    def pipetteToolAction(self):
        self.project.tool = "pipette"
        self.project.toolChanged.emit()
        self.optionsWidget.optionFill.hide()
        self.optionsWidget.optionSelect.hide()
        self.optionsWidget.optionMove.hide()

    def fillToolAction(self):
        self.project.tool = "fill"
        self.project.toolChanged.emit()
        self.optionsWidget.optionFill.show()
        self.optionsWidget.optionSelect.hide()
        self.optionsWidget.optionMove.hide()

    def moveToolAction(self):
        self.project.tool = "move"
        self.project.toolChanged.emit()
        self.optionsWidget.optionFill.hide()
        self.optionsWidget.optionSelect.hide()
        self.optionsWidget.optionMove.show()

    def selectToolAction(self):
        self.project.tool = "select"
        self.project.toolChanged.emit()
        self.optionsWidget.optionFill.hide()
        self.optionsWidget.optionSelect.show()
        self.optionsWidget.optionMove.hide()

    ######## File menu #################################################
    def openAction(self):
        xml, url = open_pix(self.project.dirUrl)
        if xml and url:
            self.project.saveToUndo("all")
            self.project.importXml(xml)
            self.project.updateViewSign.emit()
            self.project.updatePaletteSign.emit()
            self.project.updateTimelineSign.emit()
            self.project.updateBackgroundSign.emit()
            self.project.updateFpsSign.emit()
            self.project.url = url
            self.project.dirUrl = os.path.dirname(url)

    def saveAsAction(self):
        url = get_save_url(self.project.dirUrl)
        if url:
            url = save_pix(self.project.exportXml(), url)
            if url:
                self.project.url = url
                self.project.dirUrl = os.path.dirname(url)
                self.project.saved = True
                self.updateTitle()

    def saveAction(self):
        if self.project.url:
            url = save_pix(self.project.exportXml(), self.project.url)
            if url:
                self.project.url = url
                self.project.dirUrl = os.path.dirname(url)
                self.project.saved = True
                self.updateTitle()
        else:
            self.saveAsAction()

    def importAsNewAction(self):
        size, frames, colorTable = import_img(self.project,
                                              self.project.dirUrl)
        if size and frames and colorTable:
            self.project.saveToUndo("all")
            self.project.initProject(size, colorTable, frames)
            self.project.updateViewSign.emit()
            self.project.updatePaletteSign.emit()
            self.project.updateTimelineSign.emit()

    def importAsLayerAction(self):
        size, frames, colorTable = import_img(self.project,
                                              self.project.dirUrl,
                                              self.project.size,
                                              self.project.colorTable)
        if size and frames and colorTable:
            self.project.saveToUndo("all")
            self.project.importImg(size, colorTable, frames)
            self.project.updateViewSign.emit()
            self.project.updatePaletteSign.emit()
            self.project.updateTimelineSign.emit()

    def exportAction(self):
        export_png(self.project, self.project.dirUrl)

    def closeEvent(self, event):
        self.writeSettings()
        self.exitAction()

    def exitAction(self):
        message = QMessageBox()
        message.setWindowTitle("Quit?")
        message.setText("Are you sure you want to quit?");
        message.setIcon(QMessageBox.Warning)
        message.addButton("Cancel", QMessageBox.RejectRole)
        message.addButton("Yes", QMessageBox.AcceptRole)
        ret = message.exec_();
        if ret:
            qApp.quit()

    ######## View menu ##############################################
    def lockLayoutAction(self, action):
        widgets = self.findChildren(QDockWidget) + self.findChildren(QToolBar)
        for widget in widgets:
            if action.isChecked():
                if widget.isFloating():
                    if isinstance(widget, QDockWidget):
                        widget.setTitleBarWidget(None)
                        widget.setFeatures(QDockWidget.DockWidgetFloatable)
                        widget.setAllowedAreas(Qt.NoDockWidgetArea)
                    elif isinstance(widget, QToolBar):
                        widget.setAllowedAreas(Qt.NoToolBarArea)
                else:
                    if isinstance(widget, QDockWidget):
                        widget.setTitleBarWidget(QWidget())
                        widget.setFeatures(QDockWidget.NoDockWidgetFeatures)
                    elif isinstance(widget, QToolBar):
                        widget.setFloatable(False)
                        widget.setMovable(False)
            else:
                if isinstance(widget, QDockWidget):
                    widget.setFeatures(QDockWidget.AllDockWidgetFeatures)
                    widget.setTitleBarWidget(None)
                    widget.setAllowedAreas(Qt.AllDockWidgetAreas)
                elif isinstance(widget, QToolBar):
                    widget.setFloatable(True)
                    widget.setMovable(True)
                    widget.setAllowedAreas(Qt.AllToolBarAreas)

    ######## Project menu ##############################################
    def newAction(self):
        dialog = NewDialog()
        if dialog.exec_() == QDialog.Accepted:
            size = QSize(dialog.resultData["width"], dialog.resultData["height"])
            palette = import_palette(dialog.resultData["palette"])
            if size and palette:
                self.project.saveToUndo("all")
                self.project.initProject(size, palette)
                self.project.updateViewSign.emit()
                self.project.updatePaletteSign.emit()
                self.project.updateTimelineSign.emit()
                self.project.updateBackgroundSign.emit()
                self.project.updateFpsSign.emit()
                self.updateTitle()

    def cropAction(self):
        rect = CropDialog(self.project.size).getReturn()
        if rect:
            self.project.saveToUndo("size")
            self.project.timeline.applyToAllCanvas(
                lambda c: Canvas(self.project, c.copy(rect)))
            self.project.size = rect.size()
            self.project.updateViewSign.emit()

    def resizeAction(self):
        factor = ResizeDialog(self.project.size).getReturn()
        if factor and factor != 1:
            self.project.saveToUndo("size")
            newSize = self.project.size * factor
            self.project.timeline.applyToAllCanvas(
                lambda c: Canvas(self.project, c.scaled(newSize)))
            self.project.size = newSize
            self.project.updateViewSign.emit()

    def replacePaletteAction(self):
        #dir = QDir.current()
        #dir.cd("resources/palette")
        palettePath = os.path.abspath(os.path.join("resources", "palette"))
        url = QFileDialog.getOpenFileName(None, "open palette file",
                                          #dir.path(),
                                          palettePath,
                                          "Palette files (*.pal, *.gpl);;All files (*)")
        if url:
            pal = import_palette(url, len(self.project.colorTable))
            if pal:
                self.project.saveToUndo("colorTable_frames")
                self.project.colorTable = pal
                for i in self.project.timeline.getAllCanvas():
                    i.setColorTable(self.project.colorTable)
                self.project.updateViewSign.emit()
                self.project.updatePaletteSign.emit()

    def backgroundAction(self):
        color, pattern = BackgroundDialog(self.project.bgColor,
                                          self.project.bgPattern).getReturn()
        if color and pattern:
            self.project.saveToUndo("background")
            self.project.bgColor = color
            self.project.bgPattern = pattern
            self.project.updateBackgroundSign.emit()

    def savePaletteAction(self):
        url = get_save_url(os.path.join("resources", "palette"), "pal")
        pal = export_palette(self.project.colorTable)
        if url:
            try:
                save = open(url, "w")
                save.write(pal)
                save.close()
                print("saved")
            except IOError:
                print("Can't open file")

    def savePenAction(self):
        if self.project.penDict["custom"]:
            url = get_save_url(os.path.join("resources", "pen"), "py")
            pen = export_pen(self.project.penDict["custom"], os.path.splitext(os.path.basename(url))[0])
            if url:
                try:
                    save = open(url, "w")
                    save.write(pen)
                    save.close()
                    print("saved")
                except IOError:
                    print("Can't open file")


    def reloadResourcesAction(self):
        self.project.importResources()
        self.toolsWidget.penWidget.loadPen()
        self.toolsWidget.brushWidget.loadBrush()

    ######## Shortcuts #################################################
    def selectFrame(self, n):
        maxF = max([len(l) for l in self.project.timeline])
        if 0 <= self.project.curFrame + n < maxF:
            self.project.curFrame += n
            self.project.updateTimelineSign.emit()
            self.project.updateViewSign.emit()

    def selectLayer(self, n):
        if 0 <= self.project.curLayer + n < len(self.project.timeline):
            self.project.curLayer += n
            self.project.updateTimelineSign.emit()
            self.project.updateViewSign.emit()

    def updateTitle(self):
        url, sav = "untitled", "* "
        if self.project.saved:
            sav = ""
        if self.project.url:
            url = os.path.basename(self.project.url)
        self.setWindowTitle("%s%s - pixeditor" % (sav, url))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(QPixmap("icons/pixeditor.png")))
    mainWin = MainWindow()
    sys.exit(app.exec_())


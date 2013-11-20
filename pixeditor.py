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
from PyQt4 import QtCore
from PyQt4 import QtGui

from data import Project
from timeline import TimelineWidget
from sidebar import PaletteWidget
from sidebar import ContextWidget
from sidebar import OptionsWidget
from dialogs import *
from widget import Dock
from import_export import *
from widget import Background


class SelectionRect(QtGui.QGraphicsRectItem):
    """ Rect item used in scene to display a selection """

    def __init__(self, pos):
        QtGui.QGraphicsRectItem.__init__(self, pos.x(), pos.y(), 1, 1)
        self.startX = pos.x()
        self.startY = pos.y()

        self.setPen(QtGui.QPen(QtGui.QColor("black"), 0))
        dashPen = QtGui.QPen(QtGui.QColor("white"), 0, QtCore.Qt.DashLine)
        dashPen.setDashPattern([6, 6])
        self.dash = QtGui.QGraphicsRectItem(self.rect(), self)
        self.dash.setPen(dashPen)

    def scale(self, pos):
        rect = QtCore.QRectF(self.startX, self.startY, pos.x() - self.startX, pos.y() - self.startY)
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
        return QtCore.QRect(x, y, w, h)


class Scene(QtGui.QGraphicsView):
    """ widget used to display the layers, onionskin, pen, background
        it can zoom with mouseWheel, pan with mouseMiddleClic
        it send mouseRightClic info to the current Canvas"""

    def __init__(self, project):
        QtGui.QGraphicsView.__init__(self)
        self.project = project
        self.zoomN = 1
        # scene
        self.scene = QtGui.QGraphicsScene(self)
        self.scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        self.setScene(self.scene)
        self.setTransformationAnchor(
            QtGui.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.setMinimumSize(400, 400)
        self.scene.setSceneRect(0, 0,
                                self.project.size.width(), self.project.size.height())
        # background
        self.setBackgroundBrush(QtGui.QBrush(self.project.bgColor))
        self.bg = self.scene.addPixmap(
            Background(self.project.size, self.project.bgPattern))
        # frames
        self.itemList = []
        self.canvasList = []
        # OnionSkin
        p = QtGui.QPixmap(self.project.size)
        self.onionPrevItem = self.scene.addPixmap(p)
        self.onionPrevItem.setZValue(101)
        self.onionPrevItem.setOpacity(0.5)
        self.onionPrevItem.hide()
        p = QtGui.QPixmap(self.project.size)
        self.onionNextItem = self.scene.addPixmap(p)
        self.onionNextItem.setZValue(102)
        self.onionNextItem.setOpacity(0.5)
        self.onionNextItem.hide()
        # pen
        self.penItem = QtGui.QGraphicsRectItem(0, 0, 1, 1)
        self.penItem.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0, 0)))
        self.penItem.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        self.scene.addItem(self.penItem)
        self.penItem.setZValue(103)
        self.penItem.hide()
        self.project.penChangedSign.connect(self.changePen)
        self.project.toolChangedSign.connect(self.changePen)
        self.project.colorChangedSign.connect(self.changePen)
        self.changePen()

        self.project.updateViewSign.connect(self.changeFrame)
        self.project.updateBackgroundSign.connect(self.updateBackground)
        self.changeFrame()

    def changePen(self):
        for i in self.penItem.childItems():
            self.scene.removeItem(i)
        if self.project.tool == "pen" and self.project.pen:
            pen = QtGui.QPen(QtCore.Qt.NoPen)
            if len(self.project.pen[0]) == 3:
                for i in self.project.pen:
                    brush = QtGui.QColor(self.project.colorTable[i[2]])
                    p = QtGui.QGraphicsRectItem(i[0], i[1], 1, 1, self.penItem)
                    p.setPen(pen)
                    p.setBrush(brush)
            else:
                brush = QtGui.QColor(self.project.colorTable[self.project.color])
                for i in self.project.pen:
                    p = QtGui.QGraphicsRectItem(i[0], i[1], 1, 1, self.penItem)
                    p.setPen(pen)
                    p.setBrush(brush)

    def updateBackground(self):
        self.setBackgroundBrush(QtGui.QBrush(self.project.bgColor))
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
            self.itemList.append(self.scene.addPixmap(QtGui.QPixmap(1, 1)))
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
        return QtCore.QPoint(int(point.x()), int(point.y()))

    def pointToFloat(self, point):
        return QtCore.QPointF(int(point.x()), int(point.y()))

    def mousePressEvent(self, event):
        l = self.project.curLayer
        # pan
        if event.buttons() == QtCore.Qt.MidButton:
            self.startScroll = (self.horizontalScrollBar().value(),
                                self.verticalScrollBar().value())
            self.lastPos = QtCore.QPoint(QtGui.QCursor.pos())
            self.setDragMode(QtGui.QGraphicsView.NoDrag)
        # draw on canvas
        elif (self.project.timeline[l].visible
              and (event.buttons() == QtCore.Qt.LeftButton
                   or event.buttons() == QtCore.Qt.RightButton)
              and self.project.tool == "pen"
              or self.project.tool == "pipette"
              or self.project.tool == "fill"):
            pos = self.pointToInt(self.mapToScene(event.pos()))
            if not self.canvasList[l] and self.project.tool == "pen":
                self.project.timeline[self.project.curLayer].insertCanvas(
                    self.project.curFrame, self.project.makeCanvas())
                self.project.updateTimelineSign.emit()
                self.project.updateViewSign.emit()
            self.canvasList[l].clic(pos, event.buttons())
            self.itemList[l].pixmap().convertFromImage(self.canvasList[l])
            self.itemList[l].update()
        # move or select
        elif (self.project.timeline[l].visible and self.canvasList[l]
              and event.buttons() == QtCore.Qt.LeftButton):
            pos = self.pointToInt(self.mapToScene(event.pos()))
            if self.project.tool == "move":
                self.lastPos = pos
            elif self.project.tool == "select":
                self.selRect = SelectionRect(pos)
                self.selRect.setZValue(103)
                self.scene.addItem(self.selRect)
        else:
            return QtGui.QGraphicsView.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        self.penItem.show()
        self.penItem.setPos(self.pointToFloat(self.mapToScene(event.pos())))
        l = self.project.curLayer
        # pan
        if event.buttons() == QtCore.Qt.MidButton:
            globalPos = QtGui.QCursor.pos()
            self.horizontalScrollBar().setValue(self.startScroll[0] -
                                                globalPos.x() + self.lastPos.x())
            self.verticalScrollBar().setValue(self.startScroll[1] -
                                              globalPos.y() + self.lastPos.y())
        # draw on canvas
        elif (self.project.timeline[l].visible and self.canvasList[l]
              and (event.buttons() == QtCore.Qt.LeftButton
                   or event.buttons() == QtCore.Qt.RightButton)
              and self.project.tool == "pen"
              or self.project.tool == "pipette"
              or self.project.tool == "fill"):
            pos = self.pointToInt(self.mapToScene(event.pos()))
            self.canvasList[l].move(pos, event.buttons())
            self.itemList[l].pixmap().convertFromImage(self.canvasList[l])
            self.itemList[l].update()
        # move or select
        elif (self.project.timeline[l].visible and self.canvasList[l]
              and event.buttons() == QtCore.Qt.LeftButton):
            pos = self.pointToInt(self.mapToScene(event.pos()))
            if self.project.tool == "move":
                dif = pos - self.lastPos
                intPos = self.pointToInt(self.itemList[l].pos())
                self.itemList[l].setPos(QtCore.QPointF(intPos + dif))
                self.lastPos = pos
            elif self.project.tool == "select":
                self.selRect.scale(pos)
        else:
            return QtGui.QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            l = self.project.curLayer
            if self.project.tool == "move" and self.canvasList[l] and self.itemList[l].pos():
                self.project.saveToUndo("canvas")
                offset = (int(self.itemList[l].pos().x()),
                          int(self.itemList[l].pos().y()))
                self.canvasList[l].loadFromList(
                    self.canvasList[l].returnAsList(),
                    self.canvasList[l].width(), offset)
                self.itemList[l].setPos(QtCore.QPointF(0, 0))
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
            return QtGui.QGraphicsView.mouseReleaseEvent(self, event)

    def enterEvent(self, event):
        self.penItem.show()

    def leaveEvent(self, event):
        self.penItem.hide()


class MainWindow(QtGui.QMainWindow):
    """ Main windows of the application """

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        QtGui.QApplication.setOrganizationName("z-uo")
        QtGui.QApplication.setApplicationName("pixeditor")

        self.project = Project(self)
        self.contextWidget = ContextWidget(self.project)
        self.optionsWidget = OptionsWidget(self.project)
        self.paletteWidget = PaletteWidget(self.project)
        self.timelineWidget = TimelineWidget(self.project)
        self.scene = Scene(self.project)

        self.updateTitle()
        self.project.updateTitleSign.connect(self.updateTitle)

        self.setCentralWidget(self.scene)
        self.setDockNestingEnabled(True)

        #toolsDock = QtGui.QDockWidget("Tools")
        #toolsDock.setWidget(self.toolsWidget)
        #toolsDock.setObjectName("toolsDock")
        #self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, toolsDock)

        contextDock = QtGui.QDockWidget("Context")
        contextDock.setWidget(self.contextWidget)
        contextDock.setObjectName("contextDock")
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, contextDock)

        optionsDock = QtGui.QDockWidget("Options")
        optionsDock.setWidget(self.optionsWidget)
        optionsDock.setObjectName("optionsDock")
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, optionsDock)

        paletteDock = QtGui.QDockWidget("Palette")
        paletteDock.setWidget(self.paletteWidget)
        paletteDock.setObjectName("paletteDock")
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, paletteDock)

        timelineDock = Dock("Timeline")
        timelineDock.setWidget(self.timelineWidget)
        timelineDock.setObjectName("timelineDock")
        timelineDock.setFeatures(QtGui.QDockWidget.DockWidgetVerticalTitleBar | QtGui.QDockWidget.AllDockWidgetFeatures)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, timelineDock)

        ### Toolbar ###
        toolActions = QtGui.QActionGroup(self)
        toolActions.setExclusive(True)
        penToolAction = QtGui.QAction(QtGui.QIcon("icons/tool_pen.png"), "Pen", toolActions)
        penToolAction.setCheckable(True)
        penToolAction.setChecked(True)
        penToolAction.triggered.connect(self.penToolAction)
        pipetteToolAction = QtGui.QAction(QtGui.QIcon("icons/tool_pipette.png"), "Pipette", toolActions)
        pipetteToolAction.setCheckable(True)
        pipetteToolAction.triggered.connect(self.pipetteToolAction)
        fillToolAction = QtGui.QAction(QtGui.QIcon("icons/tool_fill.png"), "Fill", toolActions)
        fillToolAction.setCheckable(True)
        fillToolAction.triggered.connect(self.fillToolAction)
        moveToolAction = QtGui.QAction(QtGui.QIcon("icons/tool_move.png"), "Move", toolActions)
        moveToolAction.setCheckable(True)
        moveToolAction.triggered.connect(self.moveToolAction)
        selectToolAction = QtGui.QAction(QtGui.QIcon("icons/tool_select.png"), "Select", toolActions)
        selectToolAction.setCheckable(True)
        selectToolAction.triggered.connect(self.selectToolAction)
        toolbar = QtGui.QToolBar("Tools")
        toolbar.addAction(penToolAction)
        toolbar.addAction(pipetteToolAction)
        toolbar.addAction(fillToolAction)
        toolbar.addAction(moveToolAction)
        toolbar.addAction(selectToolAction)
        toolbar.setObjectName("toolsToolbar")
        self.addToolBar(toolbar)
        penToolAction.setShortcut('1')
        pipetteToolAction.setShortcut('2')
        fillToolAction.setShortcut('3')
        moveToolAction.setShortcut('4')
        selectToolAction.setShortcut('5')

        ### File menu ###
        menubar = self.menuBar()
        openAction = QtGui.QAction('Open', self)
        openAction.triggered.connect(self.openAction)
        saveAsAction = QtGui.QAction('Save as', self)
        saveAsAction.triggered.connect(self.saveAsAction)
        saveAction = QtGui.QAction('Save', self)
        saveAction.triggered.connect(self.saveAction)
        saveAction.setShortcut('Ctrl+S')

        importNewAction = QtGui.QAction('Import as new', self)
        importNewAction.triggered.connect(self.importAsNewAction)
        importLayerAction = QtGui.QAction('Import as layer', self)
        importLayerAction.triggered.connect(self.importAsLayerAction)
        exportAction = QtGui.QAction('Export', self)
        exportAction.triggered.connect(self.exportAction)
        exportAction.setShortcut('Ctrl+E')

        exitAction = QtGui.QAction('Exit', self)
        exitAction.triggered.connect(self.exitAction)
        exitAction.setShortcut('Ctrl+Q')

        fileMenu = menubar.addMenu('File')
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
        undoAction = QtGui.QAction('Undo', self)
        undoAction.triggered.connect(self.project.undo)
        undoAction.setShortcut('Ctrl+Z')
        redoAction = QtGui.QAction('Redo', self)
        redoAction.triggered.connect(self.project.redo)
        redoAction.setShortcut('Ctrl+Y')

        cutAction = QtGui.QAction('Cut', self)
        cutAction.triggered.connect(self.timelineWidget.cut)
        cutAction.setShortcut('Ctrl+X')
        copyAction = QtGui.QAction('Copy', self)
        copyAction.triggered.connect(self.timelineWidget.copy)
        copyAction.setShortcut('Ctrl+C')
        pasteAction = QtGui.QAction('Paste', self)
        pasteAction.triggered.connect(self.timelineWidget.paste)
        pasteAction.setShortcut('Ctrl+V')

        editMenu = menubar.addMenu('Edit')
        editMenu.addAction(undoAction)
        editMenu.addAction(redoAction)
        editMenu.addSeparator()
        editMenu.addAction(cutAction)
        editMenu.addAction(copyAction)
        editMenu.addAction(pasteAction)

        ### tools menu ###
        toolsMenu = menubar.addMenu('Tools')
        toolsMenu.addAction(penToolAction)
        toolsMenu.addAction(pipetteToolAction)
        toolsMenu.addAction(fillToolAction)
        toolsMenu.addAction(moveToolAction)
        toolsMenu.addAction(selectToolAction)

        ### view menu ###
        viewMenu = menubar.addMenu('View')
        toolbars = self.findChildren(QtGui.QToolBar)
        for toolbar in toolbars:
            viewMenu.addAction(toolbar.toggleViewAction())
        viewMenu.addSeparator()
        dockWidgets = self.findChildren(QtGui.QDockWidget)
        for dock in dockWidgets:
            viewMenu.addAction(dock.toggleViewAction())
        viewMenu.addSeparator()
        lockLayoutAction = QtGui.QAction('Lock Layout', self)
        lockLayoutAction.setCheckable(True)
        lockLayoutAction.triggered.connect(lambda: self.lockLayoutAction(lockLayoutAction))
        viewMenu.addAction(lockLayoutAction)

        ### project menu ###
        newAction = QtGui.QAction('New', self)
        newAction.triggered.connect(self.newAction)
        cropAction = QtGui.QAction('Crop', self)
        cropAction.triggered.connect(self.cropAction)
        resizeAction = QtGui.QAction('Resize', self)
        resizeAction.triggered.connect(self.resizeAction)
        replacePaletteAction = QtGui.QAction('replace palette', self)
        replacePaletteAction.triggered.connect(self.replacePaletteAction)
        prefAction = QtGui.QAction('Background', self)
        prefAction.triggered.connect(self.backgroundAction)

        projectMenu = menubar.addMenu('Project')
        projectMenu.addAction(newAction)
        projectMenu.addAction(cropAction)
        projectMenu.addAction(resizeAction)
        projectMenu.addAction(replacePaletteAction)
        projectMenu.addAction(prefAction)

        ### resources menu ###
        savePaletteAction = QtGui.QAction('save  current palette', self)
        savePaletteAction.triggered.connect(self.savePaletteAction)
        savePenAction = QtGui.QAction('save custom pen', self)
        savePenAction.triggered.connect(self.savePenAction)
        reloadResourcesAction = QtGui.QAction('reload resources', self)
        reloadResourcesAction.triggered.connect(self.reloadResourcesAction)

        resourcesMenu = menubar.addMenu('Resources')
        resourcesMenu.addAction(savePaletteAction)
        resourcesMenu.addAction(savePenAction)
        resourcesMenu.addAction(reloadResourcesAction)

        ### shortcuts ###
        shortcut = QtGui.QShortcut(self)
        shortcut.setKey(QtCore.Qt.Key_Left)
        shortcut.activated.connect(lambda: self.selectFrame(-1))
        shortcut2 = QtGui.QShortcut(self)
        shortcut2.setKey(QtCore.Qt.Key_Right)
        shortcut2.activated.connect(lambda: self.selectFrame(1))
        shortcut3 = QtGui.QShortcut(self)
        shortcut3.setKey(QtCore.Qt.Key_Up)
        shortcut3.activated.connect(lambda: self.selectLayer(-1))
        shortcut4 = QtGui.QShortcut(self)
        shortcut4.setKey(QtCore.Qt.Key_Down)
        shortcut4.activated.connect(lambda: self.selectLayer(1))
        shortcut5 = QtGui.QShortcut(self)
        shortcut5.setKey(QtCore.Qt.Key_Space)
        shortcut5.activated.connect(self.timelineWidget.playPauseClicked)

        ### settings ###
        self.readSettings()

        self.show()

    def writeSettings(self):
        settings = QtCore.QSettings()
        settings.beginGroup("mainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.endGroup()

    def readSettings(self):
        settings = QtCore.QSettings()
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
        self.project.toolChangedSign.emit()
        self.optionsWidget.optionFill.hide()
        self.optionsWidget.optionSelect.hide()

    def pipetteToolAction(self):
        self.project.tool = "pipette"
        self.project.toolChangedSign.emit()
        self.optionsWidget.optionFill.hide()
        self.optionsWidget.optionSelect.hide()

    def fillToolAction(self):
        self.project.tool = "fill"
        self.project.toolChangedSign.emit()
        self.optionsWidget.optionFill.show()
        self.optionsWidget.optionSelect.hide()

    def moveToolAction(self):
        self.project.tool = "move"
        self.project.toolChangedSign.emit()
        self.optionsWidget.optionFill.hide()
        self.optionsWidget.optionSelect.hide()

    def selectToolAction(self):
        self.project.tool = "select"
        self.project.toolChangedSign.emit()
        self.optionsWidget.optionFill.hide()
        self.optionsWidget.optionSelect.show()

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
        message = QtGui.QMessageBox()
        message.setWindowTitle("Quit?")
        message.setText("Are you sure you want to quit?");
        message.setIcon(QtGui.QMessageBox.Warning)
        message.addButton("Cancel", QtGui.QMessageBox.RejectRole)
        message.addButton("Yes", QtGui.QMessageBox.AcceptRole)
        ret = message.exec_();
        if ret:
            QtGui.qApp.quit()

    ######## View menu ##############################################
    def lockLayoutAction(self, action):
        widgets = self.findChildren(QtGui.QDockWidget) + self.findChildren(QtGui.QToolBar)
        for widget in widgets:
            if action.isChecked():
                if widget.isFloating():
                    if isinstance(widget, QtGui.QDockWidget):
                        widget.setTitleBarWidget(None)
                        widget.setFeatures(QtGui.QDockWidget.DockWidgetFloatable)
                        widget.setAllowedAreas(QtCore.Qt.NoDockWidgetArea)
                    elif isinstance(widget, QtGui.QToolBar):
                        widget.setAllowedAreas(QtCore.Qt.NoToolBarArea)
                else:
                    if isinstance(widget, QtGui.QDockWidget):
                        widget.setTitleBarWidget(QtGui.QWidget())
                        widget.setFeatures(QtGui.QDockWidget.NoDockWidgetFeatures)
                    elif isinstance(widget, QtGui.QToolBar):
                        widget.setFloatable(False)
                        widget.setMovable(False)
            else:
                if isinstance(widget, QtGui.QDockWidget):
                    widget.setFeatures(QtGui.QDockWidget.AllDockWidgetFeatures)
                    widget.setTitleBarWidget(None)
                    widget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
                elif isinstance(widget, QtGui.QToolBar):
                    widget.setFloatable(True)
                    widget.setMovable(True)
                    widget.setAllowedAreas(QtCore.Qt.AllToolBarAreas)

    ######## Project menu ##############################################
    def newAction(self):
        size, palette = NewDialog().getReturn()
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
        url = QtGui.QFileDialog.getOpenFileName(None, "open palette file",
                                                os.path.join("resources", "palette"),
                                                "Palette files (*.pal, *.gpl );;All files (*)")
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
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(QtGui.QPixmap("icons/pixeditor.png")))
    mainWin = MainWindow()
    sys.exit(app.exec_())


#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import math
import random

from widget import Button, Viewer
from colorPicker import ColorDialog
from FlowLayout import FlowLayout


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
            self.project.penChanged.emit()
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
            self.project.penChanged.emit()
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
        #layout.setSizeConstraint(QLayout.SetFixedSize)
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
        #layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.addWidget(self.optionFill)
        self.optionFill.hide()
        layout.addWidget(self.optionSelect)
        self.optionSelect.hide()
        layout.addWidget(self.optionMove)
        self.optionMove.hide()
        layout.addStretch()
        self.setLayout(layout)

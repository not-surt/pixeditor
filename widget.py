#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Python 3 Compatibility
from __future__ import division
from __future__ import print_function

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class Dock(QDockWidget):
    """ dock """

    def __init__(self, title, parent=None, flags=Qt.WindowFlags(0)):
        QDockWidget.__init__(self, title, parent, flags)
        self.setTitleBarWidget(QWidget())
        self.setTitleBarWidget(None)
        orientation = Qt.Orientation(Qt.Horizontal)


class Button(QToolButton):
    """ button """

    def __init__(self, tooltip, iconUrl, connection, checkable=False):
        QToolButton.__init__(self)
        self.setToolTip(tooltip)
        self.setAutoRaise(True)
        self.setCheckable(checkable)
        self.setIconSize(QSize(24, 24))
        self.setIcon(QIcon(QPixmap(iconUrl)))
        self.clicked.connect(connection)


class Background(QPixmap):
    """ background of the scene"""

    def __init__(self, size, arg=16):
        QPixmap.__init__(self, size)
        self.fill(QColor(0, 0, 0, 0))
        if type(arg) is int and arg:
            p = QPainter(self)
            brush = QBrush(QColor(0, 0, 0, 30))
            bol = True
            for x in range(0, size.width(), arg):
                for y in range(0, size.height(), arg * 2):
                    if bol:
                        p.fillRect(x, y, arg, arg, brush)
                    else:
                        p.fillRect(x, y + arg, arg, arg, brush)
                bol = not bol
        elif type(arg) is str:
            brush = QBrush(QPixmap(arg))
            p = QPainter(self)
            p.fillRect(0, 0, size.width(), size.height(), brush)


class Viewer(QScrollArea):
    """ QScrollArea you can move with midbutton"""
    resyzing = pyqtSignal(tuple)

    def __init__(self):
        QScrollArea.__init__(self)

    def event(self, event):
        """ capture middle mouse event to move the view """
        # clic: save position
        if (event.type() == QEvent.MouseButtonPress and
                    event.button() == Qt.MidButton):
            self.mouseX, self.mouseY = event.x(), event.y()
            return True
        # drag: move the scrollbars
        elif (event.type() == QEvent.MouseMove and
                      event.buttons() == Qt.MidButton):
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - (event.x() - self.mouseX))
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - (event.y() - self.mouseY))
            self.mouseX, self.mouseY = event.x(), event.y()
            return True
        elif (event.type() == QEvent.Resize):
            self.resyzing.emit((event.size().width(), event.size().height()))
        return QScrollArea.event(self, event)

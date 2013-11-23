#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import division
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *


def getHue(color):
    """ hack to avoid color.hue() to return -1 with grey color """
    if color.hue() >= 0:
        return color.hue()
    else:
        return 0


class SatVal(QGraphicsView):
    def __init__(self, parent, H, S, V):
        QGraphicsView.__init__(self)
        self.parent = parent

        self.scene = QGraphicsScene(self)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.setScene(self.scene)
        self.setFixedSize(258, 258)
        self.scene.setSceneRect(0, 0, 256, 256)

        self.colorGrad = QLinearGradient()
        self.colorGrad.setStart(0, 0)
        self.colorGrad.setFinalStop(0, 255)
        self.colorGrad.setColorAt(0, QColor(255, 255, 255))
        self.colorGrad.setColorAt(1, QColor().fromHsv(H, 255, 255))
        self.colorGradItem = QGraphicsRectItem(0, 0, 256, 256)
        self.colorGradItem.setBrush(QBrush(self.colorGrad))
        self.colorGradItem.setPen(QPen(Qt.NoPen))
        self.scene.addItem(self.colorGradItem)

        blackGrad = QLinearGradient()
        blackGrad.setStart(0, 0)
        blackGrad.setFinalStop(256, 0)
        blackGrad.setColorAt(0, QColor(0, 0, 0))
        blackGrad.setColorAt(1, QColor(255, 255, 255, 0))
        blackGradItem = QGraphicsRectItem(0, 0, 256, 256)
        blackGradItem.setBrush(QBrush(blackGrad))
        blackGradItem.setPen(QPen(Qt.NoPen))
        self.scene.addItem(blackGradItem)

        self.pointer = QGraphicsPixmapItem(QPixmap('icons/color_picker_pointer.png'))
        self.pointer.setOffset(-5, -5)
        self.pointer.setPos(V, S)
        self.scene.addItem(self.pointer)

    def val_changed(self, V):
        self.pointer.setPos(V, self.pointer.scenePos().y())

    def sat_changed(self, S):
        self.pointer.setPos(self.pointer.scenePos().x(), S)

    def hue_changed(self, H):
        self.colorGrad.setColorAt(1, QColor().fromHsv(H, 255, 255))
        self.colorGradItem.setBrush(QBrush(self.colorGrad))

    def move(self, pos):
        posX = pos.x()
        posY = pos.y()
        if posX < 0:
            posX = 0
        if posX > 255:
            posX = 255
        if posY < 0:
            posY = 0
        if posY > 255:
            posY = 255
        self.pointer.setPos(posX, posY)
        self.parent.sat_val_changed(posY, posX)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.pos())


class Hue(QGraphicsView):
    def __init__(self, parent, H):
        QGraphicsView.__init__(self)
        self.parent = parent
        self.setFixedSize(18, 258)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 16, 256)

        huegrad = QLinearGradient()
        huegrad.setStart(0, 0)
        huegrad.setFinalStop(0, 255)
        huegrad.setColorAt(0, QColor(255, 0, 0))
        huegrad.setColorAt(0.16, QColor(255, 255, 0))
        huegrad.setColorAt(0.33, QColor(0, 255, 0))
        huegrad.setColorAt(0.5, QColor(0, 255, 255))
        huegrad.setColorAt(0.66, QColor(0, 0, 255))
        huegrad.setColorAt(0.83, QColor(255, 0, 255))
        huegrad.setColorAt(1, QColor(255, 0, 0))
        self.hueGradient = QGraphicsRectItem(0, 0, 16, 256)
        self.hueGradient.setBrush(QBrush(huegrad))
        self.hueGradient.setPen(QColor(0, 0, 0, 0))
        self.scene.addItem(self.hueGradient)

        self.pointer = QGraphicsPixmapItem(QPixmap('icons/color_picker_slider.png'))
        self.pointer.setOffset(0, -3)
        self.pointer.setPos(0, round(H / 360 * 256))
        self.scene.addItem(self.pointer)

    def hue_changed(self, H):
        self.pointer.setPos(0, round(H / 360 * 256))

    def move(self, pos):
        posY = pos.y()
        if posY < 0:
            posY = 0
        if posY > 255:
            posY = 255
        self.pointer.setPos(0, posY)
        self.parent.hue_changed(round(posY / 256 * 360))

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.pos())


class Alpha(QGraphicsView):
    def __init__(self, parent, A):
        QGraphicsView.__init__(self)
        self.parent = parent

        self.scene = QGraphicsScene(self)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.setScene(self.scene)
        self.setFixedSize(18, 258)
        self.scene.setSceneRect(0, 0, 16, 256)
        self.setBackgroundBrush(QBrush(QPixmap('icons/color_picker_alpha.png')))

        alphagrad = QLinearGradient()
        alphagrad.setStart(0, 0)
        alphagrad.setFinalStop(0, 255)
        alphagrad.setColorAt(0, QColor(255, 255, 255))
        alphagrad.setColorAt(1, QColor(255, 255, 255, 0))
        self.alphaGradient = QGraphicsRectItem(0, 0, 16, 256)
        self.alphaGradient.setBrush(QBrush(alphagrad))
        self.alphaGradient.setPen(QColor(0, 0, 0, 0))
        self.scene.addItem(self.alphaGradient)

        self.pointer = QGraphicsPixmapItem(QPixmap('icons/color_picker_slider.png'))
        self.pointer.setOffset(0, -3)
        self.pointer.setPos(0, A)
        self.scene.addItem(self.pointer)

    def alpha_changed(self, A):
        self.pointer.setPos(0, A)

    def move(self, pos):
        posY = pos.y()
        if posY < 0:
            posY = 0
        if posY > 255:
            posY = 255
        self.pointer.setPos(0, posY)
        self.parent.alpha_changed(posY)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.pos())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.pos())


class ColorPreview(QGraphicsView):
    def __init__(self, parent, color, ex=True):
        QGraphicsView.__init__(self)
        self.parent = parent

        self.scene = QGraphicsScene(self)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)
        self.setScene(self.scene)
        self.setFixedSize(130, 66)
        self.scene.setSceneRect(0, 0, 128, 64)
        self.setBackgroundBrush(QBrush(QPixmap('icons/color_picker_alpha.png')))

        if ex:
            self.exColor = QGraphicsRectItem(0, 0, 64, 64)
            self.exColor.setBrush(QBrush(color))
            self.exColor.setPen(QPen(Qt.NoPen))
            self.scene.addItem(self.exColor)

            self.newColor = QGraphicsRectItem(64, 0, 64, 64)
        else:
            self.newColor = QGraphicsRectItem(0, 0, 128, 64)
        self.newColor.setBrush(QBrush(color))
        self.newColor.setPen(QPen(Qt.NoPen))
        self.scene.addItem(self.newColor)

    def color_changed(self, color):
        self.newColor.setBrush(QBrush(color))


class ColorDialog(QDialog):
    color_changed = pyqtSignal(QColor)

    def __init__(self, alpha=True, color=None):
        QDialog.__init__(self)
        self.setWindowTitle("color picker")
        if color is not None:
            if isinstance(color, QColor):
                self.color = QColor(color)
            elif type(color) is int:
                self.color = QColor.fromRgba(color)
            if not alpha:
                self.color.setAlpha(255)
            self.colorPreview = ColorPreview(self, self.color)
        else:
            self.color = QColor(255, 255, 255)
            self.colorPreview = ColorPreview(self, self.color, False)

        self.satVal = SatVal(self, getHue(self.color), self.color.saturation(), self.color.value())
        self.hue = Hue(self, getHue(self.color))
        if alpha:
            self.alpha = Alpha(self, 255 - self.color.alpha())
        self.color_changed.connect(self.colorPreview.color_changed)

        self.hL = QLabel("Hue")
        self.hL.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.hW = QSpinBox()
        self.hW.setRange(0, 359)
        self.hW.setValue(getHue(self.color))
        self.hW.setWrapping(True)
        self.hW.valueChanged.connect(self.h_changed)

        self.sL = QLabel("Saturation")
        self.sL.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sW = QSpinBox()
        self.sW.setRange(0, 255)
        self.sW.setValue(self.color.saturation())
        self.sW.valueChanged.connect(self.s_changed)

        self.vL = QLabel("Value")
        self.vL.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.vW = QSpinBox()
        self.vW.setRange(0, 255)
        self.vW.setValue(self.color.value())
        self.vW.valueChanged.connect(self.v_changed)

        if alpha:
            self.aL = QLabel("Alpha")
            self.aL.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.aW = QSpinBox()
            self.aW.setRange(0, 255)
            self.aW.setValue(255 - self.color.alpha())
            self.aW.valueChanged.connect(self.a_changed)

        self.cancelW = QPushButton('cancel', self)
        self.cancelW.clicked.connect(self.cancel_clicked)
        self.okW = QPushButton('ok', self)
        self.okW.clicked.connect(self.ok_clicked)
        self.okW.setDefault(True)

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.addWidget(self.satVal, 0, 0, 6, 1)
        grid.addWidget(self.hue, 0, 1, 6, 1)
        if alpha:
            grid.addWidget(self.alpha, 0, 2, 6, 1)
        grid.addWidget(self.colorPreview, 0, 3, 1, 2)
        grid.addWidget(self.hL, 1, 3)
        grid.addWidget(self.hW, 1, 4)
        grid.addWidget(self.sL, 2, 3)
        grid.addWidget(self.sW, 2, 4)
        grid.addWidget(self.vL, 3, 3)
        grid.addWidget(self.vW, 3, 4)
        if alpha:
            grid.addWidget(self.aL, 4, 3)
            grid.addWidget(self.aW, 4, 4)
        grid.setRowStretch(5, 4)

        okBox = QHBoxLayout()
        okBox.addStretch(0)
        okBox.addWidget(self.cancelW)
        okBox.addWidget(self.okW)

        vBox = QVBoxLayout()
        vBox.addLayout(grid)
        vBox.addStretch(0)
        vBox.addLayout(okBox)

        self.setLayout(vBox)
        self.exec_()

    def sat_val_changed(self, S, V):
        H = getHue(self.color)
        self.color.setHsv(H, S, V, self.color.alpha())
        self.color_changed.emit(self.color)
        self.sW.setValue(S)
        self.vW.setValue(V)

    def hue_changed(self, H):
        V = self.color.value()
        S = self.color.saturation()
        self.color.setHsv(H, S, V, self.color.alpha())
        self.color_changed.emit(self.color)
        self.satVal.hue_changed(H)
        self.hW.setValue(H)

    def h_changed(self, H):
        V = self.color.value()
        S = self.color.saturation()
        self.color.setHsv(H, S, V, self.color.alpha())
        self.color_changed.emit(self.color)
        self.satVal.hue_changed(H)
        self.hue.hue_changed(H)

    def s_changed(self, S):
        H = getHue(self.color)
        V = self.color.value()
        self.color.setHsv(H, S, V, self.color.alpha())
        self.color_changed.emit(self.color)
        self.satVal.sat_changed(S)

    def v_changed(self, V):
        H = getHue(self.color)
        S = self.color.saturation()
        self.color.setHsv(H, S, V, self.color.alpha())
        self.color_changed.emit(self.color)
        self.satVal.val_changed(V)

    def alpha_changed(self, A):
        self.color.setAlpha(255 - A)
        self.color_changed.emit(self.color)
        self.aW.setValue(A)

    def a_changed(self, A):
        self.color.setAlpha(255 - A)
        self.color_changed.emit(self.color)
        self.alpha.alpha_changed(A)

    def ok_clicked(self):
        self.accept()

    def cancel_clicked(self):
        self.reject()

    def getQColor(self):
        if self.result():
            return True, self.color
        else:
            return False, None

    def getRgba(self):
        if self.result():
            return True, self.color.rgb()
        else:
            return False, None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = ColorDialog(False).getRgba()
    print(mainWin)
    sys.exit(app.exec_())

#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Python 3 Compatibility
from __future__ import division
from __future__ import print_function

import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from colorPicker import ColorDialog
from widget import Background
from import_export import import_palette


class BackgroundDialog(QDialog):
    def __init__(self, color=QColor(150, 150, 150), arg=16):
        """ color: QColor is the background color
            arg can be
                int: square pattern, arg is the size
                str: custom pattern, arg is the filename
        """
        QDialog.__init__(self)
        self.setWindowTitle("background")
        ### color ###
        self.color = color
        self.colorL = QLabel("color :")
        self.colorIcon = QPixmap(40, 20)
        self.colorIcon.fill(self.color)
        self.colorW = QToolButton(self)
        self.colorW.setAutoRaise(True)
        self.colorW.setIcon(QIcon(self.colorIcon))
        self.colorW.setIconSize(QSize(46, 26))
        ### preview ###
        self.preview = QPixmap(128, 128)
        self.preview.fill(self.color)
        self.previewL = QLabel()
        self.previewL.setPixmap(self.preview)

        ### square pattern ###
        self.squareRadio = QRadioButton("square", self)
        self.sizeL = QLabel("size :")
        self.sizeW = QLineEdit("16", self)
        self.sizeW.setValidator(QIntValidator(self.sizeW))

        ### file pattern ###
        self.fileRadio = QRadioButton("file", self)
        ### model to store images ###
        self.modImgList = QStandardItemModel(0, 1)
        for f in os.listdir(os.path.join("resources", "pattern")):
            if f.endswith(".png"):
                i = QStandardItem(f)
                i.path = os.path.join("resources", "pattern", f)
                self.modImgList.appendRow(i)

        ### listview to display images ###
        self.imgList = QListView()
        self.imgList.setModel(self.modImgList)
        self.imgList.setSelectionMode(QAbstractItemView.SingleSelection)
        # select the first one
        self.fileName = self.modImgList.item(0).path
        sel = self.modImgList.createIndex(0, 0)
        self.imgList.selectionModel().select(sel, QItemSelectionModel.Select)

        ### init ###
        if type(arg) is int:
            self.pattern = "square"
            self.squareRadio.setChecked(True)
            self.size = arg
            self.sizeW.setText(str(self.size))
        elif type(arg) is str:
            self.pattern = "file"
            self.fileRadio.setChecked(True)
            for i in range(self.modImgList.rowCount()):
                if arg == self.modImgList.item(i).path:
                    self.imgList.selectionModel().clear()
                    sel = self.modImgList.createIndex(i, 0)
                    self.imgList.selectionModel().select(sel, QItemSelectionModel.Select)
                    self.fileName = arg
            self.size = 16

        ### preview ###
        self.updatePreview()
        # connect
        self.colorW.clicked.connect(self.colorClicked)
        self.squareRadio.toggled.connect(self.radioToggled)
        self.sizeW.textChanged.connect(self.sizeChanged)
        self.imgList.selectionModel().selectionChanged.connect(self.fileChanged)

        ### apply, undo ###
        self.cancelW = QPushButton('cancel', self)
        self.cancelW.clicked.connect(self.cancelClicked)
        self.okW = QPushButton('ok', self)
        self.okW.clicked.connect(self.okClicked)
        self.okW.setDefault(True)

        grid = QGridLayout()
        grid.setSpacing(4)
        grid.addWidget(self.colorL, 0, 1)
        grid.addWidget(self.colorW, 0, 2)

        grid.addWidget(self.squareRadio, 1, 0)
        grid.addWidget(self.sizeL, 1, 1)
        grid.addWidget(self.sizeW, 1, 2)

        grid.addWidget(self.fileRadio, 2, 0)
        grid.addWidget(self.imgList, 2, 1, 2, 2)

        grid.addWidget(self.previewL, 0, 3, 4, 1)

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

    def colorClicked(self):
        ok, color = ColorDialog(False, self.color).getQColor()
        if ok:
            self.color = color
            self.colorIcon.fill(self.color)
            self.colorW.setIcon(QIcon(self.colorIcon))
            self.updatePreview()

    def sizeChanged(self, s):
        try:
            self.size = int(s)
        except ValueError:
            self.size = 0
        if self.pattern == "square":
            self.updatePreview()

    def radioToggled(self):
        if self.squareRadio.isChecked():
            self.pattern = "square"
        elif self.fileRadio.isChecked():
            self.pattern = "file"
        self.updatePreview()

    def fileChanged(self):
        sel = self.imgList.selectionModel().selectedIndexes()[0].row()
        self.fileName = self.modImgList.item(sel).path
        if self.pattern == "file":
            self.updatePreview()

    def updatePreview(self):
        self.preview.fill(self.color)
        p = QPainter(self.preview)
        if self.pattern == "square":
            p.drawPixmap(16, 16, Background(QSize(96, 96), self.size))
        elif self.pattern == "file":
            p.drawPixmap(16, 16, Background(QSize(96, 96), self.fileName))
        self.previewL.setPixmap(self.preview)

    def okClicked(self):
        try:
            self.size = int(self.sizeW.text())
        except ValueError:
            self.size = 0
        self.accept()

    def cancelClicked(self):
        self.reject()

    def getReturn(self):
        if self.result():
            if self.pattern == "square":
                return self.color, self.size
            elif self.pattern == "file":
                return self.color, self.fileName
        return None, None


class NewDialog(QDialog):
    defaultSize = (64, 64)
    sizeRange = (16, 2048)
    sizePresets = [(32, 32),
                   (64, 64),
                   (128, 128),
                   (256, 256),
                   None,
                   (320, 240),
                   (640, 480),
                   (1024, 768),
                   None,
                   (1280, 720),
                   (1920, 1080)]

    def __init__(self, size=defaultSize):
        QDialog.__init__(self)
        self.setWindowTitle("New Animation")

        ### Presets ###
        presetsCombo = QComboBox(self)
        for preset in NewDialog.sizePresets:
            if preset is None:
                presetsCombo.insertSeparator(presetsCombo.count())
            else:
                presetsCombo.addItem(str(preset[0]) + "x" + str(preset[1]), preset)

        ### Size ###
        widthSpin = QSpinBox(self)
        widthSpin.setRange(*NewDialog.sizeRange)
        widthSpin.setValue(size[0])
        heightSpin = QSpinBox(self)
        heightSpin.setRange(*NewDialog.sizeRange)
        heightSpin.setValue(size[1])

        def applyPreset(i):
            widthSpin.setValue(NewDialog.sizePresets[i][0])
            heightSpin.setValue(NewDialog.sizePresets[i][1])

        presetsCombo.activated.connect(applyPreset)
        #presetsCombo.setCurrentIndex(0)

        ### Palette ###
        palettePath = os.path.join("resources", "palette")
        ls = os.listdir(palettePath)
        ls.sort()
        paletteDict = {}

        paletteCombo = QComboBox(self)
        for i in ls:
            paletteDict[os.path.splitext(i)[0]] = os.path.join(palettePath, i)
            paletteCombo.addItem(os.path.splitext(i)[0])

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        layout = QFormLayout()
        layout.addRow("&Preset", presetsCombo)
        layout.addRow("&Width", widthSpin)
        layout.addRow("&Height", heightSpin)
        layout.addRow(separator)
        layout.addRow("P&alette", paletteCombo)
        layout.addRow(buttonBox)

        self.setLayout(layout)
        def acceptDialog():
             self.resultData = { "width": widthSpin.value(),
                                 "height": heightSpin.value(),
                                 "palette": paletteDict[paletteCombo.currentText()]}

        self.accepted.connect(acceptDialog)


class CropDialog(QDialog):
    def __init__(self, size):
        QDialog.__init__(self)
        self.setWindowTitle("crop animation")

        ### instructions ###
        self.wL = QLabel("width")
        self.wL.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.hL = QLabel("height")
        self.hL.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.actualSizeL = QLabel("Actual size")
        self.actualSizeL.setAlignment(Qt.AlignCenter)
        self.actualWL = QLabel(str(size.width()))
        self.actualHL = QLabel(str(size.height()))
        self.newSizeL = QLabel("New size")
        self.newSizeL.setAlignment(Qt.AlignCenter)
        self.newWW = QLineEdit(str(size.width()), self)
        self.newWW.setValidator(QIntValidator(self.newWW))
        self.newHW = QLineEdit(str(size.height()), self)
        self.newHW.setValidator(QIntValidator(self.newHW))
        ### offset ###
        self.offsetL = QLabel("offset")
        self.offsetL.setAlignment(Qt.AlignCenter)
        self.horizontalL = QLabel("horizontal")
        self.horizontalL.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.horizontalOffsetW = QLineEdit(str(0), self)
        self.horizontalOffsetW.setValidator(QIntValidator(self.horizontalOffsetW))
        self.verticalL = QLabel("vertical")
        self.verticalL.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.verticalOffsetW = QLineEdit(str(0), self)
        self.verticalOffsetW.setValidator(QIntValidator(self.verticalOffsetW))

        ### error ###
        self.errorL = QLabel("")
        ### apply, undo ###
        self.cancelW = QPushButton('cancel', self)
        self.cancelW.clicked.connect(self.cancelClicked)
        self.cropW = QPushButton('crop', self)
        self.cropW.clicked.connect(self.cropClicked)
        self.cropW.setDefault(True)

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.addWidget(self.wL, 1, 0)
        grid.addWidget(self.hL, 2, 0)

        grid.addWidget(self.actualSizeL, 0, 1)
        grid.addWidget(self.actualWL, 1, 1)
        grid.addWidget(self.actualHL, 2, 1)

        grid.addWidget(self.newSizeL, 0, 2)
        grid.addWidget(self.newWW, 1, 2)
        grid.addWidget(self.newHW, 2, 2)

        grid.addWidget(self.offsetL, 3, 2)

        grid.addWidget(self.horizontalL, 4, 1)
        grid.addWidget(self.verticalL, 5, 1)
        grid.addWidget(self.horizontalOffsetW, 4, 2)
        grid.addWidget(self.verticalOffsetW, 5, 2)

        grid.addWidget(self.errorL, 6, 0, 1, 3)

        okBox = QHBoxLayout()
        okBox.addStretch(0)
        okBox.addWidget(self.cancelW)
        okBox.addWidget(self.cropW)

        vBox = QVBoxLayout()
        vBox.addLayout(grid)
        vBox.addStretch(0)
        vBox.addLayout(okBox)

        self.setLayout(vBox)
        self.exec_()

    def cropClicked(self):
        try:
            w = int(self.newWW.text())
            h = int(self.newHW.text())
        except ValueError:
            self.errorL.setText("ERROR : You must enter a number !")
            return
        try:
            wOffset = int(self.horizontalOffsetW.text())
        except ValueError:
            wOffset = 0
        try:
            hOffset = int(self.verticalOffsetW.text())
        except ValueError:
            hOffset = 0
        if w > 0 and h > 0:
            self.rect = QRect(wOffset, hOffset, w, h)
            self.accept()
        else:
            self.errorL.setText("ERROR : The size must be greater than 0 !")

    def cancelClicked(self):
        self.reject()

    def getReturn(self):
        if self.result():
            return self.rect


class ResizeDialog(QDialog):
    def __init__(self, size):
        QDialog.__init__(self)
        self.setWindowTitle("resize animation")
        self.w, self.h = size.width(), size.height()

        self.factor = 1
        self.factorW = QComboBox(self)
        self.factorW.addItems(["0.25", "0.5", "1", "2", "4"])
        self.factorW.setCurrentIndex(2)
        self.factorW.activated[str].connect(self.factorClicked)

        ### instructions ###
        self.wL = QLabel("width")
        self.wL.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.hL = QLabel("height")
        self.hL.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.actualSizeL = QLabel("Actual size")
        self.actualSizeL.setAlignment(Qt.AlignCenter)
        self.actualWL = QLabel(str(self.w))
        self.actualHL = QLabel(str(self.h))
        self.newSizeL = QLabel("New size")
        self.newSizeL.setAlignment(Qt.AlignCenter)
        self.newWL = QLabel(str(self.w))
        self.newHL = QLabel(str(self.h))

        ### apply, undo ###
        self.cancelW = QPushButton('cancel', self)
        self.cancelW.clicked.connect(self.cancelClicked)
        self.resizeW = QPushButton('resize', self)
        self.resizeW.clicked.connect(self.resizeClicked)
        self.resizeW.setDefault(True)

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.addWidget(self.factorW, 0, 1, 1, 2)
        grid.addWidget(self.wL, 1, 1)
        grid.addWidget(self.hL, 1, 2)

        grid.addWidget(self.actualSizeL, 2, 0)
        grid.addWidget(self.actualWL, 2, 1)
        grid.addWidget(self.actualHL, 2, 2)

        grid.addWidget(self.newSizeL, 3, 0)
        grid.addWidget(self.newWL, 3, 1)
        grid.addWidget(self.newHL, 3, 2)

        okBox = QHBoxLayout()
        okBox.addStretch(0)
        okBox.addWidget(self.cancelW)
        okBox.addWidget(self.resizeW)

        vBox = QVBoxLayout()
        vBox.addLayout(grid)
        vBox.addStretch(0)
        vBox.addLayout(okBox)

        self.setLayout(vBox)
        self.exec_()

    def factorClicked(self, n):
        self.factor = float(n)
        self.newWL.setText(str(int(self.w * self.factor)))
        self.newHL.setText(str(int(self.h * self.factor)))

    def resizeClicked(self):
        self.accept()

    def cancelClicked(self):
        self.reject()

    def getReturn(self):
        if self.result():
            return self.factor


class RenameLayerDialog(QDialog):
    def __init__(self, name):
        QDialog.__init__(self)
        self.setWindowTitle("rename layer")

        self.name = name
        ### instructions ###
        self.instL = QLabel("Enter the new name of the layer :")
        self.nameW = QLineEdit(name, self)
        ### error ###
        self.errorL = QLabel("")
        ### apply, undo ###
        self.cancelW = QPushButton('cancel', self)
        self.cancelW.clicked.connect(self.cancelClicked)
        self.renameW = QPushButton('rename', self)
        self.renameW.clicked.connect(self.renameClicked)
        self.renameW.setDefault(True)
        okBox = QHBoxLayout()
        okBox.addStretch(0)
        okBox.addWidget(self.cancelW)
        okBox.addWidget(self.renameW)

        vBox = QVBoxLayout()
        vBox.addWidget(self.instL)
        vBox.addWidget(self.nameW)
        vBox.addWidget(self.errorL)
        vBox.addLayout(okBox)

        self.setLayout(vBox)
        self.exec_()

    def renameClicked(self):
        n = self.nameW.text()
        if n == self.name:
            self.reject()
        else:
            self.name = n
            self.accept()

    def cancelClicked(self):
        self.reject()

    def getReturn(self):
        if self.result():
            return self.name


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    #~ mainWin = RenameLayerDialog("layer 1")
    #~ mainWin = ResizeDialog((24, 32))
    #~ mainWin = BackgroundDialog(QColor(150, 150, 150), "pattern/iso_20x11.png")
    mainWin = BackgroundDialog()
    sys.exit(app.exec_())

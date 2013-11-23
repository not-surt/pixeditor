#!/usr/bin/env python
#-*- coding: utf-8 -*-

from PyQt4.QtGui import *
from PyQt4.QtCore import *

import os
import xml.etree.ElementTree as ET

from data import Canvas

######## open/save ########
def open_pix(dirName):
    if not dirName:
        dirName = os.path.expanduser("~")
    url = QFileDialog.getOpenFileName(None, "open pix file", dirName, "Pix files (*.pix );;All files (*)")
    if url:
        try:
            save = open(url, "r")
            xml = ET.parse(save).getroot()
            save.close()
            return xml, url
        except IOError:
            print("Can't open file")
            return None, None
    return None, None


def save_pix(xml, url):
    try:
        save = open(url, "w")
        save.write(ET.tostring(xml, encoding="unicode"))
        save.close()
        print("saved")
        return url
    except IOError:
        print("Can't open file")
        return None


def get_save_url(dirName=None, ext="pix"):
    if not dirName:
        dirName = os.path.expanduser("~")
    while True:
        url = str(QFileDialog.getSaveFileName(None, "save %s file" % (ext),
                                              dirName, "%s files (*.%s )" % (ext, ext)))
        if url:
            dirName = os.path.dirname(url)
            if os.path.splitext(url)[1].lower() == ".%s" % (ext):
                return url
            else:
                url = os.path.splitext(url)[0] + ".%s" % (ext)
                if os.path.isfile(url):
                    message = "The file %s allready exist.\n" % (os.path.basename(url))
                    message = "%sDo you want to overwrite it ?" % (message)
                    messageBox = QMessageBox()
                    messageBox.setWindowTitle("Overwrite ?")
                    messageBox.setText(message);
                    messageBox.setIcon(QMessageBox.Warning)
                    messageBox.addButton("Cancel", QMessageBox.RejectRole)
                    messageBox.addButton("Overwrite", QMessageBox.AcceptRole)
                    ret = messageBox.exec_();
                    if ret:
                        return url
                else:
                    message = "The file will be save as %s.\n" % (os.path.basename(url))
                    messageBox = QMessageBox()
                    messageBox.setWindowTitle("Save ?")
                    messageBox.setText(message);
                    messageBox.setIcon(QMessageBox.Question)
                    messageBox.addButton("Cancel", QMessageBox.RejectRole)
                    messageBox.addButton("Save", QMessageBox.AcceptRole)
                    ret = messageBox.exec_();
                    if ret:
                        return url
        else:
            return

######## import ########
def import_img(project, dirName, size=QSize(0, 0), colorTable=[0]):
    if not dirName:
        dirName = os.path.expanduser("~")
    urls = QFileDialog.getOpenFileNames(
        None, "Import PNG and GIF", dirName, "PNG and GIF files (*.png *.gif);;All files (*)")
    if not urls:
        return None, None, None, None
    imgs = []
    canceled = []
    # open all img get the colortable and max size 
    canvasList = []
    for url in urls:
        if str(url).endswith("png") or str(url).endswith("PNG"):
            img = Canvas(project, str(url))
            canvasList.append((img, str(url)))
        elif str(url).endswith("gif") or str(url).endswith("GIF"):
            mov = QMovie(str(url))
            for i in range(mov.frameCount()):
                mov.jumpToFrame(i)
                img = Canvas(project, mov.currentImage())
                canvasList.append((img, str(url)))

    for img, url in canvasList:
        if img.format() == QImage.Format_Indexed8:
            colorMixed = img.mixColortable(colorTable)
        else:
            colorMixed = img.sniffColortable(colorTable)
        if colorMixed:
            colorTable = colorMixed
            imgs.append(img)
            size = size.expandedTo(img.size())
        else:
            canceled.append(url)

    for n, img in enumerate(imgs):
        img = Canvas(project, img.convertToFormat(QImage.Format_Indexed8, colorTable))
        if img.size() != size:
            li = img.returnAsList()
            width = img.width()
            img = Canvas(project, size, colorTable)
            img.loadFromList(li, width)
        imgs[n] = img

    if canceled:
        text = "Failed to import some files (too much colors):"
        for i in canceled:
            text = "%s\n %s" % (text, i)
        message = QMessageBox()
        message.setWindowTitle("Import error")
        message.setText(text);
        message.setIcon(QMessageBox.Warning)
        message.addButton("Ok", QMessageBox.AcceptRole)
        message.exec_();
    return size, imgs, colorTable


def export_png_all(project, url):
    url = os.path.splitext(str(url))[0]
    files = []
    fnexist = False
    for nl, layer in enumerate(project.timeline, 1):
        for nf, im in enumerate(layer, 1):
            fn = "%s%s%s.png" % (url, nl, nf)
            if os.path.isfile(fn):
                fnexist = True
            if im:
                files.append((fn, im))
                sim = im
            else:
                files.append((fn, sim))
    if fnexist:
        message = QMessageBox()
        message.setWindowTitle("Overwrite?")
        message.setText("Some filename allready exist.\nDo you want to overwrite them?");
        message.setIcon(QMessageBox.Warning)
        message.addButton("Cancel", QMessageBox.RejectRole)
        message.addButton("Overwrite", QMessageBox.AcceptRole)
        ret = message.exec_();
        if ret:
            for i in files:
                i[1].save(i[0])
    else:
        for i in files:
            i[1].save(i[0])


def export_png(project, fullUrl=""):
    isUrl = False
    while not isUrl:
        fullUrl = QFileDialog.getSaveFileName(
            None, "export (.png)", fullUrl, "PNG files (*.png)",
            QFileDialog.DontConfirmOverwrite)
        if not fullUrl:
            return
        isUrl = True
        url = os.path.splitext(str(fullUrl))[0]
        nFrames = project.timeline.frameVisibleCount()
        for i in range(nFrames):
            fn = "%s%s%s.png" % (url, "0" * (len(str(nFrames)) - len(str(i))), i)
            if os.path.isfile(fn):
                isUrl = False
                message = QMessageBox()
                message.setWindowTitle("Overwrite?")
                message.setText("Some filename allready exist.\nDo you want to overwrite them?");
                message.setIcon(QMessageBox.Warning)
                message.addButton("Cancel", QMessageBox.RejectRole)
                message.addButton("Overwrite", QMessageBox.AcceptRole)
                ret = message.exec_();
                if ret:
                    isUrl = True
                    break
                else:
                    isUrl = False
                    break
    for i in range(nFrames):
        fn = "%s%s%s.png" % (url, "0" * (len(str(nFrames)) - len(str(i))), i)

        canvasList = project.timeline.getVisibleCanvasList(i)
        if len(canvasList) == 1:
            canvas = canvasList[0]
        else:
            canvas = QImage(project.size, QImage.Format_ARGB32)
            canvas.fill(QColor(0, 0, 0, 0))
            p = QPainter(canvas)
            for c in reversed(canvasList):
                if c:
                    p.drawImage(0, 0, c)
            p.end()
        canvas.save(fn)

    # convert all png to a gif with imagemagick
    os.system("convert -delay 1/12 -dispose Background -loop 0 %s*.png %s.gif" % (url, url))
    return fullUrl


def import_palette(url, nColor=0):
    """ take a file palette (.gpl or .pal) and return a list of QRgba """
    save = open(url, "r")
    palette = []
    for line in save.readlines():
        palette.append([""])
        for char in line:
            if char.isdigit():
                palette[-1][-1] += char
            else:
                if len(palette[-1]) == 3 and palette[-1][-1] != "":
                    break
                if palette[-1][-1] != "":
                    palette[-1].append("")
    pal = [QColor(0, 0, 0, 0).rgba()]
    black = False
    for i in palette:
        if len(i) == 3:
            # avoid to fill palette of black as in some pal files
            if i == ["0", "0", "0"]:
                if black:
                    continue
                black = True
            pal.append(QColor(int(i[0]), int(i[1]), int(i[2])).rgb())
    save.close()
    while len(pal) < nColor:
        pal.append(QColor(0, 0, 0).rgb())
    return pal


def export_palette(pal):
    """take a list of QRgb and write a palette file .pal
       without the first alpha color"""
    text = "JASC-PAL\n0100\n%s\n" % (len(pal) - 1)
    for i in pal:
        if i == 0:
            continue
        col = QColor.fromRgb(i)
        text = "%s%s %s %s\n" % (text, col.red(), col.green(), col.blue())
    return text


def export_pen(pen, name):
    text = '#!/usr/bin/env python\n#-*- coding: utf-8 -*-\n\nname = "%s"\nicon = "custom.png"\npixelList = (' % (name)
    for i in pen:
        text = "%s(%s, %s)," % (text, i[0], i[1])
    text = "%s)" % (text)
    return text


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    print(get_save_url())
    sys.exit(app.exec_())

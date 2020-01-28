# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np

class GraphicsScene(QGraphicsScene):
    def __init__(self, mode_list, maskSizeSlider, sketchSizeSlider, paintSizeSlider, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.modes = mode_list
        self.maskSizeSlider = maskSizeSlider
        self.sketchSizeSlider = sketchSizeSlider
        self.paintSizeSlider = paintSizeSlider
        self.mouse_clicked = False
        self.updateCount = 0
        self.prev_pt = None

        # self.masked_image = None

        # save the points
        self.mask_points = []
        self.sketch_points = []
        self.stroke_points = []

        self.updateCounts = []

        # save the history of edit
        self.history = []

        # strokes color
        self.stk_color = None

    def reset(self):
        # save the points
        self.mask_points = []
        self.sketch_points = []
        self.stroke_points = []

        # save the history of edit
        self.history = []

        # strokes color
        self.stk_color = None

        self.prev_pt = None

    def mousePressEvent(self, event):
        self.mouse_clicked = True
        self.updateCount = 0

    def mouseReleaseEvent(self, event):
        self.prev_pt = None
        self.mouse_clicked = False
        self.updateCounts.append(self.updateCount)
        self.updateCount = 0

    def mouseMoveEvent(self, event):
        if self.mouse_clicked:
            self.updateCount += 1
            if self.modes[0] == 1:
                if self.prev_pt:
                    self.drawMask(self.prev_pt, event.scenePos())
                    pts = {}
                    pts['prev'] = (int(self.prev_pt.x()),int(self.prev_pt.y()))
                    pts['curr'] = (int(event.scenePos().x()),int(event.scenePos().y()))
                    tmp = [pts,self.maskSizeSlider.value()]                   
                    self.mask_points.append(tmp)
                    self.history.append(0)
                    self.prev_pt = event.scenePos()
                else:
                    self.prev_pt = event.scenePos()
            elif self.modes[1] == 1:
                if self.prev_pt:
                    self.drawSketch(self.prev_pt, event.scenePos())
                    pts = {}
                    pts['prev'] = (int(self.prev_pt.x()),int(self.prev_pt.y()))
                    pts['curr'] = (int(event.scenePos().x()),int(event.scenePos().y()))
                    tmp = [pts,self.sketchSizeSlider.value()] 
                    self.sketch_points.append(tmp)
                    self.history.append(1)
                    self.prev_pt = event.scenePos()
                else:
                    self.prev_pt = event.scenePos()
            elif self.modes[2] == 1:
                if self.prev_pt:
                    self.drawStroke(self.prev_pt, event.scenePos())
                    pts = {}
                    pts['prev'] = (int(self.prev_pt.x()),int(self.prev_pt.y()))
                    pts['curr'] = (int(event.scenePos().x()),int(event.scenePos().y()))
                    pts['color'] = self.stk_color
                    pts['width'] = self.paintSizeSlider.value()
                
                    self.stroke_points.append(pts)
                    self.history.append(2)
                    self.prev_pt = event.scenePos()
                else:
                    self.prev_pt = event.scenePos()

    def drawMask(self, prev_pt, curr_pt):
        lineItem = QGraphicsLineItem(QLineF(prev_pt, curr_pt))
        lineItem.setPen(QPen(Qt.white, self.maskSizeSlider.value(), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)) # rect
        lineItem.setZValue(2)
        self.addItem(lineItem)

    def drawSketch(self, prev_pt, curr_pt):
        lineItem = QGraphicsLineItem(QLineF(prev_pt, curr_pt))
        lineItem.setPen(QPen(Qt.black, self.sketchSizeSlider.value(), Qt.SolidLine,  Qt.RoundCap, Qt.RoundJoin)) # rect
        #lineItem.setPen(QPen(Qt.black, 1, Qt.SolidLine)) # rect
        lineItem.setZValue(4)
        self.addItem(lineItem)

    def drawStroke(self, prev_pt, curr_pt):
        lineItem = QGraphicsLineItem(QLineF(prev_pt, curr_pt))
        lineItem.setPen(QPen(QColor(self.stk_color), self.paintSizeSlider.value(), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)) # rect
        lineItem.setZValue(3)
        self.addItem(lineItem)

    def get_stk_color(self, color):
        self.stk_color = color

    def erase_prev_pt(self):
        self.prev_pt = None

    def reset_items(self):
        for i in range(len(self.items())):
            item = self.items()[0]
            self.removeItem(item)
        
    def undo(self):
        if len(self.items())>1:
            if len(self.items())>=self.updateCounts[len(self.updateCounts)-1]:
                for i in range(self.updateCounts[len(self.updateCounts)-1]-1):
                    item = self.items()[0]
                    self.removeItem(item)
                    if self.history[-1] == 0:
                        self.mask_points.pop()
                        self.history.pop()
                    elif self.history[-1] == 1:
                        self.sketch_points.pop()
                        self.history.pop()
                    elif self.history[-1] == 2:
                        self.stroke_points.pop()
                        self.history.pop()
                    elif self.history[-1] == 3:
                        self.history.pop()
            else:
                for i in range(len(self.items())-1):
                    item = self.items()[0]
                    self.removeItem(item)
                    if self.history[-1] == 0:
                        self.mask_points.pop()
                        self.history.pop()
                    elif self.history[-1] == 1:
                        self.sketch_points.pop()
                        self.history.pop()
                    elif self.history[-1] == 2:
                        self.stroke_points.pop()
                        self.history.pop()
                    elif self.history[-1] == 3:
                        self.history.pop()
        self.updateCount = 0

        if len(self.updateCounts) > 0:
            self.updateCounts.pop()

        self.update()

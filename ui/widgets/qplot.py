#-*- coding:utf-8 -*-

__author__ = 'lionel'

from __future__ import unicode_literals
import sys
import os
import random
from PyQt4 import QtGui, QtCore
import numpy as np

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class BaseCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.hold(False)
        self.initial_figure()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def initial_figure(self):
        pass


class DynamicCanvas(BaseCanvas):
    def __init__(self, *args, **kwargs):
        BaseCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def initial_figure(self, x, y):
        """ Create the initial figure with a plot.
         Parameters:
         x: The x value for the x axis
         y: A list of initial y values of each plotted lines. len(y) = number of plotted lines
        """
        self.xx = [x]
        self.yy = np.array([y])
        self.lines = self.axes.plot(self.xx, self.yy, 'o-')

    def update_figure(self, x, y):
        """ Add values to the initial lines and plot them.
        Parameters:
        x: the x value where to set the y values
        y: a list of y values to add to the intial lines
        """
        self.xx.append(x)
        self.yy = np.append(self.yy, y, axis=0)
        for i, yi in enumerate(self.yy.T):
            self.lines[i].set_data((self.xx, yi))
        self.axes.relim()
        self.axes.autoscale_view()
        self.draw()
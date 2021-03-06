# -----------------------------------------------------------------------------
# Name:        wx.lib.plot.py
# Purpose:     Line, Bar and Scatter Graphs
#
# Author:      Gordon Williams
#
# Created:     2003/11/03
# RCS-ID:      $Id: plot.py,v 1.9 2009/01/13 16:26:55 rmj01 Exp $
# Copyright:   (c) 2002
# Licence:     Use as you wish.
# -----------------------------------------------------------------------------
#

"""
This file contains two parts; first the re-usable library stuff, then,
after a "if __name__=='__main__'" test, a simple frame and a few default
plots for examples and testing.

Based on wxPlotCanvas
Written by K.Hinsen, R. Srinivasan;
Ported to wxPython Harm van der Heijden, feb 1999

Zooming controls with mouse (when enabled):
    Left mouse drag - zoom box.
    Left mouse double click - reset zoom.
    Right mouse click - zoom out centred on click location.
"""

import wx
import numpy as np
from wx import Image, BitmapFromImage
from io import BytesIO
import zlib

#
# Plotting classes...
#
class PolyPoints:
    """Base Class for lines and markers
        - All methods are private.
    """

    def __init__(self, points, attr):
        self._points = np.array(points).astype(np.float64)
        self._logscale = (False, False)
        self.currentScale = (1, 1)
        self.currentShift = (0, 0)
        self.scaled = self.points
        self.attributes = {}
        self.attributes.update(self._attributes)
        for name, value in attr.items():
            if name not in self._attributes.keys():
                raise KeyError(
                    "Style attribute incorrect. Should be one of %s" % self._attributes.keys())
            self.attributes[name] = value

    def set_log_scale(self, logscale):
        self._logscale = logscale

    def __getattr__(self, name):
        if name == 'points':
            if len(self._points) > 0:
                data = np.array(self._points, copy=True)
                if self._logscale[0]:
                    data = self.log10(data, 0)
                if self._logscale[1]:
                    data = self.log10(data, 1)
                return data
            else:
                return self._points
        else:
            raise AttributeError(name)

    @staticmethod
    def log10(data, ind):
        data = np.compress(data[:, ind] > 0, data, 0)
        data[:, ind] = np.log10(data[:, ind])
        return data

    def bounding_box(self):
        if len(self.points) == 0:
            # no curves to draw
            # defaults to (-1,-1) and (1,1) but axis can be set in draw
            minXY = np.array([-1.0, -1.0])
            maxXY = np.array([1.0, 1.0])
        else:
            minXY = np.minimum.reduce(self.points)
            maxXY = np.maximum.reduce(self.points)

        return minXY, maxXY

    def scale_shift(self, scale=(1, 1), shift=(0, 0)):
        if len(self.points) == 0:
            # no curves to draw
            return
        if (scale is not self.currentScale) or (shift is not self.currentShift):
            # update point scaling
            self.scaled = scale * self.points + shift
            self.currentScale = scale
            self.currentShift = shift
        # else unchanged use the current scaling

    def get_legend(self):
        return self.attributes['legend']

    def get_closest_pnt(self, pntXY, pnt_scaled=True):
        """Returns the index of closest point on the curve, pointXY, scaledXY, distance
            x, y in user coords
            if pointScaled == True based on screen coords
            if pointScaled == False based on user coords
        """
        if pnt_scaled:
            # Using screen coords
            p = self.scaled
            pxy = self.currentScale * np.array(pntXY) + self.currentShift
        else:
            # Using user coords
            p = self.points
            pxy = np.array(pntXY)
        # determine distance for each point
        d = np.sqrt(
            np.add.reduce((p - pxy) ** 2, 1))  # sqrt(dx^2+dy^2)
        pntIndex = np.argmin(d)
        dist = d[pntIndex]
        return [pntIndex, self.points[pntIndex], self.scaled[pntIndex], dist]


class PolyLine(PolyPoints):
    """Class to define line type and style
        - All methods except __init__ are private.
    """

    _attributes = {'colour': 'black',
                   'width': 1,
                   'style': wx.PENSTYLE_SOLID,
                   'legend': ''}

    def __init__(self, points, **attr):
        """Creates PolyLine object
            points - sequence (array, tuple or list) of (x,y) points making up line
            **attr - key word attributes
                Defaults:
                    'colour'= 'black',          - wx.Pen Colour any wx.NamedColour
                    'width'= 1,                 - Pen width
                    'style'= wx.SOLID,          - wx.Pen style
                    'legend'= ''                - Line Legend to display
        """
        PolyPoints.__init__(self, points, attr)

    def draw(self, dc, printerScale, coord=None):
        colour = self.attributes['colour']
        width = self.attributes['width'] * printerScale
        style = self.attributes['style']
        if not isinstance(colour, wx.Colour):
            colour = wx.Colour(colour)
        pen = wx.Pen(colour, width, style)
        pen.SetCap(wx.CAP_BUTT)
        dc.SetPen(pen)
        if coord is None:
            dc.DrawLines(self.scaled.astype(int))
        else:
            coord = coord.astype(int)
            dc.DrawLines(coord)      # draw legend line

    def get_sym_extent(self, printer_scale):
        """Width and Height of Marker"""
        h = self.attributes['width'] * printer_scale
        w = 5 * h
        return w, h


class PolyEllipse(PolyPoints):
    """Added by rmj 14.05.07 - class for plotting ellipse"""
    _attributes = {'colour': 'black',
                   'width': 1,
                   'dim': (1, 1),
                   'style': wx.PENSTYLE_SOLID,
                   'legend': ''}

    def __init__(self, points, **attr):
        """Creates PolyEllipse object
            points - sequence array of (x,y) points for each ellipse
            **attr - key word attributes
                Defaults:
                    'colour'= 'black',          - wx.Pen Colour any wx.NamedColour
                    'width'= 1,                 - Pen width
                    'dim'=(1,1),                - width & height of ellipse
                    'style'= wx.SOLID,          - wx.Pen style
        """
        PolyPoints.__init__(self, points, attr)

    def draw(self, dc, printerScale, coord=None):
        _ = coord
        colour = self.attributes['colour']
        width = self.attributes['width'] * printerScale
        dim = self.attributes['dim']
        style = self.attributes['style']
        dc.SetPen(wx.Pen(wx.NamedColour(colour), int(width), style))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)

        # set ellipse
        width = dim[0]
        height = dim[1]
        rect = np.zeros((len(self.scaled), 4), 'f') + [0.0, 0.0, width, height]
        rect[:, 0:2] = self.scaled
        rect[:, 2:4] = self.currentScale * rect[:, 2:4]
        rect[:, 0:2] = self.scaled - (rect[:, 2:4] / 2)
        dc.DrawEllipseList(rect)

    def get_sym_extent(self, printerScale):
        """Width and Height of Marker"""
        h = self.attributes['width'] * printerScale
        w = 5 * h
        return w, h

# noinspection PyMethodMayBeStatic
class PolyMarker(PolyPoints):
    """Class to define marker type and style
        - All methods except __init__ are private.
    """

    _attributes = {'colour': 'black',
                   'width': 1,
                   'size': 2,
                   'fillcolour': None,
                   'fillstyle': wx.BRUSHSTYLE_SOLID,
                   'marker': 'circle',
                   'legend': '',
                   'labels': None,
                   'text_colour': 'black'}

    def __init__(self, points, **attr):
        """Creates PolyMarker object
        points - sequence (array, tuple or list) of (x,y) points
        **attr - key word attributes
            Defaults:
                'colour'= 'black',          - wx.Pen Colour any wx.NamedColour
                'width'= 1,                 - Pen width
                'size'= 2,                  - Marker size
                'fillcolour'= same as colour,      - wx.Brush Colour any wx.NamedColour
                'fillstyle'= wx.SOLID,      - wx.Brush fill style (use wx.TRANSPARENT for no fill)
                'marker'= 'circle'          - Marker shape
                'legend'= ''                - Marker Legend to display
                'labels'= None              - list of strings
                'text_color'= 'black'       - wx.Pen Colour any wx.NamedColour
                
            Marker Shapes:
                - 'circle'
                - 'dot'
                - 'square'
                - 'triangle'
                - 'triangle_down'
                - 'cross'
                - 'plus'
                - 'text'
        """

        PolyPoints.__init__(self, points, attr)

    def draw(self, dc, printerScale, coord=None):
        colour = self.attributes['colour']
        width = self.attributes['width'] * printerScale
        size = self.attributes['size'] * printerScale
        fillcolour = self.attributes['fillcolour']
        fillstyle = self.attributes['fillstyle']
        marker = self.attributes['marker']

        if colour and not isinstance(colour, wx.Colour):
            colour = wx.Colour(colour)
        if fillcolour and not isinstance(fillcolour, wx.Colour):
            fillcolour = wx.Colour(fillcolour)

        dc.SetPen(wx.Pen(colour, width))
        if fillcolour:
            dc.SetBrush(wx.Brush(fillcolour, fillstyle))
        else:
            dc.SetBrush(wx.Brush(colour, fillstyle))

        if coord is None:
            self._drawmarkers(dc, self.scaled, marker, size)
        else:
            self._drawmarkers(dc, coord, marker, size)  # draw legend marker

    def get_sym_extent(self, printerScale):
        """Width and Height of Marker"""
        s = 5 * self.attributes['size'] * printerScale
        return s, s

    def _drawmarkers(self, dc, coords, marker, size=1):
        f = eval('self._' + marker)
        f(dc, coords, size)

    def _circle(self, dc, coords, size=1):
        fact = 2.5 * size
        wh = 5.0 * size
        rect = np.zeros((len(coords), 4), float) + [0.0, 0.0, wh, wh]
        rect[:, 0:2] = coords - [fact, fact]
        dc.DrawEllipseList(rect.astype(int))

    def _dot(self, dc, coords, size=1):
        _ = size
        dc.DrawPointList(coords)

    def _square(self, dc, coords, size=1):
        fact = 2.5 * size
        wh = 5.0 * size
        rect = np.zeros((len(coords), 4), float) + [0.0, 0.0, wh, wh]
        rect[:, 0:2] = coords - [fact, fact]
        dc.DrawRectangleList(rect.astype(int))

    def _triangle(self, dc, coords, size=1):
        shape = [(-2.5 * size, 1.44 * size), (2.5 * size, 1.44 * size),
                 (0.0, -2.88 * size)]
        poly = np.repeat(coords, 3)
        poly.shape = (len(coords), 3, 2)
        poly += shape
        dc.DrawPolygonList(poly.astype(int))

    def _triangle_down(self, dc, coords, size=1):
        shape = [(-2.5 * size, -1.44 * size), (2.5 * size, -1.44 * size),
                 (0.0, 2.88 * size)]
        poly = np.repeat(coords, 3)
        poly.shape = (len(coords), 3, 2)
        poly += shape
        dc.DrawPolygonList(poly.astype(int))

    def _cross(self, dc, coords, size=1):
        fact = 2.5 * size
        for f in [[-fact, -fact, fact, fact], [-fact, fact, fact, -fact]]:
            lines = np.concatenate((coords, coords), axis=1) + f
            dc.DrawLineList(lines.astype(int))

    def _plus(self, dc, coords, size=1):
        fact = 2.5 * size
        for f in [[-fact, 0, fact, 0], [0, -fact, 0, fact]]:
            lines = np.concatenate((coords, coords), axis=1) + f
            dc.DrawLineList(lines.astype(int))

    def _text(self, dc, coords, size=1):
        """Added by rmj 14.05.07"""
        _ = size
        dc.SetTextForeground(self.attributes['text_colour'])
        dc.DrawTextList(self.attributes['labels'], coords)

    def _crosshair(self, dc, coords):
        dc.CrossHair(coords[0], coords[1])


class PlotGraphics:
    """Container to hold PolyXXX objects and graph labels
        - All methods except __init__ are private.
    """

    def __init__(self, objects, title='', xLabel='', yLabel='',
                 xTickLabels=None):
        """Creates PlotGraphics object
        objects - list of PolyXXX objects to make graph
        title - title shown at top of graph
        xLabel - label shown on x-axis
        yLabel - label shown on y-axis
        """
        if type(objects) not in [list, tuple]:
            raise TypeError("objects argument should be list or tuple")

        self.printer_scale = None
        self.objects = objects
        self.title = title
        self.xLabel = xLabel
        self.yLabel = yLabel
        self.xTickLabels = xTickLabels

    def set_log_scale(self, logscale):
        if type(logscale) != tuple:
            raise TypeError(
                'logscale must be a tuple of bools, e.g. (False, False)')
        if len(self.objects) == 0:
            return
        for o in self.objects:
            o.set_log_scale(logscale)

    def bounding_box(self):
        p1, p2 = self.objects[0].bounding_box()
        for o in self.objects[1:]:
            p1o, p2o = o.bounding_box()
            p1 = np.minimum(p1, p1o)
            p2 = np.maximum(p2, p2o)
        return p1, p2

    def scale_shift(self, scale=(1, 1), shift=(0, 0)):
        for o in self.objects:
            o.scale_shift(scale, shift)

    def set_printer_scale(self, scale):
        """Thickens up lines and markers only for printing"""
        self.printer_scale = scale

    def set_xlabel(self, xLabel=''):
        """Set the X axis label on the graph"""
        self.xLabel = xLabel

    def set_ylabel(self, yLabel=''):
        """Set the Y axis label on the graph"""
        self.yLabel = yLabel

    def set_title(self, title=''):
        """Set the title at the top of graph"""
        self.title = title

    def get_xlabel(self):
        """Get x axis label string"""
        return self.xLabel

    def get_ylabel(self):
        """Get y axis label string"""
        return self.yLabel

    def get_title(self, title=''):
        """Get the title at the top of graph"""
        _ = title
        return self.title

    def get_xtick_label(self):
        """Get x axis tick label list"""
        return self.xTickLabels

    def draw(self, dc):
        for o in self.objects:
            o.draw(dc, self.printer_scale)

    def get_sym_extent(self, printer_scale):
        """Get max width and height of lines and markers symbols for legend"""
        symExt = self.objects[0].get_sym_extent(printer_scale)
        for o in self.objects[1:]:
            oSymExt = o.get_sym_extent(printer_scale)
            symExt = np.maximum(symExt, oSymExt)
        return symExt

    def get_legend_names(self):
        """Returns list of legend names"""
        lst = [None] * len(self)
        for i in range(len(self)):
            lst[i] = self.objects[i].get_legend()
        return lst

    def __len__(self):
        return len(self.objects)

    def __getitem__(self, item):
        return self.objects[item]


# -------------------------------------------------------------------------------
# Main window that you will want to import into your application.

class PlotCanvas(wx.Panel):
    """
    Subclass of a wx.Panel which holds two scrollbars and the actual
    plotting canvas (self.canvas). It allows for simple general plotting
    of data with zoom, labels, and automatic axis scaling.

    """
    def __init__(self, parent, id_=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name="plotCanvas"):
        """Constructs a panel, which can be a child of a frame or
        any other non-control window"""

        wx.Panel.__init__(self, parent, id_, pos, size, style, name)

        sizer = wx.FlexGridSizer(2, 2, 0, 0)
        self.canvas = wx.Window(self, -1)
        self.sb_vert = wx.ScrollBar(self, -1, style=wx.SB_VERTICAL)
        self.sb_vert.SetScrollbar(0, 1000, 1000, 1000)
        self.sb_hor = wx.ScrollBar(self, -1, style=wx.SB_HORIZONTAL)
        self.sb_hor.SetScrollbar(0, 1000, 1000, 1000)

        sizer.Add(self.canvas, 1, wx.EXPAND)
        sizer.Add(self.sb_vert, 0, wx.EXPAND)
        sizer.Add(self.sb_hor, 0, wx.EXPAND)
        sizer.Add((0, 0))

        sizer.AddGrowableRow(0, 1)
        sizer.AddGrowableCol(0, 1)

        self.sb_vert.Show(False)
        self.sb_hor.Show(False)

        self.SetSizer(sizer)
        self.Fit()

        self.border = (1, 1)

        self.SetBackgroundColour("white")

        # Create some mouse events for zooming
        self.canvas.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        self.canvas.Bind(wx.EVT_LEFT_UP, self.on_mouse_left_up)
        self.canvas.Bind(wx.EVT_MOTION, self.on_motion)
        self.canvas.Bind(wx.EVT_LEFT_DCLICK, self.on_mouse_double_click)
        self.canvas.Bind(wx.EVT_RIGHT_DOWN, self.on_mouse_right_down)

        # create mouse event for contextual menu
        self.canvas.Bind(wx.EVT_RIGHT_UP, self.on_mouse_right_up)

        # scrollbar events
        self.Bind(wx.EVT_SCROLL_THUMBTRACK, self.on_scroll)
        self.Bind(wx.EVT_SCROLL_PAGEUP, self.on_scroll)
        self.Bind(wx.EVT_SCROLL_PAGEDOWN, self.on_scroll)
        self.Bind(wx.EVT_SCROLL_LINEUP, self.on_scroll)
        self.Bind(wx.EVT_SCROLL_LINEDOWN, self.on_scroll)

        # set curser as cross-hairs
        self.canvas.SetCursor(wx.CROSS_CURSOR)
        self.HandCursor = wx.Cursor(get_hand_img())
        self.GrabHandCursor = wx.Cursor(get_grab_img())
        self.MagCursor = wx.Cursor(get_mag_img())

        # Things for printing
        self.print_data = wx.PrintData()
        self.print_data.SetPaperId(wx.PAPER_LETTER)
        self.print_data.SetOrientation(wx.LANDSCAPE)
        self.pageSetupData = wx.PageSetupDialogData()
        self.pageSetupData.SetMarginBottomRight((25, 25))
        self.pageSetupData.SetMarginTopLeft((25, 25))
        self.pageSetupData.SetPrintData(self.print_data)
        self.printer_scale = 1
        self.prnt = parent

        self.xSpec = None
        self.ySpec = None
        self._Buffer = None

        # scrollbar variables
        self._sb_ignore = False
        self._adjustingSB = False
        self._sb_xfullrange = []
        self._sb_yfullrange = []
        self._sb_xunit = 0
        self._sb_yunit = 0

        self._interEnabled = False
        self._interXlims = (0, 0)

        self._dragEnabled = False
        self._screenCoordinates = np.array([0.0, 0.0])

        self._logscale = (False, False)

        # Zooming variables
        self._zoomInFactor = 0.5
        self._zoomOutFactor = 2
        self._zoomCorner1 = np.array([0.0, 0.0])  # left mouse down corner
        self._zoomCorner2 = np.array([0.0, 0.0])  # left mouse up corner
        self._zoom_enabled = False
        self._hasDragged = False
        self._justDragged = False

        # Drawing Variables
        self.last_draw = None
        self._pointScale = 1
        self._pointShift = 0
        self._xSpec = 'auto'
        self._ySpec = 'auto'
        self._gridEnabled = False
        self._legendEnabled = False

        self.preview = None

        # Fonts
        self._fontCache = {}
        self._fontSizeAxis = 10
        self._fontSizeTitle = 15
        self._fontSizeLegend = 7

        # pointLabels
        self._pointLabelEnabled = False
        self.last_PointLabel = None
        self._pointLabelFunc = None
        self.canvas.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)

        self._useScientificNotation = False

        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        self.canvas.Bind(wx.EVT_SIZE, self.on_size)
        # on_size called to make sure the buffer is initialized.
        # This might result in on_size getting called twice on some
        # platforms at initialization, but little harm done.
        self.on_size(None)  # sets the initial size based on client size

        self._gridColour = wx.Colour('black')

    def set_cursor(self, cursor):
        self.canvas.SetCursor(cursor)

    def get_grid_colour(self):
        return self._gridColour

    def set_grid_colour(self, colour):
        if isinstance(colour, wx.Colour):
            self._gridColour = colour
        else:
            self._gridColour = wx.Colour(colour)

    # save_file
    def save_file(self, filename=''):
        """Saves the file to the type specified in the extension. If no file
        name is specified a dialog box is provided.  Returns True if sucessful,
        otherwise False.
        
        .bmp  Save a Windows bitmap file.
        .xbm  Save an X bitmap file.
        .xpm  Save an XPM bitmap file.
        .png  Save a Portable Network Graphics file.
        .jpg  Save a Joint Photographic Experts Group file.

        """
        ftypes = ['bmp', 'xbm', 'xpm', 'png', 'jpg']

        if filename[-3:].lower() not in ftypes:
            ftext = "BMP files (*.bmp)|*.bmp|XBM files (*.xbm)|*.xbm|" \
                     "XPM file (*.xpm)|*.xpm|PNG files (*.png)|*.png|" \
                     "JPG files (*.jpg)|*.jpg"
            msg = "Choose a file with extension bmp, gif, xbm, xpm, png, or jpg"

            dlg1 = wx.FileDialog(self, msg, ".", "", ftext,
                                 wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
            try:
                while 1:
                    if dlg1.ShowModal() == wx.ID_OK:
                        filename = dlg1.GetPath()
                        # Check for proper exension
                        if filename[-3:].lower() not in ftypes:
                            dlg2 = wx.MessageDialog(self,
                                                    'File name extension\n'
                                                    'must be one of\n'
                                                    ', '.join(ftypes),
                                                    'File Name Error',
                                                    wx.OK | wx.ICON_ERROR)
                            try:
                                dlg2.ShowModal()
                            finally:
                                dlg2.Destroy()
                        else:
                            break  # now save file
                    else:  # exit without saving
                        return False
            finally:
                dlg1.Destroy()

        # File name has required extension
        ftype = filename[-3:].lower()
        if ftype == "bmp":
            tp = wx.BITMAP_TYPE_BMP   # Save a Windows bitmap file.
        elif ftype == "xbm":
            tp = wx.BITMAP_TYPE_XBM   # Save an X bitmap file.
        elif ftype == "xpm":
            tp = wx.BITMAP_TYPE_XPM   # Save an XPM bitmap file.
        elif ftype == "jpg":
            tp = wx.BITMAP_TYPE_JPEG  # Save a JPG file.
        else:
            tp = wx.BITMAP_TYPE_PNG   # Save a PNG file.
        # Save Bitmap
        res = self._Buffer.SaveFile(filename, tp)
        return res

    def page_setup(self):
        """Brings up the page setup dialog"""
        data = self.pageSetupData
        data.SetPrintData(self.print_data)
        dlg = wx.PageSetupDialog(self.prnt, data)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetPageSetupData()  # returns wx.PageSetupDialogData
                # updates page parameters from dialog
                self.pageSetupData.SetMarginBottomRight(
                    data.GetMarginBottomRight())
                self.pageSetupData.SetMarginTopLeft(data.GetMarginTopLeft())
                self.pageSetupData.SetPrintData(data.GetPrintData())
                self.print_data = wx.PrintData(
                    data.GetPrintData())  # updates print_data
        finally:
            dlg.Destroy()

    def printout(self, paper=None):
        """Print current plot."""
        if paper is not None:
            self.print_data.SetPaperId(paper)
        pdd = wx.PrintDialogData(self.print_data)
        printer = wx.Printer(pdd)
        out = PlotPrintout(self)
        print_ok = printer.Print(self.prnt, out)
        if print_ok:
            self.print_data = wx.PrintData(
                printer.GetPrintDialogData().GetPrintData())
        out.Destroy()

    def print_preview(self):
        """Print-preview current plot."""
        printout = PlotPrintout(self)
        printout2 = PlotPrintout(self)
        self.preview = wx.PrintPreview(printout, printout2, self.print_data)
        if not self.preview.Ok():
            wx.MessageDialog(self,
                             "Print Preview failed.\n"
                             "Check that default printer is configured\n",
                             "Print error", wx.OK | wx.CENTRE).ShowModal()
        self.preview.SetZoom(40)
        # search up tree to find frame instance
        frameInst = self
        while not isinstance(frameInst, wx.Frame):
            frameInst = frameInst.GetParent()
        frame = wx.PreviewFrame(self.preview, frameInst, "Preview")
        frame.Initialize()
        frame.SetPosition(self.GetPosition())
        frame.SetSize((600, 550))
        frame.Centre(wx.BOTH)
        frame.Show(True)

    def set_log_scale(self, logscale):
        if type(logscale) != tuple:
            raise TypeError(
                'logscale must be a tuple of bools, e.g. (False, False)')
        if self.last_draw is not None:
            graphics, xAxis, yAxis = self.last_draw
            graphics.set_log_scale(logscale)
            self.last_draw = (graphics, None, None)
        self.xSpec = 'min'
        self.ySpec = 'min'
        self._logscale = logscale

    def get_log_scale(self):
        return self._logscale

    def font_size_axis(self, point=10):
        """Set the tick and axis label font size (default is 10 point)"""
        self._fontSizeAxis = point

    def get_font_size_axis(self):
        """Get current tick and axis label font size in points"""
        return self._fontSizeAxis

    def font_size_title(self, point=15):
        """Set Title font size (default is 15 point)"""
        self._fontSizeTitle = point

    def get_font_size_title(self):
        """Get current Title font size in points"""
        return self._fontSizeTitle

    def font_size_legend(self, point=7):
        """Set Legend font size (default is 7 point)"""
        self._fontSizeLegend = point

    def get_font_size_legend(self):
        """Get current Legend font size in points"""
        return self._fontSizeLegend

    def set_show_scrollbars(self, value):
        """Set True to show scrollbars"""
        if value not in [True, False]:
            raise TypeError("Value should be True or False")
        if value == self.get_show_scrollbars():
            return
        self.sb_vert.Show(value)
        self.sb_hor.Show(value)
        wx.CallAfter(self.Layout)

    def get_show_scrollbars(self):
        """Set True to show scrollbars"""
        return self.sb_vert.IsShown()

    def set_use_scientific_notation(self, useScientificNotation):
        self._useScientificNotation = useScientificNotation

    def get_use_scientific_notation(self):
        return self._useScientificNotation

    def enable_drag(self, value):
        """Set True to enable drag."""
        if value not in [True, False]:
            raise TypeError("Value should be True or False")
        if value:
            if self.get_enable_zoom():
                self.enable_zoom(False)
            if self.get_enable_interactive():
                self.enable_interactive(False)
            self.set_cursor(self.HandCursor)
        else:
            self.set_cursor(wx.CROSS_CURSOR)
        self._dragEnabled = value

    def get_enable_drag(self):
        return self._dragEnabled

    def enable_interactive(self, value):
        """Set True to enable interactive mode - RMJ 03/2008."""
        if value not in [True, False]:
            raise TypeError("Value should be True or False")
        if value:
            if self.get_enable_zoom():
                self.enable_zoom(False)
            if self.get_enable_drag():
                self.enable_drag(False)
            self.set_cursor(wx.StockCursor(wx.CURSOR_PENCIL))
        else:
            self.set_cursor(wx.CROSS_CURSOR)
        self._interEnabled = value

    def get_enable_interactive(self):
        return self._interEnabled

    def get_inter_xlims(self):
        return self._interXlims

    def enable_zoom(self, value):
        """Set True to enable zooming."""
        if value not in [True, False]:
            raise TypeError("Value should be True or False")
        if value:
            if self.get_enable_drag():
                self.enable_drag(False)
            if self.get_enable_interactive():
                self.enable_interactive(False)
            self.set_cursor(self.MagCursor)
        else:
            self.set_cursor(wx.CROSS_CURSOR)
        self._zoom_enabled = value

    def get_enable_zoom(self):
        """True if zooming enabled."""
        return self._zoom_enabled

    def enable_grid(self, value):
        """Set True to enable grid."""
        if value not in [True, False, 'Horizontal', 'Vertical']:
            raise TypeError(
                "Value should be True, False, Horizontal or Vertical")
        self._gridEnabled = value
        self.redraw()

    def get_enable_grid(self):
        """True if grid enabled."""
        return self._gridEnabled

    def enable_legend(self, value):
        """Set True to enable legend."""
        if value not in [True, False]:
            raise TypeError("Value should be True or False")
        self._legendEnabled = value
        self.redraw()

    def get_enable_legend(self):
        """True if Legend enabled."""
        return self._legendEnabled

    def enable_point_label(self, value):
        """Set True to enable pointLabel."""
        if value not in [True, False]:
            raise TypeError("Value should be True or False")
        self._pointLabelEnabled = value
        self.redraw()  # will erase existing pointLabel if present
        self.last_PointLabel = None

    def get_enable_point_label(self):
        """True if pointLabel enabled."""
        return self._pointLabelEnabled

    def set_point_label_func(self, func):
        """Sets the function with custom code for pointLabel drawing
            ******** more info needed ***************
        """
        self._pointLabelFunc = func

    def get_point_label_func(self):
        """Returns pointLabel Drawing Function"""
        return self._pointLabelFunc

    def reset(self):
        """Unzoom the plot."""
        self.last_PointLabel = None  # reset pointLabel
        if self.last_draw is not None:
            self._draw(self.last_draw[0])

    def scroll_right(self, units):
        """Move view right number of axis units."""
        self.last_PointLabel = None  # reset pointLabel
        if self.last_draw is not None:
            graphics, xAxis, yAxis = self.last_draw
            xAxis = (xAxis[0] + units, xAxis[1] + units)
            self._draw(graphics, xAxis, yAxis)

    def scroll_up(self, units):
        """Move view up number of axis units."""
        self.last_PointLabel = None  # reset pointLabel
        if self.last_draw is not None:
            graphics, xAxis, yAxis = self.last_draw
            yAxis = (yAxis[0] + units, yAxis[1] + units)
            self._draw(graphics, xAxis, yAxis)

    def get_xy(self, event):
        """Wrapper around _get_xy, which handles log scales"""
        x, y = self._get_xy(event)
        if self.get_log_scale()[0]:
            x = np.power(10, x)
        if self.get_log_scale()[1]:
            y = np.power(10, y)
        return x, y

    def _get_xy(self, event):
        """Takes a mouse event and returns the XY user axis values."""
        x, y = self.position_screen_to_user(event.GetPosition())
        return x, y

    def position_user_to_screen(self, pntXY):
        """Converts User position to Screen Coordinates"""
        userPos = np.array(pntXY)
        x, y = userPos * self._pointScale + self._pointShift
        return x, y

    def position_screen_to_user(self, pntXY):
        """Converts Screen position to User Coordinates"""
        screenPos = np.array(pntXY)
        x, y = (screenPos - self._pointShift) / self._pointScale
        return x, y

    def set_xspec(self, dtype='auto'):
        """xSpec- defines x axis type. Can be 'none', 'min' or 'auto'
        where:
            'none' - shows no axis or tick mark values
            'min' - shows min bounding box values
            'auto' - rounds axis range to sensible values
            'udef' - user defined - added by RJ
        """
        self._xSpec = dtype

    def set_yspec(self, dtype='auto'):
        """ySpec- defines x axis type. Can be 'none', 'min' or 'auto'
        where:
            'none' - shows no axis or tick mark values
            'min' - shows min bounding box values
            'auto' - rounds axis range to sensible values
        """
        self._ySpec = dtype

    def get_xspec(self):
        """Returns current XSpec for axis"""
        return self._xSpec

    def get_yspec(self):
        """Returns current YSpec for axis"""
        return self._ySpec

    def get_x_max_range(self):
        xAxis = self._get_x_max_range()
        if self.get_log_scale()[0]:
            xAxis = np.power(10, xAxis)
        return xAxis

    def _get_x_max_range(self):
        """Returns (minX, maxX) x-axis range for displayed graph"""
        graphics = self.last_draw[0]
        p1, p2 = graphics.bounding_box()  # min, max points of graphics
        xAxis = self._axis_interval(self._xSpec, p1[0], p2[0])  # in user units
        return xAxis

    def get_y_max_range(self):
        yAxis = self._get_y_max_range()
        if self.get_log_scale()[1]:
            yAxis = np.power(10, yAxis)
        return yAxis

    def _get_y_max_range(self):
        """Returns (minY, maxY) y-axis range for displayed graph"""
        graphics = self.last_draw[0]
        p1, p2 = graphics.bounding_box()  # min, max points of graphics
        yAxis = self._axis_interval(self._ySpec, p1[1], p2[1])
        return yAxis

    def get_x_current_range(self):
        xAxis = self._get_x_current_range()
        if self.get_log_scale()[0]:
            xAxis = np.power(10, xAxis)
        return xAxis

    def _get_x_current_range(self):
        """Returns (minX, maxX) x-axis for currently displayed portion of graph"""
        return self.last_draw[1]

    def get_y_current_range(self):
        yAxis = self._get_y_current_range()
        if self.get_log_scale()[1]:
            yAxis = np.power(10, yAxis)
        return yAxis

    def _get_y_current_range(self):
        """Returns (minY, maxY) y-axis for currently displayed portion of graph"""
        return self.last_draw[2]

    def draw(self, graphics, xAxis=None, yAxis=None, dc=None):
        """Wrapper around _draw, which handles log axes"""

        graphics.set_log_scale(self.get_log_scale())

        # check Axis is either tuple or none
        if type(xAxis) not in [type(None), tuple]:
            raise TypeError(
                "xAxis should be None or (minX,maxX)" + str(type(xAxis)))
        if type(yAxis) not in [type(None), tuple]:
            raise TypeError(
                "yAxis should be None or (minY,maxY)" + str(type(xAxis)))

        # check case for axis = (a,b) where a==b caused by improper zooms
        if xAxis is not None:
            if xAxis[0] == xAxis[1]:
                return
            if self.get_log_scale()[0]:
                xAxis = np.log10(xAxis)
        if yAxis is not None:
            if yAxis[0] == yAxis[1]:
                return
            if self.get_log_scale()[1]:
                yAxis = np.log10(yAxis)
        self._draw(graphics, xAxis, yAxis, dc)

    def _draw(self, graphics, xAxis=None, yAxis=None, dc=None):
        """
        draw objects in graphics with specified x and y axis.
        graphics- instance of PlotGraphics with list of PolyXXX objects
        xAxis - tuple with (min, max) axis range to view
        yAxis - same as xAxis
        dc - drawing context - doesn't have to be specified.    
        If it's not, the offscreen buffer is used
        """

        if dc is None:
            # sets new dc and clears it 
            dc = wx.BufferedDC(wx.ClientDC(self.canvas), self._Buffer)
            dc.Clear()

        # dc.BeginDrawing()
        # dc.clear()

        # set font size for every thing but title and legend
        dc.SetFont(self._get_font(self._fontSizeAxis))

        # sizes axis to axis type, create lower left and upper right corners of plot
        if xAxis is None or yAxis is None:
            # One or both axis not specified in draw
            p1, p2 = graphics.bounding_box()  # min, max points of graphics
            if xAxis is None:
                xAxis = self._axis_interval(self._xSpec, p1[0],
                                            p2[0])  # in user units
            if yAxis is None:
                yAxis = self._axis_interval(self._ySpec, p1[1], p2[1])

            # Adjust bounding box for axis spec
            # lower left corner user scale (xmin,ymin)
            p1[0], p1[1] = xAxis[0], yAxis[0]
            # upper right corner user scale (xmax,ymax)
            p2[0], p2[1] = xAxis[1], yAxis[1]
        else:
            # Both axis specified in draw
            # lower left corner user scale (xmin,ymin)
            p1 = np.array([xAxis[0], yAxis[0]])
            # upper right corner user scale (xmax,ymax)
            p2 = np.array([xAxis[1], yAxis[1]])

        # saves most recent values
        self.last_draw = (graphics, np.array(xAxis), np.array(yAxis))

        # Get ticks and textExtents for axis if required
        if self._xSpec in ['auto', 'min']:
            xticks = self._xticks(xAxis[0], xAxis[1])
            # w h of x axis text last number on axis
            xTextExtent = dc.GetTextExtent(xticks[-1][1])

        elif self._xSpec == 'udef':
            # to set xticklabels for boxplot
            tickLabels, xticks = graphics.get_xtick_label(), []
            for xti in range(1, len(tickLabels) + 1):
                xticks.append((xti, tickLabels[xti - 1]))
            xTextExtent = dc.GetTextExtent(xticks[-1][1])

        # if self._xSpec == 'none'
        else:
            xticks = None
            xTextExtent = (0, 0)  # No text for ticks

        if self._ySpec != 'none':
            yticks = self._yticks(yAxis[0], yAxis[1])
            if self.get_log_scale()[1]:
                yTextExtent = dc.GetTextExtent('-2e-2')
            else:
                yTextExtentBottom = dc.GetTextExtent(yticks[0][1])
                yTextExtentTop = dc.GetTextExtent(yticks[-1][1])
                yTextExtent = (max(yTextExtentBottom[0], yTextExtentTop[0]),
                               max(yTextExtentBottom[1], yTextExtentTop[1]))
        else:
            yticks = None
            yTextExtent = (0, 0)  # No text for ticks

        # TextExtents for Title and Axis Labels
        titleWH, xLabelWH, yLabelWH = self._title_lables_wh(dc, graphics)

        # TextExtents for Legend
        legendBoxWH, legendSymExt, legendTextExt = self._legend_wh(dc, graphics)

        # room around graph area
        # use larger of number width or legend width
        rhsW = max(xTextExtent[0], legendBoxWH[0])
        lhsW = yTextExtent[0] + yLabelWH[1]
        bottomH = max(xTextExtent[1], yTextExtent[1] // 2) + xLabelWH[1]
        topH = yTextExtent[1] // 2 + titleWH[1]

        # make plot area smaller by text size
        textSize_scale = np.array([rhsW + lhsW, bottomH + topH])
        # shift plot area by this amount
        textSize_shift = np.array([lhsW, bottomH])

        # drawing title and labels text
        dc.SetFont(self._get_font(self._fontSizeTitle))
        titlex = int(self.plotbox_origin[0] + lhsW + (
                     self.plotbox_size[0] - lhsW - rhsW - titleWH[0]) / 2)
        titley = int(self.plotbox_origin[1] - self.plotbox_size[1])

        dc.DrawText(graphics.get_title(), titlex, titley)

        dc.SetFont(self._get_font(self._fontSizeAxis))
        xlabelx = int(self.plotbox_origin[0] + lhsW + (
                self.plotbox_size[0] - lhsW - rhsW) / 2 - xLabelWH[0] / 2)
        xlabely = int(self.plotbox_origin[1] - xLabelWH[1])

        dc.DrawText(graphics.get_xlabel(), xlabelx, xlabely)

        ylabelx = int(self.plotbox_origin[0])
        ylabely = int(self.plotbox_origin[1] - bottomH -
                      (self.plotbox_size[1] - bottomH - topH) / 2 +
                      yLabelWH[0] / 2)
        if graphics.get_ylabel():  # bug fix for Linux
            dc.DrawRotatedText(graphics.get_ylabel(), ylabelx, ylabely, 90)

        # drawing legend makers and text
        if self._legendEnabled:
            self._draw_legend(dc, graphics, rhsW, topH, legendBoxWH,
                              legendSymExt, legendTextExt)

        # allow for scaling and shifting plotted points
        scale = (self.plotbox_size - textSize_scale) / (
                p2 - p1) * np.array((1, -1))
        shift = -p1 * scale + self.plotbox_origin + textSize_shift * np.array(
            (1, -1))
        self._pointScale = scale  # make available for mouse events
        self._pointShift = shift
        self._draw_axes(dc, p1, p2, scale, shift, xticks, yticks)

        graphics.scale_shift(scale, shift)
        graphics.set_printer_scale(
            self.printer_scale)  # thicken up lines and markers if printing

        # set clipping area so drawing does not occur outside axis box
        ptx, pty, rectWidth, rectHeight = self._point_to_client(p1, p2)

        dc.SetClippingRegion(ptx, pty, rectWidth, rectHeight)
        # draw the lines and markers
        # start = _time.clock()
        graphics.draw(dc)
        # print "entire graphics drawing took: %f second"%(_time.clock() - start)
        # remove the clipping region
        dc.DestroyClippingRegion()
        # dc.EndDrawing()

        self._adjust_scrollbars()

    def redraw(self, dc=None):
        """redraw the existing plot."""
        if self.last_draw is not None:
            graphics, xAxis, yAxis = self.last_draw
            self._draw(graphics, xAxis, yAxis, dc)
            # added by rmj 15.05.07 to allow for copy
            # to clipboard
            try:
                return dc.Close()
            except AttributeError:
                return None

    def clear(self):
        """Erase the window."""
        self.last_PointLabel = None  # reset pointLabel
        dc = wx.BufferedDC(wx.ClientDC(self.canvas), self._Buffer)
        dc.Clear()
        self.last_draw = None

    def zoom(self, Center, Ratio):
        """ zoom on the plot.

            Centers on the X,Y coords given in Center
            Zooms by the Ratio = (Xratio, Yratio) given

        """
        self.last_PointLabel = None  # reset maker
        x, y = Center
        if self.last_draw is not None:
            (graphics, xAxis, yAxis) = self.last_draw
            w = (xAxis[1] - xAxis[0]) * Ratio[0]
            h = (yAxis[1] - yAxis[0]) * Ratio[1]
            xAxis = (x - w / 2, x + w / 2)
            yAxis = (y - h / 2, y + h / 2)
            self._draw(graphics, xAxis, yAxis)

    def get_closest_pnts(self, pntXY, pointScaled=True):
        """Returns list with
            [curveNumber, legend, index of closest point, pointXY, scaledXY, distance]
            list for each curve.
            Returns [] if no curves are being plotted.
            
            x, y in user coords
            if pointScaled == True based on screen coords
            if pointScaled == False based on user coords
        """
        if self.last_draw is None:
            # no graph available
            return []
        graphics, xAxis, yAxis = self.last_draw
        alist = []
        for curveNum, obj in enumerate(graphics):
            # check there are points in the curve
            if len(obj.points) == 0:
                continue  # go to next obj
            # [curveNmbr, legnd, idx closest pnt, pntXY, scaledXY, distance]
            close_point = obj.get_closest_pnt(pntXY, pointScaled)
            cn = [curveNum] + [obj.get_legend()] + close_point
            alist.append(cn)
        return alist

    def get_closest_pnt(self, pntXY, pointScaled=True):
        """Returns list with
            [curveNumber, legend, index of closest point, pointXY, scaledXY, distance]
            list for only the closest curve.
            Returns [] if no curves are being plotted.
            
            x, y in user coords
            if pointScaled == True based on screen coords
            if pointScaled == False based on user coords
        """
        # closest points on screen based on screen scaling (pointScaled= True)
        # list [curveNumber, index, pointXY, scaledXY, distance] for each curve
        closestPts = self.get_closest_pnts(pntXY, pointScaled)
        if not closestPts:
            return []  # no graph present
        # find one with least distance
        dists = [c[-1] for c in closestPts]
        mdist = min(dists)  # Min dist
        i = dists.index(mdist)  # index for min dist
        return closestPts[i]  # this is the closest point on closest curve

    GetClosetPoint = get_closest_pnt

    def update_point_label(self, mDataDict):
        """Updates the pointLabel point on screen with data contained in
            mDataDict.

            mDataDict will be passed to your function set by
            set_point_label_func.  It can contain anything you
            want to display on the screen at the scaledXY point
            you specify.

            This function can be called from parent window with onClick,
            onMotion events etc.            
        """
        if self.last_PointLabel is not None:
            # compare pointXY
            if np.sometrue(
                    mDataDict["pointXY"] != self.last_PointLabel["pointXY"]):
                # closest changed
                self._draw_point_label(self.last_PointLabel)  # erase old
                self._draw_point_label(mDataDict)  # plot new
        else:
            # just plot new with no erase
            self._draw_point_label(mDataDict)  # plot new
        # save for next erase
        self.last_PointLabel = mDataDict

    # event handlers **********************************
    # noinspection PyTypeChecker
    def on_motion(self, event):
        if self._zoom_enabled and event.LeftIsDown():
            if self._hasDragged:
                self._draw_box(self._zoomCorner1,
                               self._zoomCorner2)  # remove old
            else:
                self._hasDragged = True
            self._zoomCorner2[0], self._zoomCorner2[1] = self._get_xy(event)
            self._draw_box(self._zoomCorner1,
                           self._zoomCorner2)  # add new
        elif self._dragEnabled and event.LeftIsDown():
            coordinates = event.GetPosition()
            newpos, oldpos = map(np.array, map(self.position_screen_to_user,
                                               [coordinates,
                                                self._screenCoordinates]))
            dist = newpos - oldpos
            self._screenCoordinates = coordinates
            if self.last_draw is not None:
                graphics, xAxis, yAxis = self.last_draw
                yAxis -= dist[1]
                xAxis -= dist[0]
                self._draw(graphics, xAxis, yAxis)
        elif self._interEnabled and event.LeftIsDown():
            graphics, xAxis, yAxis = self.last_draw
            self._screenCoordinates = event.GetPosition()
            xy = self.position_screen_to_user(self._screenCoordinates)
            if len(graphics.objects) == 2:
                graphics.objects.extend([PolyLine([[xy[0], yAxis[0]],
                                                   [xy[0], yAxis[1]]],
                                                  colour='red')])
            else:
                graphics.objects[2] = PolyLine([[xy[0], yAxis[0]],
                                                [xy[0], yAxis[1]]],
                                               colour='red')
                self._draw(graphics, xAxis, yAxis)
            self._hasDragged = True

    # noinspection PyTypeChecker
    def on_mouse_left_down(self, event):
        self._zoomCorner1[0], self._zoomCorner1[1] = self._get_xy(event)
        self._screenCoordinates = np.array(event.GetPosition())
        if self._dragEnabled:
            self.set_cursor(self.GrabHandCursor)
            self.canvas.CaptureMouse()
        if self._interEnabled:  # added by rmj 03/2008
            if self.last_draw is not None:
                graphics, xAxis, yAxis = self.last_draw
                xy = self.position_screen_to_user(self._screenCoordinates)
                graphics.objects.append(PolyLine([[xy[0], yAxis[0]],
                                                  [xy[0], yAxis[1]]],
                                                 colour='red'))
                self._draw(graphics, xAxis, yAxis)

    # noinspection PyTypeChecker, PyProtectedMember
    def on_mouse_left_up(self, event):
        if self._zoom_enabled:
            self._justDragged = False
            if self._hasDragged:
                # remove old
                self._draw_box(self._zoomCorner1, self._zoomCorner2)
                self._zoomCorner2[0], self._zoomCorner2[1] = self._get_xy(event)
                self._hasDragged = False  # reset flag
                self._justDragged = True
                minX, minY = np.minimum(self._zoomCorner1, self._zoomCorner2)
                maxX, maxY = np.maximum(self._zoomCorner1, self._zoomCorner2)
                # reset pointLabel
                self.last_PointLabel = None
                if self.last_draw is not None:
                    self._draw(self.last_draw[0], xAxis=(minX, maxX),
                               yAxis=(minY, maxY), dc=None)
        if self._dragEnabled:
            self.set_cursor(self.HandCursor)
            if self.canvas.HasCapture():
                self.canvas.ReleaseMouse()
        if self._interEnabled:
            graphics, xAxis, yAxis = self.last_draw
            if self._hasDragged:
                self._screenCoordinates = event.GetPosition()
                xy = self.position_screen_to_user(self._screenCoordinates)
                graphics.objects.append(PolyLine([[xy[0], yAxis[0]],
                                                  [xy[0], yAxis[1]]],
                                                 colour='red'))
                self._draw(graphics, xAxis, yAxis)
                self._hasDragged = False  # reset flag
                self._interXlims = (graphics.objects[1]._points[0, 0],
                                    graphics.objects[2]._points[0, 0])
                # instigate the calculation stuff in pychem
                self.prnt.prnt.do_peak_calculations()
            else:
                graphics.objects = graphics.objects[0:len(graphics.objects) - 1]
                self._draw(graphics, xAxis, yAxis)
            self.enable_zoom(True)

    def on_mouse_double_click(self, _):
        if self._zoom_enabled:
            # Give a little time for the click to be totally finished
            # before (possibly) removing the scrollbars and trigering
            # size events, etc.
            wx.FutureCall(200, self.reset)

    def on_mouse_right_down(self, event):
        if self._zoom_enabled:
            X, Y = self._get_xy(event)
            self.zoom((X, Y), (self._zoomOutFactor, self._zoomOutFactor))

    def on_mouse_right_up(self, event):
        pass

    def on_paint(self, _):
        # All that is needed here is to draw the buffer to screen
        if self.last_PointLabel is not None:
            self._draw_point_label(self.last_PointLabel)  # erase old
            self.last_PointLabel = None
        # noinspection PyUnusedLocal
        dc = wx.BufferedPaintDC(self.canvas, self._Buffer)

    def on_size(self, _):
        # The Buffer init is done here, to make sure the buffer is always
        # the same size as the Window
        Size = self.canvas.GetClientSize()
        Size.width = max(1, Size.width)
        Size.height = max(1, Size.height)

        # Make new offscreen bitmap: this bitmap will always have the
        # current drawing in it, so it can be used to save the image to
        # a file, or whatever.
        self._Buffer = wx.Bitmap(Size.width, Size.height)
        self._set_size()

        self.last_PointLabel = None  # reset pointLabel

        if self.last_draw is None:
            self.clear()
        else:
            graphics, xSpec, ySpec = self.last_draw
            self._draw(graphics, xSpec, ySpec)

    def on_leave(self, _):
        """Used to erase pointLabel when mouse outside window"""
        if self.last_PointLabel is not None:
            self._draw_point_label(self.last_PointLabel)  # erase old
            self.last_PointLabel = None

    def on_scroll(self, evt):
        if not self._adjustingSB:
            self._sb_ignore = True
            sbpos = evt.GetPosition()
            try:
                if evt.GetOrientation() == wx.VERTICAL:
                    fullrange, pagesize = self.sb_vert.GetRange(), self.sb_vert.GetPageSize()
                    sbpos = fullrange - pagesize - sbpos
                    dist = sbpos * self._sb_yunit - (
                            self._get_y_current_range()[0] -
                            self._sb_yfullrange[0])
                    self.scroll_up(dist)

                if evt.GetOrientation() == wx.HORIZONTAL:
                    dist = sbpos * self._sb_xunit - (
                            self._get_x_current_range()[0] -
                            self._sb_xfullrange[0])
                    self.scroll_right(dist)
            except Exception:
                raise
                # pass

    # Private Methods **************************************************
    def _set_size(self, width=None, height=None):
        """DC width and height."""
        if width is None:
            (self.width, self.height) = self.canvas.GetClientSize()
        else:
            self.width, self.height = width, height
        plotbox_size = 0.97 * np.array([self.width, self.height])
        xo = 0.5 * (self.width - plotbox_size[0])
        yo = self.height - 0.5 * (self.height - plotbox_size[1])
        plotbox_origin = np.array([xo, yo])

        self.plotbox_size = plotbox_size.astype(int)
        self.plotbox_origin = plotbox_origin.astype(int)

    def _set_printer_scale(self, scale):
        """Used to thicken lines and increase marker size for print out."""
        # line thickness on printer is very thin at 600 dot/in. Markers small
        self.printer_scale = scale

    def _print_draw(self, printDC):
        """Used for printing."""
        if self.last_draw is not None:
            graphics, xSpec, ySpec = self.last_draw
            self._draw(graphics, xSpec, ySpec, printDC)

    def _draw_point_label(self, mDataDict):
        """Draws and erases pointLabels"""
        width = self._Buffer.GetWidth()
        height = self._Buffer.GetHeight()
        tmp_Buffer = wx.Bitmap(width, height)
        dcs = wx.MemoryDC()
        dcs.SelectObject(tmp_Buffer)
        dcs.Clear()
        # dcs.BeginDrawing()
        self._pointLabelFunc(dcs, mDataDict)  # custom user pointLabel function
        # dcs.EndDrawing()

        dc = wx.ClientDC(self.canvas)
        # this will erase if called twice
        dc.Blit(0, 0, width, height, dcs, 0, 0, wx.EQUIV)  # (NOT src) XOR dst

    def _draw_legend(self, dc, graphics, rhsW, topH, legendBoxWH, legendSymExt,
                     legendTextExt):
        """Draws legend symbols and text"""
        # top right hand corner of graph box is ref corner
        trhc = self.plotbox_origin + (self.plotbox_size - [rhsW, topH]) * [1,
                                                                           -1]
        legendLHS = .091 * legendBoxWH[
            0]  # border space between legend sym and graph box
        lineHeight = max(legendSymExt[1], legendTextExt[
            1]) * 1.1  # 1.1 used as space between lines
        dc.SetFont(self._get_font(self._fontSizeLegend))
        cntLineHeight = 0
        for i in range(len(graphics)):
            o = graphics[i]
            # added by rmj 09.07.07 - any legend entries without label not plotted
            if graphics.get_legend_names()[i] not in ['']:
                s = cntLineHeight * lineHeight
                if isinstance(o, PolyMarker):
                    # draw marker with legend
                    pnt = (trhc[0] + legendLHS + legendSymExt[0] / 2.,
                           trhc[1] + s + lineHeight / 2.)
                    o.draw(dc, self.printer_scale, coord=np.array([pnt]))
                elif isinstance(o, PolyLine):
                    # draw line with legend
                    pnt1 = (trhc[0] + legendLHS, trhc[1] + s + lineHeight / 2.)
                    pnt2 = (trhc[0] + legendLHS + legendSymExt[0],
                            trhc[1] + s + lineHeight / 2.)
                    o.draw(dc, self.printer_scale,
                           coord=np.array([pnt1, pnt2]))
                else:
                    raise TypeError(
                        "object is neither PolyMarker or PolyLine instance")
                # draw legend txt
                px = int(trhc[0] + legendLHS + legendSymExt[0])
                py = int(trhc[1] + s + lineHeight / 2 - legendTextExt[1] / 2)

                dc.DrawText(o.get_legend(), px, py)
                cntLineHeight += 1
        dc.SetFont(self._get_font(self._fontSizeAxis))  # reset

    def _title_lables_wh(self, dc, graphics):
        """Draws Title and labels and returns width and height for each"""
        # TextExtents for Title and Axis Labels
        dc.SetFont(self._get_font(self._fontSizeTitle))
        title = graphics.get_title()
        titleWH = dc.GetTextExtent(title)
        dc.SetFont(self._get_font(self._fontSizeAxis))
        xLabel, yLabel = graphics.get_xlabel(), graphics.get_ylabel()
        xLabelWH = dc.GetTextExtent(xLabel)
        yLabelWH = dc.GetTextExtent(yLabel)
        return titleWH, xLabelWH, yLabelWH

    def _legend_wh(self, dc, graphics):
        """Returns the size in screen units for legend box"""
        if not self._legendEnabled:
            legendBoxWH = symExt = txtExt = (0, 0)
        else:
            # find max symbol size
            symExt = graphics.get_sym_extent(self.printer_scale)
            # find max legend text extent
            dc.SetFont(self._get_font(self._fontSizeLegend))
            txtList = graphics.get_legend_names()
            txtExt = dc.GetTextExtent(txtList[0])
            for txt in graphics.get_legend_names()[1:]:
                txtExt = np.maximum(txtExt, dc.GetTextExtent(txt))
            maxW = symExt[0] + txtExt[0]
            maxH = max(symExt[1], txtExt[1])
            # padding .1 for lhs of legend box and space between lines
            maxW = maxW * 1.1
            maxH = maxH * 1.1 * len(txtList)
            dc.SetFont(self._get_font(self._fontSizeAxis))
            legendBoxWH = (maxW, maxH)
        return legendBoxWH, symExt, txtExt

    def _draw_box(self, corner1, corner2):
        """Draws/erases rect box from corner1 to corner2"""
        ptx, pty, rectWidth, rectHeight = self._point_to_client(corner1,
                                                                corner2)
        # draw rectangle
        dc = wx.ClientDC(self.canvas)
        # dc.BeginDrawing()
        dc.SetPen(wx.Pen(wx.BLACK))
        dc.SetBrush(wx.Brush(wx.WHITE, wx.BRUSHSTYLE_TRANSPARENT))
        dc.SetLogicalFunction(wx.INVERT)
        dc.DrawRectangle(ptx, pty, rectWidth, rectHeight)
        dc.SetLogicalFunction(wx.COPY)
        # dc.EndDrawing()

    def _get_font(self, size):
        """Take font size, adjusts if printing and returns wx.Font"""
        s = size * self.printer_scale
        of = self.GetFont()
        # Linux speed up to get font from cache rather than X font server
        key = (int(s), of.GetFamily(), of.GetStyle(), of.GetWeight())
        font = self._fontCache.get(key, None)
        if font:
            return font  # yeah! cache hit
        else:
            font = wx.Font(int(s), of.GetFamily(), of.GetStyle(),
                           of.GetWeight())
            self._fontCache[key] = font
            return font

    def _point_to_client(self, corner1, corner2):
        """Converts user point coords to client screen coords x,y,width,height

        Must return integers to prevent deprecation warning with wx.dc
        DrawLine, DrawText methods.

        """
        c1 = np.array(corner1)
        c2 = np.array(corner2)

        # convert to screen coords
        pt1 = c1 * self._pointScale + self._pointShift
        pt2 = c2 * self._pointScale + self._pointShift
        # make height and width positive
        pul = np.minimum(pt1, pt2).astype(int)      # Upper left corner
        plr = np.maximum(pt1, pt2).astype(int)      # Lower right corner
        rectWidth, rectHeight = plr - pul
        ptx, pty = pul
        return ptx, pty, rectWidth, rectHeight

    # noinspection PyMethodMayBeStatic
    def _axis_interval(self, spec, lower, upper):
        """Returns sensible axis range for given spec"""
        if spec in ['none', 'min']:
            if lower == upper:
                return lower - 0.5, upper + 0.5
            else:
                return lower, upper
        elif spec in ['udef']:
            return lower - 0.5, upper + 0.5
        elif spec == 'auto':
            range_ = upper - lower
            if range_ == 0.:
                return lower - 0.5, upper + 0.5
            log = np.log10(range_)
            power = np.floor(log)
            fraction = log - power
            if fraction <= 0.05:
                power = power - 1
            grid = 10. ** power
            lower = lower - lower % grid
            mod = upper % grid
            if mod != 0:
                upper = upper - mod + grid
            return lower, upper
        elif isinstance(spec, tuple):
            lower, upper = spec
            if lower <= upper:
                return lower, upper
            else:
                return upper, lower
        else:
            raise ValueError(str(spec) + ': illegal axis specification')

    def _draw_axes(self, dc, p1, p2, scale, shift, xticks, yticks):

        penWidth = self.printer_scale  # increases thickness for printing only
        dc.SetPen(wx.Pen(self._gridColour, penWidth))

        # set length of tick marks--long ones make grid
        if self._gridEnabled:
            x, y, width, height = self._point_to_client(p1, p2)
            if self._gridEnabled == 'Horizontal':
                yTickLength = width // 2 + 1
                xTickLength = 3 * self.printer_scale
            elif self._gridEnabled == 'Vertical':
                yTickLength = 3 * self.printer_scale
                xTickLength = height // 2 + 1
            else:
                yTickLength = width // 2 + 1
                xTickLength = height // 2 + 1
        else:
            yTickLength = 3 * self.printer_scale  # lengthens lines for printing
            xTickLength = 3 * self.printer_scale

        if self._xSpec != 'none':
            lower, upper = p1[0], p2[0]
            text = 1
            # miny, maxy and tick lengths
            for y, d in [(p1[1], -xTickLength), (p2[1], xTickLength)]:
                a1 = scale * np.array([lower, y]) + shift
                a2 = scale * np.array([upper, y]) + shift

                a1 = a1.astype(int)
                a2 = a2.astype(int)
                # draws upper and lower axis line
                dc.DrawLine(a1[0], a1[1], a2[0], a2[1])

                for x, label in xticks:
                    pt = scale * np.array([x, y]) + shift

                    pt = pt.astype(int)
                    # draws tick mark d units
                    dc.DrawLine(pt[0], pt[1], pt[0], pt[1] + d)
                    if text:
                        dc.DrawText(label, pt[0], pt[1])
                text = 0  # axis values not drawn on top side

        if self._ySpec != 'none':
            lower, upper = p1[1], p2[1]
            text = 1
            h = dc.GetCharHeight()
            for x, d in [(p1[0], -yTickLength), (p2[0], yTickLength)]:
                a1 = scale * np.array([x, lower]) + shift
                a2 = scale * np.array([x, upper]) + shift

                a1 = a1.astype(int)
                a2 = a2.astype(int)
                dc.DrawLine(a1[0], a1[1], a2[0], a2[1])

                for y, label in yticks:
                    pt = scale * np.array([x, y]) + shift
                    px, py = pt.astype(int)
                    dc.DrawLine(px, py, px - d, py)

                    if text:
                        px = int(pt[0] - dc.GetTextExtent(label)[0])
                        py = int(pt[1] - 0.5 * h)
                        dc.DrawText(label, px, py)
                text = 0    # axis values not drawn on right side

    def _xticks(self, *args):
        if self._logscale[0]:
            return self._logticks(*args)
        else:
            return self._ticks(*args)

    def _yticks(self, *args):
        if self._logscale[1]:
            return self._logticks(*args)
        else:
            return self._ticks(*args)

    # noinspection PyMethodMayBeStatic
    def _logticks(self, lower, upper):
        # lower,upper = map(np.log10,[lower,upper])
        # print 'logticks',lower,upper
        ticks = []
        mag = np.power(10, np.floor(lower))
        if upper - lower > 6:
            t = np.power(10, np.ceil(lower))
            base = np.power(10, np.floor((upper - lower) / 6))

            def inc(x):
                return x * base - x
        else:
            t = np.ceil(np.power(10, lower) / mag) * mag

            def inc(x):
                return 10 ** int(np.floor(np.log10(x) + 1e-16))

        majortick = int(np.log10(mag))
        while t <= pow(10, upper):
            if majortick != int(np.floor(np.log10(t) + 1e-16)):
                majortick = int(np.floor(np.log10(t) + 1e-16))
                ticklabel = '1e%d' % majortick
            else:
                if upper - lower < 2:
                    minortick = int(t / pow(10, majortick) + .5)
                    ticklabel = '%de%d' % (minortick, majortick)
                else:
                    ticklabel = ''
            ticks.append((np.log10(t), ticklabel))
            t += inc(t)
        if len(ticks) == 0:
            ticks = [(0, '')]
        return ticks

    def _ticks(self, lower, upper):
        ideal = (upper - lower) / 7.
        log = np.log10(ideal)
        power = np.floor(log)
        fraction = log - power
        factor = 1.
        error = fraction
        for f, lf in self._multiples:
            e = np.fabs(fraction - lf)
            if e < error:
                error = e
                factor = f
        grid = factor * 10. ** power
        if self._useScientificNotation and (power > 4 or power < -4):
            txt_format = '%+7.1e'
        elif power >= 0:
            digits = max(1, int(power))
            txt_format = '%' + repr(digits) + '.0f'
        else:
            digits = -int(power)
            txt_format = '%' + repr(digits + 2) + '.' + repr(digits) + 'f'
        ticks = []
        t = -grid * np.floor(-lower / grid)
        while t <= upper:
            ticks.append((t, txt_format % (t,)))
            t = t + grid
        return ticks

    _multiples = [(2., np.log10(2.)), (5., np.log10(5.))]

    def _adjust_scrollbars(self):
        if self._sb_ignore:
            self._sb_ignore = False
            return

        self._adjustingSB = True
        needScrollbars = False

        # horizontal scrollbar
        r_current = self._get_x_current_range()
        r_max = list(self._get_x_max_range())
        sbfullrange = int(self.sb_hor.GetRange())

        r_max[0] = min(r_max[0], r_current[0])
        r_max[1] = max(r_max[1], r_current[1])

        self._sb_xfullrange = r_max

        unit = (r_max[1] - r_max[0]) / float(self.sb_hor.GetRange())
        pos = int((r_current[0] - r_max[0]) / unit)

        if pos >= 0:
            pagesize = int((r_current[1] - r_current[0]) / unit)

            self.sb_hor.SetScrollbar(pos, pagesize, sbfullrange, pagesize)
            self._sb_xunit = unit
            needScrollbars = needScrollbars or (pagesize != sbfullrange)
        else:
            self.sb_hor.SetScrollbar(0, 1000, 1000, 1000)

        # vertical scrollbar
        r_current = self._get_y_current_range()
        r_max = list(self._get_y_max_range())
        sbfullrange = int(self.sb_vert.GetRange())

        r_max[0] = min(r_max[0], r_current[0])
        r_max[1] = max(r_max[1], r_current[1])

        self._sb_yfullrange = r_max

        unit = (r_max[1] - r_max[0]) / sbfullrange
        pos = int((r_current[0] - r_max[0]) / unit)

        if pos >= 0:
            pagesize = int((r_current[1] - r_current[0]) / unit)
            pos = (sbfullrange - 1 - pos - pagesize)
            self.sb_vert.SetScrollbar(pos, pagesize, sbfullrange, pagesize)
            self._sb_yunit = unit
            needScrollbars = needScrollbars or (pagesize != sbfullrange)
        else:
            self.sb_vert.SetScrollbar(0, 1000, 1000, 1000)

        self.set_show_scrollbars(needScrollbars)
        self._adjustingSB = False


class PlotPrintout(wx.Printout):
    """Controls how the plot is made in printing and previewing"""

    # Do not change method names in this class,
    # we have to override wx.printout methods here!
    def __init__(self, graph):
        """graph is instance of plotCanvas to be printed or previewed"""
        wx.Printout.__init__(self)
        self.graph = graph

    def HasPage(self, page):
        if page == 1:
            return True
        else:
            return False

    def GetPageInfo(self):
        return 1, 1, 1, 1         # disable page numbers

    # noinspection PyProtectedMember
    def OnPrintPage(self, page):
        dc = self.GetDC()  # allows using floats for certain functions
        #        print "PPI Printer",self.GetPPIPrinter()
        #        print "PPI Screen", self.GetPPIScreen()
        #        print "DC GetSize", dc.GetSize()
        #        print "GetPageSizePixels", self.GetPageSizePixels()
        # Note PPIScreen does not give the correct number
        # Calulate everything for printer and then scale for preview
        PPIPrinter = self.GetPPIPrinter()  # printer dots/inch (w,h)
        # PPIScreen= self.GetPPIScreen()          # screen dots/inch (w,h)
        dcSize = dc.GetSize()  # DC size
        pageSize = self.GetPageSizePixels()  # page size in terms of pixcels
        clientDcSize = self.graph.GetClientSize()

        # find what the margins are (mm)
        margLeftSize, margTopSize = self.graph.pageSetupData.GetMarginTopLeft()
        margRightSize, margBottomSize = self.graph.pageSetupData.GetMarginBottomRight()

        # calculate offset and scale for dc
        pixLeft = margLeftSize * PPIPrinter[0] / 25.4  # mm*(dots/in)/(mm/in)
        pixRight = margRightSize * PPIPrinter[0] / 25.4
        pixTop = margTopSize * PPIPrinter[1] / 25.4
        pixBottom = margBottomSize * PPIPrinter[1] / 25.4

        plotAreaW = pageSize[0] - (pixLeft + pixRight)
        plotAreaH = pageSize[1] - (pixTop + pixBottom)

        # ratio offset and scale to screen size if preview
        if self.IsPreview():
            ratioW = dcSize[0] / pageSize[0]
            ratioH = dcSize[1] / pageSize[1]
            pixLeft *= ratioW
            pixTop *= ratioH
            plotAreaW *= ratioW
            plotAreaH *= ratioH

        # rescale plot to page or preview plot area
        self.graph._set_size(plotAreaW, plotAreaH)

        # Set offset and scale
        dc.SetDeviceOrigin(pixLeft, pixTop)

        # Thicken up pens and increase marker size for printing
        ratioW = float(plotAreaW) / clientDcSize[0]
        ratioH = float(plotAreaH) / clientDcSize[1]
        aveScale = (ratioW + ratioH) / 2
        self.graph._set_printer_scale(aveScale)  # tickens up pens for printing

        self.graph._print_draw(dc)
        # rescale back to original
        self.graph._set_size()
        self.graph._set_printer_scale(1)
        self.graph.redraw()  # to get point label scale and shift correct

        return True


# ----------------------------------------------------------------------

def get_mag_data():
    return zlib.decompress(
        b'x\xda\x01*\x01\xd5\xfe\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x18\
\x00\x00\x00\x18\x08\x06\x00\x00\x00\xe0w=\xf8\x00\x00\x00\x04sBIT\x08\x08\
\x08\x08|\x08d\x88\x00\x00\x00\xe1IDATx\x9c\xb5U\xd1\x0e\xc4 \x08\xa3n\xff\
\xff\xc5\xdb\xb8\xa7\xee<\x04\x86gFb\xb2\x88\xb6\x14\x90\x01m\x937m\x8f\x1c\
\xd7yh\xe4k\xdb\x8e*\x01<\x05\x04\x07F\x1cU\x9d"\x19\x14\\\xe7\xa1\x1e\xf07"\
\x90H+$?\x04\x16\x9c\xd1z\x04\x00J$m\x06\xdc\xee\x03Hku\x13\xd8C\x16\x84+"O\
\x1b\xa2\x07\xca"\xb7\xc6sY\xbdD\x926\xf5.\xce\x06!\xd2)x\xcb^\'\x08S\xe4\
\xe5x&5\xb4[A\xb5h\xb4j=\x9a\xc8\xf8\xecm\xd4\\\x9e\xdf\xbb?\x10\xf0P\x06\
\x12\xed?=\xb6a\xd8=\xcd\xa2\xc8T\xd5U2t\x11\x95d\xa3"\x9aQ\x9e\x12\xb7M\x19\
I\x9f\xff\x1e\xd8\xa63#q\xff\x07U\x8b\xd2\xd9\xa7k\xe9\xa1U\x94,\xbf\xe4\x88\
\xe4\xf6\xaf\x12x$}\x8a\xc2Q\xf1\'\x89\xf2\x9b\xfbKE\xae\xd8\x07+\xd2\xa7c\
\xdf\x0e\xc3D\x00\x00\x00\x00IEND\xaeB`\x82\xe2ovy')


def get_mag_bmp():
    return BitmapFromImage(get_mag_img())


def get_mag_img():
    stream = BytesIO(get_mag_data())
    return Image(stream)


# ----------------------------------------------------------------------
def get_grab_data():
    return zlib.decompress(
        b'x\xda\x01Z\x01\xa5\xfe\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x18\
\x00\x00\x00\x18\x08\x06\x00\x00\x00\xe0w=\xf8\x00\x00\x00\x04sBIT\x08\x08\
\x08\x08|\x08d\x88\x00\x00\x01\x11IDATx\x9c\xb5U\xd1\x12\x830\x08Kh\xff\xff\
\x8b7\xb3\x97\xd1C\xa4Zw\x93;\x1fJ1\t\x98VJ\x92\xb5N<\x14\x04 I\x00\x80H\xb4\
\xbd_\x8a9_{\\\x89\xf2z\x02\x18/J\x82\xb5\xce\xed\xfd\x12\xc9\x91\x03\x00_\
\xc7\xda\x8al\x00{\xfdW\xfex\xf2zeO\x92h\xed\x80\x05@\xa45D\xc5\xb3\x98u\x12\
\xf7\xab.\xa9\xd0k\x1eK\x95\xbb\x1a]&0\x92\xf0\'\xc6]gI\xda\tsr\xab\x8aI\x1e\
\\\xe3\xa4\x0e\xb4*`7"\x07\x8f\xaa"x\x05\xe0\xdfo6B\xf3\x17\xe3\x98r\xf1\xaf\
\x07\xd1Z\'%\x95\x0erW\xac\x8c\xe3\xe0\xfd\xd8AN\xae\xb8\xa3R\x9as>\x11\x8bl\
yD\xab\x1f\xf3\xec\x1cY\x06\x89$\xbf\x80\xfb\x14\\dw\x90x\x12\xa3+\xeeD\x16%\
I\xe3\x1c\xb8\xc7c\'\xd5Y8S\x9f\xc3Zg\xcf\x89\xe8\xaao\'\xbbk{U\xfd\xc0\xacX\
\xab\xbb\xe8\xae\xfa)AEr\x15g\x86(\t\xfe\x19\xa4\xb5\xe9f\xfem\xde\xdd\xbf$\
\xf8G<>\xa2\xc7\t>\tE\xfc\x8a\xf6\x8dqc\x00\x00\x00\x00IEND\xaeB`\x82\xdb\
\xd0\x8f\n')


def get_grab_bmp():
    return BitmapFromImage(get_grab_img())


def get_grab_img():
    stream = BytesIO(get_grab_data())
    return Image(stream)


# ----------------------------------------------------------------------
def get_hand_data():
    # made in bytes (quim)
    return zlib.decompress(
        b'x\xda\x01Y\x01\xa6\xfe\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x18\
\x00\x00\x00\x18\x08\x06\x00\x00\x00\xe0w=\xf8\x00\x00\x00\x04sBIT\x08\x08\
\x08\x08|\x08d\x88\x00\x00\x01\x10IDATx\x9c\xad\x96\xe1\x02\xc2 \x08\x849\
\xf5\xfd\x9fx\xdb\xf5\'\x8c!\xa8\xab\xee\x975\xe5\x83\x0b\\@\xa9\xb2\xab\xeb\
<\xa8\xebR\x1bv\xce\xb4\'\xc1\x81OL\x92\xdc\x81\x0c\x00\x1b\x88\xa4\x94\xda\
\xe0\x83\x8b\x88\x00\x10\x92\xcb\x8a\xca,K\x1fT\xa1\x1e\x04\xe0f_\n\x88\x02\
\xf1:\xc3\x83>\x81\x0c\x92\x02v\xe5+\xba\xce\x83\xb7f\xb8\xd1\x9c\x8fz8\xb2*\
\x93\xb7l\xa8\xe0\x9b\xa06\xb8]_\xe7\xc1\x01\x10U\xe1m\x98\xc9\xefm"ck\xea\
\x1a\x80\xa0Th\xb9\xfd\x877{V*Qk\xda,\xb4\x8b\xf4;[\xa1\xcf6\xaa4\x9cd\x85X\
\xb0\r\\j\x83\x9dd\x92\xc3 \xf6\xbd\xab\x0c2\x05\xc0p\x9a\xa7]\xf4\x14\x18]3\
7\x80}h?\xff\xa2\xa2\xe5e\x90\xact\xaf\xe8B\x14y[4\x83|\x13\xdc\x9e\xeb\x16e\
\x90\xa7\xf2I\rw\x91\x87d\xd7p\x96\xbd\xd70\x07\xda\xe3v\x9a\xf5\xc5\xb2\xb2\
+\xb24\xbc\xaew\xedZe\x9f\x02"\xc8J\xdb\x83\xf6oa\xf5\xb7\xa5\xbf8\x12\xffW\
\xcf_\xbd;\xe4\x8c\x03\x10\xdb^\x00\x00\x00\x00IEND\xaeB`\x82\xd1>\x97B')


def get_hand_bmp():
    return BitmapFromImage(get_hand_img())


def get_hand_img():
    stream = BytesIO(get_hand_data())
    return Image(stream)


# ---------------------------------------------------------------------------
# if running standalone...
#
#     ...a sample implementation using the above
#
# noinspection PyTypeChecker
def _draw1_objects():
    # 100 points sin function, plotted as green circles
    data1 = 2. * np.pi * np.arange(200) / 200.
    data1.shape = (100, 2)
    data1[:, 1] = np.sin(data1[:, 0])
    markers1 = PolyMarker(data1, legend='Green Markers', colour='green',
                          marker='circle', size=1)

    # 50 points cos function, plotted as red line
    data1 = 2. * np.pi * np.arange(100) / 100.
    data1.shape = (50, 2)
    data1[:, 1] = np.cos(data1[:, 0])
    lines = PolyLine(data1, legend='Red Line', colour='red')

    # A few more points...
    pi = np.pi
    markers2 = PolyMarker([(0., 0.), (pi / 4., 1.), (pi / 2, 0.),
                           (3. * pi / 4., -1)], legend='Cross Legend',
                          colour='blue',
                          marker='cross')

    return PlotGraphics([markers1, lines, markers2], "Graph Title", "X Axis",
                        "Y Axis")

# noinspection PyTypeChecker
def _draw2_objects():
    # 100 points sin function, plotted as green dots
    data1 = 2. * np.pi * np.arange(200) / 200.
    data1.shape = (100, 2)
    data1[:, 1] = np.sin(data1[:, 0])
    line1 = PolyLine(data1, legend='Green Line', colour='green', width=6,
                     style=wx.PENSTYLE_DOT)

    # 50 points cos function, plotted as red dot-dash
    data1 = 2. * np.pi * np.arange(100) / 100.
    data1.shape = (50, 2)
    data1[:, 1] = np.cos(data1[:, 0])
    line2 = PolyLine(data1, legend='Red Line', colour='red', width=3,
                     style=wx.PENSTYLE_DOT_DASH)

    # A few more points...
    pi = np.pi
    markers1 = PolyMarker([(0., 0.), (pi / 4., 1.), (pi / 2, 0.),
                           (3. * pi / 4., -1)], legend='Cross Hatch Square',
                          colour='blue', width=3, size=6,
                          fillcolour='red',
                          fillstyle=wx.BRUSHSTYLE_CROSSDIAG_HATCH,
                          marker='square')

    return PlotGraphics([markers1, line1, line2],
                        "Big Markers with Different Line Styles")

# noinspection PyTypeChecker
def _draw3_objects():
    markerList = ['circle', 'dot', 'square', 'triangle', 'triangle_down',
                  'cross', 'plus', 'circle']
    m = []
    for i in range(len(markerList)):
        m.append(PolyMarker([(2 * i + .5, i + .5)], legend=markerList[i],
                            colour='blue',
                            marker=markerList[i]))
    return PlotGraphics(m, "Selection of Markers", "Minimal Axis", "No Axis")

# noinspection PyTypeChecker
def _draw4_objects():
    # 25,000 point line
    data1 = np.arange(5e5, 1e6, 10)
    data1.shape = (25000, 2)
    line1 = PolyLine(data1, legend='Wide Line', colour='green', width=5)

    # A few more points...
    markers2 = PolyMarker(data1, legend='Square', colour='blue',
                          marker='square')
    return PlotGraphics([line1, markers2], "25,000 Points", "Value X", "")

# noinspection PyTypeChecker
def _draw5_objects():
    # Empty graph with axis defined but no points/lines
    points = []
    line1 = PolyLine(points, legend='Wide Line', colour='green', width=5)
    return PlotGraphics([line1], "Empty Plot With Just Axes", "Value X",
                        "Value Y")

# noinspection PyTypeChecker
def _draw6_objects():
    # Bar graph
    points1 = [(1, 0), (1, 10)]
    line1 = PolyLine(points1, colour='green', legend='Feb.', width=10)
    points1g = [(2, 0), (2, 4)]
    line1g = PolyLine(points1g, colour='red', legend='Mar.', width=10)
    points1b = [(3, 0), (3, 6)]
    line1b = PolyLine(points1b, colour='blue', legend='Apr.', width=10)

    points2 = [(4, 0), (4, 12)]
    line2 = PolyLine(points2, colour='Yellow', legend='May', width=10)
    points2g = [(5, 0), (5, 8)]
    line2g = PolyLine(points2g, colour='orange', legend='June', width=10)
    points2b = [(6, 0), (6, 4)]
    line2b = PolyLine(points2b, colour='brown', legend='July', width=10)

    return PlotGraphics([line1, line1g, line1b, line2, line2g, line2b],
                        "Bar Graph - (Turn on Grid, Legend)", "Months",
                        "Number of Students")

# noinspection PyTypeChecker
def _draw7_objects():
    # Empty graph with axis defined but no points/lines
    x = np.arange(1, 1000, 1)
    y1 = 4.5 * x ** 2
    y2 = 2.2 * x ** 3
    points1 = np.transpose([x, y1])
    points2 = np.transpose([x, y2])
    line1 = PolyLine(points1, legend='quadratic', colour='blue', width=1)
    line2 = PolyLine(points2, legend='cubic', colour='red', width=1)
    return PlotGraphics([line1, line2], "double log plot", "Value X", "Value Y")


class TestFrame(wx.Frame):
    def __init__(self, parent, fid, title):
        wx.Frame.__init__(self, parent, fid, title,
                          wx.DefaultPosition, (600, 400))

        # Now Create the menu bar and items
        self.mainmenu = wx.MenuBar()

        menu = wx.Menu()
        menu.Append(200, 'Page Setup...', 'Setup the printer page')
        self.Bind(wx.EVT_MENU, self.on_file_page_setup, id=200)

        menu.Append(201, 'Print Preview...', 'Show the current plot on page')
        self.Bind(wx.EVT_MENU, self.on_file_print_preview, id=201)

        menu.Append(202, 'Print...', 'Print the current plot')
        self.Bind(wx.EVT_MENU, self.on_file_print, id=202)

        menu.Append(203, 'Save Plot...', 'Save current plot')
        self.Bind(wx.EVT_MENU, self.on_save_file, id=203)

        menu.Append(205, 'E&xit', 'Enough of this already!')
        self.Bind(wx.EVT_MENU, self.on_file_exit, id=205)
        self.mainmenu.Append(menu, '&File')

        menu = wx.Menu()
        menu.Append(206, 'Draw1', 'draw plots1')
        self.Bind(wx.EVT_MENU, self.on_plot_1, id=206)
        menu.Append(207, 'Draw2', 'draw plots2')
        self.Bind(wx.EVT_MENU, self.on_plot_2, id=207)
        menu.Append(208, 'Draw3', 'draw plots3')
        self.Bind(wx.EVT_MENU, self.on_plot_3, id=208)
        menu.Append(209, 'Draw4', 'draw plots4')
        self.Bind(wx.EVT_MENU, self.on_plot_4, id=209)
        menu.Append(210, 'Draw5', 'draw plots5')
        self.Bind(wx.EVT_MENU, self.on_plot_5, id=210)
        menu.Append(260, 'Draw6', 'draw plots6')
        self.Bind(wx.EVT_MENU, self.on_plot_6, id=260)
        menu.Append(261, 'Draw7', 'draw plots7')
        self.Bind(wx.EVT_MENU, self.on_plot_7, id=261)

        menu.Append(211, '&redraw', 'redraw plots')
        self.Bind(wx.EVT_MENU, self.on_plot_redraw, id=211)
        menu.Append(212, '&clear', 'clear canvas')
        self.Bind(wx.EVT_MENU, self.on_plot_clear, id=212)
        menu.Append(213, '&Scale', 'Scale canvas')
        self.Bind(wx.EVT_MENU, self.on_plot_scale, id=213)
        menu.Append(214, 'Enable &zoom', 'Enable Mouse zoom',
                    kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.on_enable_zoom, id=214)
        menu.Append(215, 'Enable &Grid', 'Turn on Grid', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.on_enable_grid, id=215)
        menu.Append(217, 'Enable &Drag', 'Activates dragging mode',
                    kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.on_enable_drag, id=217)
        menu.Append(220, 'Enable &Legend', 'Turn on Legend', kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.on_enable_legend, id=220)
        menu.Append(222, 'Enable &Point Label', 'Show Closest Point',
                    kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.on_enable_point_label, id=222)

        menu.Append(225, 'Scroll Up 1', 'Move View Up 1 Unit')
        self.Bind(wx.EVT_MENU, self.on_scr_up, id=225)
        menu.Append(230, 'Scroll Rt 2', 'Move View Right 2 Units')
        self.Bind(wx.EVT_MENU, self.on_scr_rt, id=230)
        menu.Append(235, '&Plot reset', 'reset to original plot')
        self.Bind(wx.EVT_MENU, self.on_reset, id=235)

        self.mainmenu.Append(menu, '&Plot')

        menu = wx.Menu()
        menu.Append(300, '&About', 'About this thing...')
        self.Bind(wx.EVT_MENU, self.on_help_about, id=300)
        self.mainmenu.Append(menu, '&Help')

        self.SetMenuBar(self.mainmenu)

        # A status bar to tell people what's happening
        self.CreateStatusBar(1)

        self.client = PlotCanvas(self)
        # define the function for drawing pointLabels
        self.client.set_point_label_func(self.draw_point_label)
        # Create mouse event for showing cursor coords in status bar
        self.client.canvas.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        # Show closest point when enabled
        self.client.canvas.Bind(wx.EVT_MOTION, self.on_motion)

        self.Show(True)

    # noinspection PyMethodMayBeStatic
    def draw_point_label(self, dc, mDataDict):
        """This is the fuction that defines how the pointLabels are plotted
            dc - DC that will be passed
            mDataDict - Dictionary of data that you want to use for the pointLabel

            As an example I have decided I want a box at the curve point
            with some text information about the curve plotted below.
            Any wxDC method can be used.
        """
        # ----------
        dc.SetPen(wx.Pen(wx.BLACK))
        dc.SetBrush(wx.Brush(wx.BLACK, wx.BRUSHSTYLE_SOLID))

        # scaled x,y of closest point
        sx, sy = mDataDict["scaledXY"]
        sx, sy = int(sx), int(sy)
        # 10x10 square centered on point
        dc.DrawRectangle(sx - 5, sy - 5, 10, 10)
        px, py = mDataDict["pointXY"]
        cNum = mDataDict["curveNum"]
        pntIn = mDataDict["pIndex"]
        legend = mDataDict["legend"]

        # make a string to display
        s = "Crv# %i, '%s', Pt. (%.2f,%.2f), PtInd %i" % (
            cNum, legend, px, py, pntIn)
        dc.DrawText(s, sx, sy + 1)
        # -----------

    # noinspection PyProtectedMember
    def on_mouse_left_down(self, event):
        s = "Left Mouse Down at Point: (%.4f, %.4f)" % self.client._get_xy(event)
        self.SetStatusText(s)
        event.Skip()  # allows plotCanvas on_mouse_left_down to be called

    def on_motion(self, event):
        # show closest point (when enbled)
        if self.client.get_enable_point_label():
            # make up dict with info for the pointLabel
            # I've decided to mark the closest point on the closest curve
            # noinspection PyProtectedMember
            dlst = self.client.get_closest_pnt(self.client._get_xy(event),
                                               pointScaled=True)
            if dlst:  # returns [] if none
                curveNum, legend, pIndex, pointXY, scaledXY, distance = dlst
                # make up dictionary to pass to my user function (see draw_point_label)
                mDataDict = {"curveNum": curveNum, "legend": legend,
                             "pIndex": pIndex,
                             "pointXY": pointXY, "scaledXY": scaledXY}
                # pass dict to update the pointLabel
                self.client.update_point_label(mDataDict)
        event.Skip()  # go to next handler

    def on_file_page_setup(self, _):
        self.client.page_setup()

    def on_file_print_preview(self, _):
        self.client.print_preview()

    def on_file_print(self, _):
        self.client.printout()

    def on_save_file(self, _):
        self.client.save_file()

    def on_file_exit(self, _):
        self.Close()

    def on_plot_1(self, _):
        self.reset_defaults()
        self.client.draw(_draw1_objects())

    def on_plot_2(self, _):
        self.reset_defaults()
        self.client.draw(_draw2_objects())

    def on_plot_3(self, _):
        self.reset_defaults()
        self.client.SetFont(wx.Font(10, wx.FONTFAMILY_SCRIPT,
                                    wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL))
        self.client.font_size_axis = 20
        self.client.font_size_legend = 12
        self.client.xSpec = 'min'
        self.client.set_yspec('none')
        self.client.draw(_draw3_objects())

    def on_plot_4(self, _):
        self.reset_defaults()
        drawObj = _draw4_objects()
        self.client.draw(drawObj)

    def on_plot_5(self, _):
        # Empty plot with just axes
        self.reset_defaults()
        drawObj = _draw5_objects()
        # make the axis X= (0,5), Y=(0,10)
        # (default with None is X= (-1,1), Y= (-1,1))
        self.client.draw(drawObj, xAxis=(0, 5), yAxis=(0, 10))

    def on_plot_6(self, _):
        # Bar Graph Example
        self.reset_defaults()
        # self.client.enable_legend = True   # turn on Legend
        # self.client.enable_grid(True)      # turn on Grid
        self.client.xSpec = 'none'  # turns off x-axis scale
        self.client.set_yspec('auto')
        self.client.draw(_draw6_objects(), xAxis=(0, 7))

    def on_plot_7(self, _):
        # log scale example
        self.reset_defaults()
        self.client.set_log_scale((True, True))
        self.client.draw(_draw7_objects())

    def on_plot_redraw(self, _):
        self.client.redraw()

    def on_plot_clear(self, _):
        self.client.clear()

    def on_plot_scale(self, _):
        if self.client.last_draw is not None:
            graphics, xAxis, yAxis = self.client.last_draw
            self.client.draw(graphics, (1, 3.05), (0, 1))

    def on_enable_zoom(self, event):
        self.client.enable_zoom(event.IsChecked())
        self.mainmenu.Check(217, not event.IsChecked())

    def on_enable_grid(self, event):
        self.client.enable_grid(event.IsChecked())

    def on_enable_drag(self, event):
        self.client.enable_drag(event.IsChecked())
        self.mainmenu.Check(214, not event.IsChecked())

    def on_enable_legend(self, event):
        self.client.enable_legend(event.IsChecked())

    def on_enable_point_label(self, event):
        self.client.enable_point_label(event.IsChecked())

    def on_scr_up(self, _):
        self.client.scroll_up(1)

    def on_scr_rt(self, _):
        self.client.scroll_right(2)

    def on_reset(self, _):
        self.client.reset()

    def on_help_about(self, _):
        from wx.lib.dialogs import ScrolledMessageDialog
        about = ScrolledMessageDialog(self, __doc__, "About...")
        about.ShowModal()

    def reset_defaults(self):
        """Just to reset the fonts back to the PlotCanvas defaults"""
        self.client.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS,
                                    wx.FONTSTYLE_NORMAL,
                                    wx.FONTWEIGHT_NORMAL))
        self.client.font_size_axis = 10
        self.client.font_size_legend = 7
        self.client.set_log_scale((False, False))
        self.client.xSpec = 'auto'
        self.client.set_yspec('auto')


def __test():
    class MyApp(wx.App):
        def OnInit(self):
            wx.InitAllImageHandlers()
            frame = TestFrame(None, -1, "PlotCanvas")
            # frame.Show(True)
            self.SetTopWindow(frame)
            return True

    app = MyApp(0)
    app.MainLoop()


if __name__ == '__main__':
    __test()

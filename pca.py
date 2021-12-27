# -----------------------------------------------------------------------------
# Name:        pca.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2007/05/22
# RCS-ID:      $Id: pca.py, v 1.19 2009/02/26 22:19:48 rmj01 Exp $
# Copyright:   (c) 2007
# Licence:     GNU General Public Licence
# -----------------------------------------------------------------------------

from os.path import join as op_join
import copy
import numpy as np
from numpy import newaxis as nax

import wx
import wx.aui
import wx.lib.plot.plotcanvas as wlpc
import wx.lib.stattext
import wx.lib.agw.buttonpanel as bp
import wx.lib.agw.foldpanelbar as fpb
from wx.lib.anchors import LayoutAnchors
from wx.lib.stattext import GenStaticText
from wx.lib.buttons import GenToggleButton as wxTogBut
from wx.lib.plot.polyobjects import PolyLine, PlotGraphics
# from wx.lib.plot.polyobjects import PolyMarker

import mva.chemometrics as chemtrics
# noinspection PyProtectedMember
from mva.chemometrics import _index
from plot import PolyEllipse
from commons import error_box
from commons import PolyMarker

[wxID_PCA, wxID_PCAPLCPCALOADSV, wxID_PCAPLCPCASCORE, wxID_PCAPLCPCEIGS,
 wxID_PCAPLCPCVAR, 
 ] = [wx.NewId() for _init_ctrls in range(5)]

[ID_RUNPCA, ID_EXPORTPCA, ID_PCATYPE, 
 ID_SPNPCS, ID_NUMPCS1, ID_NUMPCS2,
 ] = [wx.NewId() for _init_btnpanel_ctrls in range(6)]

# FR1 (wxID_FRAME1)
[FR1_, FR1_BTNAPPLY, FR1_CBGRID,
 FR1_SPNFONTSIZEAXES, FR1_SPNXMAX, FR1_SPNXMIN,
 FR1_SPNYMAX, FR1_SPNYMIN, FR1_STFONT,
 FR1_STTITLE, FR1_STXFROM, FR1_STXLABEL,
 FR1_STXTO, FR1_STYFROM, FR1_STYLABEL, FR1_STYTO,
 FR1_TXTTITLE, FR1_TXTXLABEL, FR1_TXTXMAX,
 FR1_TXTXMIN, FR1_TXTYLABEL, FR1_TXTYMAX,
 FR1_TXTYMIN,
 ] = [wx.NewId() for _init_plot_prop_ctrls in range(23)]

[MNUPLOTCOPY, MNUPLOTPRINT, MNUPLOTSAVE, MNUPLOTPROPS, MNUPLOTCOORDS,
 ] = [wx.NewId() for _init_plot_menu_Items in range(5)]


def set_btn_state(s1, s2, tb):
    # toolbar button enabled condition
    if s1 == s2:
        state = False
    else:
        state = True
    
    buttons = [tb.tbLoadLabels, tb.tbLoadLabStd1, 
               tb.tbLoadLabStd2, tb.tbLoadSymStd2]
    
    for button in buttons:
        button.Enable(state)

def create_sym_col_select(canvas, output):
    """ populate symbol select pop-up

    """
    print(' in create_sym_col_select pca loc 76')
    # first destroy current
    canvas.tbMain.SymPopUpWin.Destroy()
    # create empty ctrl
    canvas.tbMain.SymPopUpWin = SymColSelectTool(canvas.tbMain)
    spuw = canvas.tbMain.SymPopUpWin
    # create ctrls
    count = 0
    # apply button
    spuw.btnApply = wx.Button(spuw, wx.NewId(), 'Apply')
    spuw.Bind(wx.EVT_BUTTON, spuw.on_btn_apply, spuw.btnApply)
    # close button
    spuw.btnClose = wx.Button(spuw, wx.NewId(), 'Close')
    spuw.Bind(wx.EVT_BUTTON, spuw.on_btn_close, spuw.btnClose)
    # spacer
    spuw.stSpacer = wx.StaticText(spuw, -1, '')
    # dynamic ctrls
    spuw.colctrls = []
    spuw.symctrls = []

    sc = str(count)
    for each in output:
        exec('canvas.tbMain.SymPopUpWin.st' + sc + ' = wx.StaticText(canvas.tbMain.SymPopUpWin, -1, ' +
             'each[0])')
        exec('canvas.tbMain.SymPopUpWin.btn' + sc + ' = wx.BitmapButton(canvas.tbMain.SymPopUpWin, ' +
             'bitmap=wx.Bitmap(op_join("bmp", "' + each[1] + '.bmp"), wx.BITMAP_TYPE_BMP), id_=-1)')
        exec('canvas.tbMain.SymPopUpWin.btn' + sc + '.symname = "' + each[1] + '"')
        exec('canvas.tbMain.SymPopUpWin.btn' + sc + '.Bind(wx.EVT_BUTTON, canvas.tbMain.SymPopUpWin.on_btn_symbol' + ')')
        exec('canvas.tbMain.SymPopUpWin.cp' + sc + ' = wx.ColourPickerCtrl(canvas.tbMain.SymPopUpWin, ' +
             '-1, col=' + str(each[2]) + ', style=wx.CLRP_DEFAULT_STYLE)')
        
        # output ctrl names to use later
        spuw.colctrls.append('cp' + sc)
        spuw.symctrls.append('btn' + sc)
        count += 1                          
    
    # create sizer
    spuw.grsSelect = wx.GridSizer(cols=3, hgap=2, rows=count+1, vgap=2)
    # add standard ctrls
    spuw.grsSelect.Add(spuw.btnClose, 0, border=0, flag=wx.EXPAND)
    spuw.grsSelect.Add(spuw.btnApply, 0, border=0, flag=wx.EXPAND)
    spuw.grsSelect.Add(spuw.stSpacer, 0, border=0, flag=wx.EXPAND)
    # add dynamic ctrls to sizer
    for nwin in range(count):
        exec('canvas.tbMain.SymPopUpWin.grsSelect.Add(canvas.tbMain.SymPopUpWin.st' +
             str(nwin) + ', 0, border=0, flag=wx.EXPAND)')
        exec('canvas.tbMain.SymPopUpWin.grsSelect.Add(canvas.tbMain.SymPopUpWin.btn' +
             str(nwin) + ', 0, border=0, flag=wx.EXPAND)')
        exec('canvas.tbMain.SymPopUpWin.grsSelect.Add(canvas.tbMain.SymPopUpWin.cp' +
             str(nwin) + ', 0, border=0, flag=wx.EXPAND)')
    
    # set sizer and resize
    # noinspection PyUnresolvedReferences
    canvas.tbMain.SymPopUpWin.SetSizer(canvas.tbMain.SymPopUpWin.grsSelect)
    resize = wx.Size(canvas.tbMain.SymPopUpWin.GetSize()[0], count * 35)
    canvas.tbMain.SymPopUpWin.SetSize(resize)

# noinspection PyTypeChecker
def box_plot(canvas, x, labels, **_attr):
    """Box and whisker plot; x is a column vector, labels a list of strings

    """
    objects, count = [], 1
    uG = np.unique(np.array(labels))
    for each in uG:
        # get values
        group = x[np.array(labels) == each]
        # calculate group median
        m = np.median(group)
        # lower (first) quartile
        lq = np.median(group[group < m])
        # upper (third) quartile
        uq = np.median(group[group > m])
        # interquartile range
        iqr = uq-lq
        # lower whisker
        lw = m - (1.5 * iqr)
        # upper whisker
        uw = m + (1.5 * iqr)
        # lower outlier
        lo = group[group < lw]
        # upper outlier
        uo = group[group > uw]
        # plot b&w
        solid = wx.PENSTYLE_SOLID
        objects.append(PolyLine([[count - .25, m], [count + .25, m]],
                                width=1, colour='blue', style=solid))
        objects.append(PolyLine([[count - .25, lq], [count + .25, lq]],
                                width=1, colour='black', style=solid))
        objects.append(PolyLine([[count - .25, uq], [count + .25, uq]],
                                width=1, colour='black', style=solid))
        objects.append(PolyLine([[count - .25, lq], [count - .25, uq]],
                                width=1, colour='black', style=solid))
        objects.append(PolyLine([[count + .25, lq], [count + .25, uq]],
                                width=1, colour='black', style=solid))
        objects.append(PolyLine([[count, lq], [count, lw]],
                                width=1, colour='black', style=solid))
        objects.append(PolyLine([[count, uq], [count, uw]],
                                width=1, colour='black', style=solid))
        objects.append(PolyLine([[count - .1, lw], [count + .1, lw]],
                                width=1, colour='black', style=solid))
        objects.append(PolyLine([[count - .1, uw], [count + .1, uw]],
                                width=1, colour='black', style=solid))
        if len(lo) > 0:
            objects.append(PolyMarker(np.concatenate(
                (np.ones((len(lo), 1)) * count, lo[:, nax]), 1),
                 colour='red', fillcolour='red', marker='circle', size=1))
        if len(uo) > 0:
            objects.append(PolyMarker(np.concatenate(
                (np.ones((len(uo), 1)) * count, uo[:, nax]), 1),
                 colour='red', fillcolour='red', marker='circle', size=1))
        count += 1
         
    canvas.xSpec = 'auto'
    # canvas.draw(PlotGraphics(objects, _attr['title'], _attr['xLabel'],
    #                               _attr['yLabel'], xTickLabels=uG))
    canvas.draw(PlotGraphics(objects, _attr['title'], _attr['xLabel'],
                             _attr['yLabel']))


# noinspection PyTypeChecker
def plot_error_bar(canvas, **_attr):
    """Errorbar plot
            Defaults:                                               
                'x'= None           - xaxis values, column vector
                'y'= None           - average, column vector 
                'validation'= None  - list of 0's & 1's & 2's  
                'title'= '',        - plot title
                'xLabel'= '',       - x-axis label
                'yLabel'= '',       - y-axis label
                'lsfit'=False,      - show linear fit
                'usesym'=[]
                'usecol'=[]
    """
    
    # defaults
    colours = ['black', 'red', 'blue']
    usesym = ['square', 'circle', 'triangle']
    ledgtext = ['Train', 'Validation', 'Test']

    # user defined
    if _attr['usesym']:
        # noinspection PyUnusedLocal
        symbols = _attr['usesym']
    if _attr['usecol']:
        colours = _attr['usecol']
    
    objects = []
    if _attr['lsfit']:
        # show linear fit
        objects.append(PolyLine(np.array([[_attr['x'].min(), _attr['x'].min()],
                                [_attr['x'].max(), _attr['x'].max()]]),
                                legend='Linear fit', colour='cyan',
                                width=1, style=wx.PENSTYLE_SOLID))

    for val in range(max(_attr['validation']) + 1):
        # get average and stdev of predictions for each calibration point
        average, stdev = [], []
        xsub = np.take(_attr['x'], _index(_attr['validation'], val), 0)
        uXsub = np.unique(xsub)
        ysub = np.take(_attr['y'], _index(_attr['validation'], val), 0)
        for item in range(len(uXsub)):
            average.append(np.mean(np.take(ysub, _index(xsub, uXsub[item]))))
            stdev.append(np.std(np.take(ysub, _index(xsub, uXsub[item]))))
        
        # markers
        objects.append(PolyMarker(np.concatenate((uXsub[:, nax],
                                  np.array(average)[:, nax]), 1),
                                  legend=ledgtext[val], colour=colours[val],
                                  marker=usesym[val], size=1.5,
                                  fillstyle=wx.BRUSHSTYLE_SOLID))
        
        # errorbars & horizontal bars
        for line, uxval in enumerate(uXsub):
            avgln = average[line]
            stdln = stdev[line]
            # errorbars
            objects.append(
                PolyLine(np.array([[uxval, avgln - stdln],
                                   [uxval, avgln + stdln]]),
                         colour=colours[val], width=1, style=wx.PENSTYLE_SOLID))
            # horizontal bars +ve
            amxs = .01 * abs(max(uXsub))
            objects.append(
                PolyLine(np.array([[uxval - amxs, avgln + stdln],
                                   [uxval + amxs, avgln + stdln]]),
                         colour=colours[val], width=1, style=wx.PENSTYLE_SOLID))
            # horizontal bars -ve
            objects.append(
                PolyLine(np.array([[uxval - amxs, avgln-stdln],
                                   [uxval + amxs, avgln-stdln]]),
                         colour=colours[val], width=1, style=wx.PENSTYLE_SOLID))
        
    # axis limits
    atx = _attr['x']
    aty = _attr['y']

    xAx = (atx.min() - (.05 * atx.max()), atx.max() + (.05 * atx.max()))
    yAx = (aty.min() - (.05 * aty.max()), aty.max() + (.05 * aty.max()))
   
    canvas.draw(PlotGraphics(objects, _attr['title'], _attr['xLabel'],
                             _attr['yLabel']), xAx, yAx)
    
# noinspection PyUnresolvedReferences
def plot_pls_model(canvas, model='full', tbar=None, **_attr):
    """Plot PLS predictions or scores; model = 'full' for PLSR,
       model = 'ga' for GA-PLS feature selection
                                            
    **_attr - key word _attributes                                  
            Defaults:                                               
                'predictions'= None     - pls predictions
                'cL' = None             - constituents
                'scores'     = None     - pls spectral scores
                'plScL'      = None     - false class for pls-da
                'validation' = None,    - split data
                'factors'    = 1,       - no. latent variables
                'type'       = 0        - plsr or pls-da
                'symbols'    = False    - plot with symbols
                'usetxt'     = True     - plot with text labels
                'RMSEPT'     = 0        - RMSE for independent test samples
                'col1'       = 0        - col for xaxis
                'col2'       = 1        - col for yaxis
    """
    typex = _attr['type']
    cL = None
    pRed = None
    canvPref = None

    if model in ['full']:
        canvPref = 'plcPredPls'
        prnt = canvas.parent.parent
    elif model == 'ga':
        canvPref = 'plcGaModelPlot'
        prnt = canvas.parent.parent.prnt.splitPrnt

    nBook = canvas.parent

    # Parece que Notebook no tiene 'SetTabSize' en phoenyx
    # if _attr['predictions'].shape[1] > 1:
    #     canvas.parent.SetTabSize((80, 15))
    # else:
    #     canvas.parent.SetTabSize((0, 1))
    #     canvas.parent.SetPageText(0, '')
    
    if typex == 0:
        numPlots = _attr['predictions'].shape[1]
    else:
        numPlots = _attr['predictions'].shape[1] + 1
    
    # delete pages
    nBook.SetSelection(0)
    for page in range(nBook.GetPageCount() - 1, -1, -1):
        nBook.DeletePage(page)
    
    for const in range(numPlots):
        if typex == 0:
            cL = _attr['cL'][:, const][:, nax]
            pRed = _attr['predictions'][:, const][:, nax]
        elif (typex == 1) & (const > 0) is True:
            cL = _attr['plScL'][:, const-1][:, nax]
            pRed = _attr['predictions'][:, const-1][:, nax]
        
        # create new canvas
        sc1 = str(const + 1)
        exec("prnt." + canvPref + sc1 + "= MyPlotCanvas(id_=-1, " +
             "name='" + canvPref + sc1 + "', parent=nBook, " +
             "pos=wx.Point(0, 0), size=wx.Size(302, 246), " +
             "style=0, toolbar=tbar)")
        exec("prnt." + canvPref + sc1 + ".font_size_axis = 8")
        exec("prnt." + canvPref + sc1 + ".font_size_title = 10")
        exec("prnt." + canvPref + sc1 + ".enable_zoom = True")
        exec("prnt." + canvPref + sc1 + ".SetToolTip('')")
        exec("prnt." + canvPref + sc1 + ".enable_legend = True")
        exec("prnt." + canvPref + sc1 + ".font_size_legend = 8")
        exec("prnt." + canvPref + sc1 + ".SetAutoLayout(True)")
        exec("prnt." + canvPref + sc1 +
             ".SetConstraints(LayoutAnchors(prnt." + canvPref + sc1 +
             ", True, True, True, True))")

        # create new nb page
        if _attr['predictions'].shape[1] > 1:
            exec("nBook.AddPage(imageId=-1, page=prnt." + canvPref +
                 sc1 + ", select=False, text='PLS Predictions " +
                 sc1 + "')")
        else:
            exec("nBook.AddPage(imageId=-1, page=prnt." + canvPref +
                 sc1 + ", select=False, text='')")
        
        # use it for plotting
        cmd = "ncanv = prnt." + canvPref + sc1
        exec(cmd, locals(), globals())
        
        if (typex == 1) and (const == 0):
            # plot pls-da scores
            plot_scores(ncanv, _attr['scores'], cl=_attr['cL'][:, 0],
                        labels=_attr['label'], validation=_attr['validation'],
                        col1=_attr['col1'], col2=_attr['col2'],
                        title='PLS Scores',
                        xLabel='t[%i]' % _attr['col1']+1,
                        yLabel='t[%i]' % _attr['col2']+1,
                        xval=True, pconf=False, symb=_attr['symbols'],
                        text=_attr['usetxt'], usecol=_attr['usecol'],
                        usesym=_attr['usesym'])
        
        else:  
            if _attr['symbols']:
                # pls predictions as errorbar plot
                title = 'PLS Predictions: %i factors, RMS(Indep. Test) %.2f'  % \
                        (_attr['factors']+1, _attr['RMSEPT'])
                plot_error_bar(ncanv, x=cL, y=pRed,
                               validation=_attr['validation'],
                               title=title, xLabel='Actual', yLabel='Predicted',
                               lsfit=True, usesym=_attr['usesym'],
                               usecol=_attr['usecol'])
            else:
                # pls predictions as scatter plot
                TrnPnts = np.zeros((1, 2), 'd')
                ValPnts = np.zeros((1, 2), 'd'),
                TstPnts = np.zeros((1, 2), 'd')

                for i in range(len(cL)):
                    if int(np.reshape(_attr['validation'][i], ())) == 0:
                        y = float(np.reshape(cL[i], ()))
                        py = float(np.reshape(pRed[i], ()))
                        TrnPnts = np.concatenate((TrnPnts, np.reshape((y, py), (1, 2))), 0)
                    elif int(np.reshape(_attr['validation'][i], ())) == 1:
                        y = float(np.reshape(cL[i], ()))
                        py = float(np.reshape(pRed[i], ()))
                        ValPnts = np.concatenate((ValPnts, np.reshape((y, py), (1, 2))), 0)
                    elif int(np.reshape(_attr['validation'][i], ())) == 2:
                        y = float(np.reshape(cL[i], ()))
                        py = float(np.reshape(pRed[i], ()))
                        TstPnts = np.concatenate((TstPnts, np.reshape((y, py), (1, 2))), 0)
                
                TrnPnts = TrnPnts[1:len(TrnPnts) + 1]
                ValPnts = ValPnts[1:len(ValPnts) + 1]
                TstPnts = TstPnts[1:len(TstPnts) + 1]
                
                TrnPntObj = PolyMarker(TrnPnts, legend='Train',
                                       colour='black',
                                       marker='square', size=1.5,
                                       fillstyle=wx.BRUSHSTYLE_TRANSPARENT)
                
                ValPntObj = PolyMarker(ValPnts, legend='Cross Val.',
                                       colour='red',
                                       marker='circle', size=1.5,
                                       fillstyle=wx.BRUSHSTYLE_TRANSPARENT)
                
                TstPntObj = PolyMarker(TstPnts, legend='Indep. Test',
                                       colour='blue',
                                       marker='triangle', size=1.5,
                                       fillstyle=wx.BRUSHSTYLE_TRANSPARENT)

                # noinspection PyTypeChecker
                LinearObj = PolyLine(np.array([[cL.min(), cL.min()],
                                              [cL.max(), cL.max()]]),
                                     legend='Linear fit', colour='cyan',
                                     width=1, style=wx.PENSTYLE_SOLID)
                
                PlsModel = PlotGraphics([TrnPntObj, ValPntObj, TstPntObj, LinearObj],
                                        ' '.join(('PLS Predictions:',
                                                  str(_attr['factors'] + 1),
                                                  'factors, RMS(Indep. Test)',
                                                  '%.2f' % _attr['RMSEPT'])),
                                        'Actual', 'Predicted')
                
                xAx = (cL.min() - (0.05 * cL.max()), cL.max() + (0.05 * cL.max()))
                
                ys = np.concatenate((TrnPnts, ValPnts), 0)
                # noinspection PyArgumentList
                yAx = (ys.min() - (0.05 * ys.max()), ys.max() + (0.05 * ys.max()))
            
                ncanv.draw(PlsModel, xAx, yAx)

    nBook.SetSelection(0)
    exec("canvas = prnt." + canvPref + str(1))
    
    return canvas
              
def plot_line(plotCanvas, plotArr, **_attr):
    """Line plot
        **_attr - key word _attributes
            Defaults:
                'xaxis' = None,    - Vector of x-axis values
                'rownum' = 0,      - Row of plotArr to plot
                'tit'= '',         - A small domestic bird
                'xLabel'= '',      - The desired x-axis label
                'yLabel'= '',      - The desired y-axis label
                'type'= 'single',  - 'single' or 'multi'
                'ledge'= [],       - Figure legend labels
                'wdth'= 1,         - Line width
    """

    colourList = ['blue', 'red', 'green', 'light_grey', 'cyan', 'black']
    NewplotLine = None
    
    if _attr['type'] == 'single':
        pA = plotArr[_attr['rownum'], 0:len(_attr['xaxis'])][:, nax]
        Line = PolyLine(np.concatenate((_attr['xaxis'], pA), 1),
                        colour='black', width=_attr['wdth'],
                        style=wx.PENSTYLE_SOLID)
        NewplotLine = PlotGraphics([Line], _attr['tit'],
                                   _attr['xLabel'], _attr['yLabel'])
    elif _attr['type'] == 'multi':
        ColourCount = 0
        Line = []
        for i in range(plotArr.shape[0]):
            pA = plotArr[i]
            pA = pA[:, nax]
            if _attr['ledge'] is not None:
                Line.append(PolyLine(np.concatenate((_attr['xaxis'], pA), 1),
                                     legend=_attr['ledge'][i],
                                     colour=colourList[ColourCount],
                                     width=_attr['wdth'],
                                     style=wx.PENSTYLE_SOLID))
            else:
                Line.append(PolyLine(np.concatenate((_attr['xaxis'], pA), 1),
                                     colour=colourList[ColourCount],
                                     width=_attr['wdth'],
                                     style=wx.PENSTYLE_SOLID))
            ColourCount += 1
            if ColourCount == len(colourList):
                ColourCount = 0
        NewplotLine = PlotGraphics(Line, _attr['tit'],
                                   _attr['xLabel'], _attr['yLabel'])
    
    plotCanvas.draw(NewplotLine)    # , xAxis=(_attr['xaxis'].min(), _attr['xaxis'].max()))
        
def plot_stem(plotCanvas, plotArr, **_attr):
    """Stem plot
        **_attr - key word _attributes
            Defaults:
                'tit'= '',     - Figure title
                'xLabel'= '',  - The desired x-axis label
                'yLabel'= '',  - The desired y-axis label
                'wdth'= 1,     - Line width
    """
    
    # plotArr is an n x 2 array
    plotStem = []
    for i in range(plotArr.shape[0]):
        newCoords = np.array([[plotArr[i, 0], 0], [plotArr[i, 0], plotArr[i, 1]]])
        plotStem.append(PolyLine(newCoords, colour='black',
                                 width=_attr['wdth'], style=wx.PENSTYLE_SOLID))
    # noinspection PyTypeChecker
    plotStem.append(PolyLine(
        np.array([[plotArr[0, 0] - (.1 * plotArr[0, 0]), 0],
                  [plotArr[len(plotArr) - 1, 0] + (.1 * plotArr[0, 0]), 0]]),
        colour='black',
        width=1, style=wx.PENSTYLE_SOLID))
    
    plotStem = PlotGraphics(plotStem, _attr['tit'],
                            _attr['xLabel'], _attr['yLabel'])
    
    plotCanvas.draw(plotStem)

def plot_symbols(plotCanvas, coords, **_attr):
    """Symbol plot
        **_attr - key word _attributes
            Defaults:
                'mask' = [],    - List of zeros, ones and/or twos to
                                  define train, cross-validation and
                                  test samples
                'cLass' = [],   - List of integers from 1:n, where 
                                  n=no. of groups
                'col1' = 0,     - Column to plot along abscissa
                'col2' = 1,     - Column to plot along ordinate
                'tit'= '',      - A small domestic bird
                'xL'= '',       - The desired x-axis label
                'yL'= '',       - The desired y-axis label
                'text'= [],     - List of labels to use in legend
                'usemask'= True,- Flag to define whether to use 'mask'
                'usecol'=[],    - Use a list of colours
                'usesym'= [],   - List of symbols for plotting
    """
    
    desCl = np.unique(_attr['text'])
    eCount = 0
    if not _attr['usecol']:
        colours = ['blue', 'red', 'green', 'cyan', 'black']
    else:
        colours = _attr['usecol']
    
    if not _attr['usesym']:
        symbols = ['circle', 'square', 'plus',
                   'triangle', 'cross', 'triangle_down']
    else:
        symbols = _attr['usesym']
        
    # plot scores using symbols
    valSym = ['circle', 'square']
    plotSym, countSym, countColour, output = [], 0, 0, []
    for each in desCl:
        if countSym > len(symbols)-1:
            countSym = 0
        if countColour > len(colours)-1:
            countColour = 0
        
        # slice coords
        alist = coords[np.array(_attr['text']) == each, :]

        if _attr['col1'] != _attr['col2']:
            alist = np.take(alist, (_attr['col1'], _attr['col2']), 1)
        else:
            sCount = copy.deepcopy(eCount)+1 
            eCount = eCount+len(alist)
            alist = np.concatenate((np.arange(sCount, eCount + 1)[:, nax],
                                   alist[:, _attr['col1']][:, nax]), 1)
                        
            # col = wx.Colour(round(np.rand(1).tolist()[0]*255),
            #                 round(np.rand(1).tolist()[0]*255),
            #                 round(np.rand(1).tolist()[0]*255))
        
        output.append([each, symbols[countSym], colours[countColour]])
        
        if _attr['usemask'] is False:
            plotSym.append(PolyMarker(alist, marker=symbols[countSym],
                                      fillcolour=colours[countColour],
                                      colour=colours[countColour],
                                      size=2, legend=each))
                
        else:
            listM = _attr['mask'][np.array(_attr['text']) == each]
            for m in range(3):
                if m == 0:
                    # include legend entry
                    plotSym.append(PolyMarker(alist[listM == m],
                                              marker=symbols[countSym],
                                              fillcolour=colours[countColour],
                                              colour=colours[countColour],
                                              size=2.5, legend=each))
                else:
                    # no legend
                    plotSym.append(PolyMarker(alist[listM == m],
                                              marker=symbols[countSym],
                                              fillcolour=colours[countColour],
                                              colour=colours[countColour],
                                              size=2.5))
                    if m > 0:
                        if symbols[countSym] not in ['cross', 'plus']:
                            # overlay white circle/square to indicate
                            # validation/test sample
                            plotSym.append(PolyMarker(
                                alist[listM == m],
                                marker=valSym[m - 1], colour=wx.Colour('white'),
                                fillcolour=wx.Colour('white'), size=1))
                        else:
                            # overlay white square to indicate validation sample
                            plotSym.insert(len(plotSym) - 1,
                                           PolyMarker(alist[listM == m],
                                                      marker=valSym[m - 1],
                                                      colour=wx.Colour('black'),
                                                      fillcolour=wx.Colour('white'),
                                                      size=2.5))
        
        countSym += 1
        countColour += 1
        
    draw_plotSym = PlotGraphics(plotSym, _attr['tit'],
                                xLabel=_attr['xL'], yLabel=_attr['yL'])
    
    if plotCanvas is not None:
        plotCanvas.draw(draw_plotSym)
    
    return plotSym, output

def plot_text(plotCanvas, coords, **_attr):
    """Text label plot
        **_attr - key word _attributes
            Defaults:
                'mask' = [],    - List of zeros, ones and/or twos to
                                  define train, cross-validation and
                                  test samples
                'cLass' = [],   - List of integers from 1:n, where 
                                  n=no. of groups
                'col1' = 0,     - Column to plot along abscissa
                'col2' = 1,     - Column to plot along ordinate
                'tit'= '',      - A small domestic bird
                'xL'= '',       - The desired x-axis label
                'yL'= '',       - The desired y-axis label
                'text'= [],     - List of labels to use in plotting
                'usemask'= True,- Flag to define whether to use 'mask' 
    """
        
    # make sure label string
    nt = [str(i) for i in _attr['text']]
    _attr['text'] = nt
    
    plotText = []
    colours = ['black', 'blue', 'red']
    if _attr['usemask']:
        colRange = 3
    else:
        colRange = 1

    # plot 2d
    if (coords.shape[1] > 1) & (_attr['col1'] != _attr['col2']):
        # set text colour - black=train, blue=val, red=test
        for getColour in range(colRange):
            if colRange == 3:
                idx = _index(_attr['mask'], getColour)
            else:
                idx = range(len(coords))
            plotText.append(PolyMarker(
                np.take(np.take(coords, [_attr['col1'], _attr['col2']], 1),
                        idx, 0),
                marker='text', legend=np.take(_attr['text'], idx, 0),
                colour=colours[getColour]))
    # plot 1d
    else:
        points = np.take(coords, [_attr['col1']], 1)
        nCl = np.unique(_attr['text'])
        eCount = 0
        for each in nCl:
            aslice = points[np.array(_attr['text']) == each]
            lbls = np.array(_attr['text'])[np.array(_attr['text']) == each]
            
            sCount = copy.deepcopy(eCount) + 1
            eCount = eCount + len(aslice)
            
            pointSub = np.concatenate((np.arange(sCount, eCount + 1)[:, nax],
                                       aslice), 1)
            
            if _attr['usemask'] is False:
                plotText.append(PolyMarker(pointSub, marker='text',
                                           legend=lbls.tolist()))
            else:
                msk = np.array(_attr['mask'])
                txt = np.array(_attr['text'])
                for each2 in range(3):
                    msk_lst = msk[txt == each2].tolist()
                    msk_idx = _index(msk_lst, each2)
                    plotText.append(
                        PolyMarker(np.take(pointSub, msk_idx, 0),
                                   marker='text',
                                   legend=np.take(lbls, msk_idx.tolist(),
                                   colour=colours[each2])))
                
    if (coords.shape[1] > 1) & (_attr['col1'] != _attr['col2']):
        draw_plot_text = PlotGraphics(plotText, _attr['tit'],
                                      xLabel=_attr['xL'], yLabel=_attr['yL'])
    else:
        draw_plot_text = PlotGraphics(plotText, _attr['tit'],
                                      xLabel='', yLabel=_attr['yL'])
    print('plotText ', plotText)
    if plotCanvas is not None:
        plotCanvas.draw(draw_plot_text)
    
    return plotText

def plot_loads(canvas, loads, **_attr):
    """Model loadings plot
        **_attr - key word _attributes
            Defaults:
                'xaxis' = [],   - Vector of x-axis values
                'col1' = 0,     - Column to plot along abscissa
                'col2' = 1,     - Column to plot along ordinate
                'title'= '',    - Figure title
                'xLabel'= '',   - The desired x-axis label
                'yLabel'= '',   - The desired y-axis label
                'type'= 0,      - List of labels to use in plotting
                'usecol'= [],   - List of colours for symbol plot
                'usesym'= [],   - List of symbols for plotting
    """
    i = 0

    # for model loadings plots
    plot = []
    
    if (_attr['col1'] != _attr['col2']) & (loads is not None) is True:
        # standard deviation
        select = np.concatenate((loads[:, _attr['col1']][:, nax],
                                 loads[:, _attr['col2']][:, nax]), 1)
        meanCoords = np.reshape(np.mean(select, 0), (1, 2))
        std = np.mean(np.std(select))

        if _attr['type'] == 0:
            # plot labels
            textPlot = plot_text(None, select, mask=None, cLass=None,
                                 text=_attr['xaxis'], usemask=False, col1=0,
                                 col2=1, tit='', xL='', yL='')
            for each in textPlot:
                plot.append(each)
        
        else:
            test = np.sqrt((loads[:, _attr['col1']]-meanCoords[0, 0]) ** 2 +
                           (loads[:, _attr['col2']]-meanCoords[0, 1]) ** 2)
            index = np.arange(len(_attr['xaxis']))

            if _attr['type'] == 1: 
                # >1*std error & labels
                outIdx = index[test > std]
                getOutliers = np.take(select, outIdx, 0)

                # plot labels
                labels = []
                for each in outIdx:
                    labels.append(_attr['xaxis'][each])
                textPlot = plot_text(None, getOutliers, mask=None, cLass=None,
                                     text=labels, usemask=False, col1=0, col2=1,
                                     tit='', xL='', yL='')
                for each in textPlot:
                    plot.append(each)
            
            elif _attr['type'] == 2:
                # >2*std error & labels
                outIdx = index[test > std * 2]
                
                getOutliers = np.take(select, outIdx, 0)
                
                # plot labels
                labels = []
                for each in outIdx:
                    labels.append(_attr['xaxis'][each])
                textPlot = plot_text(None, getOutliers, mask=None, cLass=None,
                                     text=labels, usemask=False, col1=0, col2=1,
                                     tit='', xL='', yL='')
                for each in textPlot:
                    plot.append(each)
                
            elif _attr['type'] == 3:
                # >2*std error & symbols
                outIdx = index[test > std * 2]
                
                # loadings > 2*std
                getOutliers = np.take(select, outIdx, 0)
                
                # identify regions
                # noinspection PyUnusedLocal
                newxvar = np.take(_attr['xaxis'], outIdx)
                regions = [outIdx[0]]
                for i in range(len(outIdx) - 1 ):
                    if outIdx[i + 1] - 1 != outIdx[i]:
                        regions.append(outIdx[i])
                        regions.append(outIdx[i + 1])
                if np.mod(len(regions), 2) == 1:
                    regions.append(outIdx[i + 1])
                
                # plot regions by symbol/colour
                cl, labels, i = [], [], 0
                while i < len(regions):
                    cl.extend((np.ones(regions[i + 1] - regions[i] + 1, ) * i).tolist())
                    for j in range(regions[i + 1]-regions[i]+1):
                        labels.append(str(_attr['xaxis'][regions[i]]) + ' - ' +
                                      str(_attr['xaxis'][regions[i + 1]]))
                    i += 2
                
                symPlot, output = plot_symbols(None, getOutliers, mask=None,
                                               cLass=np.array(cl),
                                               text=labels, usemask=False,
                                               col1=0, col2=1, tit='',
                                               xL='', yL='',
                                               usecol=_attr['usecol'],
                                               usesym=_attr['usesym'])
                
                # create window in background for changing symbols/colours
                create_sym_col_select(canvas, output)
                                            
                for each in symPlot:
                    plot.append(each)
                
            # ellipse boundary
            plot.append(PolyMarker([[meanCoords[0, 0] - (std * 2),
                                     meanCoords[0, 1] - (std * 2)],
                                    [meanCoords[0, 0] + (std * 2),
                                     meanCoords[0, 1] + (std * 2)]],
                                   colour='white', size=1, marker='circle'))
            # centroid
            plot.append(PolyMarker(meanCoords, colour='blue',
                                   size=2, marker='plus'))
            # plot 1 std
            plot.append(PolyEllipse(meanCoords, colour='green', width=1,
                                    dim=(std * 2, std * 2),
                                    style=wx.PENSTYLE_SOLID))
            # plot 2 stds
            plot.append(PolyEllipse(meanCoords, colour='green', width=1,
                                    dim=(std * 4, std * 4),
                                    style=wx.PENSTYLE_SOLID))
        
        # draw it
        canvas.draw(PlotGraphics(plot, _attr['title'], _attr['xLabel'],
                                 _attr['yLabel']))
        
        
def plot_scores(canvas, scores, **_attr):
    """Model scores plot
        **_attr - key word _attributes
            Defaults:
                'cl' = []           - List of integers
                'labels' = []       - List of sample labels
                'validation' = []   - List of zeros, ones and/or twos
                'col1' = 0,         - Column to plot along abscissa
                'col2' = 1,         - Column to plot along ordinate
                'title'= '',        - Figure title
                'xLabel'= '',       - The desired x-axis label
                'yLabel'= '',       - The desired y-axis label
                'xval'= False,      - Cross-validation used flag
                'text'= True,       - Text label plotting used flag
                'pconf'= True,      - 95% confidence limits plotted flag
                'symb'= False,      - Symbol plotting used flag
                'usecol'= [],       - List of colours to use in plotting
                'usesym'= [],       - List of symbols for plotting
    """
    
    # make sure we can plot txt
    
    if (canvas.GetName() not in ['plcDFAscores']) & \
            (len(canvas.GetName().split('plcGaModelPlot')) == 1):
        canvas.tbMain.tbConf.SetValue(False)
        if (canvas.tbMain.tbPoints.GetValue() is not True) & \
           (canvas.tbMain.tbSymbols.GetValue() is not True):
            canvas.tbMain.tbPoints.SetValue(True)
            _attr['text'] = True
    
    # get mean centres
    # nb for a dfa/cva plot scaled to unit variance
    # 95% confidence radius is 2.15
    shapex = scores.shape
    nCl = np.unique(_attr['cl'])

    plot = []
    if (shapex[1] > 1) & (_attr['col1'] != _attr['col2']):
        canvas.xSpec = 'auto'
        
        scores = np.concatenate((scores[:, _attr['col1']][:, nax],
                                 scores[:, _attr['col2']][:, nax]), 1)
        
        mScores = np.zeros((1, 2))
        for i in range(len(nCl)):
            mScores = np.concatenate(
                (mScores, np.mean(np.take(scores, _index(_attr['cl'], nCl[i]),
                                          0), 0)[nax, :]), 0)
        mScores = mScores[1: len(mScores)]
        
        if _attr['symb'] is True:
            # plot symbols
            sym_plot, output = plot_symbols(None, scores,
                                            mask=_attr['validation'],
                                            cLass=_attr['cl'],
                                            text=_attr['labels'],
                                            usemask=_attr['xval'], col1=0,
                                            col2=1, tit='', xL='', yL='',
                                            usecol=_attr['usecol'],
                                            usesym=_attr['usesym'])
            
            # create window in background for changing symbols/colours
            create_sym_col_select(canvas, output)
            
            for each in sym_plot:
                plot.append(each)
            
        if _attr['text']:
            # plot labels
            textPlot = plot_text(None, scores, mask=_attr['validation'],
                                 cLass=_attr['cl'], text=_attr['labels'],
                                 col1=0, col2=1, usemask=_attr['xval'], tit='',
                                 xL='', yL='')
            for each in textPlot:
                plot.append(each)
                  
        if _attr['pconf']:
            # 95% confidence interval
            plot.append(PolyEllipse(mScores, colour='black', width=1,
                                    dim=(2.15 * 2, 2.15 * 2),
                                    style=wx.PENSTYLE_SOLID))
            # 95% confidence about the mean
            plot.append(PolyEllipse(mScores, colour='blue', width=1,
                                    dim=((1.95 / np.sqrt(len(nCl)) * 2),
                                         (1.95 / np.sqrt(len(nCl)) * 2)),
                                    style=wx.PENSTYLE_SOLID))
            # class centroids
            plot.append(PolyMarker(mScores[:, 0:2], colour='black',
                                   size=2, marker='plus'))
            # force boundary
            plot.append(PolyMarker([[min(mScores[:, 0] - 2.15),
                                     min(mScores[:, 1] - 2.15)],
                                    [max(mScores[:, 0] + 2.15),
                                     max(mScores[:, 1] + 2.15)]],
                                   colour='white', size=1, marker='circle'))

            # class centroid label
            if (_attr['symb'] is False) & (_attr['text'] is False):
                uC, centLab, centLabOrds = np.unique(_attr['cl']), [], []
                for gC in range(len(uC)):
                    Idx = _index(_attr['cl'], uC[gC])[0]
                    centLab.append(_attr['labels'][Idx])
                    centLabOrds.append(np.reshape(mScores[gC, :], (scores.shape[1], )).tolist())
                
                # print centroid labels
                centPlot = plot_text(None, np.array(centLabOrds),
                                     cLass=np.arange(1, len(centLab) + 1),
                                     text=centLab, col1=0, col2=1,
                                     tit='', xL='', yL='', usemask=False)
                for each in centPlot:
                    plot.append(each)
        
        canvas.draw(PlotGraphics(plot, _attr['title'],
                                 _attr['xLabel'], _attr['yLabel']))
        
    else:
        canvas.xSpec = 'none'
        if _attr['text']:
            # plot labels
            textPlot = plot_text(None, scores, mask=_attr['validation'],
                                 cLass=_attr['cl'], text=_attr['labels'],
                                 col1=_attr['col1'], col2=_attr['col1'],
                                 tit=_attr['title'], xL='Arbitrary',
                                 yL=_attr['yLabel'], usemask=_attr['xval'])
            # each are PolyMarkers

            for each in textPlot:
                print('each legend', each.getLegend())
                print('each tp labels attributes:', each.attributes['labels'])
                # noinspection PyProtectedMember
                print('each tp labels _attributes:', each._attributes['labels'])
                # print('each tp labels _attr:', each._attr['labels'])
                plot.append(each)
        
        if _attr['symb']:
            # plot symbols
            sym_plot, output = plot_symbols(None, scores,
                                            mask=_attr['validation'],
                                            cLass=_attr['cl'],
                                            text=_attr['labels'],
                                            usemask=_attr['xval'],
                                            col1=_attr['col1'],
                                            col2=_attr['col1'], tit='', xL='',
                                            yL='', usecol=_attr['usecol'],
                                            usesym=_attr['usesym'])
            
            # create window in background for changing symbols/colours
            create_sym_col_select(canvas, output)
                                        
            for each in sym_plot:
                print('each sp labels attributes:', each, each.attributes['labels'])
                # noinspection PyProtectedMember
                print('each sp labels _attributes:', each._attributes['labels'])
                plot.append(each)
        
        if _attr['text'] or _attr['symb']:
            graphic = PlotGraphics(plot, _attr['title'], '', _attr['yLabel'])
            print('legen names: ', graphic.getLegendNames())
            canvas.draw(graphic)
    
              
class SymColSelectTool(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent=parent, style=0)

        self.parent = parent
        self.SetSize(wx.Size(300, 0))
        self.SetAutoLayout(True)

    def on_btn_close(self, _):
        self.Show(False)

    # noinspection PyUnresolvedReferences
    def on_btn_apply(self, _):
        # get list of new colours
        collist = []
        for each in self.colctrls:
            exec('collist.append(self.' + each + '.GetColour())')
        # get list of new symbols
        symlist = []
        for each in self.symctrls:
            exec('symlist.append(self.' + each + '.symname)')
        # plot loadings
        self.parent.do_plot(loadType=3, symcolours=collist, symsymbols=symlist)
        self.parent.loadIdx = 3
    
    def on_btn_symbol(self, evt):
        # symbol select dialog
        btn = evt.GetEventObject()
        dlg = SymDialog(self, btn)
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        dlg.SetPosition(wx.Point(pos[0]-155, pos[1] + sz[1]))
        dlg.ShowModal()
        
class SymDialog(wx.Dialog):

    def __init__(self, parent, btn):
        wx.Dialog.__init__(self, id=-1, name=u'SymDialog', parent=parent,
                           pos=wx.Point(589, 316), size=wx.Size(156, 155),
                           style=wx.DEFAULT_DIALOG_STYLE,
                           title=u'Select Symbol')

        self._init_ctrls()
        self.btn = btn

    def _init_ctrls(self):
        # generated method, don't edit

        self.SetClientSize(wx.Size(140, 119))
        self.SetToolTip(u'')

        bmp = wx.Bitmap(op_join('bmp', 'square.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbSquare = wx.BitmapButton(bitmap=bmp, id=-1, name=u'tbSquare',
                                        parent=self, pos=wx.Point(0, 0),
                                        size=wx.Size(69, 38), style=0)
        self.tbSquare.Bind(wx.EVT_BUTTON, self.on_tb_square)

        bmp = wx.Bitmap(op_join('bmp', 'circle.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbCircle = wx.BitmapButton(bitmap=bmp, id=-1, name=u'tbCircle',
                                        parent=self, pos=wx.Point(71, 0),
                                        size=wx.Size(69, 38), style=0)
        self.tbCircle.Bind(wx.EVT_BUTTON, self.on_tb_circle)

        bmp = wx.Bitmap(op_join('bmp', 'plus.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbPlus = wx.BitmapButton(bitmap=bmp, id=-1, name=u'tbPlus',
                                      parent=self, pos=wx.Point(0, 40),
                                      size=wx.Size(69, 38), style=0)
        self.tbPlus.Bind(wx.EVT_BUTTON, self.on_tb_plus)

        bmp = wx.Bitmap(op_join('bmp', 'triangle.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbTriangleUp = wx.BitmapButton(bitmap=bmp, id=-1,
                                            name=u'tbTriangleUp', parent=self,
                                            pos=wx.Point(71, 40),
                                            size=wx.Size(69, 38), style=0)
        self.tbTriangleUp.Bind(wx.EVT_BUTTON, self.on_tb_triangle_up)

        bmp = wx.Bitmap(op_join('bmp', 'triangle_down.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbTriangleDown = wx.BitmapButton(bitmap=bmp, id=-1,
                                              name=u'tbTriangleDown',
                                              parent=self, pos=wx.Point(0, 80),
                                              size=wx.Size(69, 38), style=0)
        self.tbTriangleDown.Bind(wx.EVT_BUTTON, self.on_tb_triangle_down)

        bmp = wx.Bitmap(op_join('bmp', 'cross.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbCross = wx.BitmapButton(bitmap=bmp, id=-1, name=u'tbCross',
                                       parent=self, pos=wx.Point(71, 80),
                                       size=wx.Size(69, 38), style=0)
        self.tbCross.Bind(wx.EVT_BUTTON, self.on_tb_cross)

        self._init_sizers()

    def _init_sizers(self):
        # generated method, don't edit
        self.grs_symdialog = wx.GridSizer(cols=2, hgap=2, rows=3, vgap=2)

        self._init_coll_grs_symdialog_items(self.grs_symdialog)

        self.SetSizer(self.grs_symdialog)

    def _init_coll_grs_symdialog_items(self, parent):
        """"""
        parent.Add(self.tbSquare, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.tbCircle, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.tbPlus, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.tbTriangleUp, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.tbTriangleDown, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.tbCross, 0, border=0, flag=wx.EXPAND)
        
    def on_tb_square(self, _):
        self.btn.SetBitmapLabel(wx.Bitmap(op_join('bmp', 'square.bmp')))
        self.btn.symname = 'square'
        self.Destroy()

    def on_tb_circle(self, _):
        self.btn.SetBitmapLabel(wx.Bitmap(op_join('bmp', 'circle.bmp')))
        self.btn.symname = 'circle'
        self.Destroy()

    def on_tb_plus(self, _):
        self.btn.SetBitmapLabel(wx.Bitmap(op_join('bmp', 'plus.bmp')))
        self.btn.symname = 'plus'
        self.Destroy()

    def on_tb_triangle_up(self, _):
        self.btn.SetBitmapLabel(wx.Bitmap(op_join('bmp', 'triangle.bmp')))
        self.btn.symname = 'triangle'
        self.Destroy()

    def on_tb_triangle_down(self, _):
        bmp = wx.Bitmap(op_join('bmp', 'triangle_down.bmp'))
        self.btn.SetBitmapLabel(bmp)
        self.btn.symname = 'triangle_down'
        self.Destroy()

    def on_tb_cross(self, _):
        bmp = wx.Bitmap(op_join('bmp', 'cross.bmp'))
        self.btn.SetBitmapLabel(bmp)
        self.btn.symname = 'cross'
        self.Destroy()

class MyPlotCanvas(wlpc.PlotCanvas):
    def __init__(self, parent, id_, pos, size, style, name, toolbar):
        wlpc.PlotCanvas.__init__(self, parent, id_, pos, size, style, name)

        wlpc.PlotCanvas._interEnabled = False
        wlpc.PlotCanvas._justDragged = False
        self._interEnabled = False

        self.xSpec = 'min'
        self.ySpec = 'min'

        self.minXrange = 0
        self.maxXrange = 0
        self.minYrange = 0
        self.maxYrange = 0

        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseRightDown)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)

        self._init_utils()
        self.parent = parent
        self.tbMain = toolbar

    def _init_utils(self):
        self.plotMenu = wx.Menu(title='')

        self._init_plot_menu(self.plotMenu)

    def _init_plot_menu(self, parent):
        
        parent.Append(helpString='', id=MNUPLOTCOPY, kind=wx.ITEM_NORMAL,
                      item='Copy Figure')
        parent.Append(helpString='', id=MNUPLOTCOORDS, kind=wx.ITEM_NORMAL,
                      item='Copy Coordinates')
        parent.Append(helpString='', id=MNUPLOTPRINT, kind=wx.ITEM_NORMAL,
                      item='Print')
        parent.Append(helpString='', id=MNUPLOTSAVE, kind=wx.ITEM_NORMAL,
                      item='Save')

        self.Bind(wx.EVT_MENU, self.on_mnu_plot_copy, id=MNUPLOTCOPY)
        self.Bind(wx.EVT_MENU, self.on_mnu_plot_print, id=MNUPLOTPRINT)
        self.Bind(wx.EVT_MENU, self.on_mnu_plot_save, id=MNUPLOTSAVE)
        self.Bind(wx.EVT_MENU, self.on_mnu_plot_coords, id=MNUPLOTCOORDS)
        
    def on_mnu_plot_copy(self, _):
        # for windows
        self.Redraw(wx.MetafileDC()).SetClipboard()

        # for linux
        # wx.TheClipboard.Open()
        # wx.TheClipboard.SetData(self.Copy())
        # wx.TheClipboard.Close()
    
    def on_mnu_plot_print(self, _):
        self.Printout()
    
    def on_mnu_plot_save(self, _):
        self.SaveFile()
    
    # def OnMnuPlotProperties(self, event):
    #      dlg = plotProperties(self)
    #      dlg.SetSize(wx.Size(450, 350))
    #      dlg.Center(wx.BOTH)
    #
    #      # Set up dialog for specific cases
    #      # dfa & pca score plots
    #      if self.GetName() in ['plcDFAscores',
    #                            'plcPCAscore', 'plcGaFeatPlot']:
    #          dlg.scoreSets.Enable(True)
    #      # pca score plots minus conf intervals
    #      if self.GetName() in ['plcPCAscore', 'plcGaFeatPlot']:
    #          dlg.tbConf.Enable(False)
    #          dlg.tbConf.SetValue(False)
    #      # ga-dfa score plots
    #      if self.GetName() in ['plcGaModelPlot1']:
    #          if self.prnt.prnt.splitPrnt.type in ['DFA']:
    #              dlg.scoreSets.Enable(True)
    #      if self.GetName() in ['plcPcaLoadsV', 'plcDfaLoadsV',
    #                            'plcGaSpecLoad', 'plcPLSloading']:
    #          dlg.loadSets.Enable(True)
    #      dlg.Iconize(False)
    #      dlg.ShowModal()
    
    def on_mnu_plot_coords(self, _):
        # send coords to clipboard
        getPoints = self.last_draw[0].objects
        coords = []
        for each in getPoints:
            # noinspection PyProtectedMember
            coords.extend(each._points.tolist())
        
        data = np.array2string(coords, separator='\t')
        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(wx.TextDataObject('X\tY\n' + data))
        wx.TheClipboard.Close()
        
    def OnMouseRightDown(self, event):
        pt = event.GetPosition()
        self.PopupMenu(self.plotMenu, pt)   
    
    def OnMouseLeftDown(self, event):
        # put info in tb
        self.populate_toolbar()
        # get coords for zoom centre
        self._zoomCorner1[0], self._zoomCorner1[1] = self._getXY(event)
        self._screenCoordinates = np.array(event.GetPosition())
        if self._dragEnabled:
            self.SetCursor(self.GrabHandCursor)
            self.tbMain.canvas.CaptureMouse()
        if self._interEnabled:
            if self.last_draw is not None:
                graphics, xAxis, yAxis = self.last_draw
                xy = self.PositionScreenToUser(self._screenCoordinates)
                graphics.objects.append(
                    PolyLine([[xy[0], yAxis[0]], [xy[0], yAxis[1]]],
                             colour='red'))
                self._Draw(graphics, xAxis, yAxis)
        
    def populate_toolbar(self):
        # enable plot toolbar
        self.tbMain.Enable(True)
        self.tbMain.Refresh()
        
        # populate plot toolbar
        self.tbMain.canvas = self
        self.tbMain.graph = self.last_draw[0]
        
        self.tbMain.txtPlot.SetValue(self.tbMain.graph.title)
        self.tbMain.txtXlabel.SetValue(self.tbMain.graph.xLabel)
        self.tbMain.txtYlabel.SetValue(self.tbMain.graph.yLabel)
        
        self.tbMain.spnAxesFont.SetValue(self.fontSizeAxis)
        self.tbMain.spn_title.SetValue(self.fontSizeTitle)
        
        self.minXrange = self.xCurrentRange[0]
        self.maxXrange = self.xCurrentRange[1]
        self.minYrange = self.yCurrentRange[0]
        self.maxYrange = self.yCurrentRange[1]
        
        self.tbMain.Increment = (self.maxXrange - self.minXrange)/100
        
        self.tbMain.txtXmin.SetValue('%.2f' % self.minXrange)
        self.tbMain.txtXmax.SetValue('%.2f' % self.maxXrange)
        self.tbMain.txtYmax.SetValue('%.2f' % self.maxYrange)
        self.tbMain.txtYmin.SetValue('%.2f' % self.minYrange)
        
        # enable controls
        names = ['plcPcaLoadsV', 'plcDfaLoadsV', 'plcGaSpecLoad',
                 'plcPLSloading', 'plcGaModelPlot1', 'plcDFAscores',
                 'plcGaFeatPlot']

        if self.GetName() not in names:
            # disable for general case
            self.tbMain.tbConf.Enable(False)
            self.tbMain.tbPoints.Enable(False)
            self.tbMain.tbSymbols.Enable(False)
            
        if self.GetName() in ['plcPCAscore', 'plcGaFeatPlot']:
            self.tbMain.tbPoints.Enable(True)
            self.tbMain.tbSymbols.Enable(True)
        
        if len(self.GetName().split('plcPredPls')) > 1:
            if self.parent.prnt.prnt.prnt.data['plstype'] == 1:
                self.tbMain.tbPoints.Enable(True)
                self.tbMain.tbSymbols.Enable(True)
            else:
                self.tbMain.tbSymbols.Enable(True)
            
        if self.GetName() in ['plcDFAscores']:
            # dfa score plots
            self.tbMain.tbConf.Enable(True)
            self.tbMain.tbPoints.Enable(True)
            self.tbMain.tbSymbols.Enable(True)
        else:
            self.tbMain.tbConf.Enable(False)
            
        if len(self.GetName().split('plcGaModelPlot')) > 1:
            # ga-dfa score plots
            if self.parent.prnt.prnt.splitPrnt.dtype in ['DFA']:
                self.tbMain.tbConf.Enable(True)
                self.tbMain.tbPoints.Enable(True)
                self.tbMain.tbSymbols.Enable(True)
            else:
                self.tbMain.tbConf.Enable(False)
                self.tbMain.tbPoints.Enable(False)
                self.tbMain.tbSymbols.Enable(True)
                
        if self.GetName() in ['plcPcaLoadsV', 'plcDfaLoadsV', 'plcPLSloading']:
            self.tbMain.tbLoadLabels.Enable(True)
            self.tbMain.tbLoadLabStd1.Enable(True)
            self.tbMain.tbLoadLabStd2.Enable(True)
            self.tbMain.tbLoadSymStd2.Enable(True)
            self.tbMain.tbPoints.Enable(False)
            self.tbMain.tbSymbols.Enable(False)
        else:
            self.tbMain.tbLoadLabels.Enable(False)
            self.tbMain.tbLoadLabStd1.Enable(False)
            self.tbMain.tbLoadLabStd2.Enable(False)
            self.tbMain.tbLoadSymStd2.Enable(False)

    def enable_drag(self, value):
        """Set True to enable drag."""
        if value not in [True, False]:
            raise TypeError("Value should be True or False")
        if value:
            if self.GetEnableZoom():
                self.enableZoom = False
            if self.get_enable_interactive():
                self.enable_interactive(False)
            self.SetCursor(self.HandCursor)
        else:
            self.SetCursor(wx.CROSS_CURSOR)
        self._dragEnabled = value

    def enable_interactive(self, value):
        """Set True to enable interactive mode - RMJ 03/2008."""
        if value not in [True, False]:
            raise TypeError("Value should be True or False")
        if value:
            if self.GetEnableZoom():
                self.enableZoom = False
            if self.GetEnableDrag():
                self.enable_drag(False)
            self.SetCursor(wx.Cursor(wx.CURSOR_PENCIL))
        else:
            self.SetCursor(wx.CROSS_CURSOR)
        self._interEnabled = value

    def get_enable_interactive(self):
        return self._interEnabled
        

class Pca(wx.Panel):
    """principal component analysis

    """
    def __init__(self, parent, id_, pos, size, style, name):
        """"""
        wx.Panel.__init__(self, id=wxID_PCA, name='Pca', parent=parent,
                          pos=wx.Point(-12, 22), size=wx.Size(1024, 599),
                          style=wx.TAB_TRAVERSAL)

        _, _, _, _, _ = id_, pos, size, style, name

        self.parent = parent
        self._init_ctrls()
        self._init_sizers()

    def _init_ctrls(self):
        """"""
        self.SetClientSize(wx.Size(1016, 565))
        self.SetAutoLayout(True)
        self.SetToolTip('')

        self.plcPCeigs = MyPlotCanvas(id_=-1, name='plcPCeigs',
                                      parent=self, pos=wx.Point(589, 283),
                                      size=wx.Size(200, 200), style=0,
                                      toolbar=self.parent.parent.tbMain)
        self.plcPCeigs.SetToolTip('')
        self.plcPCeigs.fontSizeTitle = 10
        self.plcPCeigs.enableZoom = True
        self.plcPCeigs.fontSizeAxis = 8
        self.plcPCeigs.SetConstraints(
            LayoutAnchors(self.plcPCeigs, False, True, False, True))
        self.plcPCeigs.fontSizeLegend = 8

        self.plcPCvar = MyPlotCanvas(id_=-1, name='plcPCvar', parent=self,
                                     pos=wx.Point(176, 283),
                                     size=wx.Size(200, 200), style=0,
                                     toolbar=self.parent.parent.tbMain)
        self.plcPCvar.fontSizeAxis = 8
        self.plcPCvar.fontSizeTitle = 10
        self.plcPCvar.enableZoom = True
        self.plcPCvar.SetToolTip('')
        self.plcPCvar.fontSizeLegend = 8

        self.plcPCAscore = MyPlotCanvas(
            parent=self, id_=-1, name='plcPCAscore', pos=wx.Point(0, 24),
            size=wx.Size(200, 200), style=0, toolbar=self.parent.parent.tbMain)
        self.plcPCAscore.fontSizeTitle = 10
        self.plcPCAscore.fontSizeAxis = 8
        self.plcPCAscore.enableZoom = True
        self.plcPCAscore.enableLegend = True
        self.plcPCAscore.SetToolTip('')
        self.plcPCAscore.fontSizeLegend = 8

        self.plcPcaLoadsV = MyPlotCanvas(
            id_=-1, name='plcPcaLoadsV', parent=self, pos=wx.Point(0, 24),
            size=wx.Size(200, 200), style=0, toolbar=self.parent.parent.tbMain)
        self.plcPcaLoadsV.SetToolTip('')
        self.plcPcaLoadsV.fontSizeTitle = 10
        self.plcPcaLoadsV.enableZoom = True
        self.plcPcaLoadsV.fontSizeAxis = 8
        self.plcPcaLoadsV.enableLegend = True
        self.plcPcaLoadsV.fontSizeLegend = 8

        self.titleBar = TitleBar(
            self, id_=-1, text="Principal Component Analysis",
            style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT)

    def _init_sizers(self):
        """"""
        self.bxsPca1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bxsPca2 = wx.BoxSizer(orient=wx.VERTICAL)
        self.grsPca1 = wx.GridSizer(cols=2, hgap=2, rows=2, vgap=2)

        self.bxsPca1.Add(self.bxsPca2, 1, border=0, flag=wx.EXPAND)

        self.bxsPca2.Add(self.titleBar, 0, border=0, flag=wx.EXPAND)
        self.bxsPca2.Add(self.grsPca1, 1, border=0, flag=wx.EXPAND)

        self.grsPca1.Add(self.plcPCAscore, 0, border=0, flag=wx.EXPAND)
        self.grsPca1.Add(self.plcPcaLoadsV, 0, border=0, flag=wx.EXPAND)
        self.grsPca1.Add(self.plcPCvar, 0, border=0, flag=wx.EXPAND)
        self.grsPca1.Add(self.plcPCeigs, 0, border=0, flag=wx.EXPAND)
        
        self.SetSizer(self.bxsPca1)

    def reset(self):
        self.titleBar.spnNumPcs1.Enable(0)
        self.titleBar.spnNumPcs2.Enable(0)
        self.titleBar.spnNumPcs1.SetValue(1)
        self.titleBar.spnNumPcs2.SetValue(2)
        
        objects = {'plcPCeigs': ['Eigenvalues', 'Principal Component', 'Eigenvalue'],
                   'plcPCvar': ['Percentage Explained Variance',
                                'Principal Component', 'Cumulative % Variance'],
                   'plcPCAscore': ['PCA Scores', 't[1]', 't[2]'],
                   'plcPcaLoadsV': ['PCA Loading', 'w[1]', 'w[2]']}

        # noinspection PyUnusedLocal, PyTypeChecker
        curve = PolyLine([[0, 0], [1, 1]], colour='white', width=1,
                         style=wx.PENSTYLE_TRANSPARENT)
        
        for each in objects.keys():
            exec('self.' + each + '.draw(PlotGraphics([curve], ' +
                 'objects["' + each + '"][0], ' + 'objects["' + each +
                 '"][1], ' + 'objects["' + each + '"][2]))')


class TitleBar(bp.ButtonPanel):
    def __init__(self, parent, id_, text, style, alignment):
        """"""
        bp.ButtonPanel.__init__(self, parent=parent, id=-1,
                                text="Principal Component Analysis",
                                agwStyle=bp.BP_USE_GRADIENT,
                                alignment=bp.BP_ALIGN_LEFT)

        _, _, _, _ = id_, text, style, alignment

        self.data = None
        self.parent = parent
        self._init_btnpanel_ctrls()
        self.create_buttons()

    def _init_btnpanel_ctrls(self):
        """"""
        self.Bind(wx.EVT_PAINT, self.on_btnpanel_paint)
        
        bmp = wx.Bitmap(op_join('bmp', 'run.png'), wx.BITMAP_TYPE_PNG)
        self.btnRunPCA = bp.ButtonInfo(self, -1, bmp, kind=wx.ITEM_NORMAL,
                                       shortHelp='Run PCA',
                                       longHelp='Run Principal Component Analysis')
        self.btnRunPCA.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.on_btn_run_pca, id=self.btnRunPCA.GetId())

        bmp = wx.Bitmap(op_join('bmp', 'export.png'), wx.BITMAP_TYPE_PNG)
        self.btnExportPcaResults = bp.ButtonInfo(self, -1, bmp,
                                                 kind=wx.ITEM_NORMAL,
                                                 shortHelp='Export PCA Results',
                                                 longHelp='Export PCA Results')
        self.btnExportPcaResults.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.on_btn_export_pca_results,
                  id=self.btnExportPcaResults.GetId())

        choices = ['Raw spectra', 'Processed spectra']
        self.cbxData = wx.Choice(choices=choices, id=-1, name='cbxData',
                                 parent=self, pos=wx.Point(118, 23),
                                 size=wx.Size(100, 23), style=0)
        self.cbxData.SetSelection(0)
              
        self.cbxPcaType = wx.Choice(choices=['NIPALS', 'SVD'], id=-1,
                                    name='cbxPcaType', parent=self,
                                    pos=wx.Point(56, 23),
                                    size=wx.Size(64, 23), style=0)
        self.cbxPcaType.Bind(wx.EVT_COMBOBOX, self.on_cbx_pca_type, id=ID_PCATYPE)
        self.cbxPcaType.SetSelection(0)
        
        choices = ['Correlation matrix', 'Covariance matrix']
        self.cbxPreprocType = wx.Choice(choices=choices, id=-1,
                                        name='cbxPreprocType', parent=self,
                                        pos=wx.Point(118, 23),
                                        size=wx.Size(110, 23), style=0, )
        self.cbxPreprocType.SetSelection(0)
        
        self.spnPCAnum = wx.SpinCtrl(id=ID_SPNPCS, initial=3, max=100,
                                     min=3, name='spnPCAnum', parent=self,
                                     pos=wx.Point(112, 158),
                                     size=wx.Size(46, 23),
                                     style=wx.SP_ARROW_KEYS)
        self.spnPCAnum.SetToolTip('')
        self.spnPCAnum.SetValue(3)
        
        self.spnNumPcs1 = wx.SpinCtrl(id=ID_NUMPCS1, initial=1,
                                      max=100, min=1, name='spnNumPcs1',
                                      parent=self, pos=wx.Point(240, 184),
                                      size=wx.Size(46, 23),
                                      style=wx.SP_ARROW_KEYS)
        self.spnNumPcs1.Enable(0)
        self.spnNumPcs1.Bind(wx.EVT_SPINCTRL, self.on_spn_num_pcs1, id=-1)
        
        self.spnNumPcs2 = wx.SpinCtrl(id=ID_NUMPCS2, initial=1, max=100, min=1,
                                      name='spnNumPcs2', parent=self,
                                      pos=wx.Point(240, 184),
                                      size=wx.Size(46, 23),
                                      style=wx.SP_ARROW_KEYS)
        self.spnNumPcs2.Enable(0)
        self.spnNumPcs2.Bind(wx.EVT_SPINCTRL, self.on_spn_num_pcs2, id=-1)

    def create_buttons(self):
        self.Freeze()
        self.set_properties()
        style = wx.TRANSPARENT_WINDOW

        self.AddControl(self.cbxData)
        self.AddControl(self.cbxPreprocType)
        self.AddControl(self.cbxPcaType)
        self.AddControl(GenStaticText(self, -1, 'No. PCs:', style=style))
        self.AddControl(self.spnPCAnum)
        self.AddSeparator()
        self.AddControl(GenStaticText(self, -1, 'PC', style=style))
        self.AddControl(self.spnNumPcs1)
        self.AddControl(GenStaticText(self, -1, ' vs. ', style=style))
        self.AddControl(self.spnNumPcs2)
        self.AddSeparator()
        self.AddButton(self.btnRunPCA)
        self.AddSeparator()
        self.AddButton(self.btnExportPcaResults)
        
        self.Thaw()
        self.DoLayout()

    # noinspection PyMethodMayBeStatic
    def on_btnpanel_paint(self, event):
        event.Skip()
    
    def set_properties(self):

        # Sets the colours for the two demos: called only if the user didn't
        # modify the colours and sizes using the Settings Panel
        bpArt = self.GetBPArt()
        
        # set the color the text is drawn with
        bpArt.SetColour(bp.BP_TEXT_COLOUR, wx.WHITE)

        background = self.GetBackgroundColour()            
        bpArt.SetColour(bp.BP_TEXT_COLOUR, wx.BLUE)
        bpArt.SetColour(bp.BP_BORDER_COLOUR,
                        bp.BrightenColour(background, 0.85))
        bpArt.SetColour(bp.BP_SEPARATOR_COLOUR,
                        bp.BrightenColour(background, 0.85))
        bpArt.SetColour(bp.BP_BUTTONTEXT_COLOUR, wx.BLACK)
        bpArt.SetColour(bp.BP_SELECTION_BRUSH_COLOUR, wx.Colour(242, 242, 235))
        bpArt.SetColour(bp.BP_SELECTION_PEN_COLOUR, wx.Colour(206, 206, 195))

    def on_btn_run_pca(self, _):
        self.run_pca()
    
    def on_btn_export_pca_results(self, _):
        dlg = wx.FileDialog(self, "Choose a file", ".", "", 
                            "Any files (*.*)|*.*", wx.FD_SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                saveFile = dlg.GetPath()
                scrs = np.array2string(self.data['pcscores'], separator='\t')
                lods = np.array2string(self.data['pcloads'], separator='\t')
                eign = np.array2string(self.data['pceigs'], separator='\t')
                pcex = np.array2string(self.data['pcpervar'], separator='\t')
                out = '#PRINCIPAL_COMPONENT_SCORES\n' + scrs + '\n' +\
                      '#PRINCIPAL_COMPONENT_LOADINGS\n' + lods + '\n' +\
                      '#EIGENVALUES\n' + eign + '\n' +\
                      '#CUMULATIVE_PERCENTAGE_EXPLAINED_VARIANCE\n' + pcex + '\n'

                with open(saveFile, 'w') as f:
                    f.write(out)

        finally:
            dlg.Destroy()
        
    def on_cbx_pca_type(self, _):
        if self.cbxPcaType.GetSelection() == 1:
            self.spnPCAnum.Enable(0)
        else:
            self.spnPCAnum.Enable(1)
    
    def get_data(self, data):
        self.data = data
    
    def run_pca(self):
        """Run principal component analysis

        """
        xdata = None

        try:
            self.spnNumPcs1.Enable(1)
            self.spnNumPcs2.Enable(1)
            self.spnNumPcs1.SetValue(1)
            self.spnNumPcs2.SetValue(2)
            
            if self.cbxData.GetSelection() == 0:
                xdata = self.data['rawtrunc']
            elif self.cbxData.GetSelection() == 1:
                xdata = self.data['proctrunc']
            
            if self.cbxPreprocType.GetSelection() == 0:
                self.data['pcatype'] = 'covar'
            elif self.cbxPreprocType.GetSelection() == 1:
                self.data['pcatype'] = 'corr'
                
            if self.cbxPcaType.GetSelection() == 1:
                # run PCA using SVD
                scores, loads, self.data['pcpervar'], eigs = \
                    chemtrics.pca_svd(xdata, self.data['pcatype'])
                
                self.data['pcscores'] = scores[:, 0: len(eigs)]
                self.data['pcloads'] = loads[0: len(eigs), :]
                self.data['pceigs'] = eigs
                self.data['niporsvd'] = 'svd'
                                
            elif self.cbxPcaType.GetSelection() == 0:
                # run PCA using NIPALS
                self.data['pcscores'], self.data['pcloads'], self.data['pcpervar'], self.data['pceigs'] = \
                    chemtrics.pca_nipals(xdata, self.spnPCAnum.GetValue(),
                                         self.data['pcatype'],
                                         self.parent.parent.parent.sbMain)
                
                self.data['niporsvd'] = 'nip'
            
            # Enable ctrls
            self.btnExportPcaResults.Enable(1)
            self.spnNumPcs1.SetRange(1, len(self.data['pceigs']))
            self.spnNumPcs1.SetValue(1)
            self.spnNumPcs2.SetRange(1, len(self.data['pceigs']))
            self.spnNumPcs2.SetValue(2)
            
            # check for metadata & setup limits for dfa
            tbar = self.parent.parent.parent.plDfa.titleBar
            klass = self.data['class']
            if (sum(klass[:, 0]) != 0) and (klass is not None):
                tbar.cbxData.SetSelection(0)
                tbar.spnDfaPcs.SetRange(2, len(self.data['pceigs']))
                tbar.spnDfaDfs.SetRange(1, len(np.unique(klass[:, 0])) - 1)
        
            # plot results
            self.plot_pca()
            
        except Exception as error:
            error_box(self, '%s' % str(error))
            raise
            
    def plot_pca(self):
        # Plot pca scores and loadings
        pc1 = self.spnNumPcs1.GetValue()
        pc2 = self.spnNumPcs2.GetValue()

        xL = 't[' + str(pc1) + '] (' + \
             '%.2f' % (self.data['pcpervar'][pc1] -
                       self.data['pcpervar'][pc1 - 1]) + '%)'
              
        yL = 't[' + str(pc2) + '] (' + \
             '%.2f' % (self.data['pcpervar'][pc2] -
                       self.data['pcpervar'][pc2-1]) + '%)'
        
        plot_scores(self.parent.plcPCAscore, self.data['pcscores'],
                    cl=self.data['class'][:, 0],
                    labels=self.data['label'],
                    validation=self.data['validation'],
                    col1=pc1-1, col2=pc2-1, pconf=False,
                    title='PCA Scores', xLabel=xL, yLabel=yL, xval=False,
                    symb=self.parent.parent.parent.tbMain.tbSymbols.GetValue(),
                    text=self.parent.parent.parent.tbMain.tbPoints.GetValue(),
                    usecol=[], usesym=[])
        
        # Plot loadings
        if pc1 != pc2:
            plot_loads(self.parent.plcPcaLoadsV,
                       np.transpose(self.data['pcloads']),
                       xaxis=self.data['indlabels'], col1=pc1-1,
                       col2=pc2-1, title='PCA Loadings',
                       xLabel='w[' + str(pc1) + ']',
                       yLabel='w[' + str(pc2) + ']',
                       type=self.parent.prnt.parent.tbMain.get_load_plot_idx(),
                       usecol=[], usesym=[])
        else:
            idx = pc1-1
            plot_line(self.parent.plcPcaLoadsV,
                      self.data['pcloads'],
                      xaxis=self.data['xaxis'], rownum=idx, tit='PCA Loadings',
                      type='single', xLabel='Variable',
                      yLabel='w['+str(idx+1)+']', wdth=1, ledge=[])
                    
        # Plot % variance
        plot_line(self.parent.plcPCvar, np.transpose(self.data['pcpervar']),
                  xaxis=np.arange(0, len(self.data['pcpervar']))[:, nax],
                  rownum=0, tit='Percentage Explained Variance', type='single',
                  xLabel='Principal Component', yLabel='Cumulative % Variance',
                  wdth=3, ledge=[])
        
        # Plot eigenvalues
        plot_line(self.parent.plcPCeigs, np.transpose(self.data['pceigs']),
                  xaxis=np.arange(1, len(self.data['pceigs']) + 1)[:, nax],
                  rownum=0, tit='Eigenvalues', xLabel='Principal Component',
                  yLabel='Eigenvalue', wdth=3, type='single', ledge=[])
        
        # make sure ctrls enabled
        self.spnNumPcs1.Enable(True)
        self.spnNumPcs2.Enable(True)
        self.btnExportPcaResults.Enable(True)
        
    def on_spn_num_pcs1(self, _):
        pc1 = self.spnNumPcs1.GetValue()
        pc2 = self.spnNumPcs2.GetValue()
        self.plot_pca()
        set_btn_state(pc1, pc2, self.parent.prnt.prnt.tbMain)
              
    def on_spn_num_pcs2(self, _):
        pc1 = self.spnNumPcs1.GetValue()
        pc2 = self.spnNumPcs2.GetValue()
        self.plot_pca()
        set_btn_state(pc1, pc2, self.parent.prnt.prnt.tbMain)


class PlotProperties(wx.Dialog):
    """"""
    def __init__(self, parent):
        """"""
        wx.Dialog.__init__(self, id=-1, name='', parent=parent,
                           pos=wx.Point(0, 0), size=wx.Size(530, 480),
                           style=wx.MAXIMIZE_BOX | wx.DEFAULT_DIALOG_STYLE,
                           title='Plot Properties')

        self._init_plot_prop_ctrls()
        self._init_plot_prop_sizers()
        self._init_grs_df_scores()
        self._init_grs_loads()

        self.foldPnl.Expand(self.genSets)
        self.foldPnl.Collapse(self.scoreSets)
        self.foldPnl.Collapse(self.loadSets)

        self.graph = parent.last_draw[0]
        self.canvas = parent

        self.minXrange = parent.get_x_current_range()[0]
        self.maxXrange = parent.get_x_current_range()[1]
        self.minYrange = parent.get_y_current_range()[0]
        self.maxYrange = parent.get_y_current_range()[1]

        self.Increment = (self.maxXrange - self.minXrange) / 100

        self.txtXmin.SetValue('%.3f' % self.minXrange)
        self.txtXmax.SetValue('%.3f' % self.maxXrange)
        self.txtYmin.SetValue('%.3f' % self.minYrange)
        self.txtYmax.SetValue('%.3f' % self.maxYrange)

        self.txtTitle.SetValue(self.graph.get_title())
        self.txtXlabel.SetValue(self.graph.get_xlabel())
        self.txtYlabel.SetValue(self.graph.get_ylabel())

        self.spnFontSizeAxes.SetValue(parent.get_font_size_axis())
        self.spnFontSizeTitle.SetValue(parent.get_font_size_title())

        if self.canvas.get_enable_grid():
            self.tbGrid.SetValue(1)
        if self.canvas.get_enable_zoom():
            self.tbZoom.SetValue(1)
        if self.canvas.get_enable_drag():
            self.tbDrag.SetValue(1)
        if self.canvas.get_enable_point_label():
            self.tbPointLabel.SetValue(1)

    def _init_grs_df_scores(self):

        self.grsDfScores = wx.GridSizer(cols=2, hgap=4, rows=2, vgap=4)

        self._init_coll_grs_df_scores(self.grsDfScores)

        self.scorePnl.SetSizer(self.grsDfScores)

    def _init_coll_grs_df_scores(self, parent):
        # generated method, don't edit

        parent.Add(self.tbConf, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.tbPoints, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.tbSymbols, 0, border=0, flag=wx.EXPAND)
    
    def _init_grs_loads(self):
        # generated method, don't edit
        self.grsLoadings = wx.GridSizer(cols=2, hgap=4, rows=2, vgap=4)

        self._init_coll_grs_loads(self.grsLoadings)

        self.loadPnl.SetSizer(self.grsLoadings)
    
    def _init_coll_grs_loads(self, parent):
        # generated method, don't edit
        parent.Add(self.tbLoadLabels, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.tbLoadLabStd1, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.tbLoadLabStd2, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.tbLoadSymStd2, 0, border=0, flag=wx.EXPAND)
        
    def _init_coll_gbs_plot_props(self, parent):
        # generated method, don't edit
        flag = wx.EXPAND
        parent.Add(self.stTitle, (0, 0), border=4, flag=flag, span=(1, 1))
        parent.Add(self.txtTitle, (0, 1), border=4, flag=flag, span=(1, 5))
        parent.Add(wx.StaticText(self.genPnl, -1, 'Axes font',
                                 style=wx.ALIGN_LEFT),
                   (1, 0), flag=flag, span=(1, 1))
        parent.Add(self.spnFontSizeAxes, (1, 1), border=4, flag=flag,
                   span=(1, 1))
        parent.Add(wx.StaticText(self.genPnl, -1, 'Title font',
                                 style=wx.ALIGN_LEFT),
                   (1, 2), flag=flag, span=(1, 1))
        parent.Add(self.spnFontSizeTitle, (1, 3), border=4, flag=flag,
                   span=(1, 1))
        parent.Add(self.stXlabel, (2, 0), border=4, flag=flag, span=(1, 1))
        parent.Add(self.txtXlabel, (2, 1), border=4, flag=flag, span=(1, 5))
        parent.Add(self.stYlabel, (3, 0), border=4, flag=flag, span=(1, 1))
        parent.Add(self.txtYlabel, (3, 1), border=4, flag=flag, span=(1, 5))
        parent.Add(self.stXfrom, (4, 0), border=4, flag=flag, span=(1, 1))
        parent.Add(self.txtXmin, (4, 1), border=4, flag=flag, span=(1, 1))
        parent.Add(self.spnXmin, (4, 2), border=4, flag=flag, span=(1, 1))
        parent.Add(self.stXto, (4, 3), border=4, flag=flag, span=(1, 1))
        parent.Add(self.txtXmax, (4, 4), border=4, flag=flag, span=(1, 1))
        parent.Add(self.spnXmax, (4, 5), border=4, flag=flag, span=(1, 1))
        parent.Add(self.stYfrom, (5, 0), border=4, flag=flag, span=(1, 1))
        parent.Add(self.txtYmin, (5, 1), border=4, flag=flag, span=(1, 1))
        parent.Add(self.spnYmin, (5, 2), border=4, flag=flag, span=(1, 1))
        parent.Add(self.stYto, (5, 3), border=4, flag=flag, span=(1, 1))
        parent.Add(self.txtYmax, (5, 4), border=4, flag=flag, span=(1, 1))
        parent.Add(self.spnYmax, (5, 5), border=4, flag=flag, span=(1, 1))
        parent.Add(self.tbDrag, (6, 1), border=4, flag=flag, span=(1, 1))
        parent.Add(self.tbGrid, (6, 2), border=4, flag=flag, span=(1, 1))
        parent.Add(self.tbPointLabel, (6, 3), border=4, flag=flag, span=(1, 1))
        parent.Add(self.tbZoom, (6, 4), border=4, flag=flag, span=(1, 1))
        parent.Add(self.cbApply, (7, 0), border=4, flag=flag, span=(1, 1))
        parent.Add(self.btnApply, (7, 1), border=4, flag=flag, span=(1, 5))
        # parent.AddSpacer(wx.Size(8, 8), (8, 0), flag=flag, span=(2, 6))

    # noinspection PyMethodMayBeStatic
    def _init_coll_gbs_plot_props_growables(self, parent):
        # generated method, don't edit
        for col in range(6):
            parent.AddGrowableCol(col)

    def _init_plot_prop_sizers(self):
        # generated method, don't edit
        self.gbsPlotProps = wx.GridBagSizer(8, 8)
        self.gbsPlotProps.SetCols(6)
        self.gbsPlotProps.SetRows(6)
        self.gbsPlotProps.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)
        self.gbsPlotProps.SetMinSize(wx.Size(250, 439))
        self.gbsPlotProps.SetEmptyCellSize(wx.Size(0, 0))
        self.gbsPlotProps.SetFlexibleDirection(wx.HORIZONTAL)

        self._init_coll_gbs_plot_props(self.gbsPlotProps)
        self._init_coll_gbs_plot_props_growables(self.gbsPlotProps)

        self.genPnl.SetSizer(self.gbsPlotProps)

    def _init_plot_prop_ctrls(self):

        self.SetAutoLayout(True)
        
        self.foldPnl = fpb.FoldPanelBar(self, -1, wx.DefaultPosition,
                                        (525, 450),
                                        fpb.FPB_EXCLUSIVE_FOLD)
        self.foldPnl.SetConstraints(
            LayoutAnchors(self.foldPnl, True, True, True, True))
        self.foldPnl.SetAutoLayout(True)
        
        icons = wx.ImageList(16, 16)
        icons.Add(wx.Bitmap(op_join('bmp', 'arrown.png'), wx.BITMAP_TYPE_PNG))
        icons.Add(wx.Bitmap(op_join('bmp', 'arrows.png'), wx.BITMAP_TYPE_PNG))
        
        self.genSets = self.foldPnl.AddFoldPanel("General properties", 
                                                 collapsed=True,
                                                 foldIcons=icons)
        
        self.scoreSets = self.foldPnl.AddFoldPanel("Score plots", 
                                                   collapsed=True,
                                                   foldIcons=icons)
        self.scoreSets.Enable(False)
        
        self.loadSets = self.foldPnl.AddFoldPanel("Loadings plots", 
                                                  collapsed=True,
                                                  foldIcons=icons)
        self.loadSets.Enable(False)
        
        self.genPnl = wx.Panel(id=-1, name='genPnl', parent=self.genSets,
                               pos=wx.Point(0, 0), size=wx.Size(20, 250),
                               style=wx.TAB_TRAVERSAL)
        self.genPnl.SetToolTip('')
        
        self.scorePnl = wx.Panel(id=-1, name='scorePnl', parent=self.scoreSets,
                                 pos=wx.Point(0, 0), size=wx.Size(20, 100),
                                 style=wx.TAB_TRAVERSAL)
        self.scorePnl.SetToolTip('')     
        
        self.loadPnl = wx.Panel(id=-1, name='loadPnl', parent=self.loadSets,
                                pos=wx.Point(0, 0), size=wx.Size(20, 100),
                                style=wx.TAB_TRAVERSAL)
        self.loadPnl.SetToolTip('')     
        
        self.stTitle = wx.StaticText(id=-1, label='Title', name=u'stTitle',
                                     parent=self.genPnl, pos=wx.Point(0, 0),
                                     size=wx.Size(21, 24), style=0)
        self.stTitle.SetToolTip('')

        self.stYfrom = wx.StaticText(id=-1, label=u'Y-Axis From:',
                                     name=u'stYfrom', parent=self.genPnl,
                                     pos=wx.Point(0, 131), size=wx.Size(42, 24),
                                     style=0)
        self.stYfrom.SetToolTip('')

        self.stYto = wx.StaticText(id=-1, label='To:', name=u'stYto',
                                   parent=self.genPnl, pos=wx.Point(144, 131),
                                   size=wx.Size(40, 21), style=0)
        self.stYto.SetToolTip('')

        self.stXfrom = wx.StaticText(id=-1, label=u'X-Axis From:',
                                     name=u'stXfrom', parent=self.genPnl,
                                     pos=wx.Point(0, 103), size=wx.Size(40, 21),
                                     style=0)
        self.stXfrom.SetToolTip('')

        self.stXto = wx.StaticText(id=-1, label='To:', name=u'stXto',
                                   parent=self.genPnl, pos=wx.Point(144, 103),
                                   size=wx.Size(40, 21), style=0)
        self.stXto.SetToolTip('')

        self.stXlabel = wx.StaticText(id=-1, label='X label', name=u'stXlabel',
                                      parent=self.genPnl, pos=wx.Point(0, 53),
                                      size=wx.Size(40, 21), style=0)
        self.stXlabel.SetToolTip('')

        self.stYlabel = wx.StaticText(id=-1, label='Y label', name=u'stYlabel',
                                      parent=self.genPnl, pos=wx.Point(0, 78),
                                      size=wx.Size(40, 21), style=0)
        self.stYlabel.SetToolTip('')

        self.txtTitle = wx.TextCtrl(id=-1, name='txtTitle', parent=self.genPnl,
                                    pos=wx.Point(15, 0), size=wx.Size(40, 21),
                                    style=0, value='')
        self.txtTitle.SetToolTip('')
        self.txtTitle.Bind(wx.EVT_TEXT, self.on_txt_title)

        self.txtYlabel = wx.TextCtrl(id=-1, name='txtYlabel', parent=self.genPnl,
                                     pos=wx.Point(15, 78), size=wx.Size(40, 21),
                                     style=0, value='')
        self.txtYlabel.SetToolTip('')

        self.txtXlabel = wx.TextCtrl(id=-1, name='txtXlabel',
                                     parent=self.genPnl, pos=wx.Point(15, 53),
                                     size=wx.Size(40, 21), style=0, value='')
        self.txtXlabel.SetToolTip('')

        self.txtXmin = wx.TextCtrl(id=-1, name='txtXmin',
                                   parent=self.genPnl, pos=wx.Point(15, 103),
                                   size=wx.Size(40, 21), style=0, value='')
        self.txtXmin.SetToolTip('')

        self.spnXmin = wx.SpinButton(id=-1, name='spnXmin',
                                     parent=self.genPnl, pos=wx.Point(96, 103),
                                     size=wx.Size(15, 21), style=wx.SP_VERTICAL)
        self.spnXmin.SetToolTip('')
        self.spnXmin.Bind(wx.EVT_SPIN_DOWN, self.on_spn_xmin_down)
        self.spnXmin.Bind(wx.EVT_SPIN_UP, self.on_spn_xmin_up)
        self.spnXmin.Bind(wx.EVT_SPIN, self.on_spn_xmin)

        self.spnXmax = wx.SpinButton(id=-1, name='spnXmax',
                                     parent=self.genPnl, pos=wx.Point(240, 103),
                                     size=wx.Size(15, 21), style=wx.SP_VERTICAL)
        self.spnXmax.SetToolTip('')
        self.spnXmax.Bind(wx.EVT_SPIN_DOWN, self.on_spn_xmax_down)
        self.spnXmax.Bind(wx.EVT_SPIN_UP, self.on_spn_xmax_up)
        self.spnXmax.Bind(wx.EVT_SPIN, self.on_spn_xmax)

        self.spnYmax = wx.SpinButton(id=-1, name='spnYmax',
                                     parent=self.genPnl, pos=wx.Point(240, 131),
                                     size=wx.Size(15, 21), style=wx.SP_VERTICAL)
        self.spnYmax.SetToolTip('')
        self.spnYmax.Bind(wx.EVT_SPIN_DOWN, self.on_spn_ymax_down)
        self.spnYmax.Bind(wx.EVT_SPIN_UP, self.on_spn_ymax_up)
        self.spnYmax.Bind(wx.EVT_SPIN, self.on_spn_ymax)

        self.spnYmin = wx.SpinButton(id=-1, name='spnYmin',
                                     parent=self.genPnl, pos=wx.Point(96, 131),
                                     size=wx.Size(15, 21), style=wx.SP_VERTICAL)
        self.spnYmin.SetToolTip('')
        self.spnYmin.Bind(wx.EVT_SPIN_DOWN, self.on_spn_ymin_down)
        self.spnYmin.Bind(wx.EVT_SPIN_UP, self.on_spn_ymin_up)
        self.spnYmin.Bind(wx.EVT_SPIN, self.on_spn_ymin)

        self.txtXmax = wx.TextCtrl(id=-1, name='txtXmax', parent=self.genPnl,
                                   pos=wx.Point(192, 103), size=wx.Size(40, 21),
                                   style=0, value='')
        self.txtXmax.SetToolTip('')

        self.txtYmax = wx.TextCtrl(id=-1, name='txtYmax', parent=self.genPnl,
                                   pos=wx.Point(192, 131), size=wx.Size(40, 21),
                                   style=0, value='')
        self.txtYmax.SetToolTip('')

        self.txtYmin = wx.TextCtrl(id=-1, name='txtYmin',
                                   parent=self.genPnl, pos=wx.Point(15, 131),
                                   size=wx.Size(40, 21), style=0, value='')
        self.txtYmin.SetToolTip('')

        self.stFont = wx.StaticText(id=-1, name=u'stFont',
                                    label='Font size axes and title (pt)',
                                    parent=self.genPnl, pos=wx.Point(0, 28),
                                    size=wx.Size(40, 21), style=0)
        self.stFont.SetToolTip('')

        self.spnFontSizeAxes = wx.SpinCtrl(id=-1, name='spnFontSizeAxes',
                                           initial=8, max=76, min=4,
                                           parent=self.genPnl,
                                           pos=wx.Point(15, 28),
                                           size=wx.Size(40, 21),
                                           style=wx.SP_ARROW_KEYS)
        self.spnFontSizeAxes.SetToolTip('')
        self.spnFontSizeAxes.SetValue(8)
        self.spnFontSizeAxes.SetRange(4, 76)
        self.spnFontSizeAxes.Bind(wx.EVT_SPIN, self.on_spn_font_size_axes)
        
        self.spnFontSizeTitle = wx.SpinCtrl(id=-1, initial=8, max=76, min=4,
                                            name='spnFontSizeTitle',
                                            parent=self.genPnl,
                                            pos=wx.Point(15, 28),
                                            size=wx.Size(40, 21),
                                            style=wx.SP_ARROW_KEYS)
        self.spnFontSizeTitle.SetToolTip('')
        self.spnFontSizeTitle.SetValue(8)
        self.spnFontSizeTitle.SetRange(4, 76)
        self.spnFontSizeTitle.Bind(wx.EVT_SPIN, self.on_spn_font_size_title)
        
        self.tbGrid = wxTogBut(id=-1, name='tbGrid', label='Grid',
                               parent=self.genPnl, pos=wx.Point(248, 48),
                               size=wx.Size(40, 21), style=0)
        self.tbGrid.SetValue(False)
        self.tbGrid.SetToolTip('')
        self.tbGrid.Bind(wx.EVT_BUTTON, self.on_tb_grid)
              
        self.tbDrag = wxTogBut(id=-1, name='tbDrag', label='Drag',
                               parent=self.genPnl, pos=wx.Point(248, 48),
                               size=wx.Size(40, 21), style=0)
        self.tbDrag.SetValue(False)
        self.tbDrag.SetToolTip('')
        self.tbDrag.Bind(wx.EVT_BUTTON, self.on_tb_drag_button)
        
        self.tbPointLabel = wxTogBut(id=-1, label='Points',
                                     name='tbPointLabel', parent=self.genPnl,
                                     pos=wx.Point(248, 48),
                                     size=wx.Size(40, 21), style=0)
        self.tbPointLabel.SetValue(False)
        self.tbPointLabel.SetToolTip('')
        self.tbPointLabel.Bind(wx.EVT_BUTTON, self.on_tb_point_label)
        
        self.tbZoom = wxTogBut(id=-1, label='zoom', name='tbZoom',
                               parent=self.genPnl, pos=wx.Point(248, 48),
                               size=wx.Size(40, 21), style=0)
        self.tbZoom.SetValue(True)
        self.tbZoom.SetToolTip('')
        self.tbZoom.Bind(wx.EVT_BUTTON, self.on_tb_zoom_button)
        
        self.cbApply = wx.CheckBox(id=-1, name='cbApply',
                                   label='Immediate Apply',
                                   parent=self.genPnl, pos=wx.Point(48, 96),
                                   size=wx.Size(70, 13), style=0)
        
        self.btnApply = wx.Button(id=-1, label='Apply & Close',
                                  name='btnApply', parent=self.genPnl,
                                  pos=wx.Point(192, 136),
                                  size=wx.Size(40, 21), style=0)
        self.btnApply.Bind(wx.EVT_BUTTON, self.on_btn_apply)
        
        self.tbConf = wxTogBut(id=-1, name='tbConf',
                               label='95% Confidence Circles',
                               parent=self.scorePnl, pos=wx.Point(248, 48),
                               size=wx.Size(40, 21))
        self.tbConf.SetValue(True)
        self.tbConf.SetToolTip('')
        self.tbConf.Bind(wx.EVT_BUTTON, self.on_tb_conf)
        
        self.tbPoints = wxTogBut(id=-1, label='Labels',
                                 name='tbPoints', parent=self.scorePnl,
                                 pos=wx.Point(248, 48), size=wx.Size(40, 21))
        self.tbPoints.SetValue(True)
        self.tbPoints.SetToolTip('')
        self.tbPoints.Bind(wx.EVT_BUTTON, self.on_tb_points)
        
        self.tbSymbols = wxTogBut(id=-1, name='tbSymbols', label='Symbols',
                                  parent=self.scorePnl, pos=wx.Point(248, 48),
                                  size=wx.Size(40, 21))
        self.tbSymbols.SetValue(False)
        self.tbSymbols.SetToolTip('')
        self.tbSymbols.Bind(wx.EVT_BUTTON, self.on_tb_symbols)
        
        self.tbLoadLabels = wx.Button(id=-1, name='tbLoadLabels',
                                      label='Labels', parent=self.loadPnl,
                                      pos=wx.Point(248, 48),
                                      size=wx.Size(40, 21))
        self.tbLoadLabels.SetToolTip('')
        self.tbLoadLabels.Bind(wx.EVT_BUTTON, self.on_tb_load_labels)
        
        self.tbLoadLabStd1 = wx.Button(id=-1, name='tbLoadLabStd1',
                                       label='Labels & 1 Std',
                                       parent=self.loadPnl,
                                       pos=wx.Point(248, 48),
                                       size=wx.Size(40, 21))
        self.tbLoadLabStd1.SetToolTip('')
        self.tbLoadLabStd1.Bind(wx.EVT_BUTTON, self.on_tb_load_lab_std1)
        
        self.tbLoadLabStd2 = wx.Button(id=-1, name='tbLoadLabStd2',
                                       label='Labels & 2 Std',
                                       parent=self.loadPnl,
                                       pos=wx.Point(248, 48),
                                       size=wx.Size(40, 21))
        self.tbLoadLabStd2.SetToolTip('')
        self.tbLoadLabStd2.Bind(wx.EVT_BUTTON, self.on_tb_load_lab_std2)
        
        self.tbLoadSymStd2 = wx.Button(id=-1, label='Symbols & 2 Std',
                                       name='tbLoadSymStd2',
                                       parent=self.loadPnl,
                                       pos=wx.Point(248, 48),
                                       size=wx.Size(40, 21))
        self.tbLoadSymStd2.SetToolTip('')
        self.tbLoadSymStd2.Bind(wx.EVT_BUTTON, self.on_tb_load_sym_std2)
        
        style = fpb.FPB_ALIGN_WIDTH
        self.foldPnl.AddFoldPanelWindow(self.genSets, self.genPnl, style)
        self.foldPnl.AddFoldPanelWindow(self.scoreSets, self.scorePnl, style)
        self.foldPnl.AddFoldPanelWindow(self.loadSets, self.loadPnl, style)
        
        #  self.btnFont = wx.Button(id_=-1, label='Font',
        #        name='btnFont', parent=self.genSets, pos=wx.Point(192, 136),
        #        size=wx.Size(40, 21), style=0)
        #  self.btnFont.Bind(wx.EVT_BUTTON, self.OnBtnFont)
    
    def on_tb_load_labels(self, _):
        # plot loadings
        self.do_plot(loadType=0)
        
    def on_tb_load_lab_std1(self, _):
        # plot loadings
        self.do_plot(loadType=1)
        
    def on_tb_load_lab_std2(self, _):
        # plot loadings
        self.do_plot(loadType=2)
        
    def on_tb_load_sym_std2(self, _):
        # plot loadings
        self.do_plot(loadType=3)
        
    def on_tb_conf(self, _):
        if (self.tbPoints.GetValue() is False) & \
              (self.tbConf.GetValue() is False) & \
              (self.tbSymbols.GetValue() is False) is False:
            # plot scores
            self.do_plot()
        
    def on_tb_points(self, _):
        if (self.tbPoints.GetValue() is False) & \
              (self.tbConf.GetValue() is False) & \
              (self.tbSymbols.GetValue() is False) is False:
            # plot scores
            self.do_plot()
    
    def on_tb_symbols(self, _):
        if (self.tbPoints.GetValue() is False) & \
              (self.tbConf.GetValue() is False) & \
              (self.tbSymbols.GetValue() is False) is False:
            # plot scores
            self.do_plot()
    
    def do_plot(self, loadType=0):
        tbar = self.canvas.prnt.titleBar
        ptbar = self.canvas.prnt.prnt.splitPrnt.titleBar
        pprnt = self.canvas.prnt.prnt.prnt.splitPrnt
        if self.canvas.GetName() in ['plcDFAscores']:
            plot_scores(self.canvas, tbar.data['dfscores'],
                        cl=tbar.data['class'][:, 0],
                        labels=tbar.data['label'],
                        validation=tbar.data['validation'],
                        col1=tbar.spnDfaScore1.GetValue() - 1,
                        col2=tbar.spnDfaScore2.GetValue() - 1,
                        title=self.graph.title, xLabel=self.graph.xLabel,
                        yLabel=self.graph.yLabel,
                        xval=tbar.cbDfaXval.GetValue(),
                        text=self.tbPoints.GetValue(),
                        pconf=self.tbConf.GetValue(),
                        symb=self.tbSymbols.GetValue(), usecol=[], usesym=[])
        
        elif self.canvas.GetName() in ['plcPCAscore']:
            plot_scores(self.canvas, tbar.data['pcscores'],
                        cl=tbar.data['class'][:, 0],
                        labels=tbar.data['label'],
                        validation=tbar.data['validation'],
                        col1=tbar.spnNumPcs1.GetValue() - 1,
                        col2=tbar.spnNumPcs2.GetValue() - 1,
                        title=self.graph.title, xLabel=self.graph.xLabel,
                        yLabel=self.graph.yLabel, xval=False,
                        text=self.tbPoints.GetValue(), pconf=False,
                        symb=self.tbSymbols.GetValue(), usecol=[], usesym=[])
        
        elif len(self.GetName().split('plcPredPls')) > 1:
            self.canvas = plot_pls_model(self.canvas, model='full',
                                         tbar=self.canvas.prnt.prnt.prnt.prnt.tbMain,
                                         cL=tbar.data['class'][:, nax],
                                         label=tbar.data['label'],
                                         scores=tbar.data['plst'],
                                         predictions=tbar.data['plspred'],
                                         validation=np.array(tbar.data['validation'], 'i')[:, nax],
                                         RMSEPT=tbar.data['RMSEPT'],
                                         factors=tbar.data['plsfactors'],
                                         type=tbar.data['plstype'],
                                         col1=tbar.spnPLSfactor1.GetValue() - 1,
                                         col2=tbar.spnPLSfactor2.GetValue() - 1,
                                         symbols=self.tbSymbols.GetValue(),
                                         usetxt=self.tbPoints.GetValue(),
                                         plScL=tbar.data['pls_class'])
            
        elif self.canvas.GetName() in ['plcGaFeatPlot']:
            plot_scores(self.canvas, ptbar.data['gavarcoords'],
                        cl=ptbar.data['class'][:, 0],
                        labels=ptbar.data['label'],
                        validation=ptbar.data['validation'],
                        col1=0, col2=1, title=self.graph.title,
                        xLabel=self.graph.xLabel, yLabel=self.graph.yLabel,
                        xval=True, text=self.tbPoints.GetValue(), pconf=False,
                        symb=self.tbSymbols.GetValue(), usecol=[], usesym=[])
        
        elif len(self.GetName().split('plcGaModelPlot')) > 1:
            if self.canvas.prnt.prnt.splitPrnt.type in ['DFA']:
                plot_scores(self.canvas, ptbar.data['gadfadfscores'],
                            cl=ptbar.data['class'][:, 0],
                            labels=ptbar.data['label'],
                            validation=ptbar.data['validation'],
                            col1=ptbar.spnGaScoreFrom.GetValue() - 1,
                            col2=ptbar.spnGaScoreTo.GetValue() - 1,
                            title=self.graph.title, xLabel=self.graph.xLabel,
                            yLabel=self.graph.yLabel, xval=True,
                            text=self.tbPoints.GetValue(),
                            pconf=self.tbConf.GetValue(),
                            symb=self.tbSymbols.GetValue(), usecol=[], usesym=[])
            else:
                self.canvas = plot_pls_model(self.canvas, model='ga',
                                             tbar=self.canvas.prnt.prnt.splitPrnt.prnt.prnt.tbMain,
                                             cL=ptbar.data['class'][:, 0],
                                             scores=None,
                                             label=ptbar.data['label'],
                                             predictions=ptbar.data['gaplsscores'],
                                             validation=ptbar.data['validation'],
                                             RMSEPT=ptbar.data['gaplsrmsept'],
                                             factors=ptbar.data['gaplsfactors'],
                                             type=0, col1=ptbar.spnGaScoreFrom.GetValue()-1,
                                             col2=ptbar.spnGaScoreTo.GetValue()-1,
                                             symbols=self.tbSymbols.GetValue(),
                                             usetxt=self.tbPoints.GetValue(),
                                             usecol=[], usesym=[],
                                             plScL=ptbar.data['pls_class'])
        
        elif self.canvas.GetName() in ['plcPcaLoadsV']:
            plot_loads(self.canvas, np.transpose(tbar.data['pcloads']),
                       xaxis=tbar.data['indlabels'],
                       col1=tbar.spnNumPcs1.GetValue()-1,
                       col2=tbar.spnNumPcs2.GetValue()-1,
                       title=self.graph.title, xLabel=self.graph.xLabel,
                       yLabel=self.graph.yLabel, type=loadType,
                       usecol=[], usesym=[])
        
        elif self.canvas.GetName() in ['plcPLSloading']:
            plot_loads(self.canvas, tbar.data['plsloads'],
                       xaxis=tbar.data['indlabels'],
                       col1=tbar.spnPLSfactor1.GetValue()-1,
                       col2=tbar.spnPLSfactor2.GetValue()-1,
                       title=self.graph.title, xLabel=self.graph.xLabel,
                       yLabel=self.graph.yLabel, type=loadType,
                       usecol=[], usesym=[])
                  
        elif self.canvas.GetName() in ['plcDfaLoadsV']:
            plot_loads(self.canvas, tbar.data['dfloads'],
                       xaxis=tbar.data['indlabels'],
                       col1=tbar.spnDfaScore1.GetValue() - 1,
                       col2=tbar.spnDfaScore2.GetValue() - 1,
                       title=self.graph.title, xLabel=self.graph.xLabel,
                       yLabel=self.graph.yLabel, type=loadType,
                       usecol=[], usesym=[])
        
        elif self.canvas.GetName() in ['plcGaSpecLoad']:
            if pprnt.type in ['DFA']:
                labels = []
                for each in pprnt.titleBar.data['gacurrentchrom']:
                    labels.append(pprnt.titleBar.data['indlabels'][int(each)])

                plot_loads(self.canvas, pprnt.titleBar.data['gadfadfaloads'],
                           xaxis=labels, title=self.graph.title,
                           xLabel=self.graph.xLabel, yLabel=self.graph.yLabel,
                           type=loadType, usecol=[], usesym=[])
                      
        elif self.canvas.GetName() in ['plcGaSpecLoad']:
            if self.canvas.prnt.prnt.splitPrnt.type in ['PLS']:
                labels = []
                for each in pprnt.titleBar.data['gacurrentchrom']:
                    labels.append(pprnt.titleBar.data['indlabels'][int(each)])

                plot_loads(self.canvas, ptbar.data['gaplsplsloads'],
                           xaxis=labels, title=self.graph.title,
                           xLabel=self.graph.xLabel, yLabel=self.graph.yLabel,
                           type=loadType, usecol=[], usesym=[])
        
    # def OnBtnFont(self, event):
    #     data = wx.FontData()
    #     data.EnableEffects(True)
    #     data.SetColour(self.canvas.GetForegroundColour())
    #     data.SetInitialFont(self.canvas.GetFont())
    #
    #     dlg = wx.FontDialog(self, data)
    #     if dlg.ShowModal() == wx.ID_OK:
    #         self.font = dlg.GetFontData().GetChosenFont()
    #         self.colour = dlg.GetFontData().GetColour()
    #
    #     if self.cbApply.GetValue() is True:
    #         self.canvas.SetFont(self.font)
    #         self.canvas.SetForegroundColour(self.colour)
    #         self.canvas.redraw()
    
    def on_txt_title(self, _):
        if self.cbApply.GetValue() is True:
            self.graph.set_title(self.txtTitle.GetValue())
            self.canvas.redraw()
            
    def on_tb_grid(self, _):
        self.canvas.enable_grid(self.tbGrid.GetValue())
    
    def on_tb_drag_button(self, _):
        self.canvas.enable_drag(self.tbDrag.GetValue())
    
    def on_tb_point_label(self, _):
        self.canvas.enable_point_label(self.tbPointLabel.GetValue())
    
    def on_tb_zoom_button(self, _):
        self.canvas.enable_zoom(self.tbZoom.GetValue())
        
    def on_btn_apply(self, _):
        self.canvas.font_size_axis = self.spnFontSizeAxes.GetValue()
        self.canvas.font_size_title = self.spnFontSizeTitle.GetValue()
        
        self.graph.set_title(self.txtTitle.GetValue())
        self.graph.set_xlabel(self.txtXlabel.GetValue())
        self.graph.set_ylabel(self.txtYlabel.GetValue())
        
        xmin = float(self.txtXmin.GetValue())
        xmax = float(self.txtXmax.GetValue())
        ymin = float(self.txtYmin.GetValue())
        ymax = float(self.txtYmax.GetValue())

        if (xmin < xmax) and (ymin < ymax):
            self.canvas.last_draw = [self.canvas.last_draw[0],
                                     np.array([xmin, xmax]),
                                     np.array([ymin, ymax])]
        self.canvas.redraw()
        self.Close()
    
    def on_spn_font_size_axes(self, _):
        if self.cbApply.GetValue() is True:
            self.canvas.font_size_axis = self.spnFontSizeAxes.GetValue()
            self.canvas.redraw()
        
    def on_spn_font_size_title(self, _):
        if self.cbApply.GetValue() is True:
            self.canvas.font_size_title = self.spnFontSizeTitle.GetValue()
            self.canvas.redraw()
    
    def resize_axes(self):
        xmin = float(self.txtXmin.GetValue())
        xmax = float(self.txtXmax.GetValue())
        ymin = float(self.txtYmin.GetValue())
        ymax = float(self.txtYmax.GetValue())

        if (xmin < xmax) and (ymin < ymax) and self.cbApply.GetValue():
            self.canvas.last_draw = [self.canvas.last_draw[0],
                                     np.array([xmin, xmax]),
                                     np.array([ymin, ymax])]
        self.canvas.redraw()
    
    def on_spn_xmin(self, _):
        self.resize_axes()
    
    def on_spn_xmax(self, _):
        self.resize_axes()
    
    def on_spn_ymin(self, _):
        self.resize_axes()
    
    def on_spn_ymax(self, _):
        self.resize_axes()
    
    def on_spn_xmin_up(self, _):
        curr = float(self.txtXmin.GetValue())
        curr = curr + self.Increment
        self.txtXmin.SetValue('%.3f' % curr)

    def on_spn_xmin_down(self, _):
        curr = float(self.txtXmin.GetValue())
        curr = curr - self.Increment
        self.txtXmin.SetValue('%.3f' % curr)

    def on_spn_xmax_up(self, _):
        curr = float(self.txtXmax.GetValue())
        curr = curr + self.Increment
        self.txtXmax.SetValue('%.3f' % curr)

    def on_spn_xmax_down(self, _):
        curr = float(self.txtXmax.GetValue())
        curr = curr - self.Increment
        self.txtXmax.SetValue('%.3f' % curr)

    def on_spn_ymax_up(self, _):
        curr = float(self.txtYmax.GetValue())
        curr = curr + self.Increment
        self.txtYmax.SetValue('%.3f' % curr)

    def on_spn_ymax_down(self, _):
        curr = float(self.txtYmax.GetValue())
        curr = curr - self.Increment
        self.txtYmax.SetValue('%.3f' % curr)

    def on_spn_ymin_up(self, _):
        curr = float(self.txtYmin.GetValue())
        curr = curr + self.Increment
        self.txtYmin.SetValue('%.3f' % curr)

    def on_spn_ymin_down(self, _):
        curr = float(self.txtYmin.GetValue())
        curr = curr - self.Increment
        self.txtYmin.SetValue('%.3f' % curr)


if __name__ == '__main__':
    app = wx.App()
    # This needs parameters to work
    # noinspection PyTypeChecker
    props = PlotProperties(None)
    app.MainLoop()

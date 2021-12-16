#-----------------------------------------------------------------------------
# Name:        plotSpectra.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2007/05/22
# RCS-ID:      $Id: plotSpectra.py,v 1.16 2009/02/26 23:20:33 rmj01 Exp $
# Copyright:   (c) 2007
# Licence:     GNU General Public Licence
#-----------------------------------------------------------------------------
#Boa:FramePanel:plotSpectra

import wx
# import wx.combo
import wx.lib.plot
import wx.lib.agw.buttonpanel as bp
# import wx.lib.agw.foldpanelbar as fpb
# import wx.lib.agw.customtreectrl as ctc

from wx.lib.anchors import LayoutAnchors

import scipy as sp
import string
import os
import copy
# import mva.process

from scipy import newaxis as nax
from Pca import MyPlotCanvas
from Pca import plotLine

[IDPLOTSPEC, ID_ADDPROCESSMETHOD, ID_PPTYPE, ID_PPMETHOD, ID_VALSLIDE
] = [wx.NewId() for _init_ctrls in range(5)]

def error_box(window, error):
    dlg = wx.MessageDialog(window,
                           string.join(('The following error occured:\n\n',error),''),
                           'Error!', wx.OK | wx.ICON_ERROR)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()

def GridRowDel(grid, data):
    # delete user defined variable row from grdIndLabels
    try:
        row = grid.GetSelectedRows()[0]
        lab = grid.GetRowLabelValue(row)
        if len(lab.split('U')) > 1:
            # count user def vars
            count = 1
            for r in range(1,grid.GetNumberRows()):
                if len(grid.GetRowLabelValue(r).split('U')) > 1:
                    count += 1
                else:
                    break
            data['raw'] = sp.delete(data['raw'],row-2,1)
            data['proc'] = sp.delete(data['proc'],row-2,1)
            grid.DeleteRows(row,1)
            # renumber rows
            ncount = 1
            for r in range(1,count-1):
                grid.SetRowLabelValue(r,'U'+str(ncount))
                ncount += 1
            ncount = 1
            for r in range(count-1,grid.GetNumberRows()):
                grid.SetRowLabelValue(r,str(ncount))
                ncount += 1
        else:
            pass
    except:
        pass

class PeakCalculations(wx.Dialog):
    def _init_pc_sizers(self):
        # generated method, don't edit
        self.grsPeakCalcs = wx.GridSizer(cols=2, hgap=2, rows=4, vgap=2)

        self._init_coll_grsPeakCalcs_Items(self.grsPeakCalcs)

        self.SetSizer(self.grsPeakCalcs)

    def _init_coll_grsPeakCalcs_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.btnIntensity, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.btnIntensityFit, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.btnAreaAxis, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.btnAreaFitAxis, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.btnAreaBaseline, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.btnAreaFitBaseline, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.btnCalculate, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.btnCancel, 0, border=0, flag=wx.EXPAND)

    def _init_pc_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=-1, name='', parent=prnt,
              pos=wx.Point(471, 248), size=wx.Size(264, 165),
              style=wx.DIALOG_MODAL | wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.CAPTION | wx.MAXIMIZE_BOX,
              title='Peak Calculations')
        self.SetClientSize(wx.Size(258, 133))
        self.Center(wx.BOTH)

        self.btnIntensity = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join('bmp','peakimax.png')),
              id=-1, name='btnIntensity', parent=self, pos=wx.Point(0, 0), 
              size=wx.Size(128, 31), style=0)
        self.btnIntensity.SetToggle(True)
        self.btnIntensity.SetLabel('')
        self.btnIntensity.SetToolTip('Calculate the maximum intensity in the selected region')

        self.btnAreaAxis = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join('bmp','peakareaaxis.png')),
              id=-1, name='btnAreaAxis', parent=self, pos=wx.Point(130, 0), 
              size=wx.Size(128, 31), style=0)
        self.btnAreaAxis.SetToggle(True)
        self.btnAreaAxis.SetLabel('')
        self.btnAreaAxis.SetToolTip('Calculate the total area to the axis')

        self.btnAreaBaseline = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join('bmp','peakareabase.png')),
              id=-1, name='btnAreaBaseline', parent=self, pos=wx.Point(0, 33), 
              size=wx.Size(128, 31), style=0)
        self.btnAreaBaseline.SetToggle(True)
        self.btnAreaBaseline.SetLabel('')
        self.btnAreaBaseline.SetToolTip('Calculate the total area to the baseline')

        self.btnAreaFitAxis = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join('bmp','peakcfitareaaxis.png')),
              id=-1, name='btnAreaFitAxis', parent=self, pos=wx.Point(130, 33), 
              size=wx.Size(128, 31), style=0)
        self.btnAreaFitAxis.SetToggle(True)
        self.btnAreaFitAxis.SetLabel('')
        self.btnAreaFitAxis.SetToolTip('Curvefit peak and calculate area to the X-axis')

        self.btnAreaFitBaseline = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join('bmp','peakcfitareabase.png')),
              id=-1, name='btnAreaFitBaseline', parent=self, pos=wx.Point(0, 66), 
              size=wx.Size(128, 31), style=0)
        self.btnAreaFitBaseline.SetToggle(True)
        self.btnAreaFitBaseline.SetLabel('')
        self.btnAreaFitBaseline.SetToolTip('Curvefit peak and calculate area to baseline')

        self.btnIntensityFit = wx.lib.buttons.GenBitmapToggleButton(bitmap=wx.Bitmap(os.path.join('bmp','peakifitmax.png')),
              id=-1, name='btnSpare', parent=self, pos=wx.Point(130, 66), 
              size=wx.Size(128, 31), style=0)
        self.btnIntensityFit.SetToggle(True)
        self.btnIntensityFit.SetLabel('')
        self.btnIntensityFit.SetToolTip('Curvefit peak and find maximum intensity')

        self.btnCalculate = wx.Button(id=-1, label='Calculate', name='btnCalculate', 
              parent=self, pos=wx.Point(0, 99), size=wx.Size(128, 31), style=0)
        self.btnCalculate.SetToolTip('')
        self.btnCalculate.Bind(wx.EVT_BUTTON, self.OnBtnCalculateButton,
              id=self.btnCalculate.GetId())

        self.btnCancel = wx.Button(id=-1, label='Cancel', name='btnCancel', 
              parent=self, pos=wx.Point(130, 99), size=wx.Size(128, 31), 
              style=0)
        self.btnCancel.SetToolTip('')
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancelButton,
              id=self.btnCancel.GetId())

        self._init_pc_sizers()

    def __init__(self, parent, xlim, data, canvas):
        self._init_pc_ctrls(parent)
        
        self._xlim = xlim
        self._data = data
        self._canvas = canvas
        self._prnt = parent
    
    def GetXdata(self, start=None):
        #use raw or processed data
        if self._prnt.titleBar.cbxData.GetSelection() == 0:
            xdata = self._data['raw'][:,sp.array(self._data['variableidx'])]
            label = '_RAW'
        else:
            xdata = self._data['proc'][:,sp.array(self._data['variableidx'])]
            label = '_PROC'
        return xdata,label
    
    def UpdateVars(self, grid, countpos, fix, x):
        #update ind var labels
        grid.InsertRows(pos=countpos, numRows=1, updateLabels=True)
        #set checkbox in first column
        grid.SetCellEditor(countpos,0,wx.grid.GridCellBoolEditor())
        grid.SetCellRenderer(countpos,0,wx.grid.GridCellBoolRenderer())
        grid.SetCellAlignment(countpos,0,wx.ALIGN_CENTRE,wx.ALIGN_CENTRE)
        grid.SetCellValue(countpos,0,'0')
        #set user defined variable row label
        grid.SetRowLabelValue(countpos,'U' + str(countpos))
        #renumber other rows
        for r in range(countpos+1,grid.GetNumberRows()):
            grid.SetRowLabelValue(r,str(r-countpos))
        #add label
        for c in range(1,grid.GetNumberCols()):
            grid.SetCellValue(countpos,c,fix[0] + '%.2f' %sp.mean(x) + fix[1])
        #make cell read only in col 1 for referencing
        grid.SetReadOnly(countpos,1)
        grid.SetCellBackgroundColour(countpos,1,wx.LIGHT_GREY)
    
    def InsertVariable(self, pos, var):
        #add new column to raw and proc data
        self._data['raw'] = sp.concatenate((self._data['raw'][:,0:pos],
              var,self._data['raw'][:,pos:self._data['raw'].shape[1]]),1)
        self._data['proc'] = sp.concatenate((self._data['proc'][:,0:pos],
              var,self._data['proc'][:,pos:self._data['proc'].shape[1]]),1)
                
    def OnBtnCalculateButton(self, event):
        #find bin range
        xaxis = self._data['xaxis'][:,0]
        mnx = min([self._xlim[0],self._xlim[1]])
        mxx = max([self._xlim[0],self._xlim[1]])
        
        #fix to deal with x-axis orientation
        if xaxis[0] < xaxis[len(xaxis)-1]:
            bin1 = len(xaxis[xaxis<=mnx])
            bin2 = len(xaxis[xaxis<=mxx])
        else:
            bin1 = len(xaxis[xaxis>=mnx])
            bin2 = len(xaxis[xaxis>=mxx])
        
        #bin range
        rng=sp.arange(min([bin1,bin2]),max([bin1,bin2]))
        x = xaxis[rng]
        
        #replot vertical lines to fit bin
        graphics,xlim,ylim = self._canvas.last_draw
        graphics.objects = [graphics.objects[0]]
        graphics.objects.append(wx.lib.plot.PolyLine([[x[0],ylim[0]],
              [x[0],ylim[1]]],colour='red'))
        graphics.objects.append(wx.lib.plot.PolyLine([[x[len(x)-1],ylim[0]],
              [x[len(x)-1],ylim[1]]],colour='red'))
        self._canvas.Draw(graphics)#,xAxis=tuple(xlim),yAxis=tuple(ylim))
        # get position of most recent user defined variable to be have been added
        grid = self._prnt.prnt.prnt.plExpset.grdIndLabels
        countpos = 0 # count number of user defined variables
        for r in range(1,grid.GetNumberRows()):
            countpos += 1
            if len(grid.GetRowLabelValue(r).split('U')) == 1:
                break 
        # get xdata for calcs
        xdata,label=self.GetXdata(start=countpos-1)
        # do calculations
        if self.btnIntensity.GetValue(): #max intensity in range
            intensity = xdata[:,rng].max(axis=1)[:, nax]
            # update variable labels grid
            self.UpdateVars(grid,countpos,['I_',label],x)
            # add new column to raw and proc data
            self.InsertVariable(countpos,intensity)
            countpos += 1
        if self.btnIntensityFit.GetValue(): # max intensity based on curve fit
            intensity_fit = self.CurveFit(xdata,x,rng,type=0)
            # update variable labels grid
            self.UpdateVars(grid,countpos,['IF_',label],x)
            # add new column to raw and proc data
            self.InsertVariable(countpos,intensity_fit)
            countpos += 1
        if self.btnAreaAxis.GetValue(): #total area in range
            area_axis = sp.sum(xdata[:,rng],axis=1)[:, nax]
            # update variable labels grid
            self.UpdateVars(grid,countpos,['AA_',label],x)
            # add new column to raw and proc data
            self.InsertVariable(countpos,area_axis)
            countpos += 1
        if self.btnAreaFitAxis.GetValue(): #total area in range with curve fit
            area_fit_axis = self.CurveFit(xdata,x,rng,type=1)  
            # update variable labels grid
            self.UpdateVars(grid,countpos,['AFA_',label],x)
            # add new column to raw and proc data
            self.InsertVariable(countpos,area_fit_axis)
            countpos += 1
        if self.btnAreaBaseline.GetValue(): #total area in to base of peak
            area_baseline = self.CurveFit(xdata,x,rng,type=3)
            # update variable labels grid
            self.UpdateVars(grid,countpos,['AB_',label],x)
            # add new column to raw and proc data
            self.InsertVariable(countpos,area_baseline)
            countpos += 1
        if self.btnAreaFitBaseline.GetValue(): #total area in to base of peak with curve fit
            area_fit_baseline = self.CurveFit(xdata,x,rng,type=2)
            # update variable labels grid
            self.UpdateVars(grid,countpos,['AFB_',label],x)
            # add new column to raw and proc data
            self.InsertVariable(countpos,area_fit_baseline)
        # update experiment setup
        self._prnt.prnt.prnt.GetExperimentDetails(case=1)
        # destroy dialog
        self.Destroy()
        
    def OnBtnCancelButton(self, event):
        self.Destroy()
    
    def CurveFit(self, xdata, x, rng, type=1):
        # fit 2nd order polynomial
        area = []
        favg = sp.zeros((len(x),))
        for r in range(xdata.shape[0]):
            p = sp.polyfit(x, xdata[r,rng], 2)
            f = sp.polyval(p, x)
            if type > 0:
                if type == 3:
                    f = xdata[r,rng]
                favg = favg + f
                area.append(sp.sum(f))
                if type > 1: #fit straight line
                    p1 = sp.polyfit(x, xdata[r,rng], 1)
                    f1 = sp.polyval(p1, x)
                    area[len(area)-1] = sp.sum(f-f1)
            else:
                area.append(max(f))
        
        area = sp.array(area)[:, nax]
        if type > 0:
            favg = favg/float(r+1) #avg curve fit for plotting
            graphics,xlim,ylim = self._canvas.last_draw
            if type < 3:
                c = 'blue'
            elif type == 3:
                c = 'green'
            graphics.objects.extend([wx.lib.plot.PolyLine(sp.concatenate((x[:, nax],
                                                                          favg[:, nax]), 1), colour=c)])
            if type > 1: 
                f1avg = sp.polyfit([x[0],x[len(x)-1]], [favg[0],favg[len(favg)-1]], 1)
                f1avg = sp.polyval(f1avg, x)
                graphics.objects.extend([wx.lib.plot.PolyLine(sp.concatenate((x[:, nax],
                                                                              f1avg[:, nax]), 1), colour=c)])
            self._canvas.Draw(graphics)#,xAxis=tuple(xlim),yAxis=tuple(ylim))
        
        return area
        
class plotSpectra(wx.Panel):
    def _init_coll_bxsPspc1_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.bxsPspc2, 1, border=0, flag=wx.EXPAND)

    def _init_coll_bxsPspc2_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.titleBar, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.Splitter, 1, border=0, flag=wx.EXPAND)
    
    def _init_sizers(self):
        # generated method, don't edit
        self.bxsPspc1 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.bxsPspc2 = wx.BoxSizer(orient=wx.VERTICAL)
        
        self._init_coll_bxsPspc1_Items(self.bxsPspc1)
        self._init_coll_bxsPspc2_Items(self.bxsPspc2)
        
        self.SetSizer(self.bxsPspc1)
        
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=-1, name='plotSpectra',
              parent=prnt, pos=wx.Point(88, 116), size=wx.Size(757, 538),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(749, 504))
        self.SetToolTip('')
        self.SetAutoLayout(True)
        
        self.Splitter = wx.SplitterWindow(
            id=-1, name='Splitter', parent=self, pos=wx.Point(16, 24),
            size=wx.Size(272, 168), style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        self.Splitter.SetAutoLayout(True)
        self.Splitter.Bind(wx.EVT_SPLITTER_DCLICK, self.OnSplitterDclick)
        
        self.p1 = wx.Panel(self.Splitter)
        self.p1.SetAutoLayout(True)
        self.p1.prnt = prnt
        self.p1.parent = self
        
        self.optDlg = selFun(self.Splitter)
        
        self.plcPlot = MyPlotCanvas(id=IDPLOTSPEC, name='plcPlot',
                                    parent=self.p1, pos=wx.Point(0, 0), size=wx.Size(200, 200),
                                    style=wx.SUNKEN_BORDER, toolbar=self.p1.prnt.parent.tbMain)
        self.plcPlot.enableZoom
        self.plcPlot.fontSizeTitle = 12
        self.plcPlot.SetToolTip('')
        self.plcPlot.fontSizeAxis = 10
        self.plcPlot.SetConstraints(LayoutAnchors(self.plcPlot,
              True, True, True, True))
        
        self.titleBar = TitleBar(self, id=-1, text="Spectral Preprocessing",
              style=bp.BP_USE_GRADIENT, alignment=bp.BP_ALIGN_LEFT, 
              canvasList=[self.plcPlot])
              
        self.Splitter.SplitVertically(self.optDlg, self.p1, 1)
        self.Splitter.SetMinimumPaneSize(1)
        
        self._init_sizers()

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)
        
        self.parent = parent
    
    def Reset(self):
        curve = wx.lib.plot.PolyLine([[0, 0],[1, 1]], colour='white',width=1, 
              style=wx.TRANSPARENT)
        curve = wx.lib.plot.PlotGraphics([curve], 'Experimental Data', 
              'Arbitrary', 'Arbitrary')
        self.plcPlot.Draw(curve)
        
        #clear preproc list
        self.optDlg.lb.Clear()
    
    def OnSplitterDclick(self, event):
        if self.Splitter.GetSashPosition() <= 5:
            self.Splitter.SetSashPosition(250)
        else:
            self.Splitter.SetSashPosition(1)
    
    def DoPeakCalculations(self):
        #get x lims for calculating peak areas etc
        coords = self.plcPlot.GetInterXlims()
        #open options dialog
        dlg = PeakCalculations(self,coords,self.titleBar.data,self.plcPlot)
        dlg.ShowModal()
        
class TitleBar(bp.ButtonPanel):
    def _init_btnpanel_ctrls(self, prnt):
        bp.ButtonPanel.__init__(self, parent=prnt, id=-1,
                                text="Spectral Preprocessing",
                                agwStyle=bp.BP_USE_GRADIENT,
                                alignment=bp.BP_ALIGN_LEFT)
        
        self.btnSetProc = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join('bmp','params.png'),
              wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL,
              shortHelp='Select Preprocessing Options',
              longHelp='Select Preprocessing Options')
        self.Bind(wx.EVT_BUTTON, self.OnBtnSetProcButton, id=self.btnSetProc.GetId())
        
        self.btnInteractive = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join('bmp','peak.png'),
              wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp='Interactive Mode',
              longHelp='Interactive mode for peak area calculations, intensities etc.')
        self.btnInteractive.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.OnBtnInteractiveButton, id=self.btnInteractive.GetId())
        
        self.btnPlot = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join('bmp','run.png'),
              wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp='Execute Plot',
              longHelp='Execute Plot')
        self.btnPlot.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.OnBtnPlotButton, id=self.btnPlot.GetId())
        
        self.btnExportData = bp.ButtonInfo(self, -1, wx.Bitmap(os.path.join('bmp','export.png'),
              wx.BITMAP_TYPE_PNG), kind=wx.ITEM_NORMAL, shortHelp='Export Data',
              longHelp='Export Data')
        self.btnExportData.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.OnBtnExportDataButton, id=self.btnExportData.GetId())
        
        self.spcPlotSpectra = wx.SpinCtrl(id=-1, initial=1, max=100, min=1,
              name='spcPlotSpectra', parent=self, pos=wx.Point(198,
              554), size=wx.Size(64, 23), style=wx.SP_ARROW_KEYS)
        self.spcPlotSpectra.SetToolTip('')
        self.spcPlotSpectra.SetValue(1)
        self.Bind(wx.EVT_SPINCTRL, self.OnSpnPlot, id=self.spcPlotSpectra.GetId())
        
        self.cbxData = wx.Choice(choices=['Raw spectra','Processed spectra'], id=-1,
              name='cbxData', parent=self, pos=wx.Point(118, 23),
              size=wx.Size(100, 23), style=0)
        self.cbxData.SetSelection(0)
        
        self.cbxNumber = wx.Choice(choices=['Single spectrum','All spectra'], id=-1,
              name='cbxNumber', parent=self, pos=wx.Point(118, 23),
              size=wx.Size(100, 23), style=0)
        self.cbxNumber.SetSelection(0)

    def __init__(self, parent, id, text, style, alignment, canvasList):
        
        self._init_btnpanel_ctrls(parent)
                                           
        self.CreateButtons()
        
        self.parent = parent
        
        self.canvas = canvasList[0]
        
    def CreateButtons(self):
        self.Freeze()
        
        self.SetProperties()
        
        self.AddControl(self.cbxData)
        self.AddControl(self.cbxNumber)
        self.AddControl(self.spcPlotSpectra)
        self.AddSeparator()
        self.AddButton(self.btnSetProc)
        self.AddSeparator()
        self.AddButton(self.btnPlot)
        self.AddSeparator()
        self.AddButton(self.btnInteractive)
        self.AddSeparator()
        self.AddButton(self.btnExportData)
        
        self.Thaw()

        self.DoLayout()
        
    def SetProperties(self):
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
        bpArt.SetColour(bp.BP_SELECTION_BRUSH_COLOUR,
              wx.Colour(242, 242, 235))
        bpArt.SetColour(bp.BP_SELECTION_PEN_COLOUR,
              wx.Colour(206, 206, 195))
    
    def OnBtnInteractiveButton(self, event):
        #plot the average spectrum
        self.PlotSpectra(average=True)
        #add details of current plot to toolbar
        self.canvas.PopulateToolbar()
        #interactive mode for plotting screen - allows to calculate peak areas etc
        self.canvas.enableInteractive(True)
    
    def OnBtnPlotButton(self, event):
        #Set enable zoom just in case
        self.canvas.enableZoom = True
        #Plot spectra
        self.PlotSpectra()
    
    def OnSpnPlot(self, event):
        if self.cbxNumber.GetSelection() == 0:
            #Set enable zoom just in case
            self.canvas.enableZoom = True
            #Plot spectra
            self.PlotSpectra()
    
    def PlotSpectra(self, average=False, xlim=None, ylim=None):
        #select data and run processing
        if self.cbxData.GetSelection() == 0:
            if not average:
                xdata = self.data['rawtrunc']
            else:
                xdata = self.data['raw'][:,sp.array(self.data['variableidx'])]
            title = 'Raw'
        else:
            self.RunProcessingSteps()
            if not average:
                xdata = self.data['proctrunc']
            else:
                xdata = self.data['proc'][:,sp.array(self.data['variableidx'])]
            title = 'Processed'
        #do plotting
        if not average:
            #set busy cursor
            wx.BeginBusyCursor()
            #Plot xdata
            if self.cbxNumber.GetSelection() == 1:
                plotLine(self.canvas,xdata,tit=title,xaxis=self.data['xaxis'],
                      xLabel='Arbitrary',yLabel='Arbitrary',type='multi',
                      wdth=1, ledge=None)
                
            elif self.cbxNumber.GetSelection() == 0:
                plotLine(self.canvas,xdata,tit=title,xaxis=self.data['xaxis'],
                      xLabel='Arbitrary',yLabel='Arbitrary',type='single',
                      rownum=self.spcPlotSpectra.GetValue()-1,wdth=1,
                      ledge=[])
                
            #remove busy cursor
            wx.EndBusyCursor()
        else:
            line = wx.lib.plot.PolyLine(sp.concatenate((self.data['xaxis'],
                  sp.mean(xdata,axis=0)[:,sp.newaxis]),1))
            line = wx.lib.plot.PlotGraphics([line],title='Average ' + title + ' Spectrum', 
                  xLabel='Arbitrary', yLabel='Average Intensity')
            if self.canvas._justDragged:
                xlim = tuple(self.canvas.GetXCurrentRange())
                ylim = tuple(self.canvas.GetYCurrentRange())
                
            self.canvas.Draw(line,xAxis=xlim,yAxis=ylim)
        
    def OnBtnExportDataButton(self, event):
        #export data
        dlg = wx.FileDialog(self, "Choose a file", ".", "", 
              "Text files (*.txt)|*.txt", wx.SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                if self.cbxData.GetSelection() == 0:
                    sp.io.write_array(dlg.GetPath(),sp.transpose(self.data['rawtrunc']),'\t')
                else:
                    sp.io.write_array(dlg.GetPath(),sp.transpose(self.data['proctrunc']),'\t')
        finally:
            dlg.Destroy()
    
    def RunProcessingSteps(self):
##        #remove any user defined processed variables
##        grid = self.parent.parent.parent.plExpset.grdIndLabels
##        for i in range(1,grid.GetNumberRows()):
##            if len(string.split(grid.GetRowLabelValue(i),'U')) > 1:
##                if string.split(grid.GetCellValue(i,1),'_')[2] in ['PROC']:
##                    GridRowDel(grid, self.data) #would need to pass row num (i) for this to work
##                    #update experiment setup
##                    self.parent.parent.parent.GetExperimentDetails(case=1)
##            else:
##                break
        #Run pre-processing 
        x = copy.deepcopy(self.data['raw'])
        for each in self.data['processlist']:
            exec(each[1])
        
        self.data['proc'] = x
        self.parent.prnt.prnt.GetExperimentDetails(case=1)
    
    def OnBtnSetProcButton(self, event):
        if self.parent.Splitter.GetSashPosition() <= 5:
            self.parent.Splitter.SetSashPosition(250)
        else:
            self.parent.Splitter.SetSashPosition(1)
    
    def get_data(self, data):
        self.data = data
        self.parent.optDlg.get_data(data)
    
                                    
class selFun(wx.Panel):
    def _init_selfun_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, parent=prnt, id=-1, style=0)
        self.SetToolTip('')
        
        new_bmp = wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, (16,16))
        del_bmp = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR, (16,16))
#        ref_bmp = wx.ArtProvider.GetBitmap(wx.ART_REFRESH, wx.ART_TOOLBAR, (16,16))
        
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self.tb = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.NO_BORDER 
                             | wx.TB_FLAT)
        self.tb.SetToolBitmapSize((16,16))
        self.tb.AddTool(10, "Add Method", new_bmp, "Add Method'")
        self.tb.AddTool(20, "Delete Method", del_bmp, "Delete Method'")
#        self.tb.AddTool(30, ref_bmp, "Reset", "Reset")
        self.tb.Bind(wx.EVT_TOOL, self.OnNewMethod, id=10)
        self.tb.Bind(wx.EVT_TOOL, self.OnNewMethod, id=20)
        
        self.lb = wx.ListBox(self, -1, (0, 0), (250, 50), [], wx.LB_SINGLE)
        
        vsizer.Add(self.tb, 0, wx.EXPAND)
        hsizer.Add(self.lb, 1, wx.EXPAND)
        vsizer.Add(hsizer, 1, wx.EXPAND)
        
        self.SetSizer(vsizer)
        
        self.tb.Realize()
        
    def __init__(self, parent):
        self._init_selfun_ctrls(parent)
        
    def get_data(self, data):
        self.data = data

    def OnNewMethod(self, event):
        tb = event.GetId()
        if tb == 10:
            win = Process(self, "Pre-processing Options")
#            win.CenterOnParent(wx.VERTICAL)
            try:
                win.ShowModal()
                ppsteps = win.GetPpSteps()
                if ppsteps is not None:
                    self.data['processlist'].append(ppsteps)
                    self.lb.Append(win.GetPpSteps()[0])
            finally:
                win.Destroy()
            
        elif tb == 20:
            if self.lb.GetSelection() > -1:
                del self.data['processlist'][self.lb.GetSelection()]
                self.lb.Delete(self.lb.GetSelection())
        elif tb == 30: #refresh or reset
            self.data['processlist'] = []
            self.data['proc'] = None
        
class Process(wx.Dialog):
    def __init__(self, parent, title, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.DEFAULT_FRAME_STYLE | wx.TINY_CAPTION):
        wx.Dialog.__init__(self, parent, -1, title, pos, size, style)
        
        self.chType = wx.Choice(choices=['Select class...','Normalisation','Scaling',
              'Baseline Correction','Smoothing','Derivatisation'], id=ID_PPTYPE,
              name='chType', parent=self, pos=wx.Point(118, 23),
              size=wx.Size(100, 23), style=0)
        self.chType.SetSelection(0)
        self.chType.Bind(wx.EVT_CHOICE, self.OnChType, id=ID_PPTYPE)

        self.chMethod= wx.Choice(choices=[], id=ID_PPMETHOD, name='chMethod', parent=self, 
              pos=wx.Point(118, 23), size=wx.Size(100, 23), style=0)
        self.chMethod.Bind(wx.EVT_CHOICE, self.OnChMethod, id=ID_PPMETHOD)
        self.chMethod.Append('Choose method...')
        self.chMethod.SetSelection(0)
        self.chMethod.Show(False)
        
        self.lbtxt = wx.StaticText(self, -1, 'Filter width: ',style=wx.ALIGN_CENTER)
        self.lbtxt.Show(False)
        
        self.ftval = wx.Slider(self, ID_VALSLIDE, 10, 1, 100, (30, 60), (250, -1), 
                          wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)
        self.ftval.Bind(wx.EVT_SCROLL_CHANGED, self.OnValSlider, id=ID_VALSLIDE) 
        self.ftval.SetTickFreq(5, 1)
        self.ftval.Show(False)
        
        self.box = wx.BoxSizer(wx.VERTICAL)
        self.box.Add(self.chType, 0, wx.EXPAND)
        self.box.Add(self.chMethod, 0, wx.EXPAND)
        self.box.Add(self.lbtxt, 0, wx.EXPAND)
        self.box.Add(self.ftval, 0, wx.EXPAND)
        
        self.SetSizer(self.box)
        
        self.ppstep = None
        
    def OnChType(self, event):
        self.chMethod.Clear()
        
        if self.chType.GetSelection() == 1: #normalisation
            self.chMethod.Append('Choose method...')
            self.chMethod.Append('Row normalisation')
            self.chMethod.Append('Column normalisation')
            self.chMethod.Append('Row mean centre')
            self.chMethod.Append('Column mean centre')
            self.chMethod.Append('Normalise total signal to +1')
            self.chMethod.Append('Normalise most intense bin to +1')
            self.chMethod.Append('Extended multiplicative scatter correction')
            self.chMethod.SetSelection(0)
        
        if self.chType.GetSelection() == 2: #scaling
            self.chMethod.Append('Choose method...')
            self.chMethod.Append('Scale minimum to 0 and maximum to +1')
            self.chMethod.SetSelection(0)
            
        if self.chType.GetSelection() == 3: #baseline
            self.chMethod.Append('Choose method...')
            self.chMethod.Append('Set first bin to zero')
            self.chMethod.Append('Substract a linear baseline')
            self.chMethod.SetSelection(0)
        
        if self.chType.GetSelection() == 4: #smoothing
            self.chMethod.Append('Choose method...')
            self.chMethod.Append('Apply a moving average filter')
#            self.chMethod.Append('Savitsky-Golay filter')
            self.chMethod.SetSelection(0)
        
        if self.chType.GetSelection() == 5: #derivatisation
            self.chMethod.Append('Choose method...')
            self.chMethod.Append('Linear derivative')
            self.chMethod.SetSelection(0)
        
        self.chMethod.Show(True)
        self.box.Layout()
        
    def OnChMethod(self, event):
        option = event.GetString()
        close = False
        if self.chType.GetSelection() == 1:
            if option == 'Row normalisation':
                self.ppstep = [option, 'x=sp.transpose(mva.process.autoscale(sp.transpose(x)))']
                close = True
            elif option == 'Column normalisation':
                self.ppstep = [option, 'x=mva.process.autoscale(x)']
                close = True
            if option == 'Row mean centre':
                self.ppstep = [option, 'x=sp.transpose(mva.process.meancent(sp.transpose(x)))']
                close = True
            elif option == 'Column mean centre':
                self.ppstep = [option, 'x=mva.process.meancent(x)']
                close = True
            elif option == 'Normalise total signal to +1':
                self.ppstep = [option, 'x=mva.process.normtot(x)']
                close = True
            elif option == 'Normalise most intense bin to +1':
                self.ppstep = [option, 'x=mva.process.normhigh(x)']
                close = True
            elif option == 'Extended multiplicative scatter correction':
                self.lbtxt.SetLabel('Polynomial order')
                self.lbtxt.Show(True)
                self.ftval.Show(True)
                self.box.Layout()
                close = False
            
        elif self.chType.GetSelection() == 2:
            if option == 'Scale minimum to 0 and maximum to +1':
                self.ppstep = [option, 'x=mva.process.scale01(x)']
            close = True
            
        elif self.chType.GetSelection() == 3:
            if option == 'Set first bin to zero':
                self.ppstep = [option, 'x=mva.process.baseline1(x)']
            elif option == 'Substract a linear baseline':
                self.ppstep = [option, 'x=mva.process.lintrend(x)']
            close = True
            
        elif self.chType.GetSelection() > 3:
            self.lbtxt.Show(True)
            self.ftval.Show(True)
            self.box.Layout()
            close = False
        
        if close:
            self.Close()
    
    def OnValSlider(self, event):
        option = self.chMethod.GetStringSelection()
        if option == 'Apply a moving average filter':
            self.ppstep = [option + ',window = ' + str(event.GetPosition()), 
                           'x=mva.process.avgfilt(x,' + str(event.GetPosition()) + ', dim="c")']
        
        elif option == 'Linear derivative':
            self.ppstep = [option + ',window = ' + str(event.GetPosition()), 
                           'x=mva.process.derivlin(x,' + str(event.GetPosition()) + ')']
        
        elif option == 'Extended multiplicative scatter correction':
            self.ppstep = [option + ',order = ' + str(event.GetPosition()), 
                           'x=mva.process.emsc(x,' + str(event.GetPosition()) + ')']
        
#        elif option == 'Savitsky-Golay filter':
#            self.ppstep = [option + ',order = ' + str(event.GetPosition()),
#                           'x=mva.process.sgolayfilt(x,5,20)'] #+ str(event.GetPosition()) + ')']
            
        self.Close()
        
    def GetPpSteps(self):
        return self.ppstep
    
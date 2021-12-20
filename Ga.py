# -----------------------------------------------------------------------------
# Name:        Ga.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2007/05/22
# RCS-ID:      $Id: Ga.py, v 1.19 2009/02/26 22:19:47 rmj01 Exp $
# Copyright:   (c) 2006
# Licence:     GNU General Public Licence
# -----------------------------------------------------------------------------

import wx
import wx.lib.buttons
import wx.lib.plot

from wx.lib.stattext import GenStaticText
import wx.lib.agw.buttonpanel as bp
import wx.lib.agw.foldpanelbar as fpb
from wx.lib.anchors import LayoutAnchors
from wx.lib.plot import PolyLine, PlotGraphics, PolyMarker

import scipy as sp
import numpy as np
import string
import os
import mva.genetic as genic
import mva.fitfun
import mva.process

from mva.chemometrics import _index
from numpy import newaxis as nax
from Pca import plotLine
from Pca import plotStem
from Pca import plotText
from Pca import plotScores
from Pca import plotLoads
from Pca import MyPlotCanvas
from Pca import PlotPlsModel
from expSetup import valSplit
from commons import error_box



class Ga(wx.Panel):
    # genetic algorithm coupled to discriminant function analysis
    def _init_coll_bxsGa1_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.bxsGa2, 1, border=0, flag=wx.EXPAND)
        
    def _init_coll_bxsGa2_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.titleBar, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.Splitter, 1, border=0, flag=wx.EXPAND)
    
    def _init_coll_grsGa_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.nbGaPlsPreds, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.plcGaFreqPlot, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.plcGaFeatPlot, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.nbGaModPlot, 0, border=0, flag=wx.EXPAND)
    
    def _init_coll_nbGaPlsPreds_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.plcGaModelPlot1, select=True,
              text='')
    
    def _init_coll_nbGaModPlot_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.plcGaOptPlot, select=True,
                       text='GA Optimisation Curve')
        parent.AddPage(imageId=-1, page=self.plcGaEigs, select=False,
                       text='Eigenvalues')
        parent.AddPage(imageId=-1, page=self.plcGaSpecLoad, select=False,
                       text='Spectral Loadings')
        parent.AddPage(imageId=-1, page=self.plcGaGrpDistPlot, select=False,
                       text='Model Error Comparisons')
    
    def _init_sizers(self):
        self.grsGa = wx.GridSizer(cols=2, hgap=2, rows=2, vgap=2)
        
        self.bxsGa2 = wx.BoxSizer(orient=wx.VERTICAL)
        
        self.bxsGa1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        
        self._init_coll_bxsGa1_Items(self.bxsGa1)
        self._init_coll_bxsGa2_Items(self.bxsGa2)
        self._init_coll_grsGa_Items(self.grsGa)
        
        self.SetSizer(self.bxsGa1)
        self.p1.SetSizer(self.grsGa)
        
    def _init_ctrls(self, prnt):
        wx.Panel.__init__(self, id=-1, name='Ga', parent=prnt,
                          pos=wx.Point(47, 118), size=wx.Size(796, 460),
                          style=wx.TAB_TRAVERSAL)
        self.SetToolTip('')
        self.SetAutoLayout(True)
        self.prnt = prnt
        
        self.Splitter = wx.SplitterWindow(id=-1,
                                          name='Splitter', parent=self,
                                          pos=wx.Point(16, 24),
                                          size=wx.Size(272, 168),
                                          style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        self.Splitter.SetAutoLayout(True)
        self.Splitter.Bind(wx.EVT_SPLITTER_DCLICK, self.OnSplitterDclick)
        self.Splitter.splitPrnt = self
        
        self.p1 = wx.Panel(self.Splitter)
        self.p1.prnt = self.Splitter
        self.p1.SetAutoLayout(True)
        
        self.optDlg = selParam(self.Splitter)
        
        self.nbGaPlsPreds = wx.Notebook(id=-1, name='nbGaPlsPreds',
                                        parent=self.p1, pos=wx.Point(176, 274),
                                        size=wx.Size(310, 272),
                                        style=wx.NB_BOTTOM)
        self.nbGaPlsPreds.SetToolTip('')
        self.nbGaPlsPreds.SetAutoLayout(True)
        self.nbGaPlsPreds.SetConstraints(
            LayoutAnchors(self.nbGaPlsPreds, True, True, True, True))

        self.nbGaPlsPreds.prnt = self.p1

        toolbar = self.nbGaPlsPreds.prnt.prnt.splitPrnt.prnt.parent.tbMain
        self.plcGaModelPlot1 = MyPlotCanvas(id=-1, name='plcGaModelPlot1',
                                            parent=self.nbGaPlsPreds,
                                            pos=wx.Point(0, 0),
                                            size=wx.Size(310, 272),
                                            style=0, toolbar=toolbar)
        self.plcGaModelPlot1.enableZoom = True
        self.plcGaModelPlot1.enableLegend = True
        self.plcGaModelPlot1.fontSizeAxis = 8
        self.plcGaModelPlot1.fontSizeLegend = 8
        self.plcGaModelPlot1.fontSizeTitle = 10
        self.plcGaModelPlot1.SetToolTip('')
        
        self.nbGaModPlot = wx.Notebook(id=-1, name='nbGaModPlot',
                                       parent=self.p1, pos=wx.Point(760, 326),
                                       size=wx.Size(310, 272),
                                       style=wx.NB_BOTTOM)
        self.nbGaModPlot.prnt = self.p1
        self.nbGaModPlot.SetToolTip('')

        self.plcGaEigs = MyPlotCanvas(id=-1, name='plcGaEigs',
                                      parent=self.nbGaModPlot,
                                      pos=wx.Point(0, 0),
                                      size=wx.Size(310, 272), style=0,
                                      toolbar=self.prnt.parent.tbMain)
        self.plcGaEigs.enableZoom = True
        self.plcGaEigs.fontSizeAxis = 8
        self.plcGaEigs.fontSizeLegend = 8
        self.plcGaEigs.fontSizeTitle = 10
        self.plcGaEigs.SetToolTip('')
        
        self.plcGaSpecLoad = MyPlotCanvas(id=-1, name='plcGaSpecLoad',
                                          parent=self.nbGaModPlot,
                                          pos=wx.Point(0, 24),
                                          size=wx.Size(503, 279), style=0,
                                          toolbar=self.prnt.parent.tbMain)
        self.plcGaSpecLoad.SetToolTip('')
        self.plcGaSpecLoad.enableZoom = True
        self.plcGaSpecLoad.fontSizeAxis = 8
        self.plcGaSpecLoad.fontSizeLegend = 8
        self.plcGaSpecLoad.fontSizeTitle = 10
        
        self.plcGaFreqPlot = MyPlotCanvas(id=-1, name='plcGaFreqPlot',
                                          parent=self.p1, pos=wx.Point(760, 0),
                                          size=wx.Size(310, 272), style=0,
                                          toolbar=self.prnt.parent.tbMain)
        self.plcGaFreqPlot.enableZoom = True
        self.plcGaFreqPlot.fontSizeAxis = 8
        self.plcGaFreqPlot.fontSizeLegend = 8
        self.plcGaFreqPlot.fontSizeTitle = 10
        self.plcGaFreqPlot.SetToolTip('')
        
        self.plcGaFeatPlot = MyPlotCanvas(id=-1, name='plcGaFeatPlot',
                                          parent=self.p1, pos=wx.Point(0, 24),
                                          size=wx.Size(310, 272), style=0,
                                          toolbar=self.prnt.parent.tbMain)
        self.plcGaFeatPlot.SetToolTip('')
        self.plcGaFeatPlot.enableZoom = True
        self.plcGaFeatPlot.enableLegend = True
        self.plcGaFeatPlot.fontSizeAxis = 8
        self.plcGaFeatPlot.fontSizeLegend = 8
        self.plcGaFeatPlot.fontSizeTitle = 10
        
        self.plcGaGrpDistPlot = MyPlotCanvas(id=-1, name='plcGaGrpDistPlot',
                                             parent=self.nbGaModPlot,
                                             pos=wx.Point(0, 0),
                                             size=wx.Size(310, 272), style=0,
                                             toolbar=self.prnt.parent.tbMain)
        self.plcGaGrpDistPlot.enableLegend = True
        self.plcGaGrpDistPlot.enableZoom = True
        self.plcGaGrpDistPlot.fontSizeAxis = 8
        self.plcGaGrpDistPlot.fontSizeLegend = 8
        self.plcGaGrpDistPlot.fontSizeTitle = 10
        self.plcGaGrpDistPlot.SetToolTip('')
        
        self.plcGaOptPlot = MyPlotCanvas(id=-1, name='plcGaOptPlot',
                                         parent=self.nbGaModPlot,
                                         pos=wx.Point(0, 0),
                                         size=wx.Size(310, 272), style=0,
                                         toolbar=self.prnt.parent.tbMain)
        self.plcGaOptPlot.enableLegend = False
        self.plcGaOptPlot.enableZoom = True
        self.plcGaOptPlot.fontSizeAxis = 8
        self.plcGaOptPlot.fontSizeLegend = 8
        self.plcGaOptPlot.fontSizeTitle = 10
        self.plcGaOptPlot.SetToolTip('')
        
        self.titleBar = TitleBar(self, id=-1, text="",
                                 style=bp.BP_USE_GRADIENT,
                                 alignment=bp.BP_ALIGN_LEFT,
                                 gatype=self.dtype)

        self.Splitter.SplitVertically(self.optDlg, self.p1, 1)
        self.Splitter.SetMinimumPaneSize(1)
        
        self._init_coll_nbGaModPlot_Pages(self.nbGaModPlot)
        self._init_coll_nbGaPlsPreds_Pages(self.nbGaPlsPreds)
        
        self._init_sizers()

    def __init__(self, parent, id, pos, size, style, name, dtype):
        self.dtype = dtype
        self._init_ctrls(parent)
        self.parent = parent
    
    def Reset(self):
        # disable ctrls
        self.titleBar.spnGaScoreFrom.Enable(False)
        self.titleBar.spnGaScoreTo.Enable(False)
        self.titleBar.cbxFeature1.Enable(False)
        self.titleBar.cbxFeature2.Enable(False)
        
        # delete multiple scores plots
        self.plcGaModelPlot1.prnt.SetSelection(0)
        self.plcGaModelPlot1.prnt.SetPageText(0, '')
        # self.plcGaModelPlot1.prnt.SetTabSize((0, 1))
        for page in range(self.plcGaModelPlot1.prnt.GetPageCount()-1, 0, -1):
            self.plcGaModelPlot1.prnt.DeletePage(page)
        
        # clear plots
        objects = {'plcGaModelPlot1': ['Predictions', 't[1]', 't[2]'],
                   'plcGaFeatPlot': ['Measured Variable Biplot', 'Variable',
                                     'Variable'],
                   'plcGaFreqPlot': ['Frequency of Variable Selection',
                                     'Independent Variable', 'Frequency'],
                   'plcGaOptPlot': ['Rate of GA Optimisation', 'Generation',
                                    'Fitness Score']}
            
        curve = PolyLine([[0, 0], [1, 1]], colour='white', width=1,
                         style=wx.TRANSPARENT)
        
        for each in objects.keys():
            exec('self.' + each + '.Draw(PlotGraphics([curve], ' +
                 'objects["' + each + '"][0], ' +
                 'objects["' + each + '"][1], ' +
                 'objects["' + each + '"][2]))')
    
    def OnSplitterDclick(self, event):
        if self.Splitter.GetSashPosition() <= 5:
            self.Splitter.SetSashPosition(250)
        else:
            self.Splitter.SetSashPosition(1)
            
class TitleBar(bp.ButtonPanel):
    def _init_btnpanel_ctrls(self, prnt):
        bp.ButtonPanel.__init__(self, parent=prnt, id=-1,
                                text="GA-" + self.dtype,
                                agwStyle=bp.BP_USE_GRADIENT,
                                alignment=bp.BP_ALIGN_LEFT)
                                
        self.cbxData = wx.Choice(choices=['Raw spectra', 'Processed spectra'], id=-1,
              name='cbxData', parent=self, pos=wx.Point(118, 23),
              size=wx.Size(100, 23), style=0)
        self.cbxData.SetSelection(0)
        
        bmp = wx.Bitmap(os.path.join('bmp', 'run.png'), wx.BITMAP_TYPE_PNG)
        self.btnRunGa = bp.ButtonInfo(self, -1, bmp, kind=wx.ITEM_NORMAL,
                                      shortHelp='Run Genetic Algorithm',
                                      longHelp='Run Genetic Algorithm')
        self.btnRunGa.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.OnBtnrungaButton, id=self.btnRunGa.GetId())
        
        bmp = wx.Bitmap(os.path.join('bmp', 'export.png'), wx.BITMAP_TYPE_PNG)
        self.btnExportGa = bp.ButtonInfo(self, -1, bmp, kind=wx.ITEM_NORMAL,
                                         shortHelp='Export GA Results',
                                         longHelp='Export Genetic Algorithm Results')
        self.btnExportGa.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.OnBtnexportgaButton, id=self.btnExportGa.GetId())
        
        self.cbxFeature1 = wx.Choice(choices=[''], id=-1, name='cbxFeature1',
                                     parent=self, pos=wx.Point(118, 23),
                                     size=wx.Size(60, 23), style=0)
        self.cbxFeature1.SetSelection(0)
        self.cbxFeature1.Bind(wx.EVT_CHOICE, self.on_cbx_feat1, id=-1)
        
        self.cbxFeature2 = wx.Choice(choices=[''], id=-1, name='cbxFeature2',
                                     parent=self, pos=wx.Point(118, 23),
                                     size=wx.Size(60, 23), style=0)
        self.cbxFeature2.SetSelection(0)
        self.cbxFeature2.Bind(wx.EVT_CHOICE, self.on_cbx_feat2, id=-1)
        
        self.spnGaScoreFrom = wx.SpinCtrl(id=-1,
              initial=1, max=100, min=1, name='spnGaScoreFrom',
              parent=self, pos=wx.Point(184, 2), size=wx.Size(40,
              23), style=wx.SP_ARROW_KEYS)
        self.spnGaScoreFrom.SetToolTip('')
        self.spnGaScoreFrom.Bind(wx.EVT_SPINCTRL, self.on_spn_ga_scores_from,
                                 id=-1)

        self.spnGaScoreTo = wx.SpinCtrl(id=-1, initial=1, max=100, min=1,
                                        name='spnGaScoreTo', parent=self,
                                        pos=wx.Point(256, 2),
                                        size=wx.Size(40, 23),
                                        style=wx.SP_ARROW_KEYS)
        self.spnGaScoreTo.SetToolTip('')
        self.spnGaScoreTo.Bind(wx.EVT_SPINCTRL, self.on_spn_ga_scores_to,
                               id=-1)

        bmp = wx.Bitmap(os.path.join('bmp', 'params.png'), wx.BITMAP_TYPE_PNG)
        self.btnSetParams = bp.ButtonInfo(self, -1, bmp, kind=wx.ITEM_NORMAL,
                                          shortHelp='Set GA Parameters',
                                          longHelp='Set Genetic Algorithm Parameters')
        self.Bind(wx.EVT_BUTTON, self.OnBtnbtnSetParamsButton, id=self.btnSetParams.GetId())
        
    def __init__(self, parent, id, text, style, alignment, gatype):

        self.parent = parent
        self.dtype = gatype
        
        self._init_btnpanel_ctrls(parent)
        
        self.spnGaScoreFrom.Show(False)
        self.spnGaScoreTo.Show(False)

        self.data = None
        self.grid = None

        self.CreateButtons()
    
    def get_data(self, data):
        self.data = data
        
    def getExpGrid(self, grid):
        self.grid = grid
    
    def getValSplitPc(self, pc):
        self.pcSplit = pc
    
    def CreateButtons(self):
        self.Freeze()
        
        self.SetProperties()
                    
        self.AddControl(self.cbxData)
        self.AddSeparator()
        style = wx.TRANSPARENT_WINDOW
        if self.dtype == 'DFA':
            self.AddControl(GenStaticText(self, -1, 'DF ', style=style))
            self.AddControl(self.spnGaScoreFrom)
            self.AddControl(GenStaticText(self, -1, ' vs. ', style=style))
            self.AddControl(self.spnGaScoreTo)
            self.AddSeparator()
        self.AddControl(GenStaticText(self, -1, 'Variable', style=style))
        self.AddControl(self.cbxFeature1)
        self.AddControl(GenStaticText(self, -1, ' vs. ', style=style))
        self.AddControl(self.cbxFeature2)
        self.AddSeparator()
        self.AddButton(self.btnSetParams)
        self.AddSeparator()
        self.AddButton(self.btnRunGa)
        self.AddSeparator()
        self.AddButton(self.btnExportGa)
        
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
        bpArt.SetColour(bp.BP_SELECTION_BRUSH_COLOUR, wx.Colour(242, 242, 235))
        bpArt.SetColour(bp.BP_SELECTION_PEN_COLOUR, wx.Colour(206, 206, 195))
    
    def OnBtnbtnSetParamsButton(self, event):
        if self.parent.Splitter.GetSashPosition() <= 5:
            self.parent.Splitter.SetSashPosition(250)
        else:
            self.parent.Splitter.SetSashPosition(1)
        
    def OnBtnrungaButton(self, event):
        self.run_ga(varfrom=self.parent.optDlg.spnGaVarsFrom.GetValue(),
                    varto=self.parent.optDlg.spnGaVarsTo.GetValue(),
                    inds=self.parent.optDlg.spnGaNoInds.GetValue(),
                    runs=self.parent.optDlg.spnGaNoRuns.GetValue(),
                    xovr=float(self.parent.optDlg.stGaXoverRate.GetValue()),
                    mutr=float(self.parent.optDlg.stGaMutRate.GetValue()),
                    insr=float(self.parent.optDlg.stGaInsRate.GetValue()),
                    maxf=self.parent.optDlg.spnGaMaxFac.GetValue(),
                    mgen=self.parent.optDlg.spnGaMaxGen.GetValue(),
                    rgen=self.parent.optDlg.spnGaRepUntil.GetValue(),
                    resample=self.parent.optDlg.spnResample.GetValue())
    
    def OnBtnexportgaButton(self, event):
        dlg = wx.FileDialog(self, "Choose a file", ".", "", 
                            "Any files (*.*)|*.*", wx.FD_SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                saveFile = dlg.GetPath()
                gatype = 'ga' + self.dtype.lower()
                chroms = np.array2string(self.data[gatype + 'chroms'], separator='\t')
                curves = np.array2string(self.data[gatype + 'curves'], separator='\t')

                out = '#CHROMOSOMES\n%s\n#FITNESS_OPTIMISATION\n%s' % (chroms, curves)
                with open(saveFile, 'w') as f:
                    f.write(out)
        finally:
            dlg.Destroy()
              
    def on_spn_ga_scores_from(self, _):
        # Set loadings plot options
        self.on_spn_ga_scores()

    def on_spn_ga_scores_to(self, _):
        # Set loadings plot options
        self.on_spn_ga_scores()

    def on_spn_ga_scores(self):
        # Set loadings plot options
        #
        # GA scores plot
        plotScores(self.parent.plcGaModelPlot1, self.data['gadfadfscores'],
                   cl=self.data['class'][:, 0],
                   labels=self.data['label'],
                   validation=self.data['validation'],
                   col1=self.spnGaScoreFrom.GetValue() - 1,
                   col2=self.spnGaScoreTo.GetValue() - 1, title='DF Scores',
                   xLabel='t[%f]' % self.spnGaScoreFrom.GetValue(),
                   yLabel='t[%f]' % self.spnGaScoreTo.GetValue(),
                   xval=True, text=self.parent.prnt.tbMain.tbPoints.GetValue(),
                   pconf=self.parent.prnt.tbMain.tbConf.GetValue(),
                   symb=self.parent.prnt.tbMain.tbSymbols.GetValue(),
                   usecol=[], usesym=[])

        # DF loadings
        exec(
            "self.parent.optDlg.plotGaLoads(self.parent.optDlg.currentChrom, self.data['ga" +
            self.dtype.lower() + self.dtype.lower() +
            "loads'], self.parent.plcGaSpecLoad, self.spnGaScoreFrom.GetValue()-1)")

    def on_cbx_feat1(self, event):
        self.parent.optDlg.PlotGaVariables(self.parent.plcGaFeatPlot)
    
    def on_cbx_feat2(self, event):
        self.parent.optDlg.PlotGaVariables(self.parent.plcGaFeatPlot)
        
    def run_ga(self, **_attr):
        """Runs GA
            **_attr - key word _attributes
                Defaults:
                    'varfrom' = 2,  - No of ind. variables from
                    'varto' = 2,    - No of ind. variables to
                    'inds'= 10,     - No. of individuals
                    'runs'= 1,      - No. of independent GA runs
                    'xovr'= 0.8,    - Crossover rate
                    'mutr'= 0.4,    - Mutation rate
                    'insr'= 0.8,    - Insertion rate
                    'maxf'= 1,      - Maximum no.of latent variables
                    'mgens'= 5,     - Max. no. of generations
                    'rgens'= 5,     - No. of repeat gens
                    'resample'= 1,  - No. of random resampling iterations
        """
        
        dlg = wx.MessageDialog(self, 'This can take a while, are you sure?', 
                               'Preparing to run GA',
                               wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
        try:
            go = 0
            if dlg.ShowModal() == wx.ID_OK:
                go = 1
        finally:
            dlg.Destroy()
        
        if go == 1: 
            self.parent.reset()
            # try:
            # set busy cursor
            wx.BeginBusyCursor()
            
            # Set xdata
            if self.cbxData.GetSelection() == 0:
                xdata = self.data['rawtrunc']
            elif self.cbxData.GetSelection() == 1:
                xdata = self.data['proctrunc']
            
            # Set validation samples for resampling
            if _attr['resample'] == 1:
                mask = np.array(self.data['validation'])[:, nax]
            else:
                mask = np.array(self.data['validation'])[:, nax]
                for nF in range(1, _attr['resample']):
                    # split in to training and test
                    mask = np.concatenate((mask, np.array(valSplit(self.grid,
                          self.data, self.pcSplit))[:, nax]), 1)
                
            # Run DFA - set containers
            scoreList = [] 
            chromList = []
            cUrves = []
            
            varFrom = _attr['varfrom']
            varTo = _attr['varto']
            if varTo-varFrom == 0:
                varRange = 1
            else:
                varRange = varTo-varFrom+1
                
            for Vars in range(varRange):
                # set num latent variables
                for Runs in range(_attr['runs']):            
                    # run ga-dfa
                    # create initial population
                    chrom = genic.crtpop(_attr['inds'],
                                         Vars+varFrom, xdata.shape[1])
                    
                    # evaluate initial population
                    if self.dtype == 'DFA':
                        # check factors
                        if int(_attr['maxf']) >= int(max(self.data['class'][:, 0])):
                            Lvs = int(max(self.data['class'][:, 0])) - 1
                        else:
                            Lvs = int(_attr['maxf'])
                        # run dfa
                        scores = mva.fitfun.call_dfa(chrom, xdata, Lvs, mask,
                                                     self.data)
                        
                    elif self.dtype == 'PLS':
                        # set factors
                        Lvs = int(_attr['maxf'])
                        # run pls
                        scores = mva.fitfun.call_pls(chrom, xdata, Lvs, mask,
                                                     self.data)
                    
                    # add additional methods here
                    
                    count = 0
                    
                    # set stopping criterion
                    if self.parent.optDlg.cbGaRepUntil.GetValue() is False:
                        stop = _attr['mgen']
                    else:
                        stop = 1000
                        chromRecord = np.zeros((1, Vars+varFrom))
                    
                    while count < stop:
                        # linear ranking
                        ranksc, chrom, scores = genic.rank(chrom, scores)
                        
                        # select individuals from population
                        chromSel = genic.select(ranksc, chrom, _attr['insr'])
                        
                        # perform crossover
                        if self.parent.optDlg.cbGaXover.GetValue():
                            chromSel = genic.xover(chromSel, _attr['xovr'],
                                                         xdata.shape[1])
                            
                        # perform mutation
                        if self.parent.optDlg.cbGaMut.GetValue():
                            chromSel = genic.mutate(chromSel, _attr['mutr'],
                                        xdata.shape[1])
                            
                        # evaluate chromSel
                        if self.dtype == 'DFA':
                            scoresSel = mva.fitfun.call_dfa(chromSel, xdata,
                                                            Lvs, mask, self.data)
                            
                        elif self.dtype == 'PLS':
                            scoresSel = mva.fitfun.call_pls(chromSel, xdata,
                                                            Lvs, mask, self.data)
                        # add additional methods here
                        
                        # reinsert chromSel replacing worst parents in chrom
                        chrom, scores = genic.reinsert(chrom, chromSel,
                                                             scores, scoresSel)
                        
                        if count == 0:
                            scoresOut = [min(min(scores))]
                        else:
                            scoresOut.append(min(min(scores)))
                        
                        # Build history for second stopping criterion
                        if self.parent.optDlg.cbGaRepUntil.GetValue() is True:
                            Best = scores[0]
                            tChrom = chrom[0]
                            chromRecord = np.concatenate((chromRecord,
                                                          tChrom[nax, :]), 0)
                            if count >= int(_attr['rgen']):
                                chk = 0
                                for n in range(count + 1, count - _attr['rgen'] + 1, -1):
                                    a = chromRecord[n-1].tolist()
                                    a.extend(chromRecord[n].tolist())
                                    if len(np.unique(np.array(a))) == chromRecord.shape[1]:
                                        chk += 1
                                if chk == _attr['rgen']:
                                    break
                        
                        count += 1
                        
                        # report progress to status bar
                        self.parent.prnt.sbMain.SetStatusText(' '.join(('Variable',
                                                                        str(Vars+varFrom))), 0)
                        self.parent.prnt.sbMain.SetStatusText(' '.join(('Run', str(Runs + 1))
                                                                       ), 1)
                        self.parent.prnt.sbMain.SetStatusText(' '.join(('Generation',
                                                                        str(count))), 2)
                        
                    # Save GA optimisation curve
                    scoresOut = np.asarray(scoresOut)
                    
                    # concatenate run result
                    if varRange == 1:
                        if Vars+Runs == 0:
                            # scores
                            if self.dtype in ['PLS']:
                                scoreList = [float(scores[0])]
                                cUrves = np.reshape(scoresOut,
                                                    (1, len(scoresOut)))
                            else:
                                scoreList = [1 / float(scores[0])]
                                cUrves = np.reshape(1 / scoresOut,
                                                    (1, len(scoresOut)))
                            # chromosomes
                            chromList = np.take(self.data['variableidx'],
                                                chrom[0, :].tolist())[nax, :]
                            chromList.sort()
                            # opt curves
                            
                        else:
                            # scores
                            if self.dtype in ['PLS']:
                                scoreList.append(float(scores[0]))
                            else:
                                scoreList.append(1 / float(scores[0]))
                                scoresOut = 1 / scoresOut
                            # chromosomes
                            ins = np.take(self.data['variableidx'],
                                          chrom[0, :].tolist())[nax, :]
                            ins.sort()
                            chromList = np.concatenate((chromList, ins), 0)
                            # opt curves
                            length = cUrves.shape[1]
                            if length < len(scoresOut):
                                cUrves = np.concatenate(
                                    (cUrves, np.zeros((len(cUrves),
                                                       len(scoresOut)-length))), 1)

                            elif length > len(scoresOut):
                                scoresOut = np.concatenate(
                                    (np.reshape(scoresOut, (1, len(scoresOut))),
                                     np.zeros((1, length-len(scoresOut)))), 1)
                                scoresOut = np.reshape(scoresOut, (scoresOut.shape[1], ))
                            cUrves = np.concatenate((cUrves, np.reshape(scoresOut,
                                                (1, len(scoresOut)))), 0)
                    elif varRange > 1:
                        if Vars+Runs == 0:
                            # scores
                            if self.dtype in ['PLS']:
                                scoreList = [float(scores[0])]
                                cUrves = np.reshape(scoresOut, (1, len(scoresOut)))
                            else:
                                scoreList = [1/float(scores[0])]
                                cUrves = np.reshape(1.0/scoresOut, (1, len(scoresOut)))
                            #           scoreList = [1.0/float(scores[0])]
                            # chromosomes
                            ins = np.take(self.data['variableidx'],
                                          chrom[0, :].tolist())[nax, :]
                            ins.sort()
                            chromList = np.concatenate(
                                (ins, np.zeros((1, varRange-Vars-1), 'd')), 1)
                            # opt curves
                            # cUrves = np.reshape(scoresOut, (1, len(scoresOut)))
                        else:
                            # scores
                            if self.dtype in ['PLS']:
                                scoreList.append(float(scores[0]))
                            else:
                                scoreList.append(1/float(scores[0]))
                                scoresOut = 1.0/scoresOut
                            #   scoreList.append(1.0/float(scores[0]))
                            # chromosomes
                            ins = np.take(self.data['variableidx'],
                                          chrom[0, :].tolist())[nax, :]
                            ins.sort()
                            chromList = np.concatenate((chromList,
                                  np.concatenate((ins, np.zeros((1,
                                  varRange-Vars-1), 'd')), 1)), 0)
                            
                            # opt curves
                            length = cUrves.shape[1]
                            lscout = len(scoresOut)

                            if length < lscout:
                                cUrves = np.concatenate(
                                    (cUrves, np.zeros((len(cUrves),
                                                       lscout-length))), 1)
                            elif length > lscout:
                                scoresOut = np.concatenate(
                                    (np.reshape(scoresOut, (1, lscout)),
                                     np.zeros((1, length-lscout))), 1)
                                scoresOut = np.reshape(scoresOut, (scoresOut.shape[1], ))
                            
                            cUrves = np.concatenate((cUrves, np.reshape(scoresOut,
                                  (1, lscout))), 0)
                            
            # add results to disctionary
            exec("self.data['ga" + self.dtype.lower() + "chroms'] = chromList")
            exec("self.data['ga" + self.dtype.lower() + "scores'] = scoreList")
            exec("self.data['ga" + self.dtype.lower() + "curves'] = cUrves")
            
            # Create results tree
            self.CreateGaResultsTree(self.parent.optDlg.treGaResults, 
                                     gacurves=cUrves, chroms=chromList,
                                     varfrom=_attr['varfrom'],
                                     varto=_attr['varto'],
                                     runs=_attr['runs']-1)
            
            # enable export btn
            self.btnExportGa.Enable(1)
            
            # reset cursor
            wx.EndBusyCursor()
                    
        # except Exception, error:
        #    wx.EndBusyCursor()
        #    error_box(self, '%s' %str(error))
        #    raise
            
        # clear status bar
        self.parent.prnt.sbMain.SetStatusText('Status', 0)
        self.parent.prnt.sbMain.SetStatusText('', 1)
        self.parent.prnt.sbMain.SetStatusText('', 2)
    
    def CreateGaResultsTree(self, tree, **_attr):
        """Populates GA results tree ctrl
            **_attr - key word _attributes
                Defaults:
                    'gacurves' = None      - Optimisation curves from each ind. run
                    'chroms' = None        - Array of chromosomes
                    'varfrom' = 2          - Min. no. of vars selected
                    'varto' = 2            - Max. no. of vars selected
                    'runs' = 1             - Number of ind. GA runs
                    
        """
        
        # clear tree ctrl
        tree.DeleteAllItems()
        tree.AddRoot('Root') 
        dfaRoot = tree.GetRootItem() 
        
        # generate top score list
        _attr['gacurves'] = np.concatenate(
            (_attr['gacurves'], np.zeros((len(_attr['gacurves']), 1))), 1)
        gaScoreList = []
        for x in range(len(_attr['gacurves'])):
            t = _attr['gacurves'][x, ].tolist().index(0)
            gaScoreList.append(_attr['gacurves'][x, t-1])
        
        idx = []
        for varbls in range(_attr['varto'] - _attr['varfrom'] + 1):
            idx.extend((np.argsort(np.array(gaScoreList[varbls * (_attr['runs'] + 1):\
                        (varbls * (_attr['runs'] + 1)) + _attr['runs'] + 1])) +
                        (varbls * (_attr['runs'] + 1))).tolist())
        exec("self.data['ga" + self.dtype.lower() + "treeorder'] = idx")
        
        tree.DeleteAllItems()
        tree.AddRoot('Root') 
        dfaRoot = tree.GetRootItem() 
        
        #  if self.cbDfaSavePc.GetValue() is False:   # saved only best result
        noSaveChroms = 1
        #  elif self.cbDfaSavePc.GetValue() is True:  # saved % of results
        #       noSaveChroms = int((float(self.stDfaSavePc.GetValue())/100)*int(self.stDfaNoInds.GetValue()))
            
        TreeItemIdList = []
        Count, IterCount = 0, 0
        for varbls in range(_attr['varto'] - _attr['varfrom'] + 1):
            text = ' variables'.join(str(varbls + _attr['varfrom']))
            NewVar = tree.AppendItem(dfaRoot, text)
            TreeItemIdList.append(NewVar)
            for runs in range(_attr['runs']+1):
                # for mch in range(noSaveChroms):
                #      RunLabel = np.sort(_attr['chroms'][Count+mch, 0:vars+_attr['varfrom']]).tolist()
                #      NewChrom = tree.AppendItem(NewVar, string.join(('#', str(IterCount+1), ' ',
                #      str(np.take(np.reshape(self.data['indlabelsfull'],
                #      (len(self.data['indlabelsfull']), )), RunLabel)), ' ',
                #       '%.2f' %(gaScoreList[Count+mch])), ''))
                #      TreeItemIdList.append(NewChrom)
                #      IterCount += 1
                #      Count += (mch+1)

                nruns = _attr['runs'] + 1
                RunLabel = np.sort(_attr['chroms'][idx[(varbls * nruns) + runs],
                                   0:varbls + _attr['varfrom']]).tolist()

                indlabelsfull = self.data['indlabelsfull']
                indlabels = str(np.take(np.reshape(indlabelsfull,
                                        (len(indlabelsfull),)), RunLabel))
                ga_score = '%.2f' % (gaScoreList[idx[(varbls * nruns) + runs]])

                text = '#%i %s %s' % (IterCount+1, indlabels, ga_score)
                NewChrom = tree.AppendItem(NewVar, text)

                TreeItemIdList.append(NewChrom)
                IterCount += 1
                # Count += (mch+1)
                
        tree.Expand(dfaRoot)
        for i in range(len(TreeItemIdList)):
            tree.Expand(TreeItemIdList[i])

class selParam(fpb.FoldPanelBar):
    def _init_coll_gbsGaParams_Growables(self, parent):
        
        parent.AddGrowableCol(0)
        parent.AddGrowableCol(1)
        parent.AddGrowableCol(2)
    
    def _init_coll_gbsGaParams_Items(self, parent):
        
        parent.Add(wx.StaticText(self.plParams, -1, 'No. vars. from',
                                 style=wx.ALIGN_RIGHT),
                   (0, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.spnGaVarsFrom, (0, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        # parent.AddSpacer(wx.Size(8, 8), (0, 2), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(wx.StaticText(self.plParams, -1, 'No. vars. to',
                                 style=wx.ALIGN_RIGHT),
                   (1, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.spnGaVarsTo, (1, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        # parent.AddSpacer(wx.Size(8, 8), (1, 2), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(wx.StaticText(self.plParams, -1, 'No. inds.',
                                 style=wx.ALIGN_RIGHT),
                   (2, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.spnGaNoInds, (2, 1), border=10, flag=wx.EXPAND,
              span=(1, 1))
        # parent.AddSpacer(wx.Size(8, 8), (2, 2), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(wx.StaticText(self.plParams, -1, 'No. runs', style=wx.ALIGN_RIGHT), 
              (3, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.spnGaNoRuns, (3, 1), border=10, flag=wx.EXPAND,
              span=(1, 1))              
        # parent.AddSpacer(wx.Size(8, 8), (3, 2), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(wx.StaticText(self.plParams, -1, 'Crossover rate', style=wx.ALIGN_RIGHT), 
              (4, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.stGaXoverRate, (4, 1), border=10, flag=wx.EXPAND,
              span=(1, 1))
        parent.Add(self.cbGaXover, (4, 2), border=10, flag=wx.EXPAND,
              span=(1, 1))
        parent.Add(wx.StaticText(self.plParams, -1, 'Mutation rate', style=wx.ALIGN_RIGHT), 
              (5, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.stGaMutRate, (5, 1), border=10, flag=wx.EXPAND,
              span=(1, 1))              
        parent.Add(self.cbGaMut, (5, 2), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        parent.Add(wx.StaticText(self.plParams, -1, 'Insertion rate', style=wx.ALIGN_RIGHT), 
                   (6, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.stGaInsRate, (6, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        # parent.AddSpacer(wx.Size(8, 8), (6, 2), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(wx.StaticText(self.plParams, -1, 'Max. factors',
                                 style=wx.ALIGN_RIGHT),
                  (7, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.spnGaMaxFac, (7, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        # parent.AddSpacer(wx.Size(8, 8), (7, 2), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(wx.StaticText(self.plParams, -1, 'Max. gens',
                                 style=wx.ALIGN_RIGHT),
                  (8, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.spnGaMaxGen, (8, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        parent.Add(self.cbGaMaxGen, (8, 2), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        parent.Add(wx.StaticText(self.plParams, -1, 'Repeat until',
                                 style=wx.ALIGN_RIGHT),
                   (9, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.spnGaRepUntil, (9, 1), border=10, flag=wx.EXPAND,
              span=(1, 1))
        parent.Add(self.cbGaRepUntil, (9, 2), border=10, flag=wx.EXPAND,
              span=(1, 1))
        parent.Add(wx.StaticText(self.plParams, -1, 'Resample',
                                 style=wx.ALIGN_RIGHT),
                  (10, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.spnResample, (10, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        # parent.AddSpacer(wx.Size(8, 8), (11, 2), border=10, flag=wx.EXPAND, span=(2, 3))
              
    def _init_selparam_sizers(self):
        # generated method, don't edit
        self.gbsGaParams = wx.GridBagSizer(5, 5)
        self.gbsGaParams.SetCols(3)
        self.gbsGaParams.SetRows(12)
        
        self._init_coll_gbsGaParams_Items(self.gbsGaParams)
        self._init_coll_gbsGaParams_Growables(self.gbsGaParams)
        
        self.fpParams.SetSizer(self.gbsGaParams)
    
    def _init_selparam_ctrls(self, prnt):
        fpb.FoldPanelBar.__init__(self, prnt, -1, pos=wx.DefaultPosition, 
              size=wx.DefaultSize, agwStyle= fpb.FPB_SINGLE_FOLD)
        self.SetAutoLayout(True)
        
        icons = wx.ImageList(16, 16)
        icons.Add(wx.Bitmap(os.path.join('bmp', 'arrown.png'), wx.BITMAP_TYPE_PNG))
        icons.Add(wx.Bitmap(os.path.join('bmp', 'arrows.png'), wx.BITMAP_TYPE_PNG))
        
        self.fpParams = self.AddFoldPanel("Parameters", collapsed=True, 
              foldIcons=icons)
        self.fpParams.SetAutoLayout(True)
        
        self.fpResults = self.AddFoldPanel("Results", collapsed=True, 
              foldIcons=icons)  
        self.fpResults.SetAutoLayout(True)
        self.fpResults.Bind(wx.EVT_SIZE, self.OnFpbResize)
        
        self.plParams = wx.Panel(id=-1, name='plParams', parent=self.fpParams,
              pos=wx.Point(0, 0), size=wx.Size(200, 350),
              style=wx.TAB_TRAVERSAL)
        self.plParams.SetToolTip('')
        self.plParams.SetConstraints(LayoutAnchors(self.plParams, True, True,
              True, True))
        
        self.spnGaVarsFrom = wx.SpinCtrl(id=-1, initial=2, max=100, min=2,
              name='spnGaVarsFrom', parent=self.plParams, pos=wx.Point(73,
              0), size=wx.Size(15, 21), style=wx.SP_ARROW_KEYS)
        self.spnGaVarsFrom.SetToolTip('Variable range from')
        
        self.spnGaVarsTo = wx.SpinCtrl(id=-1, initial=2, max=100, min=2,
              name='spnGaVarsTo', parent=self.plParams, pos=wx.Point(219,
              0), size=wx.Size(15, 21), style=wx.SP_ARROW_KEYS)
        self.spnGaVarsTo.SetToolTip('Variable range to')
        
        self.spnGaNoInds = wx.SpinCtrl(id=-1, initial=10, max=1000, min=10,
              name='spnGaNoInds', parent=self.plParams, pos=wx.Point(73,
              23), size=wx.Size(15, 21), style=wx.SP_ARROW_KEYS)
        self.spnGaVarsTo.SetToolTip('Number of individuals')
        
        self.spnGaNoRuns = wx.SpinCtrl(id=-1, initial=1, max=1000, min=1,
              name='spnGaNoRuns', parent=self.plParams, pos=wx.Point(219,
              23), size=wx.Size(15, 21), style=wx.SP_ARROW_KEYS)
        self.spnGaVarsTo.SetToolTip('Number of independent GA runs')
        
        self.stGaXoverRate = wx.TextCtrl(id=-1, name='stGaXoverRate',
                                         value='0.8', parent=self.plParams,
                                         pos=wx.Point(216, 48),
                                         size=wx.Size(15, 21), style=0)
        self.stGaXoverRate.SetToolTip('Crossover rate')
        
        self.cbGaXover = wx.CheckBox(id=-1, label='', name='cbGaXover',
              parent=self.plParams, pos=wx.Point(0, 46), size=wx.Size(10, 21), 
              style=wx.ALIGN_LEFT)
        self.cbGaXover.SetValue(True)
        self.cbGaXover.SetToolTip('')
        
        self.stGaMutRate = wx.TextCtrl(id=-1, name='stGaMutRate', value='0.4',
                                       parent=self.plParams,
                                       pos=wx.Point(216, 48),
                                       size=wx.Size(15, 21), style=0)
        self.stGaMutRate.SetToolTip('Mutation rate')

        self.cbGaMut = wx.CheckBox(id=-1, label='', name='cbGaMut',
                                   parent=self.plParams, pos=wx.Point(146, 46),
                                   size=wx.Size(10, 21), style=wx.ALIGN_LEFT)
        self.cbGaMut.SetValue(True)
        self.cbGaMut.SetToolTip('')
        
        self.stGaInsRate = wx.TextCtrl(id=-1, name='stGaInsRate', value='0.8',
                                       parent=self.plParams,
                                       pos=wx.Point(216, 48),
                                       size=wx.Size(15, 21), style=0)
        self.stGaXoverRate.SetToolTip('Insertion rate')

        self.spnGaMaxFac = wx.SpinCtrl(id=-1, initial=1, max=100, min=1,
                                       name='spnGaMaxFac', parent=self.plParams,
                                       pos=wx.Point(219, 69),
                                       size=wx.Size(15, 21),
                                       style=wx.SP_ARROW_KEYS)
        self.spnGaMaxFac.SetToolTip('Maximum number of latent variables')
        
        self.spnGaMaxGen = wx.SpinCtrl(id=-1, initial=5, max=1000, min=5,
                                       name='spnGaMaxGen', parent=self.plParams,
                                       pos=wx.Point(73, 92),
                                       size=wx.Size(15, 21),
                                       style=wx.SP_ARROW_KEYS)
        self.spnGaMaxGen.SetToolTip('Maximum number of generations')
        
        self.cbGaMaxGen = wx.CheckBox(id=-1, label='', name='cbGaMaxGen',
                                      parent=self.plParams, pos=wx.Point(0, 92),
                                      size=wx.Size(10, 21), style=wx.ALIGN_LEFT)
        self.cbGaMaxGen.SetValue(True)
        self.cbGaMaxGen.SetToolTip('')
        self.cbGaMaxGen.Show(False)
        
        self.spnGaRepUntil = wx.SpinCtrl(id=-1, initial=5, max=1000, min=5,
                                         name='spnGaRepUntil',
                                         parent=self.plParams,
                                         pos=wx.Point(219, 92),
                                         size=wx.Size(15, 21),
                                         style=wx.SP_ARROW_KEYS)
        self.spnGaRepUntil.SetToolTip('Repeat generations until')

        self.cbGaRepUntil = wx.CheckBox(id=-1, label='', name='cbGaRepUntil',
                                        parent=self.plParams,
                                        pos=wx.Point(146, 92),
                                        size=wx.Size(10, 21),
                                        style=wx.ALIGN_LEFT)
        self.cbGaRepUntil.SetValue(False)
        self.cbGaRepUntil.SetToolTip('')
        
        self.spnResample = wx.SpinCtrl(id=-1, initial=1,
              max=100, min=1, name='spnResample', parent=self.plParams, pos=wx.Point(73,
              92), size=wx.Size(15, 21), style=wx.SP_ARROW_KEYS)
        self.spnResample.SetToolTip('Number of n-fold validation steps')
        
        self.treGaResults = wx.TreeCtrl(id=-1, name='treGaResults',
                                        parent=self.fpResults,
                                        pos=wx.Point(0, 23),
                                        size=wx.Size(100, 100),
                                        style=wx.TR_DEFAULT_STYLE |
                                        wx.TR_HAS_BUTTONS,
                                        validator=wx.DefaultValidator)
        self.treGaResults.SetToolTip('')
        self.treGaResults.Bind(wx.EVT_TREE_ITEM_ACTIVATED,
                               self.OnTregaaresultsTreeItemActivated)
        self.treGaResults.SetConstraints(LayoutAnchors(
            self.treGaResults, True, True, True, True))
        
        self.AddFoldPanelWindow(self.fpParams, self.plParams, fpb.FPB_ALIGN_WIDTH)
        self.AddFoldPanelWindow(self.fpResults, self.treGaResults, fpb.FPB_ALIGN_WIDTH)
        
        self._init_selparam_sizers()

    def __init__(self, parent):
        self._init_selparam_ctrls(parent)
        
        self.Expand(self.fpParams)
        self.Expand(self.fpResults)
        
        self.prnt = parent
        # self.tbar = self.prnt.splitPrnt.titleBar
        
    def OnFpbResize(self, event):
        self.treGaResults.SetSize((self.treGaResults.GetSize()[0],
              self.GetSize()[1]-50))
    
    def CountForOptCurve(self, curve):
        count = 0
        for item in curve:
            if item != 0:
                count += 1
        return count
    
    def OnTregaaresultsTreeItemActivated(self, event):
        self.tbar = self.prnt.splitPrnt.titleBar
        # define dfa or pls
        exec("self.chroms = self.tbar.data['ga" + self.prnt.splitPrnt.dtype.lower() + "chroms']")
        exec("self.scores = self.tbar.data['ga" + self.prnt.splitPrnt.dtype.lower() + "scores']")
        exec("self.curves = self.tbar.data['ga" + self.prnt.splitPrnt.dtype.lower() + "curves']")
        exec("self.treeorder = self.tbar.data['ga" + self.prnt.splitPrnt.dtype.lower() + "treeorder']")
        
        # colours and markers for plotting
        markerList = ['circle', 'square', 'cross', 'plus']
        colourList = ['BLUE', 'BROWN', 'CYAN', 'GREY', 'GREEN',
                      'MAGENTA', 'ORANGE', 'PURPLE', 'VIOLET']
        
        # set busy cursor
        # wx.BeginBusyCursor()
        
        if self.tbar.cbxData.GetSelection() == 0:
            xdata = self.tbar.data['raw']
        elif self.tbar.cbxData.GetSelection() == 1:
            xdata = self.tbar.data['proc']
            
        currentItem = event.GetItem()
        chromId = self.treGaResults.GetItemText(currentItem)
        chkValid = float(chromId.split(']')[1])
        chromId = chromId.split('[')[0]
        chromId = int(chromId.split('#')[1])-1
        currentChrom = self.chroms[self.treeorder[chromId]].tolist()
        
        # Plot frequency of variable selection for no. vars
        # Get chrom data and error data for each child
        Chroms = []
        VarsId = self.treGaResults.GetItemParent(currentItem)
        NoVars = self.treGaResults.GetItemText(VarsId)
        NoVars = int(NoVars.split(' ')[0])
        
        # adjust chrom length if mutliple var subsets used
        currentChrom = currentChrom[0:NoVars]
        self.currentChrom = currentChrom
        
        # if chkValid > 10.0**-5:
        # Re-Running DFA
        # set no. DFs
        if len(currentChrom) < int(self.spnGaMaxFac.GetValue()):
            Lvs = len(currentChrom)
        else:
            Lvs = int(self.spnGaMaxFac.GetValue())            
        
        # run dfa
        if self.prnt.splitPrnt.dtype == 'DFA':
            self.tbar.data['gadfadfscores'], \
            self.tbar.data['gadfadfaloads'], gaError = \
                mva.fitfun.rerun_dfa(
                    currentChrom, xdata,
                    self.tbar.data['validation'],
                    self.tbar.data['class'][:, 0],
                    self.tbar.data['label'], Lvs)
            
            # plot scores
            self.tbar.spnGaScoreFrom.SetRange(1, self.tbar.data['gadfadfaloads'].shape[1])
            self.tbar.spnGaScoreFrom.SetValue(1)
            self.tbar.spnGaScoreTo.SetRange(1, self.tbar.data['gadfadfaloads'].shape[1])
            self.tbar.spnGaScoreTo.SetValue(1)
            if self.tbar.data['gadfadfaloads'].shape[1] > 1:
                self.tbar.spnGaScoreTo.SetValue(2)
            
            plotScores(self.prnt.splitPrnt.plcGaModelPlot1,
                       self.tbar.data['gadfadfscores'],
                       cl=self.tbar.data['class'][:, 0],
                       labels=self.tbar.data['label'],
                       validation=self.tbar.data['validation'],
                       col1=self.tbar.spnGaScoreFrom.GetValue()-1,
                       col2=self.tbar.spnGaScoreTo.GetValue()-1,
                       title='DF Scores',
                       xLabel='t[' + str(self.tbar.spnGaScoreFrom.GetValue()) + ']',
                       yLabel='t[' + str(self.tbar.spnGaScoreTo.GetValue()) +']',
                       xval=True, text=True, pconf=True, symb=False, usecol=[], usesym=[])
            
        if self.prnt.splitPrnt.dtype in ['PLS']:
            # select only chrom vars from x
            pls_output = mva.fitfun.rerun_pls(currentChrom, xdata, 
                  self.tbar.data['class'],
                  self.tbar.data['validation'],
                  Lvs)
            
            self.tbar.data['gaplsplsloads'] = pls_output['W']
            self.tbar.data['gaplsscores'] = pls_output['predictions']
            self.tbar.data['gaplsfactors'] = pls_output['facs']
            self.tbar.data['gaplsrmsept'] = pls_output['RMSEPT']
            # self.data['rmsec'] = pls_output['rmsec']
            # self.data['rmsepc'] = pls_output['rmsepc']
            # self.data['rmsept'] = pls_output['rmsept']
            # self.data['RMSEC'] = pls_output['RMSEC']
            # self.data['RMSEPC'] = pls_output['RMSEPC']
            # self.data['RMSEPT'] = pls_output['RMSEPT']
            
            gaError = np.concatenate((np.array(pls_output['rmsec'])[nax, :],
                                      np.array(pls_output['rmsepc'])[nax, :]), 0)
        
            # set defaults
            self.tbar.spnGaScoreFrom.SetValue(1)
            self.tbar.spnGaScoreTo.SetValue(1)
            
            # plot pls predictions
            self.prnt.splitPrnt.plcGaModelPlot1 = \
                PlotPlsModel(self.prnt.splitPrnt.plcGaModelPlot1,
                             model='ga', tbar=self.prnt.splitPrnt.prnt.prnt.tbMain,
                             cL=self.tbar.data['class'],
                             scores=pls_output['plsscores'],
                             predictions=pls_output['predictions'],
                             validation=self.tbar.data['validation'],
                             RMSEPT=pls_output['RMSEPT'],
                             factors=pls_output['facs'],
                             dtype=0, col1=0, col2=1, label=self.tbar.data['label'],
                             symbols=self.prnt.splitPrnt.prnt.tbMain.tbSymbols.GetValue(),
                             usetxt=self.prnt.splitPrnt.prnt.tbMain.tbPoints.GetValue(),
                             errplot=False, usecol=[], usesym=[])
                        
        # if self.cbDfaSavePc.GetValue() is False:
        NoRuns = int(self.spnGaNoRuns.GetValue())
        # else:
        #    tp = int((float(self.stDfaSavePc.GetValue())/100)*int(self.stDfaNoInds.GetValue()))
        #    NoRuns = int(self.stDfaNoRuns.GetValue())*tp
        
        for runs in range(NoRuns):
            if runs == 0:
                ChildId = self.treGaResults.GetFirstChild(VarsId)[0]
            else:
                ChildId = self.treGaResults.GetNextSibling(ChildId) 
            
            # get chrom ids
            itemId = self.treGaResults.GetItemText(ChildId)
            itemId = itemId.split('[')[0]
            itemId = int(itemId.split('#')[1])-1
            items = self.chroms[itemId][0:NoVars]
            for each in items:
                Chroms.append(each)
        
        # calculate variable frequencies
        VarFreq = np.zeros((1, 2), 'i')
        while len(Chroms) > 1:
            VarFreq = np.concatenate((VarFreq,
                                      np.reshape([float(Chroms[0]), 1.0], (1, 2))),
                                     0)
            NewChroms = []
            for i in range(1, len(Chroms), 1):
                if Chroms[i] == VarFreq[VarFreq.shape[0]-1, 0]:
                    VarFreq[VarFreq.shape[0]-1, 1] += 1.0
                else:
                    NewChroms.append(float(Chroms[i]))
            Chroms = NewChroms
        if len(Chroms) == 1:
            VarFreq = np.concatenate((VarFreq, np.reshape([float(Chroms[0]), 1.0], (1, 2))), 0)
        VarFreq = VarFreq[1:VarFreq.shape[0]] 
        
        # Plot var freq as percentage
        VarFreq[:, 1] = (VarFreq[:, 1]/sum(VarFreq[:, 1]))*100
        # plot variable frequencies
        LineObj = []
        for i in range(VarFreq.shape[0]):
            Start = np.concatenate(
                (np.reshape(self.tbar.data['xaxisfull'][int(VarFreq[i, 0])], (1, 1)),
                 np.reshape(0.0, (1, 1))), 1)
            FullVarFreq = np.concatenate(
                (np.reshape(self.tbar.data['xaxisfull'][int(VarFreq[i, 0])], (1, 1)),
                 np.reshape(VarFreq[i, 1], (1, 1))), 1)
            FullVarFreq = np.concatenate((Start, FullVarFreq), 0)

            if int(VarFreq[i, 0]) in currentChrom:
                LineObj.append(PolyLine(FullVarFreq, colour='red', width=2,
                                        style=wx.SOLID))
            else:
                LineObj.append(PolyLine(FullVarFreq, colour='black', width=2,
                                        style=wx.SOLID))
        
        meanSpec = np.concatenate(
            (np.reshape(self.tbar.data['xaxisfull'],
                        (len(self.tbar.data['xaxisfull']), 1)),
             np.reshape(mva.process.scale01(np.reshape(np.mean(xdata, 0),
              (1, xdata.shape[1])))*max(VarFreq[:, 1]), (xdata.shape[1], 1))), 1)

        meanSpec = PolyLine(meanSpec, colour='black', width=0.75, style=wx.SOLID)
        LineObj.append(meanSpec)
        DfaPlotFreq = PlotGraphics(LineObj, 'Frequency of Variable Selection',
                                   'Variable ID', 'Frequency (%)')
        xAx = (min(self.tbar.data['xaxisfull']),
              max(self.tbar.data['xaxisfull']))
        yAx = (0, max(VarFreq[:, 1])*1.1)
        self.prnt.splitPrnt.plcGaFreqPlot.Draw(DfaPlotFreq, xAxis=xAx, yAxis=yAx)
        
        # plot variables
        list = []
        for each in currentChrom:
            list.append(str(self.tbar.data['indlabelsfull'][int(each)]))
        
        self.tbar.cbxFeature1.SetItems(list)
        self.tbar.cbxFeature2.SetItems(list)
        self.tbar.cbxFeature1.SetSelection(0)
        self.tbar.cbxFeature2.SetSelection(0)
        
        self.PlotGaVariables(self.prnt.splitPrnt.plcGaFeatPlot)
        
        # plot ga optimisation curve
        noGens = self.CountForOptCurve(self.curves[chromId])
        gaPlotOptLine = plotLine(self.prnt.splitPrnt.plcGaOptPlot,
                                 np.reshape(self.curves[chromId, 0:noGens], (1, noGens)),
                                 xaxis=np.arange(1, noGens+1)[:, nax], rownum=0,
                                 tit='GA Optimisation Curve',
                                 xLabel='Generation',
                                 yLabel='Objective function score', wdth=3,
                                 dtype='single', ledge=[])
        
        # plot loadings
        self.tbar.data['gacurrentchrom'] = currentChrom
        
        exec("self.plotGaLoads(currentChrom, self.tbar.data['ga" +
             self.prnt.splitPrnt.dtype.lower() +
             self.prnt.splitPrnt.dtype.lower() +
             "loads'], self.prnt.splitPrnt.plcGaSpecLoad, 0)")
        
        # plot eigenvalues
        if gaError.shape[0] == 1:
            plotLine(self.prnt.splitPrnt.plcGaEigs, gaError,
                     xaxis=np.arange(1, gaError.shape[1]+1)[:, nax],
                     rownum=0, xLabel='Discriminant Function', tit='',
                     yLabel='Eigenvalues', wdth=3, dtype='single',
                     ledge=[])
        else:
            plotLine(self.prnt.splitPrnt.plcGaEigs, gaError,
                     xaxis=np.arange(1, gaError.shape[1]+1)[:, nax],
                     xLabel='Latent Variable', tit='',
                     yLabel='RMS Error', dtype='multi',
                     ledge=['Train err', 'Test err'], wdth=3)
            
            self.prnt.splitPrnt.nbGaModPlot.SetPageText(1, 'RMS Error')
        
        # plot variables vs. error for pairs
        gaVarFrom = int(self.spnGaVarsFrom.GetValue())
        gaVarTo = int(self.spnGaVarsTo.GetValue())
        if gaVarTo-gaVarFrom == 0:
            gaVarRange = 1
        else:
            gaVarRange = gaVarTo-gaVarFrom+1
        
        VarErrObj = []
        MaxVarErr = 0
        MinVarErr = 0
        for vars in range(gaVarRange):
            VarErr = np.zeros((1, 2), 'd')
            if vars == 0:
                gaRoot = self.treGaResults.GetRootItem() 
                VarsId = self.treGaResults.GetFirstChild(gaRoot)[0]
            else:
                VarsId = self.treGaResults.GetNextSibling(VarsId)
                
            Var = self.treGaResults.GetItemText(VarsId)
            
            Var = Var.split(' ')[0]
            
            for runs in range(int(self.spnGaNoRuns.GetValue())):        
                if runs == 0:
                    RunsId = self.treGaResults.GetFirstChild(VarsId)[0]
                else:
                    RunsId = self.treGaResults.GetNextSibling(RunsId)
                Run = self.treGaResults.GetItemText(RunsId)
                Run = Run.split(' ')
                Run = Run[len(Run)-1]
                VarErr = np.concatenate((VarErr, np.reshape([float(Var),
                      float(Run)], (1, 2))), 0)
        
            VarErr = VarErr[1:VarErr.shape[0], :]
            
            if max(VarErr[:, 1]) > MaxVarErr:
                MaxVarErr = max(VarErr[:, 1])
            if min(VarErr[:, 1]) < MinVarErr:
                MinVarErr = min(VarErr[:, 1])
            
            # select marker shape and colour for pair
            VarErrObj.append(PolyMarker(VarErr, legend='%s vars' % Var,
                  colour=colourList[int(round(sp.rand(1, )[0]*(len(colourList)-1)))],
                  fillstyle=wx.SOLID, marker=markerList[int(round(sp.rand(1, )[0]*(len(markerList)-1)))],
                  size=1.5))
            gaPlotVarErr = PlotGraphics(VarErrObj, 'Fitness Summary  ',
                                        'Total no. variables selected',
                                        'Fitness')
            Xax = (gaVarFrom-0.25, gaVarTo+0.25)
            Yax = (MinVarErr, MaxVarErr)
            self.prnt.splitPrnt.plcGaGrpDistPlot.Draw(gaPlotVarErr, xAxis=Xax, yAxis=Yax)
            
            # Enable ctrls
            self.tbar.spnGaScoreFrom.Enable(1)
            self.tbar.spnGaScoreTo.Enable(1)
            self.tbar.cbxFeature1.Enable(1)
            self.tbar.cbxFeature2.Enable(1)
        
    def PlotGaVariables(self, canvas):
        self.tbar = self.prnt.splitPrnt.titleBar
        chrom = self.currentChrom
        
        pos1 = int(self.tbar.cbxFeature1.GetSelection())
        pos2 = int(self.tbar.cbxFeature2.GetSelection())
        
        if self.tbar.cbxData.GetSelection() == 0:
            xdata = self.tbar.data['raw']
        else:
            xdata = self.tbar.data['proc']
                
        if pos1 == pos2:
            coords = np.reshape(np.take(xdata, [int(chrom[pos1])], 1), (len(xdata), 1))
            L1 = 'Dummy'
            L2 = str(self.tbar.data['indlabelsfull'][int(chrom[pos1])])
            plotScores(canvas, coords, cl=self.tbar.data['class'][:, 0],
                       labels=self.tbar.data['label'],
                       validation=self.tbar.data['validation'],
                       col1=0, col2=0, title=canvas.last_draw[0].title, xLabel=L1,
                       yLabel=L2, xval=True,
                       pconf=False,   # , self.prnt.splitPrnt.parent.parent.tbMain.tbConf.GetValue(),
                       text=self.prnt.splitPrnt.prnt.tbMain.tbPoints.GetValue(),
                       symb=self.prnt.splitPrnt.prnt.tbMain.tbSymbols.GetValue(),
                       usecol=[], usesym=[])
                        
        else:
            coords = np.reshape(np.take(xdata, [int(chrom[pos1]), int(chrom[pos2])], 1), (len(xdata), 2))
            L1 = str(self.tbar.data['indlabelsfull'][int(chrom[pos1])])
            L2 = str(self.tbar.data['indlabelsfull'][int(chrom[pos2])])
            plotScores(canvas, coords, cl=self.tbar.data['class'][:, 0],
                       labels=self.tbar.data['label'],
                       validation=self.tbar.data['validation'],
                       col1=0, col2=1, title=canvas.last_draw[0].title, xLabel=L1,
                       yLabel=L2, xval=True,
                       pconf=False,  # self.prnt.splitPrnt.parent.parent.tbMain.tbConf.GetValue(),
                       text=self.prnt.splitPrnt.prnt.tbMain.tbPoints.GetValue(),
                       symb=self.prnt.splitPrnt.prnt.tbMain.tbSymbols.GetValue(),
                       usecol=[], usesym=[])
        
        self.tbar.data['gavarcoords'] = coords
        
    def plotGaLoads(self, chrom, loads, canvas, xL='Variable'):
        self.tbar = self.prnt.splitPrnt.titleBar
        # factors
        col1 = self.tbar.spnGaScoreFrom.GetValue()-1
        col2 = self.tbar.spnGaScoreTo.GetValue()-1
        
        # Plot loadings
        labels = []
        for each in self.tbar.data['gacurrentchrom']:
            labels.append(self.tbar.data['indlabelsfull'][int(each)])
        
        # gather values
        plotVals = np.concatenate((loads[:, col1][:, nax],
                                   loads[:, col2][:, nax]), 1)
  
        if col1 != col2:
            plotLoads(canvas, plotVals, xaxis=labels, title='DF Loadings', 
                      xLabel='w[' + str(self.tbar.spnGaScoreFrom.GetValue()) + ']',
                      yLabel='w[' + str(self.tbar.spnGaScoreTo.GetValue()) + ']',
                      dtype=1, col1=0, col2=1, usecol=[], usesym=[])
        else:
            # plot loadings as line
            xAx = np.take(self.tbar.data['xaxis'], chrom)[:, nax]
            plotLine(canvas, np.transpose(plotVals), xaxis=xAx, tit='', rownum=col1,
                     xLabel='Variable', yLabel='w[' + str(self.tbar.spnGaScoreTo.GetValue()) + ']',
                     wdth=1, ledge=[], dtype='single')


# -----------------------------------------------------------------------------
# Name:        ga.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2007/05/22
# RCS-ID:      $Id: ga.py, v 1.19 2009/02/26 22:19:47 rmj01 Exp $
# Copyright:   (c) 2006
# Licence:     GNU General Public Licence
# -----------------------------------------------------------------------------

import os

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
from numpy import newaxis as nax

import mva.genetic as genic
import mva.fitfun
import mva.process

from pca import plot_line
from pca import plot_scores
from pca import plot_loads
from pca import MyPlotCanvas
from pca import plot_pls_model
from exp_setup import val_split


class Ga(wx.Panel):
    """genetic algorithm coupled to discriminant function analysis"""
    def __init__(self, parent, id_, pos, size, style, name, dtype):
        """"""
        wx.Panel.__init__(self, id=-1, name='Ga', parent=parent,
                          pos=(47, 118), size=(796, 460),
                          style=wx.TAB_TRAVERSAL)

        _, _, _, _, _ = id_, pos, size, style, name
        self.dtype = dtype
        self.parent = parent
        self._init_ctrls()

    def _init_ctrls(self):
        """"""
        self.SetToolTip('')
        self.SetAutoLayout(True)

        self.splitter = wx.SplitterWindow(id=-1, name='Splitter', parent=self,
                                          pos=(16, 24), size=(272, 168),
                                          style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        self.splitter.SetAutoLayout(True)
        self.splitter.Bind(wx.EVT_SPLITTER_DCLICK, self.on_splitter_dclick)
        self.splitter.splitPrnt = self

        self.p1 = wx.Panel(self.splitter)
        self.p1.prnt = self.splitter
        self.p1.SetAutoLayout(True)

        self.optDlg = SelParam(self.splitter)

        self.nbGaPlsPreds = wx.Notebook(id=-1, name='nbGaPlsPreds',
                                        parent=self.p1, pos=(176, 274),
                                        size=(310, 272),
                                        style=wx.NB_BOTTOM)
        self.nbGaPlsPreds.SetToolTip('')
        self.nbGaPlsPreds.SetAutoLayout(True)
        self.nbGaPlsPreds.SetConstraints(
            LayoutAnchors(self.nbGaPlsPreds, True, True, True, True))

        self.nbGaPlsPreds.prnt = self.p1
        # noinspection PyUnresolvedReferences
        pretoolbar = self.nbGaPlsPreds.prnt.prnt
        toolbar = pretoolbar.splitPrnt.parent.parent.tbMain
        self.plc_ga_model_plot1 = MyPlotCanvas(id_=-1, name='plcGaModelPlot1',
                                               parent=self.nbGaPlsPreds,
                                               pos=(0, 0), size=(310, 272),
                                               style=0, toolbar=toolbar)
        self.plc_ga_model_plot1.enableZoom = True
        self.plc_ga_model_plot1.enableLegend = True
        self.plc_ga_model_plot1.fontSizeAxis = 8
        self.plc_ga_model_plot1.fontSizeLegend = 8
        self.plc_ga_model_plot1.fontSizeTitle = 10
        self.plc_ga_model_plot1.SetToolTip('')

        self.nbGaModPlot = wx.Notebook(id=-1, name='nbGaModPlot',
                                       parent=self.p1, pos=(760, 326),
                                       size=(310, 272), style=wx.NB_BOTTOM)
        self.nbGaModPlot.prnt = self.p1
        self.nbGaModPlot.SetToolTip('')

        self.plc_ga_eigs = MyPlotCanvas(id_=-1, name='plcGaEigs',
                                        parent=self.nbGaModPlot,
                                        pos=(0, 0), size=(310, 272), style=0,
                                        toolbar=self.parent.parent.tbMain)
        self.plc_ga_eigs.enableZoom = True
        self.plc_ga_eigs.fontSizeAxis = 8
        self.plc_ga_eigs.fontSizeLegend = 8
        self.plc_ga_eigs.fontSizeTitle = 10
        self.plc_ga_eigs.SetToolTip('')

        self.plc_ga_spec_load = MyPlotCanvas(id_=-1, name='plcGaSpecLoad',
                                             parent=self.nbGaModPlot, style=0,
                                             pos=(0, 24), size=(503, 279),
                                             toolbar=self.parent.parent.tbMain)
        self.plc_ga_spec_load.SetToolTip('')
        self.plc_ga_spec_load.enableZoom = True
        self.plc_ga_spec_load.fontSizeAxis = 8
        self.plc_ga_spec_load.fontSizeLegend = 8
        self.plc_ga_spec_load.fontSizeTitle = 10

        self.plc_ga_freq_plot = MyPlotCanvas(id_=-1, name='plcGaFreqPlot',
                                             parent=self.p1, pos=(760, 0),
                                             size=(310, 272), style=0,
                                             toolbar=self.parent.parent.tbMain)
        self.plc_ga_freq_plot.enableZoom = True
        self.plc_ga_freq_plot.fontSizeAxis = 8
        self.plc_ga_freq_plot.fontSizeLegend = 8
        self.plc_ga_freq_plot.fontSizeTitle = 10
        self.plc_ga_freq_plot.SetToolTip('')

        self.plcGaFeatPlot = MyPlotCanvas(id_=-1, name='plcGaFeatPlot',
                                          parent=self.p1, pos=(0, 24),
                                          size=(310, 272), style=0,
                                          toolbar=self.parent.parent.tbMain)
        self.plcGaFeatPlot.SetToolTip('')
        self.plcGaFeatPlot.enableZoom = True
        self.plcGaFeatPlot.enableLegend = True
        self.plcGaFeatPlot.fontSizeAxis = 8
        self.plcGaFeatPlot.fontSizeLegend = 8
        self.plcGaFeatPlot.fontSizeTitle = 10

        self.plcGaGrpDistPlot = MyPlotCanvas(id_=-1, name='plcGaGrpDistPlot',
                                             parent=self.nbGaModPlot, style=0,
                                             pos=(0, 0), size=(310, 272),
                                             toolbar=self.parent.parent.tbMain)
        self.plcGaGrpDistPlot.enableLegend = True
        self.plcGaGrpDistPlot.enableZoom = True
        self.plcGaGrpDistPlot.fontSizeAxis = 8
        self.plcGaGrpDistPlot.fontSizeLegend = 8
        self.plcGaGrpDistPlot.fontSizeTitle = 10
        self.plcGaGrpDistPlot.SetToolTip('')

        self.plcGaOptPlot = MyPlotCanvas(id_=-1, name='plcGaOptPlot',
                                         parent=self.nbGaModPlot,
                                         pos=(0, 0), size=(310, 272), style=0,
                                         toolbar=self.parent.parent.tbMain)
        self.plcGaOptPlot.enableLegend = False
        self.plcGaOptPlot.enableZoom = True
        self.plcGaOptPlot.fontSizeAxis = 8
        self.plcGaOptPlot.fontSizeLegend = 8
        self.plcGaOptPlot.fontSizeTitle = 10
        self.plcGaOptPlot.SetToolTip('')

        self.titleBar = TitleBar(self, id_=-1, text="",
                                 style=bp.BP_USE_GRADIENT,
                                 alignment=bp.BP_ALIGN_LEFT,
                                 gatype=self.dtype)

        self.splitter.SplitVertically(self.optDlg, self.p1, 1)
        self.splitter.SetMinimumPaneSize(1)

        self._init_coll_nb_ga_mod_plot_pages(self.nbGaModPlot)
        self._init_coll_nb_ga_pls_preds_pages(self.nbGaPlsPreds)

        self._init_sizers()

    def _init_coll_bxs_ga1_items(self, parent):
        # generated method, don't edit

        parent.Add(self.bxsGa2, 1, border=0, flag=wx.EXPAND)
        
    def _init_coll_bxs_ga2_items(self, parent):
        # generated method, don't edit

        parent.Add(self.titleBar, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.splitter, 1, border=0, flag=wx.EXPAND)
    
    def _init_coll_grs_ga_items(self, parent):
        # generated method, don't edit

        parent.Add(self.nbGaPlsPreds, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.plc_ga_freq_plot, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.plcGaFeatPlot, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.nbGaModPlot, 0, border=0, flag=wx.EXPAND)
    
    def _init_coll_nb_ga_pls_preds_pages(self, parent):
        """"""
        parent.AddPage(imageId=-1, page=self.plc_ga_model_plot1, select=True,
                       text='')
    
    def _init_coll_nb_ga_mod_plot_pages(self, parent):
        """"""
        parent.AddPage(imageId=-1, page=self.plcGaOptPlot, select=True,
                       text='GA Optimisation Curve')
        parent.AddPage(imageId=-1, page=self.plc_ga_eigs, select=False,
                       text='Eigenvalues')
        parent.AddPage(imageId=-1, page=self.plc_ga_spec_load, select=False,
                       text='Spectral Loadings')
        parent.AddPage(imageId=-1, page=self.plcGaGrpDistPlot, select=False,
                       text='Model Error Comparisons')
    
    def _init_sizers(self):
        self.grsGa = wx.GridSizer(cols=2, hgap=2, rows=2, vgap=2)
        
        self.bxsGa2 = wx.BoxSizer(orient=wx.VERTICAL)
        
        self.bxsGa1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        
        self._init_coll_bxs_ga1_items(self.bxsGa1)
        self._init_coll_bxs_ga2_items(self.bxsGa2)
        self._init_coll_grs_ga_items(self.grsGa)
        
        self.SetSizer(self.bxsGa1)
        self.p1.SetSizer(self.grsGa)
    
    def reset(self):
        # disable ctrls
        self.titleBar.spnGaScoreFrom.Enable(False)
        self.titleBar.spnGaScoreTo.Enable(False)
        self.titleBar.cbxFeature1.Enable(False)
        self.titleBar.cbxFeature2.Enable(False)
        
        # delete multiple scores plots
        self.plc_ga_model_plot1.parent.SetSelection(0)
        self.plc_ga_model_plot1.parent.SetPageText(0, '')
        # self.plcGaModelPlot1.prnt.SetTabSize((0, 1))
        for page in range(self.plc_ga_model_plot1.parent.GetPageCount() - 1, 0, -1):
            self.plc_ga_model_plot1.parent.DeletePage(page)
        
        # clear plots
        objects = {'plc_ga_model_plot1': ['Predictions', 't[1]', 't[2]'],
                   'plcGaFeatPlot': ['Measured Variable Biplot', 'Variable',
                                     'Variable'],
                   'plc_ga_freq_plot': ['Frequency of Variable Selection',
                                        'Independent Variable', 'Frequency'],
                   'plcGaOptPlot': ['Rate of GA Optimisation', 'Generation',
                                    'Fitness Score']}

        # noinspection PyUnusedLocal, PyTypeChecker
        curve = PolyLine([[0, 0], [1, 1]], colour='white', width=1,
                         style=wx.PENSTYLE_TRANSPARENT)
        
        for each in objects.keys():
            exec('self.' + each + '.draw(PlotGraphics([curve], ' +
                 'objects["' + each + '"][0], ' +
                 'objects["' + each + '"][1], ' +
                 'objects["' + each + '"][2]))')
    
    def on_splitter_dclick(self, _):
        if self.splitter.GetSashPosition() <= 5:
            self.splitter.SetSashPosition(250)
        else:
            self.splitter.SetSashPosition(1)

            
class TitleBar(bp.ButtonPanel):
    """"""
    def __init__(self, parent, id_, text, style, alignment, gatype):
        """"""
        bp.ButtonPanel.__init__(self, parent=parent, id=-1,
                                text="GA-" + gatype,
                                agwStyle=bp.BP_USE_GRADIENT,
                                alignment=bp.BP_ALIGN_LEFT)

        _, _, _, _ = id_, text, style, alignment

        self.parent = parent
        self.dtype = gatype
        self.data = None
        self.grid = None
        self.pcSplit = None

        self._init_btnpanel_ctrls()
        self.create_btns()

        self.spnGaScoreFrom.Show(False)
        self.spnGaScoreTo.Show(False)

    def _init_btnpanel_ctrls(self):
        """"""
        choices = ['Raw spectra', 'Processed spectra']
        self.cbxData = wx.Choice(choices=choices, id=-1, name='cbxData',
                                 parent=self, pos=(118, 23),
                                 size=(100, 23), style=0)
        self.cbxData.SetSelection(0)
        
        bmp = wx.Bitmap(os.path.join('bmp', 'run.png'), wx.BITMAP_TYPE_PNG)
        self.btnRunGa = bp.ButtonInfo(self, -1, bmp, kind=wx.ITEM_NORMAL,
                                      shortHelp='Run Genetic Algorithm',
                                      longHelp='Run Genetic Algorithm')
        self.btnRunGa.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.on_btn_run_ga, id=self.btnRunGa.GetId())
        
        bmp = wx.Bitmap(os.path.join('bmp', 'export.png'), wx.BITMAP_TYPE_PNG)
        self.btnExportGa = bp.ButtonInfo(self, -1, bmp, kind=wx.ITEM_NORMAL,
                                         shortHelp='Export GA Results',
                                         longHelp='Export Genetic Algorithm Results')
        self.btnExportGa.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.on_btn_export_ga, id=self.btnExportGa.GetId())
        
        self.cbxFeature1 = wx.Choice(choices=[''], id=-1, name='cbxFeature1',
                                     parent=self, pos=(118, 23),
                                     size=(60, 23), style=0)
        self.cbxFeature1.SetSelection(0)
        self.cbxFeature1.Bind(wx.EVT_CHOICE, self.on_cbx_feat1, id=-1)
        
        self.cbxFeature2 = wx.Choice(choices=[''], id=-1, name='cbxFeature2',
                                     parent=self, pos=(118, 23),
                                     size=(60, 23), style=0)
        self.cbxFeature2.SetSelection(0)
        self.cbxFeature2.Bind(wx.EVT_CHOICE, self.on_cbx_feat2, id=-1)
        
        self.spnGaScoreFrom = wx.SpinCtrl(id=-1, initial=1, max=100, min=1,
                                          name='spnGaScoreFrom', parent=self,
                                          pos=(184, 2), size=(40, 23),
                                          style=wx.SP_ARROW_KEYS)
        self.spnGaScoreFrom.SetToolTip('')
        self.spnGaScoreFrom.Bind(wx.EVT_SPINCTRL, self.on_spn_ga_scores_from,
                                 id=-1)

        self.spnGaScoreTo = wx.SpinCtrl(id=-1, initial=1, max=100, min=1,
                                        name='spnGaScoreTo', parent=self,
                                        pos=(256, 2), size=(40, 23),
                                        style=wx.SP_ARROW_KEYS)
        self.spnGaScoreTo.SetToolTip('')
        self.spnGaScoreTo.Bind(wx.EVT_SPINCTRL, self.on_spn_ga_scores_to,
                               id=-1)

        bmp = wx.Bitmap(os.path.join('bmp', 'params.png'), wx.BITMAP_TYPE_PNG)
        self.btnSetParams = bp.ButtonInfo(self, -1, bmp, kind=wx.ITEM_NORMAL,
                                          shortHelp='Set GA Parameters',
                                          longHelp='Set Genetic Algorithm Parameters')
        self.Bind(wx.EVT_BUTTON, self.on_btn_set_params, id=self.btnSetParams.GetId())
    
    def get_data(self, data):
        self.data = data
        
    def get_exp_grid(self, grid):
        self.grid = grid
    
    def get_val_split_pc(self, pc):
        self.pcSplit = pc
    
    def create_btns(self):
        self.Freeze()
        
        self.set_properties()
                    
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
    
    def on_btn_set_params(self, _):
        if self.parent.splitter.GetSashPosition() <= 5:
            self.parent.splitter.SetSashPosition(250)
        else:
            self.parent.splitter.SetSashPosition(1)
        
    def on_btn_run_ga(self, _):
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
    
    def on_btn_export_ga(self, _):
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
        plot_scores(self.parent.plc_ga_model_plot1, self.data['gadfadfscores'],
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
            "self.parent.optDlg.plot_ga_loads(self.parent.optDlg.currentChrom, self.data['ga" +
            self.dtype.lower() + self.dtype.lower() +
            "loads'], self.parent.plcGaSpecLoad, self.spnGaScoreFrom.GetValue()-1)")

    def on_cbx_feat1(self, _):
        self.parent.optDlg.plot_ga_vars(self.parent.plcGaFeatPlot)
    
    def on_cbx_feat2(self, _):
        self.parent.optDlg.plot_ga_vars(self.parent.plcGaFeatPlot)
        
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
        # except Exception, error:
        #    wx.EndBusyCursor()
        #    error_box(self, '%s' %str(error))
        #    raise
        finally:
            dlg.Destroy()

        set_text = self.parent.parent.sbMain.SetStatusText
        chromRecord = None
        scoresOut = None
        scoresSel = None
        xdata = None

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
                    mask = np.concatenate(
                        (mask, np.array(val_split(self.grid, self.data,
                                                  self.pcSplit))[:, nax]), 1)
                
            # Run DFA - set containers
            score_lst = []
            chrom_lst = []
            cUrves = []
            Lvs = None
            
            var_from = _attr['varfrom']
            var_to = _attr['varto']
            if var_to-var_from == 0:
                var_range = 1
            else:
                var_range = var_to-var_from + 1
                
            for var in range(var_range):
                # set num latent variables
                for run in range(_attr['runs']):
                    # run ga-dfa
                    # create initial population
                    chrom = genic.crtpop(_attr['inds'],
                                         var+var_from, xdata.shape[1])
                    
                    # evaluate initial population
                    scores = None
                    if self.dtype == 'DFA':
                        # check factors
                        if int(_attr['maxf']) >= int(max(self.data['class'][:, 0])):
                            Lvs = int(max(self.data['class'][:, 0])) - 1
                        else:
                            Lvs = int(_attr['maxf'])
                        # run dfa
                        scores = mva.fitfun.call_dfa(chrom, xdata, Lvs, mask,
                                                     self.data)
                        print('DFA SCORES:', scores)
                        
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
                        chromRecord = np.zeros((1, var+var_from))
                    
                    while count < stop:
                        print('count: ', count)
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
                                                            Lvs, mask,
                                                            self.data)
                            
                        elif self.dtype == 'PLS':
                            scoresSel = mva.fitfun.call_pls(chromSel, xdata,
                                                            Lvs, mask,
                                                            self.data)
                        # add additional methods here
                        
                        # reinsert chromSel replacing worst parents in chrom
                        chrom, scores = \
                            genic.reinsert(chrom, chromSel, scores, scoresSel)
                        
                        if count == 0:
                            scoresOut = [min(min(scores))]
                        else:
                            scoresOut.append(min(min(scores)))
                        
                        # Build history for second stopping criterion
                        if self.parent.optDlg.cbGaRepUntil.GetValue():
                            Best = scores[0]
                            print('Best: ', Best)
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

                        set_text('Variable %i' % (var+var_from,), 0)
                        set_text('Run %i' % (run + 1,), 1)
                        set_text('Generation %i' % count, 2)
                        
                    # Save GA optimisation curve
                    scoresOut = np.asarray(scoresOut)
                    print('scoresOut: ', scoresOut)
                    # concatenate run result
                    if var_range == 1:
                        if var+run == 0:
                            # scores
                            if self.dtype == 'PLS':
                                score_lst = [float(scores[0])]
                                cUrves = np.reshape(scoresOut,
                                                    (1, len(scoresOut)))
                            else:
                                score_lst = [1 / float(scores[0])]
                                cUrves = np.reshape(1 / scoresOut,
                                                    (1, len(scoresOut)))
                            # chromosomes
                            chrom_lst = np.take(self.data['variableidx'],
                                                chrom[0, :].tolist())[nax, :]
                            chrom_lst.sort()
                            # opt curves
                            
                        else:
                            # scores
                            if self.dtype in ['PLS']:
                                score_lst.append(float(scores[0]))
                            else:
                                score_lst.append(1 / float(scores[0]))
                                scoresOut = 1 / scoresOut
                            # chromosomes
                            ins = np.take(self.data['variableidx'],
                                          chrom[0, :].tolist())[nax, :]
                            ins.sort()
                            chrom_lst = np.concatenate((chrom_lst, ins), 0)
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
                    elif var_range > 1:
                        if var+run == 0:
                            # scores
                            if self.dtype in ['PLS']:
                                score_lst = [float(scores[0])]
                                cUrves = np.reshape(scoresOut, (1, len(scoresOut)))
                            else:
                                score_lst = [1/float(scores[0])]
                                cUrves = np.reshape(1.0/scoresOut, (1, len(scoresOut)))
                            #           scoreList = [1.0/float(scores[0])]
                            # chromosomes
                            ins = np.take(self.data['variableidx'],
                                          chrom[0, :].tolist())[nax, :]
                            ins.sort()
                            chrom_lst = np.concatenate(
                                (ins, np.zeros((1, var_range-var-1), 'd')), 1)
                            # opt curves
                            # cUrves = np.reshape(scoresOut, (1, len(scoresOut)))
                        else:
                            # scores
                            if self.dtype in ['PLS']:
                                score_lst.append(float(scores[0]))
                            else:
                                score_lst.append(1/float(scores[0]))
                                scoresOut = 1.0/scoresOut
                            #   scoreList.append(1.0/float(scores[0]))
                            # chromosomes
                            ins = np.take(self.data['variableidx'],
                                          chrom[0, :].tolist())[nax, :]
                            ins.sort()
                            chrom_lst = np.concatenate(
                                (chrom_lst,
                                 np.concatenate(
                                     (ins, np.zeros((1, var_range-var-1), 'd')),
                                     1)), 0)
                            
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
                            
                            cUrves = np.concatenate(
                                (cUrves, np.reshape(scoresOut, (1, lscout))), 0)
                            
            print("gadfachroms :", self.data['gadfachroms'])
            # add results to dictionary
            type_low = self.dtype.lower()
            print("self.data['ga%schroms'] = chrom_lst" % type_low)

            cmd1 = "self.data['ga%schroms'] = chrom_lst" % type_low
            cmd2 = "self.data['ga%sscores'] = score_lst" % type_low
            cmd3 = "self.data['ga%scurves'] = cUrves" % type_low

            for cmd in [cmd1, cmd2, cmd3]:
                exec(cmd, locals(), globals())

            print("gadfachroms_exec :", self.data['gadfachroms'])

            # Create results tree
            self.create_ga_results_tree(self.parent.optDlg.treGaResults,
                                        gacurves=cUrves, chroms=chrom_lst,
                                        varfrom=_attr['varfrom'],
                                        varto=_attr['varto'],
                                        runs=_attr['runs']-1)
            
            # enable export btn
            self.btnExportGa.Enable(1)
            
            # reset cursor
            wx.EndBusyCursor()

        # clear status bar
        set_text('Status', 0)
        set_text('', 1)
        set_text('', 2)
    
    def create_ga_results_tree(self, tree, **_attr):
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
        # noinspection PyUnusedLocal
        dfa_root = tree.GetRootItem()

        print('attrs\n', _attr)
        
        # generate top score list
        _attr['gacurves'] = np.concatenate(
            (_attr['gacurves'], np.zeros((len(_attr['gacurves']), 1))), 1)
        gaScoreList = []
        for x in range(len(_attr['gacurves'])):
            t = _attr['gacurves'][x, ].tolist().index(0)
            gaScoreList.append(_attr['gacurves'][x, t-1])
        
        idx = []
        for varbls in range(_attr['varto'] - _attr['varfrom'] + 1):
            idx.extend((np.argsort(np.array(gaScoreList[varbls * (_attr['runs'] + 1):
                        (varbls * (_attr['runs'] + 1)) + _attr['runs'] + 1])) +
                        (varbls * (_attr['runs'] + 1))).tolist())
        exec("self.data['ga" + self.dtype.lower() + "treeorder'] = idx")
        
        tree.DeleteAllItems()
        tree.AddRoot('Root') 
        dfa_root = tree.GetRootItem()
        
        #  if self.cbDfaSavePc.GetValue() is False:
        #       # saved only best result
        #       noSaveChroms = 1
        #  elif self.cbDfaSavePc.GetValue() is True:
        #       # saved % of results
        #       noSaveChroms = int((self.stDfaSavePc.GetValue()/100)*int(self.stDfaNoInds.GetValue()))
            
        tree_item_id_list = []
        count, iter_count = 0, 0
        nruns = _attr['runs'] + 1
        for varbls in range(_attr['varto'] - _attr['varfrom'] + 1):
            text = ' variables'.join(str(varbls + _attr['varfrom']))
            new_var = tree.AppendItem(dfa_root, text)
            tree_item_id_list.append(new_var)
            for runs in range(nruns):

                # for mch in range(noSaveChroms):
                #      RunLabel = np.sort(_attr['chroms'][Count+mch, 0:vars+_attr['varfrom']]).tolist()
                #      NewChrom = tree.AppendItem(NewVar, string.join(('#', str(IterCount+1), ' ',
                #      str(np.take(np.reshape(self.data['indlabelsfull'],
                #      (len(self.data['indlabelsfull']), )), RunLabel)), ' ',
                #       '%.2f' %(gaScoreList[Count+mch])), ''))
                #      TreeItemIdList.append(NewChrom)
                #      IterCount += 1
                #      Count += (mch+1)

                run_label = np.sort(_attr['chroms'][idx[(varbls * nruns) + runs],
                                    0:varbls + _attr['varfrom']]).tolist()

                indlabelsfull = self.data['indlabelsfull']
                indlabels = str(np.take(np.reshape(indlabelsfull,
                                        (len(indlabelsfull),)), run_label))
                ga_score = '%.2f' % (gaScoreList[idx[(varbls * nruns) + runs]])

                text = '#%i %s %s' % (iter_count+1, indlabels, ga_score)
                new_chrom = tree.AppendItem(new_var, text)

                tree_item_id_list.append(new_chrom)
                iter_count += 1
                # Count += (mch+1)
                
        tree.Expand(dfa_root)
        for i in range(len(tree_item_id_list)):
            tree.Expand(tree_item_id_list[i])

class SelParam(fpb.FoldPanelBar):
    """"""
    def __init__(self, parent):
        fpb.FoldPanelBar.__init__(self, parent, -1, pos=wx.DefaultPosition,
                                  size=wx.DefaultSize,
                                  agwStyle=fpb.FPB_SINGLE_FOLD)
        self.tbar = None
        self.current_chrom = None

        self.parent = parent

        self._init_selparam_ctrls()
        self._init_selparam_sizers()

        self.Expand(self.fpParams)
        self.Expand(self.fpResults)

    def _init_selparam_ctrls(self):
        """"""
        self.SetAutoLayout(True)

        icons = wx.ImageList(16, 16)
        bmp = wx.Bitmap(os.path.join('bmp', 'arrown.png'), wx.BITMAP_TYPE_PNG)
        icons.Add(bmp)
        bmp = wx.Bitmap(os.path.join('bmp', 'arrows.png'), wx.BITMAP_TYPE_PNG)
        icons.Add(bmp)

        self.fpParams = self.AddFoldPanel("Parameters", collapsed=True,
                                          foldIcons=icons)
        self.fpParams.SetAutoLayout(True)

        self.fpResults = self.AddFoldPanel("Results", collapsed=True,
                                           foldIcons=icons)
        self.fpResults.SetAutoLayout(True)
        self.fpResults.Bind(wx.EVT_SIZE, self.on_fpb_resize)

        self.plParams = wx.Panel(id=-1, name='plParams', parent=self.fpParams,
                                 pos=(0, 0), size=(200, 350),
                                 style=wx.TAB_TRAVERSAL)
        self.plParams.SetToolTip('')
        self.plParams.SetConstraints(
            LayoutAnchors(self.plParams, True, True, True, True))

        self.spnGaVarsFrom = wx.SpinCtrl(id=-1, initial=2, max=100, min=2,
                                         name='spnGaVarsFrom',
                                         parent=self.plParams,
                                         pos=(73, 0),
                                         size=(15, 21),
                                         style=wx.SP_ARROW_KEYS)
        self.spnGaVarsFrom.SetToolTip('Variable range from')

        self.spnGaVarsTo = wx.SpinCtrl(id=-1, initial=2, max=100, min=2,
                                       name='spnGaVarsTo', parent=self.plParams,
                                       pos=(219, 0),
                                       size=(15, 21),
                                       style=wx.SP_ARROW_KEYS)
        self.spnGaVarsTo.SetToolTip('Variable range to')

        self.spnGaNoInds = wx.SpinCtrl(id=-1, initial=10, max=1000, min=10,
                                       name='spnGaNoInds', parent=self.plParams,
                                       pos=(73, 23),
                                       size=(15, 21),
                                       style=wx.SP_ARROW_KEYS)
        self.spnGaVarsTo.SetToolTip('Number of individuals')

        self.spnGaNoRuns = wx.SpinCtrl(id=-1, initial=1, max=1000, min=1,
                                       name='spnGaNoRuns', parent=self.plParams,
                                       pos=(219, 23),
                                       size=(15, 21),
                                       style=wx.SP_ARROW_KEYS)
        self.spnGaVarsTo.SetToolTip('Number of independent GA runs')

        self.stGaXoverRate = wx.TextCtrl(id=-1, name='stGaXoverRate',
                                         value='0.8', parent=self.plParams,
                                         pos=(216, 48),
                                         size=(15, 21), style=0)
        self.stGaXoverRate.SetToolTip('Crossover rate')

        self.cbGaXover = wx.CheckBox(id=-1, label='', name='cbGaXover',
                                     parent=self.plParams, pos=(0, 46),
                                     size=(10, 21),
                                     style=wx.ALIGN_LEFT)
        self.cbGaXover.SetValue(True)
        self.cbGaXover.SetToolTip('')

        self.stGaMutRate = wx.TextCtrl(id=-1, name='stGaMutRate', value='0.4',
                                       parent=self.plParams,
                                       pos=(216, 48),
                                       size=(15, 21), style=0)
        self.stGaMutRate.SetToolTip('Mutation rate')

        self.cbGaMut = wx.CheckBox(id=-1, label='', name='cbGaMut',
                                   parent=self.plParams, pos=(146, 46),
                                   size=(10, 21), style=wx.ALIGN_LEFT)
        self.cbGaMut.SetValue(True)
        self.cbGaMut.SetToolTip('')

        self.stGaInsRate = wx.TextCtrl(id=-1, name='stGaInsRate', value='0.8',
                                       parent=self.plParams,
                                       pos=(216, 48),
                                       size=(15, 21), style=0)
        self.stGaXoverRate.SetToolTip('Insertion rate')

        self.spnGaMaxFac = wx.SpinCtrl(id=-1, initial=1, max=100, min=1,
                                       name='spnGaMaxFac', parent=self.plParams,
                                       pos=(219, 69),
                                       size=(15, 21),
                                       style=wx.SP_ARROW_KEYS)
        self.spnGaMaxFac.SetToolTip('Maximum number of latent variables')

        self.spnGaMaxGen = wx.SpinCtrl(id=-1, initial=5, max=1000, min=5,
                                       name='spnGaMaxGen', parent=self.plParams,
                                       pos=(73, 92),
                                       size=(15, 21),
                                       style=wx.SP_ARROW_KEYS)
        self.spnGaMaxGen.SetToolTip('Maximum number of generations')

        self.cbGaMaxGen = wx.CheckBox(id=-1, label='', name='cbGaMaxGen',
                                      parent=self.plParams, pos=(0, 92),
                                      size=(10, 21), style=wx.ALIGN_LEFT)
        self.cbGaMaxGen.SetValue(True)
        self.cbGaMaxGen.SetToolTip('')
        self.cbGaMaxGen.Show(False)

        self.spnGaRepUntil = wx.SpinCtrl(id=-1, initial=5, max=1000, min=5,
                                         name='spnGaRepUntil',
                                         parent=self.plParams,
                                         pos=(219, 92),
                                         size=(15, 21),
                                         style=wx.SP_ARROW_KEYS)
        self.spnGaRepUntil.SetToolTip('Repeat generations until')

        self.cbGaRepUntil = wx.CheckBox(id=-1, label='', name='cbGaRepUntil',
                                        parent=self.plParams,
                                        pos=(146, 92),
                                        size=(10, 21),
                                        style=wx.ALIGN_LEFT)
        self.cbGaRepUntil.SetValue(False)
        self.cbGaRepUntil.SetToolTip('')

        self.spnResample = wx.SpinCtrl(id=-1, initial=1, max=100, min=1,
                                       name='spnResample', parent=self.plParams,
                                       pos=(73, 92),
                                       size=(15, 21),
                                       style=wx.SP_ARROW_KEYS)
        self.spnResample.SetToolTip('Number of n-fold validation steps')

        self.treGaResults = wx.TreeCtrl(id=-1, name='treGaResults',
                                        parent=self.fpResults,
                                        pos=(0, 23), size=(100, 100),
                                        style=wx.TR_DEFAULT_STYLE |
                                        wx.TR_HAS_BUTTONS,
                                        validator=wx.DefaultValidator)
        self.treGaResults.SetToolTip('')
        self.treGaResults.Bind(wx.EVT_TREE_ITEM_ACTIVATED,
                               self.on_ga_results_tree_item_activated)
        self.treGaResults.SetConstraints(LayoutAnchors(
            self.treGaResults, True, True, True, True))

        self.AddFoldPanelWindow(self.fpParams, self.plParams,
                                fpb.FPB_ALIGN_WIDTH)
        self.AddFoldPanelWindow(self.fpResults, self.treGaResults,
                                fpb.FPB_ALIGN_WIDTH)

    def _init_selparam_sizers(self):
        # generated method, don't edit
        self.gbsGaParams = wx.GridBagSizer(5, 5)
        self.gbsGaParams.SetCols(3)
        self.gbsGaParams.SetRows(12)

        self._init_coll_gbs_ga_params(self.gbsGaParams)
        self.fpParams.SetSizer(self.gbsGaParams)

    def _init_coll_gbs_ga_params(self, parent):
        """"""
        parent.Add(wx.StaticText(self.plParams, -1, 'No. vars. from',
                                 style=wx.ALIGN_RIGHT),
                   (0, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.spnGaVarsFrom, (0, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        # parent.AddSpacer((8, 8), (0, 2), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(wx.StaticText(self.plParams, -1, 'No. vars. to',
                                 style=wx.ALIGN_RIGHT),
                   (1, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.spnGaVarsTo, (1, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        # parent.AddSpacer((8, 8), (1, 2), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(wx.StaticText(self.plParams, -1, 'No. inds.',
                                 style=wx.ALIGN_RIGHT),
                   (2, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.spnGaNoInds, (2, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))

        wxtxt = wx.StaticText(self.plParams, -1, 'No. runs',
                              style=wx.ALIGN_RIGHT)
        parent.Add(wxtxt, (3, 0), border=10, flag=wx.EXPAND, span=(1, 1))

        parent.Add(self.spnGaNoRuns, (3, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))

        wxtxt = wx.StaticText(self.plParams, -1, 'Crossover rate',
                              style=wx.ALIGN_RIGHT)
        parent.Add(wxtxt, (4, 0), border=10, flag=wx.EXPAND, span=(1, 1))

        parent.Add(self.stGaXoverRate, (4, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        parent.Add(self.cbGaXover, (4, 2), border=10, flag=wx.EXPAND,
                   span=(1, 1))

        wxtxt = wx.StaticText(self.plParams, -1, 'Mutation rate',
                              style=wx.ALIGN_RIGHT)
        parent.Add(wxtxt, (5, 0), border=10, flag=wx.EXPAND, span=(1, 1))

        parent.Add(self.stGaMutRate, (5, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        parent.Add(self.cbGaMut, (5, 2), border=10, flag=wx.EXPAND,
                   span=(1, 1))

        wxtxt = wx.StaticText(self.plParams, -1, 'Insertion rate',
                              style=wx.ALIGN_RIGHT)
        parent.Add(wxtxt, (6, 0), border=10, flag=wx.EXPAND, span=(1, 1))

        parent.Add(self.stGaInsRate, (6, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))

        wxtxt = wx.StaticText(self.plParams, -1, 'Max. factors',
                              style=wx.ALIGN_RIGHT)
        parent.Add(wxtxt, (7, 0), border=10, flag=wx.EXPAND, span=(1, 1))

        parent.Add(self.spnGaMaxFac, (7, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))

        wxtxt = wx.StaticText(self.plParams, -1, 'Max. gens',
                              style=wx.ALIGN_RIGHT)
        parent.Add(wxtxt, (8, 0), border=10, flag=wx.EXPAND, span=(1, 1))

        parent.Add(self.spnGaMaxGen, (8, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        parent.Add(self.cbGaMaxGen, (8, 2), border=10, flag=wx.EXPAND,
                   span=(1, 1))

        wxtxt = wx.StaticText(self.plParams, -1, 'Repeat until',
                              style=wx.ALIGN_RIGHT)
        parent.Add(wxtxt, (9, 0), border=10, flag=wx.EXPAND, span=(1, 1))

        parent.Add(self.spnGaRepUntil, (9, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        parent.Add(self.cbGaRepUntil, (9, 2), border=10, flag=wx.EXPAND,
                   span=(1, 1))

        wxtxt = wx.StaticText(self.plParams, -1, 'Resample',
                              style=wx.ALIGN_RIGHT)
        parent.Add(wxtxt, (10, 0), border=10, flag=wx.EXPAND, span=(1, 1))

        parent.Add(self.spnResample, (10, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))

        parent.AddGrowableCol(0)
        parent.AddGrowableCol(1)
        parent.AddGrowableCol(2)
    
    def on_fpb_resize(self, _):
        self.treGaResults.SetSize((self.treGaResults.GetSize()[0],
                                   self.GetSize()[1]-50))

    # noinspection PyMethodMayBeStatic
    def count_for_opt_curve(self, curve):
        """"""
        count = 0
        for item in curve:
            if item != 0:
                count += 1
        return count
    
    def on_ga_results_tree_item_activated(self, event):
        """"""
        self.tbar = self.parent.splitPrnt.titleBar
        ga_error = None
        child_id = None
        xdata = None

        # define dfa or pls
        exec("self.chroms = self.tbar.data['ga" + self.parent.splitPrnt.dtype.lower() + "chroms']")
        exec("self.scores = self.tbar.data['ga" + self.parent.splitPrnt.dtype.lower() + "scores']")
        exec("self.curves = self.tbar.data['ga" + self.parent.splitPrnt.dtype.lower() + "curves']")
        exec("self.treeorder = self.tbar.data['ga" + self.parent.splitPrnt.dtype.lower() + "treeorder']")
        
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
        # chkValid = float(chromId.split(']')[1])
        chromId = chromId.split('[')[0]
        chromId = int(chromId.split('#')[1])-1
        # noinspection PyUnresolvedReferences
        currentChrom = self.chroms[self.treeorder[chromId]].tolist()
        
        # Plot frequency of variable selection for no. vars
        # Get chrom data and error data for each child
        Chroms = []
        VarsId = self.treGaResults.GetItemParent(currentItem)
        NoVars = self.treGaResults.GetItemText(VarsId)
        NoVars = int(NoVars.split(' ')[0])
        
        # adjust chrom length if mutliple var subsets used
        currentChrom = currentChrom[0:NoVars]
        self.current_chrom = currentChrom
        
        # if chkValid > 10.0**-5:
        # Re-Running DFA
        # set no. DFs
        if len(currentChrom) < int(self.spnGaMaxFac.GetValue()):
            Lvs = len(currentChrom)
        else:
            Lvs = int(self.spnGaMaxFac.GetValue())            
        
        # run dfa
        if self.parent.splitPrnt.dtype == 'DFA':
            scores, loads, ga_error = \
                mva.fitfun.rerun_dfa(currentChrom, xdata,
                                     self.tbar.data['validation'],
                                     self.tbar.data['class'][:, 0],
                                     self.tbar.data['label'], Lvs)

            self.tbar.data['gadfadfscores'] = scores
            self.tbar.data['gadfadfaloads'] = loads
            # plot scores

            self.tbar.spnGaScoreFrom.SetRange(1, loads.shape[1])
            self.tbar.spnGaScoreFrom.SetValue(1)
            self.tbar.spnGaScoreTo.SetRange(1, loads.shape[1])
            self.tbar.spnGaScoreTo.SetValue(1)
            if loads.shape[1] > 1:
                self.tbar.spnGaScoreTo.SetValue(2)
            
            plot_scores(self.parent.splitPrnt.plc_ga_model_plot1, scores,
                        cl=self.tbar.data['class'][:, 0],
                        labels=self.tbar.data['label'],
                        validation=self.tbar.data['validation'],
                        col1=self.tbar.spnGaScoreFrom.GetValue()-1,
                        col2=self.tbar.spnGaScoreTo.GetValue()-1,
                        title='DF Scores',
                        xLabel='t[%f]' % self.tbar.spnGaScoreFrom.GetValue(),
                        yLabel='t[%f]' % self.tbar.spnGaScoreTo.GetValue(),
                        xval=True, text=True, pconf=True,
                        symb=False, usecol=[], usesym=[])
            
        if self.parent.splitPrnt.dtype in ['PLS']:
            # select only chrom vars from x
            pls_output = mva.fitfun.rerun_pls(currentChrom, xdata, 
                                              self.tbar.data['class'],
                                              self.tbar.data['validation'],
                                              Lvs)
            
            self.tbar.data['gaplsplsloads'] = pls_output['W']
            self.tbar.data['gaplsscores'] = pls_output['predictions']
            self.tbar.data['gaplsfactors'] = pls_output['facs']
            self.tbar.data['gaplsrmsept'] = pls_output['RMSEPT']

            ga_error = np.concatenate((np.array(pls_output['rmsec'])[nax, :],
                                      np.array(pls_output['rmsepc'])[nax, :]),
                                      0)
        
            # set defaults
            self.tbar.spnGaScoreFrom.SetValue(1)
            self.tbar.spnGaScoreTo.SetValue(1)
            
            # plot pls predictions
            self.parent.splitPrnt.plc_ga_model_plot1 = \
                plot_pls_model(self.parent.splitPrnt.plc_ga_model_plot1,
                               model='ga', tbar=self.parent.splitPrnt.prnt.prnt.tbMain,
                               cL=self.tbar.data['class'],
                               scores=pls_output['plsscores'],
                               predictions=pls_output['predictions'],
                               validation=self.tbar.data['validation'],
                               RMSEPT=pls_output['RMSEPT'],
                               factors=pls_output['facs'],
                               dtype=0, col1=0, col2=1, label=self.tbar.data['label'],
                               symbols=self.parent.splitPrnt.prnt.tbMain.tbSymbols.GetValue(),
                               usetxt=self.parent.splitPrnt.prnt.tbMain.tbPoints.GetValue(),
                               errplot=False, usecol=[], usesym=[])
                        
        # if self.cbDfaSavePc.GetValue() is False:
        NoRuns = int(self.spnGaNoRuns.GetValue())
        # else:
        #    tp = int((float(self.stDfaSavePc.GetValue())/100)*int(self.stDfaNoInds.GetValue()))
        #    NoRuns = int(self.stDfaNoRuns.GetValue())*tp
        
        for run in range(NoRuns):
            if run == 0:
                child_id = self.treGaResults.GetFirstChild(VarsId)[0]
            else:
                child_id = self.treGaResults.GetNextSibling(child_id)
            
            # get chrom ids
            itemId = self.treGaResults.GetItemText(child_id)
            itemId = itemId.split('[')[0]
            itemId = int(itemId.split('#')[1])-1
            items = self.chroms[itemId][0:NoVars]
            for each in items:
                Chroms.append(each)
        
        # calculate variable frequencies
        var_freq = np.zeros((1, 2), 'i')
        while len(Chroms) > 1:
            var_freq = np.concatenate((var_freq,
                                      np.reshape([float(Chroms[0]), 1.0], (1, 2))),
                                      0)
            NewChroms = []
            for i in range(1, len(Chroms), 1):
                if Chroms[i] == var_freq[var_freq.shape[0]-1, 0]:
                    var_freq[var_freq.shape[0]-1, 1] += 1.0
                else:
                    NewChroms.append(float(Chroms[i]))
            Chroms = NewChroms
        if len(Chroms) == 1:
            shaped_chroms = np.reshape([float(Chroms[0]), 1.0], (1, 2))
            var_freq = np.concatenate((var_freq, shaped_chroms), 0)
        var_freq = var_freq[1:var_freq.shape[0]]
        
        # Plot var freq as percentage
        var_freq[:, 1] = (var_freq[:, 1]/sum(var_freq[:, 1]))*100
        # plot variable frequencies
        LineObj = []
        for i in range(var_freq.shape[0]):
            Start = np.concatenate(
                (np.reshape(self.tbar.data['xaxisfull'][int(var_freq[i, 0])], (1, 1)),
                 np.reshape(0.0, (1, 1))), 1)
            FullVarFreq = np.concatenate(
                (np.reshape(self.tbar.data['xaxisfull'][int(var_freq[i, 0])], (1, 1)),
                 np.reshape(var_freq[i, 1], (1, 1))), 1)
            FullVarFreq = np.concatenate((Start, FullVarFreq), 0)

            if int(var_freq[i, 0]) in currentChrom:
                # noinspection PyTypeChecker
                LineObj.append(PolyLine(FullVarFreq, colour='red', width=2,
                                        style=wx.PENSTYLE_SOLID))
            else:
                # noinspection PyTypeChecker
                LineObj.append(PolyLine(FullVarFreq, colour='black', width=2,
                                        style=wx.PENSTYLE_SOLID))
        
        meanSpec = np.concatenate(
            (np.reshape(self.tbar.data['xaxisfull'],
                        (len(self.tbar.data['xaxisfull']), 1)),
             np.reshape(mva.process.scale01(np.reshape(np.mean(xdata, 0),
                        (1, xdata.shape[1])))*max(var_freq[:, 1]),
                        (xdata.shape[1], 1))), 1)

        # noinspection PyTypeChecker
        meanSpec = PolyLine(meanSpec, colour='black', width=0.75,
                            style=wx.PENSTYLE_SOLID)
        LineObj.append(meanSpec)
        DfaPlotFreq = PlotGraphics(LineObj, 'Frequency of Variable Selection',
                                   'Variable ID', 'Frequency (%)')
        xAx = (min(self.tbar.data['xaxisfull']),
               max(self.tbar.data['xaxisfull']))
        yAx = (0, max(var_freq[:, 1])*1.1)
        self.parent.splitPrnt.plc_ga_freq_plot.draw(DfaPlotFreq, xAxis=xAx, yAxis=yAx)
        
        # plot variables
        alist = []
        for each in currentChrom:
            alist.append(str(self.tbar.data['indlabelsfull'][int(each)]))
        
        self.tbar.cbxFeature1.SetItems(alist)
        self.tbar.cbxFeature2.SetItems(alist)
        self.tbar.cbxFeature1.SetSelection(0)
        self.tbar.cbxFeature2.SetSelection(0)
        
        self.plot_ga_vars(self.parent.splitPrnt.plcGaFeatPlot)
        
        # plot ga optimisation curve
        noGens = self.count_for_opt_curve(self.curves[chromId])
        # noinspection PyUnusedLocal
        gaPlotOptLine = plot_line(self.parent.splitPrnt.plcGaOptPlot,
                                  np.reshape(self.curves[chromId, 0:noGens], (1, noGens)),
                                  xaxis=np.arange(1, noGens+1)[:, nax], rownum=0,
                                  tit='GA Optimisation Curve',
                                  xLabel='Generation',
                                  yLabel='Objective function score', wdth=3,
                                  dtype='single', ledge=[])
        
        # plot loadings
        self.tbar.data['gacurrentchrom'] = currentChrom
        
        exec("self.plot_ga_loads(currentChrom, self.tbar.data['ga" +
             self.parent.splitPrnt.dtype.lower() +
             self.parent.splitPrnt.dtype.lower() +
             "loads'], self.parent.splitPrnt.plcGaSpecLoad, 0)")
        
        # plot eigenvalues
        if ga_error.shape[0] == 1:
            plot_line(self.parent.splitPrnt.plc_ga_eigs, ga_error,
                      xaxis=np.arange(1, ga_error.shape[1]+1)[:, nax],
                      rownum=0, xLabel='Discriminant Function', tit='',
                      yLabel='Eigenvalues', wdth=3, dtype='single',
                      ledge=[])
        else:
            plot_line(self.parent.splitPrnt.plc_ga_eigs, ga_error,
                      xaxis=np.arange(1, ga_error.shape[1]+1)[:, nax],
                      xLabel='Latent Variable', tit='',
                      yLabel='RMS Error', dtype='multi',
                      ledge=['Train err', 'Test err'], wdth=3)
            
            self.parent.splitPrnt.nbGaModPlot.SetPageText(1, 'RMS Error')
        
        # plot variables vs. error for pairs
        ga_var_from = int(self.spnGaVarsFrom.GetValue())
        ga_var_to = int(self.spnGaVarsTo.GetValue())
        if ga_var_to - ga_var_from == 0:
            ga_var_range = 1
        else:
            ga_var_range = ga_var_to - ga_var_from + 1
        
        VarErrObj = []
        MaxVarErr = 0
        MinVarErr = 0
        for xvars in range(ga_var_range):
            VarErr = np.zeros((1, 2), 'd')
            if xvars == 0:
                gaRoot = self.treGaResults.GetRootItem() 
                VarsId = self.treGaResults.GetFirstChild(gaRoot)[0]
            else:
                VarsId = self.treGaResults.GetNextSibling(VarsId)
                
            Var = self.treGaResults.GetItemText(VarsId)
            Var = Var.split(' ')[0]

            run_id = None
            for run in range(int(self.spnGaNoRuns.GetValue())):
                if run == 0:
                    run_id = self.treGaResults.GetFirstChild(VarsId)[0]
                else:
                    run_id = self.treGaResults.GetNextSibling(run_id)
                run_txt = self.treGaResults.GetItemText(run_id)
                run_lst = run_txt.split(' ')
                run_txt = run_lst[-1]
                VarErr = np.concatenate(
                    (VarErr, np.reshape([float(Var), float(run_txt)], (1, 2))), 0)
        
            VarErr = VarErr[1:VarErr.shape[0], :]
            
            if max(VarErr[:, 1]) > MaxVarErr:
                MaxVarErr = max(VarErr[:, 1])
            if min(VarErr[:, 1]) < MinVarErr:
                MinVarErr = min(VarErr[:, 1])
            
            # select marker shape and colour for pair
            color = colourList[int(round(sp.rand(1, )[0]*(len(colourList)-1)))]
            marker = markerList[int(round(sp.rand(1, )[0]*(len(markerList)-1)))]
            # noinspection PyTypeChecker
            VarErrObj.append(
                PolyMarker(VarErr, legend='%s vars' % Var, colour=color,
                           fillstyle=wx.BRUSHSTYLE_SOLID, marker=marker,
                           size=1.5))

            gaPlotVarErr = PlotGraphics(VarErrObj, 'Fitness Summary  ',
                                        'Total no. variables selected',
                                        'Fitness')
            Xax = (ga_var_from-0.25, ga_var_to+0.25)
            Yax = (MinVarErr, MaxVarErr)
            self.parent.splitPrnt.plcGaGrpDistPlot.draw(gaPlotVarErr, xAxis=Xax, yAxis=Yax)
            
            # Enable ctrls
            self.tbar.spnGaScoreFrom.Enable(1)
            self.tbar.spnGaScoreTo.Enable(1)
            self.tbar.cbxFeature1.Enable(1)
            self.tbar.cbxFeature2.Enable(1)
        
    def plot_ga_vars(self, canvas):
        self.tbar = self.parent.splitPrnt.titleBar
        chrom = self.current_chrom
        
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
            plot_scores(canvas, coords, cl=self.tbar.data['class'][:, 0],
                        labels=self.tbar.data['label'],
                        validation=self.tbar.data['validation'],
                        col1=0, col2=0, title=canvas.last_draw[0].title, xLabel=L1,
                        yLabel=L2, xval=True,
                        pconf=False,  # , self.parent.splitPrnt.parent.parent.tbMain.tbConf.GetValue(),
                        text=self.parent.splitPrnt.prnt.tbMain.tbPoints.GetValue(),
                        symb=self.parent.splitPrnt.prnt.tbMain.tbSymbols.GetValue(),
                        usecol=[], usesym=[])
                        
        else:
            coords = np.reshape(np.take(xdata, [int(chrom[pos1]), int(chrom[pos2])], 1), (len(xdata), 2))
            L1 = str(self.tbar.data['indlabelsfull'][int(chrom[pos1])])
            L2 = str(self.tbar.data['indlabelsfull'][int(chrom[pos2])])
            plot_scores(canvas, coords, cl=self.tbar.data['class'][:, 0],
                        labels=self.tbar.data['label'],
                        validation=self.tbar.data['validation'],
                        col1=0, col2=1, title=canvas.last_draw[0].title, xLabel=L1,
                        yLabel=L2, xval=True,
                        pconf=False,  # self.parent.splitPrnt.parent.parent.tbMain.tbConf.GetValue(),
                        text=self.parent.splitPrnt.prnt.tbMain.tbPoints.GetValue(),
                        symb=self.parent.splitPrnt.prnt.tbMain.tbSymbols.GetValue(),
                        usecol=[], usesym=[])
        
        self.tbar.data['gavarcoords'] = coords
        
    def plot_ga_loads(self, chrom, loads, canvas, xL='Variable'):
        """"""
        _ = xL
        self.tbar = self.parent.splitPrnt.titleBar

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
            plot_loads(canvas, plotVals, xaxis=labels, title='DF Loadings',
                       xLabel='w[' + str(self.tbar.spnGaScoreFrom.GetValue()) + ']',
                       yLabel='w[' + str(self.tbar.spnGaScoreTo.GetValue()) + ']',
                       dtype=1, col1=0, col2=1, usecol=[], usesym=[])
        else:
            # plot loadings as line
            xAx = np.take(self.tbar.data['xaxis'], chrom)[:, nax]
            plot_line(canvas, np.transpose(plotVals), xaxis=xAx, tit='', rownum=col1,
                      xLabel='Variable', yLabel='w[' + str(self.tbar.spnGaScoreTo.GetValue()) + ']',
                      wdth=1, ledge=[], dtype='single')

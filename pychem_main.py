# -----------------------------------------------------------------------------
# Name:        pychem_main.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2007/05/24
# RCS-ID:      $Id: pychem_main.py,v 1.26 2009/03/11 15:02:25 rmj01 Exp $
# Copyright:   (c) 2007
# Licence:     GNU General Public Licence
# -----------------------------------------------------------------------------

from os.path import join as opjoin
import sys

import numpy as np
from numpy import loadtxt
from numpy import newaxis as nax
from xml.etree import ElementTree as ET

import wx
import wx.richtext
import wx.lib.agw.flatnotebook as fnb
import wx.lib.filebrowsebutton as fbrowsebtn
from wx.lib.buttons import GenBitmapToggleButton as BmpToggleBtn
from wx.lib.anchors import LayoutAnchors
from wx.lib.stattext import GenStaticText
from wx.adv import AboutDialogInfo, SashWindow, SW_3D, AboutBox

import exp_setup
import plot_spectra
import pca
import cluster
import dfa
import plsr
import ga
import univariate

from pca import plot_scores
from pca import plot_loads
from pca import plot_pls_model
from pca import SymColSelectTool
from plot_spectra import GridRowDel
from commons import error_box


def create(parent):
    return PyChemMain(parent)

# PYCHEM_MAIN (PCM)
[wxID_PCM, wxID_PCMNBMAIN, wxID_PCMPLCLUSTER, wxID_PCMPLDFA, wxID_PCMPLEXPSET, 
 wxID_PCMPLGADFA, wxID_PCMPLGADPLS, wxID_PCMPLGAPLSC, wxID_PCMPLPCA,
 wxID_PCMPLPLS, wxID_PCMPLPREPROC, wxID_PCMSBMAIN, wxID_PCMPLUNIVARIATE
 ] = [wx.NewId() for _init_ctrls in range(13)]

[wxID_PCMMNUFILEAPPEXIT, wxID_PCMMNUFILEFILEIMPORT, wxID_PCMMNUFILELOADEXP, 
 wxID_PCMMNUFILELOADWS, wxID_PCMMNUFILESAVEEXP, wxID_PCMMNUFILESAVEWS,
 ] = [wx.NewId() for _init_coll_mnuFile_Items in range(6)]

[wxID_PCMMNUTOOLSEXPSET, wxID_PCMMNUTOOLSMNUCLUSTER, wxID_PCMMNUTOOLSMNUDFA, 
 wxID_PCMMNUTOOLSMNUGADFA, wxID_PCMMNUTOOLSMNUGAPLSC, wxID_PCMMNUTOOLSMNUPCA,
 wxID_PCMMNUTOOLSMNUPLSR, wxID_PCMMNUTOOLSPREPROC,
 ] = [wx.NewId() for _init_coll_mnuTools_Items in range(8)]

[wxID_PCMMNUHELPCONTENTS, wxID_PCMMNUABOUTCONTENTS,
 ] = [wx.NewId() for _init_coll_mnuHelp_Items in range(2)]

# WX_IMPORT_CONFIRM_DIALOG (WXICD)
[wxID_WXICD, wxID_WXICDBTNOK, wxID_WXICDGRDSAMPLEDATA, wxID_WXICDSTATICTEXT1, 
 wxID_WXICDSTATICTEXT2, wxID_WXICDSTATICTEXT4, wxID_WXICDSTCOLS,
 wxID_WXICDSTROWS, wxID_WXICDSWLOADX,
 ] = [wx.NewId() for _init_importconfirm_ctrls in range(9)]

# WX_WORKSPACE_DIALOG (WXWSD)
[wxID_WXWSD, wxID_WXWSDBTNCANCEL, wxID_WXWSDBTNDELETE, wxID_WXWSDBTNEDIT,
 wxID_WXWSDBTNOK, wxID_WXWSDLBSAVEWORKSPACE,
 ] = [wx.NewId() for _init_savews_ctrls in range(6)]

[MNUGRIDCOPY, MNUGRIDPASTE, MNUGRIDDELETECOL, MNUGRIDRENAMECOL,
 MNUGRIDRESETSORT
 ] = [wx.NewId() for _init_grid_menu_Items in range(5)]

[MNUGRIDROWDEL
 ] = [wx.NewId() for _init_grid_row_menu_Items in range(1)]


# noinspection PyUnresolvedReferences
class PlotToolBar(wx.ToolBar):
    """"""
    def __init__(self, parent):
        """"""
        wx.ToolBar.__init__(self, parent, id=-1, pos=(0, 0), size=(0, 0),
                            style=wx.NO_BORDER | wx.TB_HORIZONTAL, name='')

        self.stTitle = GenStaticText(self, -1, 'Title:', pos=(2, 5),
                                     style=wx.TRANSPARENT_WINDOW)
        self.AddControl(self.stTitle)

        self.txtPlot = wx.TextCtrl(id=-1, name='txtPlot', parent=self,
                                   pos=(26, 2), size=(120, 21),
                                   style=wx.TE_PROCESS_ENTER, value='Title')
        self.txtPlot.SetToolTip('Graph Title')
        self.txtPlot.Bind(wx.EVT_TEXT_ENTER, self.on_txt_plot)
        self.AddControl(self.txtPlot)

        self.spn_title = wx.SpinCtrl(id=-1, initial=12, max=76, min=5,
                                     name='spnTitleFont', parent=self,
                                     pos=(148, 2),
                                     size=(50, 21),
                                     style=wx.SP_ARROW_KEYS)
        self.spn_title.SetToolTip('Title Font Size')
        self.spn_title.Bind(wx.EVT_SPIN, self.on_spn_title_font)
        self.AddControl(self.spn_title)

        self.AddSeparator()

        self.stXlabel = GenStaticText(self, -1, 'X-label:',
                                      pos=(202, 5),
                                      style=wx.TRANSPARENT_WINDOW)
        self.AddControl(self.stXlabel)

        self.txtXlabel = wx.TextCtrl(id=-1, name='txtXlabel', parent=self,
                                     pos=(240, 2), size=(70, 21),
                                     style=wx.TE_PROCESS_ENTER, value='X-label')
        self.txtXlabel.SetToolTip('Abscissa (X-axis) Label')
        self.txtXlabel.Bind(wx.EVT_TEXT_ENTER, self.on_txt_xlabel)
        self.AddControl(self.txtXlabel)

        self.stYlabel = GenStaticText(self, -1, 'Y-label:',
                                      pos=(314, 5),
                                      style=wx.TRANSPARENT_WINDOW)
        self.AddControl(self.stYlabel)

        self.txtYlabel = wx.TextCtrl(id=-1, name='txtYlabel', parent=self,
                                     pos=(352, 2), size=(70, 21),
                                     style=wx.TE_PROCESS_ENTER, value='Y-label')
        self.txtYlabel.SetToolTip('Ordinate (Y-axis) Label')
        self.txtYlabel.Bind(wx.EVT_TEXT_ENTER, self.on_txt_ylabel)
        self.AddControl(self.txtYlabel)

        self.spnAxesFont = wx.SpinCtrl(id=-1, initial=12, max=76, min=5,
                                       name='spnTitleFont', parent=self,
                                       pos=(424, 2),
                                       size=(50, 21),
                                       style=wx.SP_ARROW_KEYS)
        self.spnAxesFont.SetToolTip('Axes Font Size')
        self.spnAxesFont.Bind(wx.EVT_SPIN, self.on_spn_axes_font)
        self.AddControl(self.spnAxesFont)

        self.AddSeparator()

        self.stXrange = GenStaticText(self, -1, 'X-range:',
                                      pos=(480, 5),
                                      style=wx.TRANSPARENT_WINDOW)
        self.AddControl(self.stXrange)

        self.txtXmin = wx.TextCtrl(id=-1, name='txtXmin', parent=self,
                                   pos=(522, 2), size=(40, 21),
                                   style=0, value='0.0')
        self.txtXmin.SetToolTip('Minimum X-axis range')
        self.AddControl(self.txtXmin)

        self.spnXmin = wx.SpinButton(id=-1, name='spnXmin', parent=self,
                                     pos=(562, 2), size=(15, 21),
                                     style=wx.SP_VERTICAL)
        self.spnXmin.SetToolTip('Minimum X-axis range')
        self.spnXmin.Bind(wx.EVT_SPIN_DOWN, self.on_spn_xmin_down)
        self.spnXmin.Bind(wx.EVT_SPIN_UP, self.on_spn_xmin_up)
        self.spnXmin.Bind(wx.EVT_SPIN, self.on_spn_xmin)
        self.AddControl(self.spnXmin)

        self.stDummy1 = GenStaticText(self, -1, ' : ', pos=(579, 5),
                                      style=wx.TRANSPARENT_WINDOW)
        self.AddControl(self.stDummy1)

        self.txtXmax = wx.TextCtrl(id=-1, name='txtXmax', parent=self,
                                   pos=(590, 2), size=(40, 21),
                                   style=0, value='0.0')
        self.txtXmax.SetToolTip('Maximum X-axis range')
        self.AddControl(self.txtXmax)

        self.spnXmax = wx.SpinButton(id=-1, name='spnXmax', parent=self,
                                     pos=(630, 2), size=(15, 21),
                                     style=wx.SP_VERTICAL)
        self.spnXmax.SetToolTip('Maximum X-axis range')
        self.spnXmax.Bind(wx.EVT_SPIN_DOWN, self.on_spn_xmax_down)
        self.spnXmax.Bind(wx.EVT_SPIN_UP, self.on_spn_xmax_up)
        self.spnXmax.Bind(wx.EVT_SPIN, self.on_spn_xmax)
        self.AddControl(self.spnXmax)

        self.AddSeparator()

        self.stYrange = GenStaticText(self, -1, 'Y-range:',
                                      pos=(647, 5),
                                      style=wx.TRANSPARENT_WINDOW)
        self.AddControl(self.stYrange)

        self.txtYmin = wx.TextCtrl(id=-1, name='txtYmin', parent=self,
                                   pos=(690, 2), size=(40, 21),
                                   style=0, value='0.0')
        self.txtYmin.SetToolTip('Minimum Y-axis range')
        self.AddControl(self.txtYmin)

        self.spnYmin = wx.SpinButton(id=-1, name='spnYmin',
                                     parent=self, pos=(732, 2),
                                     size=(15, 21),
                                     style=wx.SP_VERTICAL)
        self.spnYmin.SetToolTip('Minimum Y-axis range')
        self.spnYmin.Bind(wx.EVT_SPIN_DOWN, self.on_spn_ymin_down)
        self.spnYmin.Bind(wx.EVT_SPIN_UP, self.on_spn_ymin_up)
        self.spnYmin.Bind(wx.EVT_SPIN, self.on_spn_ymin)
        self.AddControl(self.spnYmin)

        self.stDummy2 = GenStaticText(self, -1, ' : ', pos=(749, 5),
                                      style=wx.TRANSPARENT_WINDOW)
        self.AddControl(self.stDummy2)

        self.txtYmax = wx.TextCtrl(id=-1, name='txtYmax', parent=self,
                                   pos=(760, 2), size=(40, 21),
                                   style=0, value='0.0')
        self.txtYmax.SetToolTip('Maximum Y-axis range')
        self.AddControl(self.txtYmax)

        self.spnYmax = wx.SpinButton(id=-1, name='spnYmax',
                                     parent=self, pos=(800, 2),
                                     size=(15, 21),
                                     style=wx.SP_VERTICAL)
        self.spnYmax.SetToolTip('Maximum Y-axis range')
        self.spnYmax.Bind(wx.EVT_SPIN_DOWN, self.on_spn_ymax_down)
        self.spnYmax.Bind(wx.EVT_SPIN_UP, self.on_spn_ymax_up)
        self.spnYmax.Bind(wx.EVT_SPIN, self.on_spn_ymax)
        self.AddControl(self.spnYmax)

        self.AddSeparator()

        bmp = wx.Bitmap(opjoin('bmp', 'conf_int.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbConf = BmpToggleBtn(bitmap=bmp, id=-1, name='tbConf',
                                   parent=self, pos=(817, 2), size=(21, 21))
        self.tbConf.SetValue(False)
        self.tbConf.SetToolTip('')
        self.tbConf.Enable(False)
        self.AddControl(self.tbConf)
        self.tbConf.Bind(wx.EVT_BUTTON, self.on_tb_conf)

        bmp = wx.Bitmap(opjoin('bmp', 'plot_text.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbPoints = BmpToggleBtn(bitmap=bmp, id=-1, name='tbPoints',
                                     parent=self, pos=(839, 2), size=(21, 21))
        self.tbPoints.SetValue(True)
        self.tbPoints.SetToolTip('Plot using text labels')
        self.tbPoints.Enable(True)
        self.tbPoints.Bind(wx.EVT_BUTTON, self.OnTbPointsButton)
        self.AddControl(self.tbPoints)

        bmp = wx.Bitmap(opjoin('bmp', 'plot_symbol.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbSymbols = BmpToggleBtn(bitmap=bmp, id=-1, name='tbSymbols',
                                      parent=self, pos=(861, 2), size=(21, 21))
        self.tbSymbols.SetValue(False)
        self.tbSymbols.SetToolTip('Plot using colored symbols')
        self.tbSymbols.Enable(True)
        self.tbSymbols.Bind(wx.EVT_BUTTON, self.on_tb_symbols)
        self.tbSymbols.Bind(wx.EVT_RIGHT_DOWN, self.on_tb_symbols_rclick)
        self.AddControl(self.tbSymbols)

        bmp = wx.Bitmap(opjoin('bmp', 'conf_0.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbLoadLabels = wx.BitmapButton(bitmap=bmp, id=-1,
                                            name='tbLoadLabels', parent=self,
                                            pos=(883, 2), size=(20, 21))
        self.tbLoadLabels.SetToolTip('')
        self.tbLoadLabels.Enable(False)
        self.tbLoadLabels.Bind(wx.EVT_BUTTON, self.on_tb_load_labels)
        self.AddControl(self.tbLoadLabels)
        
        bmp = wx.Bitmap(opjoin('bmp', 'conf_1.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbLoadLabStd1 = wx.BitmapButton(bitmap=bmp, id=-1, 
                                             name='tbLoadLabStd1', parent=self,
                                             pos=(905, 2), size=(20, 21))
        self.tbLoadLabStd1.SetToolTip('')
        self.tbLoadLabStd1.Enable(False)
        self.tbLoadLabStd1.Bind(wx.EVT_BUTTON, self.on_tb_load_lab_std1)
        self.AddControl(self.tbLoadLabStd1)

        bmp = wx.Bitmap(opjoin('bmp', 'conf_2.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbLoadLabStd2 = wx.BitmapButton(bitmap=bmp, id=-1, 
                                             name='tbLoadLabStd2', parent=self, 
                                             pos=(927, 2), size=(20, 21))
        self.tbLoadLabStd2.SetToolTip('')
        self.tbLoadLabStd2.Enable(False)
        self.tbLoadLabStd2.Bind(wx.EVT_BUTTON, self.on_tb_load_lab_std2)
        self.AddControl(self.tbLoadLabStd2)

        bmp = wx.Bitmap(opjoin('bmp', 'conf_2_sym.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbLoadSymStd2 = wx.BitmapButton(bitmap=bmp, id=-1,
                                             name='tbLoadSymStd2', parent=self,
                                             pos=(949, 2), size=(20, 21))
        self.tbLoadSymStd2.SetToolTip('')
        self.tbLoadSymStd2.Enable(False)
        self.tbLoadSymStd2.Bind(wx.EVT_BUTTON, self.on_tb_load_sym_std2)
        self.tbLoadSymStd2.Bind(wx.EVT_RIGHT_DOWN,
                                self.on_tb_load_sym_std2_rclick)
        self.AddControl(self.tbLoadSymStd2)

        self.AddSeparator()

        bmp = wx.Bitmap(opjoin('bmp', 'xlog.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbXlog = wx.BitmapButton(bitmap=bmp, id=-1, name='tbXlog',
                                      parent=self, pos=(971, 2), size=(20, 21))
        self.tbXlog.SetToolTip('')
        self.tbXlog.Bind(wx.EVT_BUTTON, self.on_tb_xlog)
        self.AddControl(self.tbXlog)

        bmp = wx.Bitmap(opjoin('bmp', 'ylog.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbYlog = wx.BitmapButton(bitmap=bmp, id=-1, name='tbYlog',
                                      parent=self, pos=(993, 2), size=(20, 21))
        self.tbYlog.SetToolTip('')
        self.tbYlog.Bind(wx.EVT_BUTTON, self.on_tb_ylog)
        self.AddControl(self.tbYlog)

        bmp = wx.Bitmap(opjoin('bmp', 'scinote.bmp'), wx.BITMAP_TYPE_BMP)
        self.tbScinote = wx.BitmapButton(bitmap=bmp, id=-1, name='tbScinote',
                                         parent=self, pos=(1015, 2),
                                         size=(20, 21))
        self.tbScinote.SetToolTip('')
        self.tbScinote.Bind(wx.EVT_BUTTON, self.on_tb_scinote)
        self.AddControl(self.tbScinote)

        self.SymPopUpWin = SymColSelectTool(self)

        self.loadIdx = 0

    def get_load_plot_idx(self):
        return self.loadIdx

    def on_tb_symbols_rclick(self, event):
        # symbol/colour options for scores plots
        self.tbSymbols.SetValue(True)
        self.do_plot()
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        self.SymPopUpWin.SetPosition((pos[0] - 200, pos[1] + sz[1]))

        # show plot options
        self.SymPopUpWin.ShowModal()

    def on_tb_load_labels(self, _):
        """plot loadings"""
        self.do_plot(loadType=0)
        self.loadIdx = 0

    def on_txt_plot(self, _):
        self.graph.setTitle(self.txtPlot.GetValue())
        self.graph.setXLabel(self.txtXlabel.GetValue())
        self.graph.setYLabel(self.txtYlabel.GetValue())
        self.canvas.Redraw()

    def on_txt_xlabel(self, _):
        self.graph.setTitle(self.txtPlot.GetValue())
        self.graph.setXLabel(self.txtXlabel.GetValue())
        self.graph.setYLabel(self.txtYlabel.GetValue())
        self.canvas.Redraw()

    def on_txt_ylabel(self, _):
        self.graph.setTitle(self.txtPlot.GetValue())
        self.graph.setXLabel(self.txtXlabel.GetValue())
        self.graph.setYLabel(self.txtYlabel.GetValue())
        self.canvas.Redraw()

    def on_tb_load_lab_std1(self, _):
        # plot loadings
        self.do_plot(loadType=1)
        self.loadIdx = 1

    def on_tb_load_lab_std2(self, _):
        # plot loadings
        self.do_plot(loadType=2)
        self.loadIdx = 2

    def on_tb_load_sym_std2(self, _):
        # plot loadings
        self.do_plot(loadType=3)
        self.loadIdx = 3

    def on_tb_load_sym_std2_rclick(self, event):
        # invoke loadings plot sym/col selector
        self.do_plot(loadType=3)
        self.loadIdx = 3
        btn = event.GetEventObject()
        pos = btn.ClientToScreen((0, 0))
        sz = btn.GetSize()
        self.SymPopUpWin.SetPosition((pos[0] - 200, pos[1] + sz[1]))

        # show plot options
        self.SymPopUpWin.ShowModal()

    def on_tb_conf(self, _):
        if (self.tbPoints.GetValue() is False) & \
                (self.tbConf.GetValue() is False) & \
                (self.tbSymbols.GetValue() is False) is False:
            # plot scores
            self.do_plot()

    def OnTbPointsButton(self, _):
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

    def on_tb_xlog(self, _):
        if self.canvas.getLogScale()[0]:
            self.canvas.set_log_scale((False, self.canvas.getLogScale()[1]))
        else:
            self.canvas.set_log_scale((True, self.canvas.getLogScale()[1]))
        self.canvas.Redraw()

    def on_tb_ylog(self, _):
        if self.canvas.getLogScale()[1]:
            self.canvas.set_log_scale((self.canvas.getLogScale()[0], False))
        else:
            self.canvas.set_log_scale((self.canvas.getLogScale()[0], True))
        self.canvas.Redraw()

    def on_tb_scinote(self, _):
        if self.canvas.GetUseScientificNotation() is False:
            self.canvas.SetUseScientificNotation(True)
        else:
            self.canvas.SetUseScientificNotation(False)
        self.canvas.Redraw()

    def do_plot(self, loadType=0, symcolours=[], symsymbols=[]):
        """"""
        if self.canvas.GetName() in ['plcDFAscores']:
            if self.canvas.prnt.titleBar.data['dfscores'] is not None:
                plot_scores(self.canvas,
                            self.canvas.prnt.titleBar.data['dfscores'],
                            cl=self.canvas.prnt.titleBar.data['class'][:, 0],
                            labels=self.canvas.prnt.titleBar.data['label'],
                            validation=self.canvas.prnt.titleBar.data['validation'],
                            col1=self.canvas.prnt.titleBar.spnDfaScore1.GetValue() - 1,
                            col2=self.canvas.prnt.titleBar.spnDfaScore2.GetValue() - 1,
                            title=self.graph.title, xLabel=self.graph.xLabel,
                            yLabel=self.graph.yLabel,
                            xval=self.canvas.prnt.titleBar.cbDfaXval.GetValue(),
                            text=self.tbPoints.GetValue(),
                            pconf=self.tbConf.GetValue(),
                            symb=self.tbSymbols.GetValue(), usecol=symcolours,
                            usesym=symsymbols)

        elif self.canvas.GetName() in ['plcPCAscore']:
            if self.canvas.prnt.titleBar.data['pcscores'] is not None:
                plot_scores(self.canvas,
                            self.canvas.prnt.titleBar.data['pcscores'],
                            cl=self.canvas.prnt.titleBar.data['class'][:, 0],
                            labels=self.canvas.prnt.titleBar.data['label'],
                            validation=self.canvas.prnt.titleBar.data['validation'],
                            col1=self.canvas.prnt.titleBar.spnNumPcs1.GetValue() - 1,
                            col2=self.canvas.prnt.titleBar.spnNumPcs2.GetValue() - 1,
                            title=self.graph.title, xLabel=self.graph.xLabel,
                            yLabel=self.graph.yLabel, xval=False,
                            text=self.tbPoints.GetValue(), pconf=False,
                            symb=self.tbSymbols.GetValue(), usecol=symcolours,
                            usesym=symsymbols)

        elif len(self.canvas.GetName().split('plcPredPls')) > 1:
            self.canvas = plot_pls_model(
                self.canvas, model='full',
                tbar=self.canvas.prnt.prnt.prnt.prnt.tbMain,
                cL=self.canvas.prnt.prnt.titleBar.data['class'],
                scores=self.canvas.prnt.prnt.titleBar.data['plst'],
                label=self.canvas.prnt.prnt.titleBar.data['label'],
                predictions=self.canvas.prnt.prnt.titleBar.data['plspred'],
                validation=self.canvas.prnt.prnt.titleBar.data['validation'],
                RMSEPT=self.canvas.prnt.prnt.titleBar.data['RMSEPT'],
                factors=self.canvas.prnt.prnt.titleBar.data['plsfactors'],
                dtype=self.canvas.prnt.prnt.titleBar.data['plstype'],
                col1=self.canvas.prnt.prnt.titleBar.spnPLSfactor1.GetValue() - 1,
                col2=self.canvas.prnt.prnt.titleBar.spnPLSfactor2.GetValue() - 1,
                symbols=self.tbSymbols.GetValue(),
                usetxt=self.tbPoints.GetValue(),
                usecol=symcolours, usesym=symsymbols,
                errplot=self.tbSymbols.GetValue(),
                plScL=self.canvas.prnt.prnt.titleBar.data['pls_class'])

        elif self.canvas.GetName() in ['plcGaFeatPlot']:
            plot_scores(
                self.canvas,
                self.canvas.prnt.prnt.splitPrnt.titleBar.data['gavarcoords'],
                cl=self.canvas.prnt.prnt.splitPrnt.titleBar.data['class'][:, 0],
                labels=self.canvas.prnt.prnt.splitPrnt.titleBar.data['label'],
                validation=self.canvas.prnt.prnt.splitPrnt.titleBar.data['validation'],
                col1=0, col2=1, title=self.graph.title,
                xLabel=self.graph.xLabel,
                yLabel=self.graph.yLabel, xval=True,
                text=self.tbPoints.GetValue(),
                pconf=False, symb=self.tbSymbols.GetValue(),
                usecol=symcolours,
                usesym=symsymbols)

        elif len(self.canvas.GetName().split('plcGaModelPlot')) > 1:

            self.splitPrnt = self.canvas.prnt.prnt.prnt.splitPrnt

            if self.splitPrnt.dtype in ['DFA']:
                if self.splitPrnt.titleBar.data['gadfadfscores'] is not None:
                    plot_scores(
                        self.canvas,
                        self.splitPrnt.titleBar.data['gadfadfscores'],
                        cl=self.splitPrnt.titleBar.data['class'][:, 0],
                        labels=self.splitPrnt.titleBar.data['label'],
                        validation= self.splitPrnt.titleBar.data['validation'],
                        col1=self.splitPrnt.titleBar.spnGaScoreFrom.GetValue() - 1,
                        col2=self.splitPrnt.titleBar.spnGaScoreTo.GetValue() - 1,
                        title=self.graph.title, xLabel=self.graph.xLabel,
                        yLabel=self.graph.yLabel, xval=True,
                        text=self.tbPoints.GetValue(),
                        pconf=self.tbConf.GetValue(),
                        symb=self.tbSymbols.GetValue(),
                        usecol=symcolours,
                        usesym=symsymbols)
            else:
                self.canvas = plot_pls_model(
                    self.canvas, model='ga',
                    tbar=self.splitPrnt.prnt.prnt.tbMain,
                    cL=self.splitPrnt.titleBar.data['class'],
                    scores=None,
                    label=self.splitPrnt.titleBar.data['label'],
                    predictions=self.splitPrnt.titleBar.data['gaplsscores'],
                    validation=self.splitPrnt.titleBar.data['validation'],
                    RMSEPT=self.splitPrnt.titleBar.data['gaplsrmsept'],
                    factors=self.canvas.splitPrnt.titleBar.data['gaplsfactors'],
                    dtype=0,
                    col1=self.splitPrnt.titleBar.spnGaScoreFrom.GetValue() - 1,
                    col2=self.canvas.splitPrnt.titleBar.spnGaScoreTo.GetValue() - 1,
                    symbols=self.tbSymbols.GetValue(),
                    usetxt=self.tbPoints.GetValue(),
                    usecol=symcolours, usesym=symsymbols,
                    plScL=self.canvas.splitPrnt.titleBar.data['pls_class'])

        elif self.canvas.GetName() in ['plcPcaLoadsV']:
            if self.canvas.prnt.titleBar.data['pcloads'] is not None:
                plot_loads(self.canvas, np.transpose(
                    self.canvas.prnt.titleBar.data['pcloads']),
                           xaxis=self.canvas.prnt.titleBar.data['indlabels'],
                           col1=self.canvas.prnt.titleBar.spnNumPcs1.GetValue() - 1,
                           col2=self.canvas.prnt.titleBar.spnNumPcs2.GetValue() - 1,
                           title=self.graph.title, xLabel=self.graph.xLabel,
                           yLabel=self.graph.yLabel, dtype=loadType,
                           usecol=symcolours,
                           usesym=symsymbols)

        elif self.canvas.GetName() in ['plcPLSloading']:
            if self.canvas.prnt.titleBar.data['plsloads'] is not None:
                plot_loads(self.canvas,
                           self.canvas.prnt.titleBar.data['plsloads'],
                           xaxis=self.canvas.prnt.titleBar.data['indlabels'],
                           col1=self.canvas.prnt.titleBar.spnPLSfactor1.GetValue() - 1,
                           col2=self.canvas.prnt.titleBar.spnPLSfactor2.GetValue() - 1,
                           title=self.graph.title, xLabel=self.graph.xLabel,
                           yLabel=self.graph.yLabel, dtype=loadType,
                           usecol=symcolours,
                           usesym=symsymbols)

        elif self.canvas.GetName() in ['plcDfaLoadsV']:
            if self.canvas.prnt.titleBar.data['dfloads'] is not None:
                plot_loads(self.canvas,
                           self.canvas.prnt.titleBar.data['dfloads'],
                           xaxis=self.canvas.prnt.titleBar.data['indlabels'],
                           col1=self.canvas.prnt.titleBar.spnDfaScore1.GetValue() - 1,
                           col2=self.canvas.prnt.titleBar.spnDfaScore2.GetValue() - 1,
                           title=self.graph.title, xLabel=self.graph.xLabel,
                           yLabel=self.graph.yLabel, dtype=loadType,
                           usecol=symcolours,
                           usesym=symsymbols)

        elif self.canvas.GetName() in ['plcGaSpecLoad']:
            if self.splitPrnt.dtype in ['DFA']:
                labels = []
                for each in self.splitPrnt.titleBar.data['gacurrentchrom']:
                    labels.append(
                        self.splitPrnt.titleBar.data['indlabels'][int(each)])

                plot_loads(self.canvas,
                           self.splitPrnt.titleBar.data['gadfadfaloads'],
                           xaxis=labels, title=self.graph.title,
                           xLabel=self.graph.xLabel,
                           yLabel=self.graph.yLabel, dtype=loadType,
                           usecol=symcolours,
                           usesym=symsymbols)

        elif self.canvas.GetName() == 'plcGaSpecLoad':
            if self.canvas.prnt.prnt.splitPrnt.dtype == 'PLS':
                labels = []
                for each in self.splitPrnt.titleBar.data['gacurrentchrom']:
                    labels.append(
                        self.splitPrnt.titleBar.data['indlabels'][int(each)])

                plot_loads(self.canvas,
                           self.canvas.prnt.prnt.splitPrnt.titleBar.data[
                              'gaplsplsloads'],
                           xaxis=labels, title=self.graph.title,
                           xLabel=self.graph.xLabel,
                           yLabel=self.graph.yLabel, dtype=loadType,
                           usecol=symcolours,
                           usesym=symsymbols)

    def OnTxtTitle(self, _):
        self.graph.setTitle(self.txtTitle.GetValue())
        self.canvas.Redraw()

    def OnBtnApply(self, _):
        self.canvas.fontSizeAxis = self.spnAxesFont.GetValue()
        self.canvas.fontSizeTitle = self.spn_title.GetValue()

        self.graph.setTitle(self.txtTitle.GetValue())
        self.graph.setXLabel(self.txtXlabel.GetValue())
        self.graph.setYLabel(self.txtYlabel.GetValue())

        xmin = float(self.txtXmin.GetValue())
        xmax = float(self.txtXmax.GetValue())
        ymin = float(self.txtYmin.GetValue())
        ymax = float(self.txtYmax.GetValue())
        
        if (xmin < xmax) and (ymin < ymax):
            self.canvas.last_draw = [self.canvas.last_draw[0],
                                     np.array([xmin, xmax]),
                                     np.array([ymin, ymax])]
        
        self.canvas.Redraw()
        self.Close()

    def on_spn_axes_font(self, _):
        self.canvas.fontSizeAxis = self.spnAxesFont.GetValue()
        self.canvas.Redraw()

    def on_spn_title_font(self, _):
        self.canvas.fontSizeTitle = self.spn_title.GetValue()
        self.canvas.Redraw()

    def resizeAxes(self):
        xmin = float(self.txtXmin.GetValue())
        xmax = float(self.txtXmax.GetValue())
        ymin = float(self.txtYmin.GetValue())
        ymax = float(self.txtYmax.GetValue())

        if (xmin < xmax) and (ymin < ymax):
            self.canvas.last_draw = [self.canvas.last_draw[0],
                                     np.array([xmin, xmax]),
                                     np.array([ymin, ymax])]
        self.canvas.Redraw()

    def on_spn_xmin(self, _):
        self.resizeAxes()

    def on_spn_xmax(self, _):
        self.resizeAxes()

    def on_spn_ymin(self, _):
        self.resizeAxes()

    def on_spn_ymax(self, _):
        self.resizeAxes()

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


class PyChemMain(wx.Frame):
    """"""
    _custom_classes = {'wx.Panel': ['expSetup', 'plotSpectra', 'Pca', 'Cluster',
                                    'Dfa', 'Plsr', 'Ga', 'Univariate']}
    def __init__(self, parent):
        """"""
        wx.Frame.__init__(self, id=wxID_PCM, name='PyChemMain',
                          parent=parent, pos=(0, 0), size=(1024, 738),
                          style=wx.DEFAULT_FRAME_STYLE,
                          title='PyChem 3.0.5g Beta')
        self.data = None
        self.tbar = None
        self.parent = parent
        self._init_utils()
        self._init_ctrls()
        # set defaults
        self.reset()

    def _init_utils(self):
        """"""
        self.mnuMain = wx.MenuBar()
        self.mnuFile = wx.Menu(title='')
        self.mnuTools = wx.Menu(title='')
        self.mnuHelp = wx.Menu(title='')
        self.gridMenu = wx.Menu(title='')
        self.indRowMenu = wx.Menu(title='')

        self._init_coll_mnuMain_Menus(self.mnuMain)
        self._init_coll_mnu_file(self.mnuFile)
        self._init_coll_mnu_tools(self.mnuTools)
        self._init_coll_mnu_help(self.mnuHelp)
        self._init_grid_menu(self.gridMenu)
        self._init_grid_row_menu(self.indRowMenu)

    def _init_ctrls(self):
        """"""
        self.SetClientSize((1016, 704))
        self.SetToolTip('')
        self.SetHelpText('')
        self.Center(wx.BOTH)

        icon = wx.Icon(opjoin('ico', 'pychem.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        self.SetMinSize((200, 400))
        self.SetMenuBar(self.mnuMain)
        self.Bind(wx.EVT_SIZE, self.OnMainFrameSize)

        self.nbMain = fnb.FlatNotebook(id=wxID_PCMNBMAIN, name='nbMain',
                                       parent=self, pos=(0, 0),
                                       size=(1016, 730),
                                       style=fnb.FNB_NODRAG | fnb.FNB_NO_X_BUTTON)
        self.nbMain.SetToolTip('')
        self.nbMain.SetMinSize((200, 400))
        self.nbMain.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CHANGING,
                         self.on_nb_main_nbook_page_changing,
                         id=wxID_PCMNBMAIN)
        self.nbMain.parent = self

        self.sbMain = wx.StatusBar(id=wxID_PCMSBMAIN, name='sbMain',
                                   parent=self, style=0)
        self.sbMain.SetToolTip('')
        self._init_coll_stb_main_fields(self.sbMain)
        self.SetStatusBar(self.sbMain)

        self.tbMain = PlotToolBar(self)
        self.tbMain.Enable(False)
        self.tbMain.Bind(wx.EVT_SIZE, self.on_tb_main_size)
        self.SetToolBar(self.tbMain)
        self.tbMain.Realize()

        self.plExpset = exp_setup.ExpSetup(id=wxID_PCMPLEXPSET,
                                           name='plExpset',
                                           parent=self.nbMain,
                                           pos=(0, 0), size=(1008, 635),
                                           style=wx.TAB_TRAVERSAL)
        self.plExpset.getFrame(self)
        self.plExpset.SetToolTip('')

        self.plPreproc = plot_spectra.plotSpectra(id=wxID_PCMPLPREPROC,
                                                  name='plPreproc',
                                                  parent=self.nbMain,
                                                  pos=(0, 0), size=(1008, 635),
                                                  style=wx.TAB_TRAVERSAL)
        self.plPreproc.SetToolTip('')

        self.plPca = pca.Pca(id_=wxID_PCMPLPCA, name='plPca',
                             parent=self.nbMain, pos=(0, 0), size=(1008, 635),
                             style=wx.TAB_TRAVERSAL)
        self.plPca.SetToolTip('')

        self.plCluster = cluster.Cluster(id_=wxID_PCMPLCLUSTER,
                                         name='plCluster', parent=self.nbMain,
                                         pos=(0, 0), size=(1008, 635),
                                         style=wx.TAB_TRAVERSAL)
        self.plCluster.SetToolTip('')
        self.plCluster.parent = self

        self.plDfa = dfa.Dfa(id_=wxID_PCMPLDFA, name='plDfa',
                             parent=self.nbMain, pos=(0, 0), size=(1008, 635),
                             style=wx.TAB_TRAVERSAL)
        self.plDfa.SetToolTip('')

        self.plPls = plsr.Plsr(id_=wxID_PCMPLPLS, name='plPls',
                               parent=self.nbMain, pos=(0, 0), size=(1008, 635),
                               style=wx.TAB_TRAVERSAL)
        self.plPls.SetToolTip('')
        self.plPls.parent = self

        self.plGadfa = ga.Ga(id_=wxID_PCMPLGADFA, name='plGadfa',
                             parent=self.nbMain, pos=(0, 0), size=(1008, 635),
                             style=wx.TAB_TRAVERSAL, dtype='DFA')
        self.plGadfa.SetToolTip('')
        self.plGadfa.parent = self

        self.plGapls = ga.Ga(id_=wxID_PCMPLGAPLSC, name='plGaplsc',
                             parent=self.nbMain, pos=(0, 0), size=(1008, 635),
                             style=wx.TAB_TRAVERSAL, dtype='PLS')
        self.plGapls.SetToolTip('')
        self.plGapls.parent = self

        self.plUnivariate = univariate.Univariate(
            id_=wxID_PCMPLUNIVARIATE,
            name='plUnivariate', parent=self.nbMain, pos=(0, 0),
            size=(1008, 635), style=wx.TAB_TRAVERSAL)
        self.plUnivariate.SetToolTip('')
        self.plUnivariate.parent = self

        self._init_coll_nb_main_pages(self.nbMain)

    def _init_coll_nb_main_pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.plExpset, select=True,
                       text='Experiment Setup')
        parent.AddPage(imageId=-1, page=self.plPreproc, select=False,
                       text='Spectral Pre-processing')
        parent.AddPage(imageId=-1, page=self.plUnivariate, select=False,
                       text='Univariate Tests')
        parent.AddPage(imageId=-1, page=self.plPca, select=False,
                       text='Principal Component Analysis')
        parent.AddPage(imageId=-1, page=self.plCluster, select=False,
                       text='Cluster Analysis')
        parent.AddPage(imageId=-1, page=self.plDfa, select=False,
                       text='Discriminant Function Analysis')
        parent.AddPage(imageId=-1, page=self.plPls, select=False,
                       text='Partial Least Squares Regression')
        parent.AddPage(imageId=-1, page=self.plGadfa, select=False,
                       text='GA - Discriminant Function Analysis')
        parent.AddPage(imageId=-1, page=self.plGapls, select=False,
                       text='GA - PLSR Calibration')

    def _init_coll_mnu_tools(self, parent):
        # generated method, don't edit

        parent.Append(helpString='', id=wxID_PCMMNUTOOLSEXPSET,
                      kind=wx.ITEM_NORMAL, item='Experiment Setup')
        parent.Append(helpString='', id=wxID_PCMMNUTOOLSPREPROC,
                      kind=wx.ITEM_NORMAL, item='Spectral Pre-processing')
        parent.Append(helpString='', id=wxID_PCMPLUNIVARIATE,
                      kind=wx.ITEM_NORMAL, item='Univariate Tests')
        parent.Append(helpString='', id=wxID_PCMMNUTOOLSMNUPCA,
                      kind=wx.ITEM_NORMAL,
                      item='Principal Component Analysis (PCA)')
        parent.Append(helpString='', id=wxID_PCMMNUTOOLSMNUCLUSTER,
                      kind=wx.ITEM_NORMAL, item='Cluster Analysis')
        parent.Append(helpString='', id=wxID_PCMMNUTOOLSMNUDFA,
                      kind=wx.ITEM_NORMAL,
                      item='Discriminant Function Analysis (DFA)')
        parent.Append(helpString='', id=wxID_PCMMNUTOOLSMNUPLSR,
                      kind=wx.ITEM_NORMAL,
                      item='Partial Least Squares Regression (PLSR)')
        parent.Append(helpString='', id=wxID_PCMMNUTOOLSMNUGADFA,
                      kind=wx.ITEM_NORMAL,
                      item='GA-Discriminant Function Analysis')
        parent.Append(helpString='', id=wxID_PCMMNUTOOLSMNUGAPLSC,
                      kind=wx.ITEM_NORMAL,
                      item='GA-Partial Least Squares Calibration')
        self.Bind(wx.EVT_MENU, self.on_mnu_tools_expset,
                  id=wxID_PCMMNUTOOLSEXPSET)
        self.Bind(wx.EVT_MENU, self.on_mnu_tools_preproc,
                  id=wxID_PCMMNUTOOLSPREPROC)
        self.Bind(wx.EVT_MENU, self.on_mnu_tools_mnu_univariate,
                  id=wxID_PCMPLUNIVARIATE)
        self.Bind(wx.EVT_MENU, self.on_mnu_tools_mnu_pca,
                  id=wxID_PCMMNUTOOLSMNUPCA)
        self.Bind(wx.EVT_MENU, self.on_mnu_tools_mnu_cluster,
                  id=wxID_PCMMNUTOOLSMNUCLUSTER)
        self.Bind(wx.EVT_MENU, self.on_mnu_tools_mnu_plsr,
                  id=wxID_PCMMNUTOOLSMNUPLSR)
        self.Bind(wx.EVT_MENU, self.on_mnu_tools_mnu_dfa,
                  id=wxID_PCMMNUTOOLSMNUDFA)
        self.Bind(wx.EVT_MENU, self.on_mnu_tools_mnu_gadfa,
                  id=wxID_PCMMNUTOOLSMNUGADFA)
        self.Bind(wx.EVT_MENU, self.on_mnu_tools_mnu_gaplsc,
                  id=wxID_PCMMNUTOOLSMNUGAPLSC)

    def _init_coll_mnu_file(self, parent):
        # generated method, don't edit

        parent.Append(helpString='', id=wxID_PCMMNUFILELOADEXP,
                      kind=wx.ITEM_NORMAL, item='Load Experiment')
        parent.Append(helpString='', id=wxID_PCMMNUFILELOADWS,
                      kind=wx.ITEM_NORMAL, item='Load Workspace')
        parent.Append(helpString='', id=wxID_PCMMNUFILESAVEEXP,
                      kind=wx.ITEM_NORMAL, item='Save Experiment As..')
        parent.Append(helpString='', id=wxID_PCMMNUFILESAVEWS,
                      kind=wx.ITEM_NORMAL, item='Save Workspace As...')
        parent.Append(helpString='', id=wxID_PCMMNUFILEFILEIMPORT,
                      kind=wx.ITEM_NORMAL, item='Import')
        parent.Append(helpString='', id=wxID_PCMMNUFILEAPPEXIT,
                      kind=wx.ITEM_NORMAL, item='Exit')
        self.Bind(wx.EVT_MENU, self.on_mnu_file_loadexp,
                  id=wxID_PCMMNUFILELOADEXP)
        self.Bind(wx.EVT_MENU, self.on_mnu_file_loadws,
                  id=wxID_PCMMNUFILELOADWS)
        self.Bind(wx.EVT_MENU, self.on_mnu_file_saveexp,
                  id=wxID_PCMMNUFILESAVEEXP)
        self.Bind(wx.EVT_MENU, self.OnMnuFileSavewsMenu,
                  id=wxID_PCMMNUFILESAVEWS)
        self.Bind(wx.EVT_MENU, self.OnMnuFileFileimportMenu,
                  id=wxID_PCMMNUFILEFILEIMPORT)
        self.Bind(wx.EVT_MENU, self.on_mnu_file_app_exit,
                  id=wxID_PCMMNUFILEAPPEXIT)

    def _init_coll_mnuMain_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.mnuFile, title='File')
        parent.Append(menu=self.mnuTools, title='Tools')
        parent.Append(menu=self.mnuHelp, title='Help')

    def _init_coll_mnu_help(self, parent):
        # generated method, don't edit

        parent.Append(helpString='', id=wxID_PCMMNUHELPCONTENTS,
                      kind=wx.ITEM_NORMAL, item='Contents')
        parent.Append(helpString='', id=wxID_PCMMNUABOUTCONTENTS,
                      kind=wx.ITEM_NORMAL, item='About')
        self.Bind(wx.EVT_MENU, self.on_mnu_help_contents,
                  id=wxID_PCMMNUHELPCONTENTS)
        self.Bind(wx.EVT_MENU, self.on_mnu_about,
                  id=wxID_PCMMNUABOUTCONTENTS)

    # noinspection PyMethodMayBeStatic
    def _init_coll_stb_main_fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(5)

        parent.SetStatusText(i=0, text='Status')
        parent.SetStatusText(i=1, text='')
        parent.SetStatusText(i=2, text='')
        parent.SetStatusText(i=3, text='')
        parent.SetStatusText(i=4, text='')

        parent.SetStatusWidths([-2, -2, -2, -2, -5])

    def _init_grid_menu(self, parent):
        # generated method, don't edit

        parent.Append(helpString='', id=MNUGRIDCOPY, kind=wx.ITEM_NORMAL,
                      item='Copy')
        parent.Append(helpString='', id=MNUGRIDPASTE, kind=wx.ITEM_NORMAL,
                      item='Paste')
        parent.Append(helpString='', id=MNUGRIDRENAMECOL, kind=wx.ITEM_NORMAL,
                      item='Rename column')
        parent.Append(helpString='', id=MNUGRIDDELETECOL, kind=wx.ITEM_NORMAL,
                      item='Delete column')
        parent.Append(helpString='', id=MNUGRIDRESETSORT, kind=wx.ITEM_NORMAL,
                      item='reset row sort')

        self.Bind(wx.EVT_MENU, self.on_mnu_grid_copy, id=MNUGRIDCOPY)
        self.Bind(wx.EVT_MENU, self.on_mnu_grid_paste, id=MNUGRIDPASTE)
        self.Bind(wx.EVT_MENU, self.on_mnu_grid_rename_column, id=MNUGRIDRENAMECOL)
        self.Bind(wx.EVT_MENU, self.on_mnu_grid_delete_column, id=MNUGRIDDELETECOL)
        self.Bind(wx.EVT_MENU, self.OnMnuGridResetSort, id=MNUGRIDRESETSORT)

    def _init_grid_row_menu(self, parent):
        parent.Append(helpString='', id=MNUGRIDROWDEL, kind=wx.ITEM_NORMAL,
                      item='Delete User Defined Variable')
        self.Bind(wx.EVT_MENU, self.on_mnu_grid_row_del, id=MNUGRIDROWDEL)

    def OnMainFrameSize(self, event):
        event.Skip()

    # self.Layout()
    # self.plUnivariate.Refresh()

    def on_tb_main_size(self, _):
        self.tbMain.Refresh()

    # noinspection PyMethodMayBeStatic
    def on_mnu_help_contents(self, _):
        from wx.tools import helpviewer
        helpviewer.main(['', opjoin('docs', 'PAChelp.hhp')])

    def on_mnu_about(self, _):
        from wx.lib.wordwrap import wordwrap
        info = AboutDialogInfo()
        info.Name = "PyChem"
        info.Version = "3.0.5g Beta"
        info.Copyright = "(C) 2010 Roger Jarvis"
        info.Description = wordwrap(
            "PyChem is a software program for multivariate "
            "data analysis (MVA).  It includes algorithms for "
            "calibration and categorical analyses.  In addition, "
            "novel genetic algorithm tools for spectral feature "
            "selection"

            "\n\nFor more information please go to the PyChem "
            "website using the link below, or email the project "
            "author, roger.jarvis@manchester.ac.uk",
            350, wx.ClientDC(self))
        info.WebSite = ("http://pychem.sf.net/", "PyChem home page")

        # Then we call wx.AboutBox giving it that info object
        AboutBox(info)

    def on_mnu_file_loadexp(self, _):
        loadFile = wx.FileSelector("Load PyChem Experiment", "", "",
                                   "", "XML files (*.xml)|*.xml")
        dlg = WorkspaceDialog(self, loadFile)
        try:
            tree = dlg.get_tree()
            if tree is not None:
                dlg.ShowModal()
                workSpace = dlg.get_workspace()
                if workSpace != 0:
                    self.reset()
                    self.xml_load(tree, workSpace)
                    self.data['exppath'] = loadFile
                    mb = self.GetMenuBar()
                    mb.Enable(wxID_PCMMNUFILESAVEEXP, True)
                    mb.Enable(wxID_PCMMNUFILESAVEWS, True)
                    mb.Enable(wxID_PCMMNUFILELOADWS, True)
        finally:
            dlg.Destroy()

    def on_mnu_file_loadws(self, _):
        dlg = WorkspaceDialog(self, self.data['exppath'])
        if self.data['exppath'] is not None:
            try:
                dlg.ShowModal()
                workSpace = dlg.get_workspace()
                if workSpace != 0:
                    self.reset(1)
                    tree = dlg.get_tree()
                    self.xml_load(tree, workSpace, 'ws')
            finally:
                dlg.Destroy()
        else:
            dlg.Destroy()

    def on_mnu_file_saveexp(self, _):
        dlg = wx.FileDialog(self, "Choose a file", ".", "",
                            "XML files (*.xml)|*.xml", wx.FD_SAVE)

        # print('raw: ', self.data['raw'])   # OK

        if self.data['raw'] is not None:
            try:
                if dlg.ShowModal() == wx.ID_OK:
                    self.data['exppath'] = dlg.GetPath()
                    # workspace name entry dialog
                    msg = 'Type in a name under which to save the current workspace'
                    texTdlg = wx.TextEntryDialog(self, msg,
                                                 'Save Workspace as...',
                                                 'Default')
                    ws_name = ''
                    try:
                        if texTdlg.ShowModal() == wx.ID_OK:
                            ws_name = texTdlg.GetValue()
                    finally:
                        texTdlg.Destroy()

                    self.xml_save(self.data['exppath'], ws_name, 'new')
                    # activate workspace save menu option
                    mb = self.GetMenuBar()
                    mb.Enable(wxID_PCMMNUFILESAVEEXP, True)
                    mb.Enable(wxID_PCMMNUFILESAVEWS, True)
                    mb.Enable(wxID_PCMMNUFILELOADWS, True)
                    # show workspace dialog so that default can be edited
                    dlgws = WorkspaceDialog(self, self.data['exppath'],
                                            dtype='Save')
                    try:
                        dlgws.ShowModal()
                    finally:
                        dlgws.Destroy()
            finally:
                dlg.Destroy()
        else:
            dlg.Destroy()

    def OnMnuFileSavewsMenu(self, _):
        if self.data['exppath'] is not None:
            wsName = ''
            # text entry dialog
            msg = 'Type in a name under which to save the current workspace'
            dlg = wx.TextEntryDialog(self, msg,
                                     'Save Workspace as...', 'Default')
            # try:
            if dlg.ShowModal() == wx.ID_OK:
                wsName = dlg.GetValue()
            # finally:
            dlg.Destroy()

            # workspace dialog for editing
            if wsName != '':
                # save workspace to xml file
                self.xml_save(self.data['exppath'], wsName.replace(' ', '_'),
                              dtype=self.data['exppath'])

                # show workspace dialog
                dlg = WorkspaceDialog(self, self.data['exppath'],
                                      dtype='Save')
                try:
                    dlg.ShowModal()
                    dlg.append_workspace(wsName)
                finally:
                    dlg.Destroy()
            else:
                dlg = wx.MessageDialog(self, 'No workspace name was provided',
                                       'Error!', wx.OK | wx.ICON_ERROR)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()

    def OnMnuFileFileimportMenu(self, _):
        dlg = ImportDialog(self)
        try:
            dlg.ShowModal()
            if dlg.is_ok() == 1:
                # Apply default settings
                self.reset()

                # Load arrays
                wx.BeginBusyCursor()

                # test for commas in file indicating csv filetype
                infile = open(dlg.get_file())
                lineFromFile = infile.readline()
                infile.close()

                # if comma present, assume csv file and add delimiter to loadtxt function
                if ',' in lineFromFile:
                    if dlg.transpose() == 0:
                        self.data['raw'] = loadtxt(dlg.get_file(), delimiter=',')
                    else:
                        self.data['raw'] = np.transpose(
                            loadtxt(dlg.get_file(), delimiter=','))
                else:
                    if dlg.transpose() == 0:
                        self.data['raw'] = loadtxt(dlg.get_file())
                    else:
                        self.data['raw'] = np.transpose(loadtxt(dlg.get_file()))

                # create additional arrays of experimental data
                self.data['rawtrunc'] = self.data['raw']
                self.data['proc'] = self.data['raw']
                self.data['proctrunc'] = self.data['raw']

                # Resize grids
                exp_setup.ResizeGrids(self.plExpset.grdNames,
                                      self.data['raw'].shape[0], 3, 2)
                exp_setup.ResizeGrids(self.plExpset.grdIndLabels,
                                      self.data['raw'].shape[1], 0, 3)

                # activate ctrls
                self.enable_ctrls()

                # set x-range 1 to n
                self.plExpset.indTitleBar.stcRangeFrom.SetValue('1')
                self.plExpset.indTitleBar.stcRangeTo.SetValue(
                    str(self.data['raw'].shape[1]))

                # set plot spn range
                self.plPreproc.titleBar.spcPlotSpectra.SetValue(1)
                self.plPreproc.titleBar.spcPlotSpectra.SetRange(1, self.data[
                    'raw'].shape[0])

                # Calculate Xaxis
                self.data['xaxis'] = exp_setup.get_xaxis(
                    self.plExpset.indTitleBar.stcRangeFrom.GetValue(),
                    self.plExpset.indTitleBar.stcRangeTo.GetValue(),
                    self.data['raw'].shape[1],
                    self.plExpset.grdIndLabels)

                # Display preview of data
                raw = self.data['raw']
                rows = raw.shape[0]
                cols = raw.shape[1]
                data = None

                if (rows > 10) and (cols > 10):
                    data = raw[0:10, 0:10]
                elif (rows <= 10) and (cols > 10):
                    data = raw[0:rows, 0:10]
                elif (rows > 10) and (cols <= 10):
                    data = raw[0:10, 0:cols]
                elif (rows <= 10) and (cols <= 10):
                    data = raw[0:rows, 0:cols]

                # allow for experiment save on file menu
                mb = self.GetMenuBar()
                mb.Enable(wxID_PCMMNUFILESAVEEXP, True)
                mb.Enable(wxID_PCMMNUFILESAVEWS, False)
                mb.Enable(wxID_PCMMNUFILELOADWS, False)

                dlgConfirm = ImportConfirmDialog(self, data, rows, cols)
                try:
                    dlgConfirm.ShowModal()
                finally:
                    dlgConfirm.Destroy()

                wx.EndBusyCursor()

        except Exception:
            wx.EndBusyCursor()
            self.reset()
            dlg.Destroy()
            error_box(self, 'Unable to load array.\nPlease check file format.')
            raise

    def on_mnu_file_app_exit(self, _):
        self.Close()

    def on_mnu_tools_expset(self, _):
        self.nbMain.SetSelection(0)

    def on_mnu_tools_preproc(self, _):
        if self.nbMain.GetSelection() == 0:
            self.get_experiment_details()
        self.nbMain.SetSelection(1)

    def on_mnu_tools_mnu_pca(self, _):
        if self.nbMain.GetSelection() == 0:
            self.get_experiment_details()
        self.nbMain.SetSelection(3)

    def on_mnu_tools_mnu_cluster(self, _):
        if self.nbMain.GetSelection() == 0:
            self.get_experiment_details()
        self.nbMain.SetSelection(4)

    def on_mnu_tools_mnu_plsr(self, _):
        if self.nbMain.GetSelection() == 0:
            self.get_experiment_details()
        self.nbMain.SetSelection(6)

    def on_mnu_tools_mnu_dfa(self, _):
        if self.nbMain.GetSelection() == 0:
            self.get_experiment_details()
        self.nbMain.SetSelection(5)

    def on_mnu_tools_mnu_gadfa(self, _):
        if self.nbMain.GetSelection() == 0:
            self.get_experiment_details()
        self.nbMain.SetSelection(7)

    def on_mnu_tools_mnu_gaplsc(self, _):
        if self.nbMain.GetSelection() == 0:
            self.get_experiment_details()
        self.nbMain.SetSelection(8)

    def on_mnu_tools_mnu_univariate(self, _):
        if self.nbMain.GetSelection() == 0:
            self.get_experiment_details()
        self.nbMain.SetSelection(2)

    def on_mnu_grid_delete_column(self, _):
        grid = self.data['gridsel']
        col = grid.GetGridCursorCol()
        this = 0
        heads = []
        if grid == self.plExpset.grdNames:
            if col != 0:
                # noinspection PyUnusedLocal
                count = {'Label': 0, 'Class': 0, 'Validation': 0}
                for i in range(1, grid.GetNumberCols()):
                    cmd = 'count["%s"] += 1' % grid.GetCellValue(0, i)
                    exec(cmd, locals(), globals())
                    heads.append(grid.GetColLabelValue(i))

                cmd = 'this = count["%s"]' % grid.GetCellValue(0, col)
                exec(cmd, locals(), globals())
            if this > 1:
                #     flag = 1
                #     #check this col isn't used in a saved workspace
                #     if self.data['exppath'] is not None:
                #         tree = ET.ElementTree(file=self.data['exppath'])
                #         root = tree.getroot()
                #         #get workspaces subelement
                #         WSnode = root.findall("Workspaces")[0]
                #         workspaces = WSnode.getchildren()
                #         #run through each workspace to see it grid col used
                #         for each in workspaces:
                #             for item in each.getchildren():
                #                 if item.tag == 'Lists':
                #                     for list in item.getchildren():
                #                         if list.tag == 'depvarsel':
                #                             L = string.split(list.text,'\t')
                #                             Didx = []
                #                             for iL in range(len(L)-1):
                #                                 Didx.append(int(iL))
                #             for Lind in Didx:
                #                 if (Lind < 0) & (-Lind == col) is True:
                #                     flag = 0
                #                     wsdel = each
                #     if flag == 1:
                msg = 'Are you sure you want to delete the column?'
                #     else:
                #         msg = 'The workspace "' + wsdel + '" uses this column, if you delete this ' +\
                #               'entry then the workspace must also be deleted.  Are you sure you want ' +\
                #               'to continue?'
                #
                dlg = wx.MessageDialog(self, msg, 'Confirm',
                                       wx.OK | wx.CANCEL | wx.ICON_WARNING)
                try:
                    if dlg.ShowModal() == wx.ID_OK:
                        grid.DeleteCols(col)
                        # restore col headings
                        del heads[col - 1]
                        for i in range(1, len(heads) + 1):
                            grid.SetColLabelValue(i, heads[i - 1])
                finally:
                    dlg.Destroy()
        else:
            if (grid.GetNumberCols() > 2) & (col > 1) is True:
                msg = 'Are you sure you want to delete the column?'
                dlg = wx.MessageDialog(self, msg, 'Confirm',
                                       wx.OK | wx.CANCEL | wx.ICON_WARNING)
                try:
                    if dlg.ShowModal() == wx.ID_OK:
                        heads = []
                        for i in range(1, grid.GetNumberCols()):
                            heads.append(grid.GetColLabelValue(i))
                        grid.DeleteCols(col)
                        # restore col headings
                        del heads[col - 1]
                        for i in range(1, len(heads) + 1):
                            grid.SetColLabelValue(i, heads[i - 1])
                finally:
                    dlg.Destroy()

    def OnMnuGridResetSort(self, _):
        # order rows in grid by row number
        grid = self.data['gridsel']
        order = []
        # get index
        for i in range(2, grid.GetNumberRows()):
            order.append(int(grid.GetRowLabelValue(i)))
        index = np.argsort(order)
        # create list of grid contents
        gList = []
        for i in index:
            tp = []
            for j in range(grid.GetNumberCols()):
                tp.append(grid.GetCellValue(i + 2, j))
            gList.append(tp)
        # replace current grid contents with ordered
        for i in range(len(gList)):
            grid.SetRowLabelValue(i + 2, str(i + 1))
            for j in range(grid.GetNumberCols()):
                grid.SetCellValue(i + 2, j, gList[i][j])

    def on_mnu_grid_row_del(self, _):
        # delete user defined variable row from grdIndLabels
        GridRowDel(self.data['gridsel'], self.data)
        # update experiment details
        self.get_experiment_details(case=1)

    def on_mnu_grid_rename_column(self, _):
        grid = self.data['gridsel']
        col = grid.GetGridCursorCol()
        dlg = wx.TextEntryDialog(self, '', 'Enter new column heading', '')
        try:
            if dlg.ShowModal() == wx.ID_OK:
                answer = dlg.GetValue()
                col = grid.GetGridCursorCol()
                grid.SetColLabelValue(col, answer)
        finally:
            dlg.Destroy()

    def on_mnu_grid_paste(self, _):
        # Paste cells
        grid = self.data['gridsel']
        wx.TheClipboard.Open()
        Data = wx.TextDataObject('')
        wx.TheClipboard.GetData(Data)
        wx.TheClipboard.Close()
        Data = Data.GetText()
        X = grid.GetGridCursorRow()
        Y = grid.GetGridCursorCol()
        if grid == self.plExpset.grdNames:
            if X < 2: X = 2
            if Y < 1: Y = 1
        elif grid == self.plExpset.grdIndLabels:
            if X < 1: X = 1
            if Y < 1: Y = 1
        Data = Data.split('\n')
        for i in range(len(Data)):
            if X + i < grid.GetNumberRows():
                for j in range(len(Data[0].split('\t'))):
                    if Y + j < grid.GetNumberCols():
                        item = Data[i].split('\r')[0]
                        item = item.split('\t')[j]
                        grid.SetCellValue(X + i, Y + j, item)

    def on_mnu_grid_copy(self, _):
        grid = self.data['gridsel']

        From = grid.GetSelectionBlockTopLeft()
        To = grid.GetSelectionBlockBottomRight()
        row = grid.GetGridCursorRow()
        col = grid.GetGridCursorCol()

        if len(From) > 0:
            From = From[0]
            To = To[0]
        else:
            From = (row, col)
            To = (row, col)

        Data = ''
        for i in range(From[0], To[0] + 1):
            for j in range(From[1], To[1] + 1):
                if j < To[1]:
                    Data = Data + grid.GetCellValue(i, j) + '\t'
                else:
                    Data = Data + grid.GetCellValue(i, j)
            if i < To[0]:
                Data = Data + '\n'

        wx.TheClipboard.Open()
        wx.TheClipboard.SetData(wx.TextDataObject(Data))
        wx.TheClipboard.Close()

    def reset(self, case=0):
        varList = "'split':None,'processlist':[]," + \
                  "'pcscores':None,'pcloads':None,'pcpervar':None," + \
                  "'pceigs':None,'pcadata':None,'niporsvd':None," + \
                  "'plsloads':None,'pcatype':None," + \
                  "'dfscores':None,'dfloads':None,'dfeigs':None," + \
                  "'gadfachroms':None,'gadfascores':None," + \
                  "'gadfacurves':None,'gaplschroms':None," + \
                  "'gaplsscores':None,'gaplscurves':None," + \
                  "'gadfadfscores':None,'gadfadfaloads':None," + \
                  "'gaplsplsloads':None,'gridsel':None,'plotsel':None," + \
                  "'tree':None,'order':None,'plsfactors':None," + \
                  "'rmsec':None,'rmsepc':None,'rmsept':None," + \
                  "'gacurrentchrom':None,'plspred':None,'pcaloadsym':None," + \
                  "'dfaloadsym':None,'plsloadsym':None,'plst':None," + \
                  "'plstype':0,'pls_class':None,'gaplstreeorder':None," + \
                  "'gadfatreeorder':None,'utest':None,'p_aur':None," + \
                  "'indvarlist':None,'depvarlist':None,'plotp':None"

        if case == 0:
            exec(
                'self.data = {"raw":None,"proc":None,"exppath":None,"indlabels":None,' + \
                '"class":None,"label":None,"validation":None,"xaxis":[],' + \
                '"sampleidx":None,"variableidx":None,"rawtrunc":None,' + \
                '"proctrunc":None,' + varList + '}')

            # disable options on file menu
            mb = self.GetMenuBar()
            mb.Enable(wxID_PCMMNUFILESAVEEXP, False)
            mb.Enable(wxID_PCMMNUFILESAVEWS, False)
            mb.Enable(wxID_PCMMNUFILELOADWS, False)
        else:
            exec(
                'self.data = {"raw":self.data["raw"],"proc":self.data["raw"],' +
                '"exppath":self.data["exppath"],' +
                '"indlabels":self.data["indlabels"],' +
                '"class":self.data["class"],"label":self.data["label"],' +
                '"validation":self.data["validation"],"xaxis":self.data["xaxis"],' +
                '"sampleidx":self.data["sampleidx"],' +
                '"variableidx":self.data["variableidx"],' +
                '"rawtrunc":self.data["rawtrunc"],' +
                '"proctrunc":self.data["proctrunc"],' +
                varList + '}', locals(), globals())

        # for returning application to default settings
        self.plPreproc.Reset()
        self.plExpset.Reset(case)
        self.plPca.Reset()
        self.plDfa.reset()
        self.plCluster.reset()
        self.plPls.Reset()
        self.plGadfa.reset()
        self.plGapls.reset()
        self.plUnivariate.reset()

        # make data dictionary available to modules
        self.plExpset.depTitleBar.get_data(self.data)
        self.plExpset.indTitleBar.get_data(self.data)
        self.plPreproc.titleBar.get_data(self.data)
        self.plPca.titleBar.get_data(self.data)
        self.plCluster.titleBar.get_data(self.data)
        self.plDfa.titleBar.get_data(self.data)
        self.plPls.titleBar.get_data(self.data)
        self.plUnivariate.titleBar.get_data(self.data)
        self.plGadfa.titleBar.get_data(self.data)
        self.plGadfa.titleBar.get_exp_grid(self.plExpset.grdNames)
        self.plGadfa.titleBar.get_val_split_pc(
            self.plExpset.depTitleBar.spcGenMask.GetValue())
        self.plGapls.titleBar.get_data(self.data)
        self.plGapls.titleBar.get_val_split_pc(
            self.plExpset.depTitleBar.spcGenMask.GetValue())
        self.plGapls.titleBar.get_exp_grid(self.plExpset.grdNames)

    # noinspection PyUnresolvedReferences
    def xml_save(self, path, workspace, dtype=None):
        """

        dtype is either "new" (in which case workspace = "Default")
        or path to saved xml file

        """
        wx.BeginBusyCursor()

        proceed = 1
        if dtype == 'new':
            # build a tree structure
            root = ET.Element('pychem_305_experiment')
            # save raw data
            rawdata = ET.SubElement(root, 'rawdata')
            rawdata.set('key', 'array')
            rawdata.text = np.array2string(self.data['raw'], separator='\t')
            # save grdindlabels content
            indgrid = ET.SubElement(root, 'indgrid')
            # get data
            grd = self.get_grid(self.plExpset.grdIndLabels)
            # save grid
            indgrid.set("key", "indgrid")
            indgrid.text = grd
            # add workspace subelement
            workspaces = ET.SubElement(root, 'Workspaces')
            nws = 1

        else:
            tree = ET.ElementTree(file=dtype)
            root = tree.getroot()
            # delete old raw data and exp setup stuff
            for each in root:
                if each.tag in ['rawdata', 'indgrid']:
                    root.remove(each)
            # save raw data in case any user defined variables created
            rawdata = ET.SubElement(root, 'rawdata')
            rawdata.set('key', 'array')
            rawdata.text = np.array2string(self.data['raw'], separator='\t')

            # save grdindlabels content
            indgrid = ET.SubElement(root, 'indgrid')
            # get data
            grd = self.get_grid(self.plExpset.grdIndLabels)
            # save grid
            indgrid.set("key", "indgrid")
            indgrid.text = grd

            # get workspaces subelement
            workspaces = None
            for each in root:
                if each.tag == 'Workspaces':
                    workspaces = each

            # check that workspace name is not currently used
            msg = 'The workspace name provided is currently used\n'\
                  'for this experiment, please try again'
            for each in workspaces:
                if each.tag == workspace:
                    dlg = wx.MessageDialog(self, msg,
                                           'Error!', wx.OK | wx.ICON_ERROR)
                    try:
                        dlg.ShowModal()
                        proceed = 0
                    finally:
                        dlg.Destroy()

        # add new workspace
        if proceed == 1:
            try:
                cmd = workspace + ' = ET.SubElement(Workspaces, "' + workspace + '")'
                exec(cmd, locals(), globals())

                # save experiment setup stuff
                wxGrids = ['plExpset.grdNames', 'plExpset.grdIndLabels']
                cmd = 'grid = ET.SubElement(' + workspace + ', "grid")'
                exec(cmd, locals(), globals())

                for each in wxGrids:
                    name = each.split('.')[-1]
                    # get data
                    exec('g = self.get_grid(self.' + each + ')')
                    exec(name + ' = ET.SubElement(grid, "' + each + '")')
                    # save grid
                    exec(name + '.set("key", "grid")')
                    exec(name + '.text = g')

                # get preprocessing options
                if len(self.data['processlist']) != 0:
                    exec(
                        'ppOptions = ET.SubElement(' + workspace + ', "ppOptions")')
                    for each in self.data['processlist']:
                        item = ET.SubElement(ppOptions, "item")
                        item.set("key", "str")
                        item.text = each[0] + '|' + each[1]

                # save spin, string and boolean ctrl values
                # Controls = ET.SubElement(workspace, "Controls")
                exec('Controls = ET.SubElement(' + workspace + ',"Controls")')
                # spin controls
                spinCtrls = ['plGadfa.titleBar.spnGaScoreFrom',
                             'plGadfa.titleBar.spnGaScoreTo',
                             'plGadfa.optDlg.spnGaMaxFac',
                             'plGadfa.optDlg.spnGaMaxGen',
                             'plGadfa.optDlg.spnGaVarsFrom',
                             'plGadfa.optDlg.spnGaVarsTo',
                             'plGadfa.optDlg.spnGaNoInds',
                             'plGadfa.optDlg.spnGaNoRuns',
                             'plGadfa.optDlg.spnGaRepUntil',
                             'plGadfa.optDlg.spnResample',
                             'plGapls.titleBar.spnGaScoreFrom',
                             'plGapls.titleBar.spnGaScoreTo',
                             'plGapls.optDlg.spnGaMaxFac',
                             'plGapls.optDlg.spnGaMaxGen',
                             'plGapls.optDlg.spnGaVarsFrom',
                             'plGapls.optDlg.spnGaVarsTo',
                             'plGapls.optDlg.spnGaNoInds',
                             'plGapls.optDlg.spnGaNoRuns',
                             'plGapls.optDlg.spnGaRepUntil',
                             'plGapls.optDlg.spnResample',
                             'plPls.titleBar.spnPLSmaxfac',
                             'plPls.titleBar.spnPLSfactor1',
                             'plPls.titleBar.spnPLSfactor2',
                             'plPca.titleBar.spnNumPcs1',
                             'plPca.titleBar.spnNumPcs2',
                             'plPca.titleBar.spnPCAnum',
                             'plDfa.titleBar.spnDfaDfs',
                             'plDfa.titleBar.spnDfaScore1',
                             'plDfa.titleBar.spnDfaScore2',
                             'plDfa.titleBar.spnDfaPcs']

                for each in spinCtrls:
                    name = each.split('.')[len(each.split('.')) - 1]
                    exec(name + ' = ET.SubElement(Controls, "' + each + '")')
                    exec(name + '.set("key", "int")')
                    exec(name + '.text = str(self.' + each + '.GetValue())')

                # string controls
                stringCtrls = ['plExpset.indTitleBar.stcRangeFrom',
                               'plExpset.indTitleBar.stcRangeTo',
                               'plGadfa.optDlg.stGaXoverRate',
                               'plGadfa.optDlg.stGaMutRate',
                               'plGadfa.optDlg.stGaInsRate',
                               'plGapls.optDlg.stGaXoverRate',
                               'plGapls.optDlg.stGaMutRate',
                               'plGapls.optDlg.stGaInsRate']

                self.tbar = self.plExpset.indTitleBar
                for each in stringCtrls:
                    # quick fix!
                    if each == 'plExpset.indTitleBar.stcRangeFrom':
                        if self.tbar.stcRangeFrom.GetValue() in ['']:
                            self.tbar.stcRangeFrom.SetValue('1')
                    if each == 'plExpset.indTitleBar.stcRangeTo':
                        if self.tbar.stcRangeTo.GetValue() in ['']:
                            self.tbar.stcRangeTo.SetValue(
                                                 str(self.data['raw'].shape[1]))

                    name = each.split('.')[len(each.split('.')) - 1]

                    exec(name + ' = ET.SubElement(Controls, "' + each + '")')
                    exec(name + '.set("key", "str")')
                    exec(name + '.text = self.' + each + '.GetValue()')

                boolCtrls = ['plCluster.optDlg.rbKmeans',
                             'plCluster.optDlg.rbKmedian',
                             'plCluster.optDlg.rbKmedoids',
                             'plCluster.optDlg.rbHcluster',
                             'plCluster.optDlg.rbSingleLink',
                             'plCluster.optDlg.rbMaxLink',
                             'plCluster.optDlg.rbAvLink',
                             'plCluster.optDlg.rbCentLink',
                             'plCluster.optDlg.rbEuclidean',
                             'plCluster.optDlg.rbCorrelation',
                             'plCluster.optDlg.rbAbsCorr',
                             'plCluster.optDlg.rbUncentredCorr',
                             'plCluster.optDlg.rbAbsUncentCorr',
                             'plCluster.optDlg.rbSpearmans',
                             'plCluster.optDlg.rbKendalls',
                             'plCluster.optDlg.rbCityBlock',
                             'plCluster.optDlg.rbPlotName',
                             'plCluster.optDlg.rbPlotColours',
                             'plGadfa.optDlg.cbGaRepUntil',
                             'plGadfa.optDlg.cbGaMaxGen',
                             'plGadfa.optDlg.cbGaMut',
                             'plGadfa.optDlg.cbGaXover',
                             'plDfa.titleBar.cbDfaXval']

                for each in boolCtrls:
                    name = each.split('.')[-1]

                    cmd1 = name + ' = ET.SubElement(Controls, "' + each + '")'
                    exec(cmd1, locals(), globals())
                    cmd2 = name + '.set("key", "bool")'
                    exec(cmd2, locals(), globals())
                    cmd3 = name + '.text = str(self.' + each + '.GetValue())'
                    exec(cmd3, locals(), globals())
                    print('name_exec: ', name)

                # save choice options
                cmd = 'Choices = ET.SubElement(' + workspace + ',"Choices")'
                exec(cmd, locals(), globals())

                print('Choices: ', Choices)   # no defined

                choiceCtrls = ['plPls.titleBar.cbxData',
                               'plPca.titleBar.cbxPcaType',
                               'plPca.titleBar.cbxPreprocType',
                               'plPca.titleBar.cbxData',
                               'plDfa.titleBar.cbxData',
                               'plCluster.titleBar.cbxData',
                               'plGadfa.titleBar.cbxFeature1',
                               'plGadfa.titleBar.cbxFeature2',
                               'plGapls.titleBar.cbxFeature1',
                               'plGapls.titleBar.cbxFeature2',
                               'plGadfa.titleBar.cbxData',
                               'plGapls.titleBar.cbxData',
                               'plPls.titleBar.cbxType',
                               'plPls.titleBar.cbxPreprocType',
                               'plUnivariate.titleBar.cbxData',
                               'plUnivariate.titleBar.cbxVariable',
                               'plUnivariate.titleBar.cbxTest']

                for each in choiceCtrls:
                    name = each.split('.')[len(each.split('.')) - 1]
                    exec(name + ' = ET.SubElement(Choices, "' + each + '")')
                    exec(name + '.set("key", "int")')
                    exec(
                        name + '.text = str(self.' + each + '.GetCurrentSelection())')

                # any sp arrays
                scipyArrays = ['pcscores', 'pcloads', 'pcpervar', 'pceigs',
                               'plsloads',
                               'dfscores', 'dfloads', 'dfeigs', 'gadfachroms',
                               'gadfascores',
                               'gadfacurves', 'gaplschroms', 'gaplsscores',
                               'gaplscurves',
                               'gadfadfscores', 'gadfadfloads', 'gaplsplsloads',
                               'p_aur']
                cmd = 'Array = ET.SubElement(' + workspace + ', "Array")'
                exec(cmd, locals(), globals())
                # print('Array :', Array)

                for each in scipyArrays:
                    # print('*****  each in scipyArrays  ****** ')
                    # print(type(each))        # str
                    # print('each:', each)   # pcscores
                    # print(pcscores)        # not defined

                    try:
                        # save array elements
                        cmd = 'isthere = self.data["%s"]' % each
                        exec(cmd, locals(), globals())

                        if isthere is not None:
                            if each not in ['p_aur']:  # for numeric array
                                cmd1 = 'item%s = ET.SubElement(Array, "%s")' % (each, each)
                                cmd2 = 'arrData = np.array2string(' \
                                       'self.data["%s"], col_sep="\t")' % each
                                cmd3 = 'item%s.set("key", "array")' % each
                                cmd4 = 'item%s.text = arrData' % each

                                for cmd in [cmd1, cmd2, cmd3, cmd4]:
                                    exec(cmd, locals(), globals())

                            else:  # for string array type
                                cmd = 'target = self.data["%s"]' % each
                                exec(cmd, locals(), globals())
                                arrData = ''
                                for row in target:
                                    for element in row:
                                        arrData = arrData + element + '\t'
                                    arrData = arrData[0:-1] + '\n'

                                cmd1 = 'item' + each + ' = ET.SubElement(Array, "' + each + '")'
                                cmd2 = 'item' + each + '.set("key", "array")'
                                cmd3 = 'item' + each + '.text = arrData[0:len(arrData)-1]'

                                for cmd in [cmd1, cmd2, cmd3]:
                                    exec(cmd, locals(), globals())
                    except KeyError as e:
                        print(e)
                        continue

                # create run clustering flag
                cmd = 'Flags = ET.SubElement(' + workspace + ', "Flags")'
                exec(cmd, locals(), globals())
                # print(type(workspace))
                # print(workspace)
                # Flags = ET.SubElement(workspace, "Flags")

                doClustering = ET.SubElement(Flags, "doClustering")
                doClustering.set("key", "int")
                if (self.data['tree'] is not None) is True:
                    doClustering.text = '1'
                else:
                    doClustering.text = '0'

                # create run plsr flag global variable

                doPlsr = ET.SubElement(Flags, "doPlsr")
                doPlsr.set("key", "int")
                if self.data['plsloads'] is not None:
                    doPlsr.text = '1'
                else:
                    doPlsr.text = '0'

                # create plot univariate flag
                doUni = ET.SubElement(Flags, "doUni")
                doUni.set("key", "int")
                if self.data['plotp'] is not None:
                    doUni.text = str(self.data['plotp'])
                else:
                    doUni.text = '0'

                # wrap it in an ElementTree instance, and save as XML
                tree = ET.ElementTree(root)
                tree.write(path)

                # enable menu options
                self.mnuMain.Enable(wxID_PCMMNUFILESAVEWS, True)
                self.mnuMain.Enable(wxID_PCMMNUFILELOADWS, True)

            except Exception as error:
                msg = 'Unable to save under current name.\n\nCharacters ' + \
                      'such as "%", "&", "-", "+" can not be used for the workspace name'
                dlg = wx.MessageDialog(self, msg, 'Error!',
                                       wx.OK | wx.ICON_ERROR)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()
                raise

        # end busy cursor
        wx.EndBusyCursor()

    def xml_load(self, tree, workspace, dtype='new'):
        # load pychem experiments from saved xml files
        # if dtype == 'new':
        #   load raw data
        rdArray = []
        getRows = tree.findtext("rawdata")
        rows = getRows.split('\n')
        for each in rows:
            newRow = []
            items = each.split('\t')
            for item in items:
                if item not in ['', ' ']:
                    newRow.append(float(item))
            rdArray.append(newRow)

        self.data['raw'] = np.array(rdArray)
        self.data['proc'] = self.data['raw']

        # load grdindlabels
        gCont = tree.findtext("indgrid")
        rows = gCont.split('\n')
        r = len(rows) - 3
        c = len(rows[0].split('\t')) - 2

        # size grid accordingly
        exp_setup.ResizeGrids(self.plExpset.grdIndLabels, r, c - 1, dtype=-1)

        # add column labels
        cl = rows[0].split('\t')
        for col in range(1, len(cl)):
            self.plExpset.grdIndLabels.SetColLabelValue(col - 1, cl[col])
        for row in range(1, len(rows) - 1):
            items = rows[row].split('\t')
            self.plExpset.grdIndLabels.SetRowLabelValue(row - 1, items[0])
            for ci in range(1, len(items) - 1):
                self.plExpset.grdIndLabels.SetCellValue(row - 1, ci - 1,
                                                        items[ci])
        # set read only and grey background
        grid = self.plExpset.grdIndLabels
        for rx in range(1, grid.GetNumberRows()):
            if len(grid.GetRowLabelValue(rx).split('U')) > 1:
                grid.SetReadOnly(rx, 1, 1)
                grid.SetCellBackgroundColour(rx, 1, wx.LIGHT_GREY)
            else:
                break
        # set plot spn range
        self.plPreproc.titleBar.spcPlotSpectra.SetValue(1)
        self.plPreproc.titleBar.spcPlotSpectra.SetRange(1,
                                                        self.data['raw'].shape[
                                                            0])

        # load workspace
        getWsElements = tree.getroot().findall(''.join(("*/", workspace)))[
            0].getchildren()

        for each in getWsElements:
            if each.tag == 'grid':
                gName = each.getchildren()
                for item in gName:
                    gCont = item.text
                    rows = gCont.split('\n')
                    r = len(rows) - 3
                    c = len(rows[0].split('\t')) - 2
                    # size grid accordingly
                    if item.tag in ['plExpset.grdNames']:
                        cmd = 'exp_setup.ResizeGrids(self.%s, r, c-1, dtype=0)' % item.tag
                        exec(cmd, locals(), globals())
                        # add column labels
                        cl = rows[0].split('\t')
                        for col in range(1, len(cl)):
                            cmd =  'self.%s.SetColLabelValue(%i,"%s")' % (item.tag, col-1, cl[col])
                            exec(cmd, locals(), globals())
                        for row in range(1, len(rows) - 1):
                            items = rows[row].split('\t')
                            cmd = 'self.%s.SetRowLabelValue(%i,"%s")' % (item.tag, row-1, items[0])
                            exec(cmd, locals(), globals())
                            for ci in range(1, len(items) - 1):
                                cmd = 'self.%s.SetCellValue(%i,%i,"%s")' % (item.tag, row-1, ci-1, items[ci])
                                exec(cmd, locals(), globals())
                        # set read only and grey background
                        exec('grid = self.' + item.tag, locals(), globals())
                        for rx in range(1, grid.GetNumberRows()):
                            if len(grid.GetRowLabelValue(rx).split('U')) > 1:
                                grid.SetReadOnly(rx, 1, 1)
                                grid.SetCellBackgroundColour(rx, 1,
                                                             wx.LIGHT_GREY)
                            else:
                                break
                        # Validation column renderer for grdnames
                        #     if grid == self.plExpset.grdNames:
                        exp_setup.set_validation_editor(grid)

                    else:  # just set check boxes for grdindlabels
                        for row in range(1, len(rows) - 1):
                            items = rows[row].split('\t')
                            # spectral variable
                            if len(items[0].split('U')) == 1:
                                self.plExpset.grdIndLabels.SetCellValue(
                                    row - 1, 0, items[1])
                # set exp details
                self.get_experiment_details()

            # apply preprocessing steps
            if each.tag == 'ppOptions':
                getOpts = each.getchildren()
                for item in getOpts:
                    listItems = item.text.split('|')
                    self.data['processlist'].append(
                        [listItems[0], listItems[1]])
                    self.plPreproc.optDlg.lb.Append(listItems[0])
                self.plPreproc.titleBar.run_process_steps()

            # load ctrl values
            if each.tag == 'Controls':
                getVars = each.getchildren()
                for item in getVars:
                    exec('self.' + item.tag + '.SetValue(' + item.items()[0][
                        1] + '(' + item.text + '))')

            # load choice values
            if each.tag == 'Choices':
                getVars = each.getchildren()
                for item in getVars:
                    exec(
                        'self.' + item.tag + '.SetSelection(' + item.items()[0][
                            1] + '(' + item.text + '))')

            # load arrays
            if each.tag == 'Array':
                getArrays = each.getchildren()
                for array in getArrays:
                    try:
                        newArray = []
                        makeArray = array.text
                        makeArray = makeArray.split('\n')
                        for row in makeArray:
                            getRow = []
                            row = row.split('\t')
                            for element in row:
                                if array.tag not in ['p_aur']:
                                    getRow.append(float(element))
                                else:
                                    getRow.append(element)
                            newArray.append(getRow)
                        cmd = 'self.data["%s"] = np.array(newArray)' % array.tag
                        exec(cmd, locals(), globals())

                    except Exception:
                        cmd = 'self.data["%s"] = None' % array.tag
                        exec(cmd, locals(), globals())
                        raise

                # reload any plots
                self.reload_any_plots(getArrays)

            # load flags for re-running cluster
            # analysis, plsr and plotting univariate test output
            if each.tag == 'Flags':
                getVars = each.getchildren()
                for item in getVars:
                    if (item.tag == 'doClustering') & (
                            item.text == '1') is True:
                        self.plCluster.titleBar.run_cluster()
                    elif (item.tag == 'doPlsr') & (item.text == '1'):
                        self.plPls.titleBar.run_pls()
                    elif (item.tag == 'doUni') & (item.text != '0'):
                        if self.plUnivariate.titleBar.cbxData.GetSelection() == 0:
                            x = np.take(self.data['rawtrunc'],
                                        [self.plUnivariate.titleBar.cbxVariable.GetSelection()],
                                        1)
                        elif self.plUnivariate.titleBar.cbxData.GetSelection() == 1:
                            x = np.take(self.data['proctrunc'],
                                        [self.plUnivariate.titleBar.cbxVariable.GetSelection()]
                                        , 1)
                        if self.plUnivariate.titleBar.cbxTest.GetSelection() < 2:
                            self.data['utest'] = [
                                self.plUnivariate.titleBar.cbxTest.GetSelection(),
                                self.plUnivariate.titleBar.cbxData.GetSelection()]
                            self.plUnivariate._init_class_sizers()
                            self.plUnivariate.titleBar.plot_results(
                                x, float(item.text),
                                np.unique(np.array(self.data['label'])),
                                ['black', 'blue', 'red', 'cyan', 'green'],
                                psum=True)
                        else:
                            self.data['utest'] = None
                            self.plUnivariate._init_corr_sizers()
                            self.plUnivariate.titleBar.run_univariate()

        # unlock ctrls
        self.enable_ctrls()

    #    #gather data
    #    self.get_experiment_details()

    def reload_any_plots(self, getArrays):
        """"""
        pca_tb = self.plPca.titleBar
        dfa_tb = self.plDfa.titleBar
        gadfa_tb = self.plGadfa.titleBar

        klass = self.data['class']

        for array in getArrays:
            for i in ['pc', 'dfs', 'gadfa', 'gapls']:
                if len(array.tag.split(i)) > 1:
                    pceigs = len(self.data['pceigs'])
                    dfeigs = self.data['dfeigs'].shape[1]
                    if i == 'pc':
                        # set spn limits
                        pca_tb.spnNumPcs1.SetRange(1, pceigs)
                        pca_tb.spnNumPcs2.SetRange(1, pceigs)
                        # check for metadata & setup limits for dfa
                        if (sum(klass[:, 0]) != 0) and (klass is not None):
                            dfa_tb.spnDfaPcs.SetRange(2, pceigs)
                            dfa_tb.spnDfaDfs.SetRange(
                                1, len(np.unique(klass[:, 0])) - 1)
                        # plot pca results
                        pca_tb.plot_pca()
                    elif i == 'dfs':
                        # set spn limits
                        dfa_tb.spnDfaScore1.SetRange(1, dfeigs)
                        dfa_tb.spnDfaScore2.SetRange(1, dfeigs)
                        # plot results
                        dfa_tb.plot_dfa()

                    elif i == 'gadfa':
                        try:
                            gadfa_tb.create_ga_results_tree(
                                self.plGadfa.optDlg.treGaResults,
                                gacurves=self.data['gadfacurves'],
                                chroms=self.data['gadfachroms'],
                                varfrom=self.plGadfa.optDlg.spnGaVarsFrom.getValue(),
                                varto=self.plGadfa.optDlg.spnGaVarsTo.getValue(),
                                runs=self.plGadfa.optDlg.spnGaNoRuns.getValue() - 1)
                        except Exception:
                            raise
                            # continue
                    elif i == 'gapls':
                        try:
                            self.plGapls.titleBar.create_ga_results_tree(
                                self.plGapls.optDlg.treGaResults,
                                gacurves=self.data['gaplscurves'],
                                chroms=self.data['gaplschroms'],
                                varfrom=self.plGapls.optDlg.spnGaVarsFrom.getValue(),
                                varto=self.plGapls.optDlg.spnGaVarsTo.getValue(),
                                runs=self.plGapls.optDlg.spnGaNoRuns.getValue() - 1)
                        except Exception:
                            raise
                            # continue

    # noinspection PyMethodMayBeStatic
    def get_grid(self, grid):
        r = grid.GetNumberRows()
        c = grid.GetNumberCols()

        # get column labels
        gridout = '\t'
        for i in range(c):
            gridout = gridout + grid.GetColLabelValue(i) + '\t'
        gridout = gridout + '\n'
        # get grid contents & row labels
        for i in range(r):
            row = ''
            row = row + grid.GetRowLabelValue(i) + '\t'
            for j in range(c):
                row = row + grid.GetCellValue(i, j) + '\t'
            gridout = gridout + row + '\n'

        return gridout

    def get_experiment_details(self, case=0):
        if self.data['raw'] is not None:
            self.plExpset.grdNames.SetGridCursor(2, 0)
            self.plExpset.grdIndLabels.SetGridCursor(1, 0)
            # show busy egg timer
            wx.BeginBusyCursor()
            # count active samples and get index to sort by
            countActive, order = 0, []
            for i in range(2, self.plExpset.grdNames.GetNumberRows()):
                if self.plExpset.grdNames.GetCellValue(i, 0) == '1':
                    order.append(
                        int(self.plExpset.grdNames.GetRowLabelValue(i)))
                    countActive += 1
            index = np.argsort(order)
            # index for removing samples from analysis
            self.data['sampleidx'] = np.sort(np.array(order) - 1).tolist()
            # get col headings
            colHeads, self.data['class'], classCols = [], [], 0
            for i in range(1, self.plExpset.grdNames.GetNumberCols()):
                colHeads.append(self.plExpset.grdNames.GetColLabelValue(i))
                # get label vector
                if (self.plExpset.grdNames.GetCellValue(0, i) == 'Label') and \
                        (self.plExpset.grdNames.GetCellValue(1,
                                                             i) == '1') is True:
                    self.data['label'] = []
                    for j in range(2, self.plExpset.grdNames.GetNumberRows()):
                        if self.plExpset.grdNames.GetCellValue(j, 0) == '1':
                            # self.data['sampleidx'].append(j-2) #for removing samples from analysis
                            self.data['label'].append(
                                self.plExpset.grdNames.GetCellValue(j, i))

                    # reorder by index
                    # self.data['sampleidx'] = np.array(self.data['sampleidx'])[index].tolist()
                    self.data['label'] = np.array(self.data['label'])[
                        index].tolist()

                # get class vector
                if (self.plExpset.grdNames.GetCellValue(0, i) == 'Class') and \
                        (self.plExpset.grdNames.GetCellValue(1,
                                                             i) == '1') is True:

                    if self.data['class'] == []:
                        self.data['class'] = np.zeros((countActive, 1))
                    else:
                        self.data['class'] = np.concatenate((self.data['class'],
                                                             np.zeros((
                                                                 countActive,
                                                                 1))), 1)

                    countSample = 0
                    for j in range(2, self.plExpset.grdNames.GetNumberRows()):
                        if self.plExpset.grdNames.GetCellValue(j, 0) == '1':
                            try:
                                self.data['class'][
                                    countSample, classCols] = float(
                                    self.plExpset.grdNames.GetCellValue(j, i))
                            except ValueError:
                                pass
                            countSample += 1
                    classCols += 1

                    # reorder by index
                    self.data['class'] = self.data['class'][index, :]

                    # set max dfs that can be calculated
                    self.plDfa.titleBar.spnDfaDfs.SetRange(1, len(np.unique(
                        self.data['class'][:, 0])) - 1)
                #       self.plCluster.titleBar.dlg.spnNumClass.SetValue(max(self.data['class']))

                # get validation vector
                if (self.plExpset.grdNames.GetCellValue(0,
                                                        i) == 'Validation') and \
                        (self.plExpset.grdNames.GetCellValue(1,
                                                             i) == '1') is True:
                    self.data['validation'] = []
                    for j in range(2, self.plExpset.grdNames.GetNumberRows()):
                        if self.plExpset.grdNames.GetCellValue(j, 0) == '1':
                            try:
                                if self.plExpset.grdNames.GetCellValue(j,
                                                                       i) == 'Train':
                                    self.data['validation'].append(0)
                                elif self.plExpset.grdNames.GetCellValue(j,
                                                                         i) == 'Validation':
                                    self.data['validation'].append(1)
                                elif self.plExpset.grdNames.GetCellValue(j,
                                                                         i) == 'Test':
                                    self.data['validation'].append(2)
                                else:
                                    self.data['validation'].append(0)
                            except:
                                continue
                    self.data['validation'] = np.array(self.data['validation'])

                    # reorder by index
                    self.data['validation'] = self.data['validation'][index]

            # get x-axis labels/values
            self.plUnivariate.titleBar.cbxVariable.Clear()
            for j in range(1, self.plExpset.grdIndLabels.GetNumberCols()):
                if self.plExpset.grdIndLabels.GetCellValue(0, j) == '1':
                    self.data['variableidx'] = []
                    self.data['indlabelsfull'] = []
                    self.data['xaxisfull'] = []
                    for i in range(1,
                                   self.plExpset.grdIndLabels.GetNumberRows()):
                        val = self.plExpset.grdIndLabels.GetCellValue(i, j)
                        self.data['indlabelsfull'].append(val)
                        # for removing variables from analysis
                        if self.plExpset.grdIndLabels.GetCellValue(i, 0) == '1':
                            self.data['variableidx'].append(i - 1)
                            # append to list of variables for univariate testing
                            self.plUnivariate.titleBar.cbxVariable.Append(val)
                        # check for float or txt
                        try:
                            self.data['xaxisfull'].append(float(val))
                        except:
                            self.data['xaxisfull'].append(val)

            self.plUnivariate.titleBar.cbxVariable.SetSelection(0)

            self.data['xaxis'] = []
            for each in self.data['variableidx']:
                self.data['xaxis'].append(self.data['xaxisfull'][each])
            self.data['xaxis'] = np.array(self.data['xaxis'])[:, nax]
            num = 1
            for row in range(len(self.data['xaxis'])):
                try:
                    val = float(self.data['xaxis'][row, 0])
                except Exception:
                    raise
                    # num = 0

            # xaxis values not numeric therefore define xaxis range
            if num == 0:
                self.data['xaxisfull'] = np.arange(1, self.data['raw'].shape[
                    1] + 1)
                self.data['xaxis'] = np.take(self.data['xaxisfull'],
                                             self.data['variableidx'])[:, nax]

            self.data['indlabels'] = np.take(
                np.array(self.data['indlabelsfull']),
                self.data['variableidx']).tolist()

            #    #if any udv's have been calculated then possible that data array larger than
            #    #number of rows in indlabels
            #    nL = self.plExpset.grdIndLabels.GetNumberRows()-1
            #    rS = self.data['raw'].shape[1]
            #    if rS > nL:
            #        self.data['raw'] = self.data['raw'][:,rS-nL:rS]
            #        #run pre-processing funcs
            #        self.plPreproc.titleBar.run_process_steps()

            # remove any unwanted samples & variables, always following any preprocessing
            self.data['rawtrunc'] = np.take(self.data['raw'],
                                            self.data['variableidx'], 1)
            self.data['rawtrunc'] = np.take(self.data['rawtrunc'],
                                            self.data['sampleidx'], 0)

            if self.data['proc'] is not None:
                self.data['proctrunc'] = np.take(self.data['proc'],
                                                 self.data['variableidx'], 1)
                self.data['proctrunc'] = np.take(self.data['proctrunc'],
                                                 self.data['sampleidx'], 0)

            # change ga results lists
            try:
                self.plGapls.titleBar.create_ga_results_tree(
                    self.plGapls.optDlg.treGaResults,
                    gacurves=self.data['gaplscurves'],
                    chroms=self.data['gaplschroms'],
                    varfrom=self.plGapls.optDlg.spnGaVarsFrom.GetValue(),
                    varto=self.plGapls.optDlg.spnGaVarsTo.GetValue(),
                    runs=self.plGapls.optDlg.spnGaNoRuns.GetValue() - 1)
                self.plGapls.titleBar.btnExportGa.Enable(1)
            except TypeError:
                pass

            try:
                self.plGadfa.titleBar.create_ga_results_tree(
                    self.plGadfa.optDlg.treGaResults,
                    gacurves=self.data['gadfacurves'],
                    chroms=self.data['gadfachroms'],
                    varfrom=self.plGadfa.optDlg.spnGaVarsFrom.GetValue(),
                    varto=self.plGadfa.optDlg.spnGaVarsTo.GetValue(),
                    runs=self.plGadfa.optDlg.spnGaNoRuns.GetValue() - 1)
                self.plGadfa.titleBar.btnExportGa.Enable(1)
            except TypeError:
                pass

            try:  # set number of centroids for cluster analysis based on class structure
                self.plCluster.optDlg.spnNumClass.SetValue(
                    len(np.unique(self.data['class'][:, 0])))
            except Exception:
                raise
                # pass

            # check if necessary to do a soft reset
            if case == 0:
                if self.data['indvarlist'] is not None:
                    if (self.data['indvarlist'] != self.data['variableidx']) | \
                            (self.data['depvarlist'] != self.data[
                                'sampleidx']) is True:
                        msg = ('Changes have been made to the samples and/or ' +
                               'variables selected for analysis, the system must be reset.  Would you ' +
                               'like to continue without saving your current work?')
                        dlg = wx.MessageDialog(self, msg, caption='Attention!',
                                               style=wx.OK | wx.CANCEL | wx.CENTRE | wx.ICON_QUESTION)
                        if dlg.ShowModal() == wx.ID_OK:
                            # clear all modelling screens
                            self.reset(1)
                        else:
                            # set checkmarks to original
                            for ri in range(2,
                                            self.plExpset.grdNames.GetNumberRows()):
                                if ri - 2 in self.data['depvarlist']:
                                    self.plExpset.grdNames.SetCellValue(ri, 0,
                                                                        '1')
                                else:
                                    self.plExpset.grdNames.SetCellValue(ri, 0,
                                                                        '0')
                            for ri in range(1,
                                            self.plExpset.grdIndLabels.GetNumberRows()):
                                if ri - 1 in self.data['indvarlist']:
                                    self.plExpset.grdIndLabels.SetCellValue(ri,
                                                                            0,
                                                                            '1')
                                else:
                                    self.plExpset.grdIndLabels.SetCellValue(ri,
                                                                            0,
                                                                            '0')
                    else:
                        # save indices to compare to next
                        self.data['indvarlist'] = self.data['variableidx']
                        self.data['depvarlist'] = self.data['sampleidx']
                else:
                    # save indices to compare to next
                    self.data['indvarlist'] = self.data['variableidx']
                    self.data['depvarlist'] = self.data['sampleidx']
            else:
                # save indices to compare to next
                self.data['indvarlist'] = self.data['variableidx']
                self.data['depvarlist'] = self.data['sampleidx']

            # remove egg timer
            wx.EndBusyCursor()

    def enable_ctrls(self):
        self.plExpset.grdNames.Enable(1)
        self.plExpset.depTitleBar.btnImportMetaData.Enable(1)
        self.plExpset.depTitleBar.btnAddName.Enable(1)
        self.plExpset.depTitleBar.btnAddClass.Enable(1)
        self.plExpset.depTitleBar.btnAddMask.Enable(1)

        self.plExpset.grdIndLabels.Enable(1)
        self.plExpset.indTitleBar.btnImportIndVar.Enable(1)
        self.plExpset.indTitleBar.btnInsertRange.Enable(1)

        self.plPreproc.titleBar.btnPlot.Enable(1)
        self.plPreproc.titleBar.btnInteractive.Enable(1)
        self.plPreproc.titleBar.btnExportData.Enable(1)

        self.plPca.titleBar.btnRunPCA.Enable(1)

        self.plCluster.titleBar.btnRunClustering.Enable(1)

        self.plDfa.titleBar.btnRunDfa.Enable(1)

        self.plPls.titleBar.btnRunFullPls.Enable(1)

        self.plGadfa.titleBar.btnRunGa.Enable(1)

        self.plGapls.titleBar.btnRunGa.Enable(1)

        self.plUnivariate.titleBar.btnRunTest.Enable(1)

    def on_nb_main_nbook_page_changing(self, _):
        if self.nbMain.GetSelection() == 0:
            self.get_experiment_details()


class ImportConfirmDialog(wx.Dialog):
    """"""
    def __init__(self, parent, data, rows, cols):
        """"""
        wx.Dialog.__init__(self, id=wxID_WXICD,
                           name='wx.ImportDialog', parent=parent,
                           pos=(483, 225), size=(313, 319),
                           style=wx.DEFAULT_DIALOG_STYLE,
                           title='Import Complete')

        self._init_importconf_ctrls()

        # create grid
        self.grdSampleData.CreateGrid(data.shape[0], data.shape[1])

        # report rows x cols
        self.stRows.SetLabel(str(rows))
        self.stCols.SetLabel(str(cols))

        # populate grid
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                self.grdSampleData.SetCellValue(i, j, str(data[i, j]))

    def _init_importconf_ctrls(self):
        # generated method, don't edit

        self.SetClientSize((305, 285))
        self.SetToolTip('')
        self.Center(wx.BOTH)

        self.swLoadX = SashWindow(id=wxID_WXICDSWLOADX,
                                  name='swLoadX', parent=self,
                                  pos=(0, 0), size=(408, 352),
                                  style=wx.CLIP_CHILDREN | SW_3D)
        self.swLoadX.SetToolTip('')

        self.btnOK = wx.Button(id=wxID_WXICDBTNOK, label='OK',
                               name='btnOK', parent=self.swLoadX,
                               pos=(104, 248),
                               size=(104, 26), style=0)
        self.btnOK.Bind(wx.EVT_BUTTON, self.on_btn_ok,
                        id=wxID_WXICDBTNOK)

        self.grdSampleData = wx.grid.Grid(
            id=wxID_WXICDGRDSAMPLEDATA,
            name='grdSampleData', parent=self.swLoadX, pos=(16, 24),
            size=(272, 208), style=wx.DOUBLE_BORDER)
        self.grdSampleData.SetDefaultColSize(80)
        self.grdSampleData.SetDefaultRowSize(20)
        self.grdSampleData.Enable(True)
        self.grdSampleData.EnableEditing(False)
        self.grdSampleData.SetToolTip('')
        self.grdSampleData.SetColLabelSize(20)
        self.grdSampleData.SetRowLabelSize(20)

        self.staticText1 = wx.StaticText(
            id=wxID_WXICDSTATICTEXT1,
            label='Sample Data: ', name='staticText1', parent=self.swLoadX,
            pos=(16, 8), size=(67, 13), style=0)
        self.staticText1.SetToolTip('')

        self.stRows = wx.StaticText(id=wxID_WXICDSTROWS, label='0',
                                    name='stRows', parent=self.swLoadX,
                                    pos=(88, 8), size=(32, 13), style=0)

        self.staticText2 = wx.StaticText(
            id=wxID_WXICDSTATICTEXT2,
            label='rows by ', name='staticText2', parent=self.swLoadX,
            pos=(128, 8), size=(39, 13), style=0)

        self.stCols = wx.StaticText(id=wxID_WXICDSTCOLS, label='0',
                                    name='stCols', parent=self.swLoadX,
                                    pos=(176, 8), size=(32, 13), style=0)

        self.staticText4 = wx.StaticText(
            id=wxID_WXICDSTATICTEXT4,
            label='columns', name='staticText4', parent=self.swLoadX,
            pos=(216, 8), size=(39, 13), style=0)

    def on_btn_ok(self, _):
        self.Close()


class ImportDialog(wx.Dialog):
    """"""
    def __init__(self, parent):
        """"""
        wx.Dialog.__init__(self, id=-1, name='wx.ImportDialog',
                           parent=parent, pos=(496, 269), size=(400, 120),
                           style=wx.DEFAULT_DIALOG_STYLE,
                           title='Import X-data File')

        self._init_import_ctrls()
        self._init_plot_prop_sizers()
        self.chk_ok = 0

    def _init_coll_gbs_import_dialog(self, parent):
        parent.Add(self.fileBrowse, (0, 0), border=10, flag=wx.EXPAND,
                   span=(1, 4))
        # parent.AddSpacer((0, 0), (1, 0), border=10, flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.cbTranspose, (1, 1), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        parent.Add(self.btnCancel, (1, 2), border=10, flag=wx.EXPAND,
                   span=(1, 1))
        parent.Add(self.btnOK, (1, 3), border=10, flag=wx.EXPAND,
                   span=(1, 1))

    # noinspection PyMethodMayBeStatic
    def _init_coll_gbs_import_dialog_grobs(self, parent):
        parent.AddGrowableCol(0)
        parent.AddGrowableCol(1)
        parent.AddGrowableCol(2)
        parent.AddGrowableCol(3)

    def _init_plot_prop_sizers(self):
        self.gbsImportDialog = wx.GridBagSizer(hgap=4, vgap=4)
        self.gbsImportDialog.SetCols(4)
        self.gbsImportDialog.SetRows(2)

        self._init_coll_gbs_import_dialog(self.gbsImportDialog)
        self._init_coll_gbs_import_dialog_grobs(self.gbsImportDialog)

        self.SetSizer(self.gbsImportDialog)

    def _init_import_ctrls(self):
        # generated method, don't edit

        self.SetToolTip('')
        self.Center(wx.BOTH)

        self.btnOK = wx.Button(id=-1, label='OK', name='btnOK', parent=self,
                               pos=(0, 0), size=(85, 21), style=0)
        self.btnOK.Bind(wx.EVT_BUTTON, self.on_btn_ok)

        self.btnCancel = wx.Button(id=-1, label='Cancel', name='btnCancel',
                                   parent=self, pos=(0, 0), size=(85, 21),
                                   style=0)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.on_btn_cancel)

        self.fileBrowse = fbrowsebtn.FileBrowseButton(
            buttonText='Browse', dialogTitle='Choose a file', fileMask='*.*',
            id=-1, initialValue='', labelText='', parent=self, pos=(48, 40),
            size=(296, 48),  startDirectory='.', style=wx.TAB_TRAVERSAL,
            toolTip='Type filename or click browse to choose file')

        self.cbTranspose = wx.CheckBox(id=-1, label='transpose',
                                       name='cbTranspose', parent=self,
                                       pos=(160, 128), size=(73, 23), style=0)
        self.cbTranspose.SetValue(False)
        self.cbTranspose.SetToolTip('')

        self.staticLine = wx.StaticLine(id=-1, name='staticLine', parent=self,
                                        pos=(400, 5), size=(1, 2), style=0)

    def is_ok(self):
        return self.chk_ok

    def get_file(self):
        return self.fileBrowse.GetValue()

    def transpose(self):
        return self.cbTranspose.GetValue()

    def on_btn_cancel(self, _):
        self.chk_ok = 0
        self.Close()

    def on_btn_ok(self, _):
        self.chk_ok = 1
        self.Close()


class WorkspaceDialog(wx.Dialog):
    """"""
    def __init__(self, parent, filename='', dtype='Load'):
        """"""
        wx.Dialog.__init__(self, id=wxID_WXWSD,
                           name='wxWorkspaceDialog', parent=parent,
                           pos=(453, 245),
                           size=(374, 280),
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER |
                           wx.CAPTION | wx.MAXIMIZE_BOX,
                           title='Save Workspace')

        self.currentItem = None
        self.tree = None
        self.workspace = None

        # dtype to be either "load" or "save"
        self._init_savews_ctrls()

        # set some defaults
        self.SetTitle(dtype + ' Workspace')
        self.dtype = dtype
        self.filename = filename

        # need to populate listbox
        try:
            # check that it's a pychem file
            if self.filename not in ['']:
                self.tree = ET.ElementTree(file=self.filename)
                workspaces = self.tree.getroot().findall("Workspaces")[0]
                self.lbSaveWorkspace.SetColumnWidth(0, 260)
                for each in workspaces:
                    count = self.lbSaveWorkspace.GetItemCount()
                    index = self.lbSaveWorkspace.InsertItem(count, each.tag)
                    self.lbSaveWorkspace.SetItem(index, 0,
                                                 each.tag.replace('_', ' '))

                # behaviour for save dialog
                if dtype == 'Save':
                    self.btnCancel.Enable(0)
        except Exception:
            msg = 'Unable to load data - this is not a PyChem Experiment file'
            dlg = wx.MessageDialog(self, msg, 'Error!', wx.OK | wx.ICON_ERROR)
            try:
                dlg.ShowModal()
            finally:
                dlg.Destroy()
            raise

    # noinspection PyMethodMayBeStatic
    def _init_coll_lb_save_workspace(self, parent):
        """"""
        parent.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT,
                            heading='Workspaces', width=260)

    def _init_savews_ctrls(self):
        """"""
        self.SetClientSize((366, 246))
        self.SetToolTip('')
        self.SetAutoLayout(True)
        self.Center(wx.BOTH)

        self.btnDelete = wx.Button(id=wxID_WXWSDBTNDELETE,
                                   label='Delete', name='btnDelete',
                                   parent=self, pos=(16, 7),
                                   size=(70, 23), style=0)
        self.btnDelete.SetToolTip('')
        self.btnDelete.SetAutoLayout(True)
        self.btnDelete.Bind(wx.EVT_BUTTON, self.on_btn_delete,
                            id=wxID_WXWSDBTNDELETE)

        self.btnCancel = wx.Button(id=wxID_WXWSDBTNCANCEL,
                                   label='Cancel', name='btnCancel',
                                   parent=self, pos=(16, 40),
                                   size=(72, 23), style=0)
        self.btnCancel.SetToolTip('')
        self.btnCancel.SetAutoLayout(True)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.on_btn_cancel,
                            id=wxID_WXWSDBTNCANCEL)

        self.btnEdit = wx.Button(id=wxID_WXWSDBTNEDIT,
                                 label='Edit', name='btnEdit', parent=self,
                                 pos=(16, 152),
                                 size=(70, 23), style=0)
        self.btnEdit.SetToolTip('')
        self.btnEdit.SetAutoLayout(True)
        self.btnEdit.Show(False)
        self.btnEdit.Bind(wx.EVT_BUTTON, self.on_btn_edit,
                          id=wxID_WXWSDBTNEDIT)

        self.btnOK = wx.Button(id=wxID_WXWSDBTNOK, label='OK',
                               name='btnOK', parent=self, pos=(16, 71),
                               size=(72, 23), style=0)
        self.btnOK.SetToolTip('')
        self.btnOK.SetAutoLayout(True)
        self.btnOK.Show(True)
        self.btnOK.Bind(wx.EVT_BUTTON, self.on_btn_ok,
                        id=wxID_WXWSDBTNOK)

        self.lbSaveWorkspace = wx.ListCtrl(
            id=wxID_WXWSDLBSAVEWORKSPACE,
            name='lbSaveWorkspace', parent=self, pos=(96, 8),
            size=(264, 232),
            style=wx.LC_REPORT | wx.LC_SORT_ASCENDING | wx.LC_SINGLE_SEL)
        self.lbSaveWorkspace.SetConstraints(LayoutAnchors(self.lbSaveWorkspace,
                                                          True, True, True,
                                                          True))
        self.lbSaveWorkspace.SetAutoLayout(True)
        self.lbSaveWorkspace.SetToolTip('')
        self._init_coll_lb_save_workspace(self.lbSaveWorkspace)
        self.lbSaveWorkspace.Bind(wx.EVT_LEFT_DCLICK,
                                  self.on_lb_save_workspace_left_dclick)
        self.lbSaveWorkspace.Bind(wx.EVT_LIST_END_LABEL_EDIT,
                                  self.on_lb_save_workspace_end_label_edit,
                                  id=wxID_WXWSDLBSAVEWORKSPACE)
        self.lbSaveWorkspace.Bind(wx.EVT_LIST_ITEM_SELECTED,
                                  self.on_lb_save_workspace_selected,
                                  id=wxID_WXWSDLBSAVEWORKSPACE)

    def on_btn_delete(self, _):
        if self.lbSaveWorkspace.GetItemCount() > 1:
            # need to delete the workspace in the xml file
            WSnode = self.tree.getroot().findall("Workspaces")[0]
            workspaces = WSnode.getchildren()
            for each in workspaces:
                if each.tag == self.lbSaveWorkspace.GetItemText(
                        self.currentItem).replace(' ', '_'):
                    WSnode.remove(each)
            self.tree.write(self.filename)

            # delete listbox entry
            self.lbSaveWorkspace.DeleteItem(self.currentItem)

    def on_btn_cancel(self, _):
        self.Close()

    # noinspection PyMethodMayBeStatic
    def on_btn_edit(self, event):
        event.Skip()

    def get_workspace(self):
        if (self.filename not in ['']) & (self.workspace != 0) is True:
            return self.workspace.replace(' ', '_')
        else:
            return 0

    def append_workspace(self, ws):
        index = self.lbSaveWorkspace.InsertStringItem(sys.maxint, ws)
        self.lbSaveWorkspace.SetStringItem(index, 0, ws)

    def on_btn_ok(self, _):
        if self.dtype == 'Load':
            try:
                self.workspace = self.lbSaveWorkspace.GetItemText(
                    self.currentItem)
                self.Close()
            except Exception:
                dlg = wx.MessageDialog(self,
                                       'Please select a Workspace to load',
                                       'Error!', wx.OK | wx.ICON_ERROR)
                try:
                    dlg.ShowModal()
                finally:
                    dlg.Destroy()
                raise
        else:
            self.Close()

    def on_lb_save_workspace_left_dclick(self, event):
        # get workspace
        if self.dtype == 'Load':
            self.workspace = self.lbSaveWorkspace.GetItemText(self.currentItem)
            self.Close()
        else:
            event.Skip()

    def on_lb_save_workspace_end_label_edit(self, _):
        self.lbSaveWorkspace.SetColumnWidth(0, wx.LIST_AUTOSIZE)

    def on_lb_save_workspace_selected(self, event):
        self.currentItem = event.GetIndex()

    def get_tree(self):
        return self.tree

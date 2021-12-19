# .-----------------------------------------------------------------------------
# Name:        Dfa.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2007/05/22
# RCS-ID:      $Id: Dfa.py, v 1.16 2009/02/26 22:19:46 rmj01 Exp $
# Copyright:   (c) 2006
# Licence:     GNU General Public Licence
# -----------------------------------------------------------------------------

import wx
import wx.lib.buttons
import wx.lib.plot
from wx.lib.stattext import GenStaticText
import wx.lib.agw.buttonpanel as bp
from wx.lib.anchors import LayoutAnchors
from wx.lib.plot import PolyMarker, PlotGraphics, PolyLine


import scipy as sp
import numpy as np
import os
from mva import chemometrics as chemtrics
from commons import error_box

from mva.chemometrics import _index
from numpy import newaxis as nax
from Bio.Cluster import *
from Pca import plotLine
from Pca import plotStem
from Pca import plotText
from Pca import plotScores
from Pca import plotLoads
from Pca import SetButtonState
from Pca import MyPlotCanvas

[wxID_DFA, wxID_DFABTNEXPDFA, wxID_DFABTNGOGADFA, wxID_DFABTNGOPCA,
 wxID_DFAbtnRunDfa, wxID_DFACBDFAXVAL, wxID_DFAPLCDFAEIGS,
 wxID_DFAPLCDFAERROR, wxID_DFAPLCDFALOADSV, wxID_DFAPLCDFASCORES,
 wxID_DFAPLDFALOADS, wxID_DFAPLDFASCORES, wxID_DFARBDFAPROCDATA,
 wxID_DFARBDFARAWDATA, wxID_DFARBDFAUSEPCSCORES, wxID_DFASASHWINDOW5,
 wxID_DFASPNDFABILOAD1, wxID_DFASPNDFABILOAD2, wxID_DFASPNDFADFS,
 wxID_DFASPNDFAPCS, wxID_DFASPNDFASCORE1, wxID_DFASPNDFASCORE2,
 wxID_DFASTATICTEXT2, wxID_DFASTATICTEXT23, wxID_DFASTATICTEXT24,
 wxID_DFASTATICTEXT28, wxID_DFASTATICTEXT3, wxID_DFASTATICTEXT4,
 wxID_DFASTATICTEXT5, wxID_DFASTATICTEXT7, wxID_DFASTATICTEXT8,
 wxID_DFASTDFA6, wxID_DFASTDFA7,
 ] = [wx.NewId() for _init_ctrls in range(33)]


class Dfa(wx.Panel):
    # discriminant function analysis
    def _init_coll_grsDfa_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.plcDFAscores, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.plcDfaLoadsV, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.plcDfaCluster, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.plcDFAeigs, 0, border=0, flag=wx.EXPAND)

    def _init_coll_bxsDfa1_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.bxsDfa2, 1, border=0, flag=wx.EXPAND)

    def _init_coll_bxsDfa2_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.titleBar, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.grsDfa, 1, border=0, flag=wx.EXPAND)

    def _init_sizers(self):
        # generated method, don't edit
        self.bxsDfa1 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.bxsDfa2 = wx.BoxSizer(orient=wx.VERTICAL)

        self.grsDfa = wx.GridSizer(cols=2, hgap=2, rows=2, vgap=2)

        self._init_coll_bxsDfa1_Items(self.bxsDfa1)
        self._init_coll_bxsDfa2_Items(self.bxsDfa2)
        self._init_coll_grsDfa_Items(self.grsDfa)

        self.SetSizer(self.bxsDfa1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_DFA, name='Dfa', parent=prnt,
                          pos=wx.Point(47, 118), size=wx.Size(796, 460),
                          style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(788, 426))
        self.SetToolTip('')
        self.SetAutoLayout(True)
        self.prnt = prnt

        self.plcDFAscores = MyPlotCanvas(
            id=-1, name='plcDFAscores', parent=self, pos=wx.Point(0, 24),
            size=wx.Size(24, 20), style=0, toolbar=self.prnt.parent.tbMain)
        self.plcDFAscores.fontSizeTitle = 10
        self.plcDFAscores.fontSizeAxis = 8
        self.plcDFAscores.enableZoom = True
        self.plcDFAscores.enableLegend = True
        self.plcDFAscores.SetToolTip('')
        self.plcDFAscores.SetAutoLayout(True)
        self.plcDFAscores.SetConstraints(
            LayoutAnchors(self.plcDFAscores, True, True, True, True))
        self.plcDFAscores.fontSizeLegend = 8

        self.plcDfaLoadsV = MyPlotCanvas(id=-1, name='plcDfaLoadsV',
                                         parent=self, pos=wx.Point(-5, 24),
                                         size=wx.Size(24, 20), style=0,
                                         toolbar=self.prnt.parent.tbMain)
        self.plcDfaLoadsV.fontSizeAxis = 8
        self.plcDfaLoadsV.fontSizeTitle = 10
        self.plcDfaLoadsV.enableZoom = True
        self.plcDfaLoadsV.enableLegend = True
        self.plcDfaLoadsV.SetToolTip('')
        self.plcDfaLoadsV.SetAutoLayout(True)
        self.plcDfaLoadsV.SetConstraints(
            LayoutAnchors(self.plcDfaLoadsV, True, True, True, True))
        self.plcDfaLoadsV.fontSizeLegend = 8

        self.plcDFAeigs = MyPlotCanvas(
            id=-1, name='plcDFAeigs', parent=self, pos=wx.Point(483, 214),
            size=wx.Size(305, 212), style=0, toolbar=self.prnt.parent.tbMain)
        self.plcDFAeigs.fontSizeAxis = 8
        self.plcDFAeigs.fontSizeTitle = 10
        self.plcDFAeigs.enableZoom = True
        self.plcDFAeigs.SetToolTip('')
        self.plcDFAeigs.SetAutoLayout(True)
        self.plcDFAeigs.SetConstraints(LayoutAnchors(self.plcDFAeigs, False,
                                                     True, False, True))
        self.plcDFAeigs.fontSizeLegend = 8

        self.plcDfaCluster = MyPlotCanvas(
            id=-1, name='plcDfaCluster', parent=self, pos=wx.Point(176, 214),
            size=wx.Size(305, 212), style=0, toolbar=self.prnt.parent.tbMain)
        self.plcDfaCluster.fontSizeAxis = 8
        self.plcDfaCluster.fontSizeTitle = 10
        self.plcDfaCluster.enableZoom = True
        self.plcDfaCluster.enableLegend = False
        self.plcDfaCluster.SetToolTip('')
        self.plcDfaCluster.SetAutoLayout(True)
        self.plcDfaCluster.xSpec = 'none'
        self.plcDfaCluster.ySpec = 'none'
        self.plcDfaCluster.SetConstraints(
            LayoutAnchors(self.plcDfaCluster, True,
                          True, False, True))
        self.plcDfaCluster.fontSizeLegend = 8

        self.titleBar = TitleBar(self, id=-1,
                                 text="Discriminant Function Analysis",
                                 style=bp.BP_USE_GRADIENT,
                                 alignment=bp.BP_ALIGN_LEFT)

        self._init_sizers()

    def __init__(self, parent, id_, pos, size, style, name):
        self._init_ctrls(parent)

        self.parent = parent

    def reset(self):
        self.titleBar.spnDfaScore1.Enable(0)
        self.titleBar.spnDfaScore2.Enable(0)
        self.titleBar.spnDfaScore1.SetValue(1)
        self.titleBar.spnDfaScore2.SetValue(2)

        objects = {'plcDFAeigs': ['Eigenvalues', 'Discriminant Function',
                                  'Eigenvalue'],
                   'plcDfaCluster': ['Hierarchical Cluster Analysis',
                                     'Distance', 'Sample'],
                   'plcDFAscores': ['DFA Scores', 't[1]', 't[2]'],
                   'plcDfaLoadsV': ['DFA Loading', 'w[1]', 'w[2]']}

        curve = PolyLine([[0, 0], [1, 1]],
                         colour='white', width=1, style=wx.TRANSPARENT)

        for each in objects.keys():
            cmd = ('self.%s.Draw(wx.lib.plot.PlotGraphics([curve], '
                   'objects["%s"][0], objects["%s"][1], objects["%s"][2]))')
            exec(cmd % (each, each, each, each))


class TitleBar(bp.ButtonPanel):
    def _init_btnpanel_ctrls(self, prnt):
        bp.ButtonPanel.__init__(self, parent=prnt, id=-1,
                                text="Discriminant Function Analysis",
                                agwStyle=bp.BP_USE_GRADIENT,
                                alignment=bp.BP_ALIGN_LEFT)

        chcs = ['PC Scores', 'PLS Scores', 'Raw spectra', 'Processed spectra']
        self.cbxData = wx.Choice(choices=chcs, id=-1, name='cbxData',
                                 parent=self, pos=wx.Point(118, 21),
                                 size=wx.Size(100, 23), style=0)

        self.cbxData.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.on_cbx_data, id=self.cbxData.GetId())

        self.btnRunDfa = bp.ButtonInfo(self, -1,
                                       wx.Bitmap(os.path.join('bmp', 'run.png'),
                                                 wx.BITMAP_TYPE_PNG),
                                       kind=wx.ITEM_NORMAL, shortHelp='Run DFA',
                                       longHelp='Run Discriminant Function Analysis')
        self.btnRunDfa.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.on_run_dfa, id=self.btnRunDfa.GetId())

        self.spnDfaPcs = wx.SpinCtrl(id=-1, initial=1, max=100, min=3,
                                     name='spnDfaPcs', parent=self,
                                     pos=wx.Point(104, 104),
                                     size=wx.Size(46, 23),
                                     style=wx.SP_ARROW_KEYS)
        self.spnDfaPcs.SetValue(3)
        self.spnDfaPcs.SetToolTip('')

        self.spnDfaDfs = wx.SpinCtrl(id=-1, initial=1, max=100, min=2,
                                     name='spnDfaDfs', parent=self,
                                     pos=wx.Point(57, 168),
                                     size=wx.Size(46, 23),
                                     style=wx.SP_ARROW_KEYS)
        self.spnDfaDfs.SetValue(2)
        self.spnDfaDfs.SetToolTip('')

        self.cbDfaXval = wx.CheckBox(id=-1, label='',
                                     name='cbDfaXval', parent=self,
                                     pos=wx.Point(16, 216),
                                     size=wx.Size(14, 13), style=0)
        self.cbDfaXval.SetValue(False)
        self.cbDfaXval.SetToolTip('')

        self.btnExpDfa = bp.ButtonInfo(self, -1, wx.Bitmap(
            os.path.join('bmp', 'export.png'), wx.BITMAP_TYPE_PNG),
                                       kind=wx.ITEM_NORMAL,
                                       shortHelp='Export DFA Results',
                                       longHelp='Export DFA Results')
        self.btnExpDfa.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.on_exp_dfa, id=self.btnExpDfa.GetId())

        self.spnDfaScore1 = wx.SpinCtrl(id=-1, initial=1, max=100, min=1,
                                        name='spnDfaScore1', parent=self,
                                        pos=wx.Point(199,
                                                     4), size=wx.Size(46, 23),
                                        style=wx.SP_ARROW_KEYS)
        self.spnDfaScore1.SetToolTip('')
        self.spnDfaScore1.Enable(0)
        self.spnDfaScore1.Bind(wx.EVT_SPINCTRL, self.on_spn_dfa_score1,
                               id=-1)

        self.spnDfaScore2 = wx.SpinCtrl(id=-1, initial=1, max=100, min=1,
                                        name='spnDfaScore2', parent=self,
                                        pos=wx.Point(287,
                                                     4), size=wx.Size(46, 23),
                                        style=wx.SP_ARROW_KEYS)
        self.spnDfaScore2.SetToolTip('')
        self.spnDfaScore2.Enable(0)
        self.spnDfaScore2.Bind(wx.EVT_SPINCTRL, self.on_spn_dfa_score2,
                               id=-1)

    def __init__(self, parent, id, text, style, alignment):

        self._init_btnpanel_ctrls(parent)
        self.parent = parent
        self.create_buttons()

    def create_buttons(self):
        style = wx.TRANSPARENT_WINDOW
        self.Freeze()
        self.SetProperties()

        self.AddControl(self.cbxData)
        self.AddControl(GenStaticText(self, -1, 'No. LVs', style=style))
        self.AddControl(self.spnDfaPcs)
        self.AddControl(GenStaticText(self, -1, 'No. DFs', style=style))
        self.AddControl(self.spnDfaDfs)
        self.AddControl(GenStaticText(self, -1, 'Cross validate?', style=style))
        self.AddControl(self.cbDfaXval)
        self.AddSeparator()
        self.AddControl(GenStaticText(self, -1, 'DF ', style=style))
        self.AddControl(self.spnDfaScore1)
        self.AddControl(GenStaticText(self, -1, ' vs. ', style=style))
        self.AddControl(self.spnDfaScore2)
        self.AddSeparator()
        self.AddButton(self.btnRunDfa)
        self.AddSeparator()
        self.AddButton(self.btnExpDfa)

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

    def get_data(self, data):
        self.data = data

    def on_cbx_data(self, _):
        if self.cbxData.GetSelection() == 0:
            if self.data['pcscores'] is not None:
                self.spnDfaPcs.SetRange(1, self.data['pcscores'].shape[1])
                if self.data['pcscores'].shape[1] < self.spnDfaPcs.GetValue():
                    self.spnDfaPcs.SetValue(self.data['pcscores'].shape[1])
        elif self.cbxData.GetSelection() == 1:
            if self.data['plst'] is not None:
                self.spnDfaPcs.SetRange(1, self.data['plst'].shape[1])
                if self.data['plst'].shape[1] < self.spnDfaPcs.GetValue():
                    self.spnDfaPcs.SetValue(self.data['plst'].shape[1])

    def on_run_dfa(self, _):
        try:
            # run discriminant function analysis
            if self.cbxData.GetSelection() == 0:
                xdata = self.data['pcscores'][:, 0:self.spnDfaPcs.GetValue()]
                loads = self.data['pcloads']
            elif self.cbxData.GetSelection() == 1:
                xdata = self.data['plst'][:, 0:self.spnDfaPcs.GetValue()]
                loads = np.transpose(self.data['plsloads'])
            elif self.cbxData.GetSelection() == 2:
                xdata = self.data['rawtrunc']
            elif self.cbxData.GetSelection() == 3:
                xdata = self.data['proctrunc']

            # if using xval
            # select data
            if self.parent.prnt.prnt.plPca.titleBar.cbxData.GetSelection() == 0:
                xvaldata = self.data['rawtrunc']
            elif self.parent.prnt.prnt.plPca.titleBar.cbxData.GetSelection() == 1:
                xvaldata = self.data['proctrunc']

            # select pca method
            if self.parent.prnt.prnt.plPca.titleBar.cbxPcaType.GetSelection() == 0:
                self.data['niporsvd'] = 'nip'
            elif self.parent.prnt.prnt.plPca.titleBar.cbxPcaType.GetSelection() == 1:
                self.data['niporsvd'] = 'svd'

            # check appropriate number of pcs/dfs
            if self.spnDfaPcs.GetValue() <= self.spnDfaDfs.GetValue():
                self.spnDfaDfs.SetValue(self.spnDfaPcs.GetValue() - 1)

            # check for pca preproc method
            if self.parent.prnt.prnt.plPca.titleBar.cbxPreprocType.GetSelection() == 0:
                self.data['pcatype'] = 'covar'
            elif self.parent.prnt.prnt.plPca.titleBar.cbxPreprocType.GetSelection() == 1:
                self.data['pcatype'] = 'corr'

            # Reset controls
            self.spnDfaScore1.Enable(1)
            self.spnDfaScore2.Enable(1)
            self.spnDfaScore1.SetRange(1, self.spnDfaDfs.GetValue())
            self.spnDfaScore1.SetValue(1)
            self.spnDfaScore2.SetRange(1, self.spnDfaDfs.GetValue())
            self.spnDfaScore2.SetValue(2)
            self.btnExpDfa.Enable(1)

            if not self.cbDfaXval.GetValue():
                # just a fix to recover original loadings when using PC-DFA
                if self.cbxData.GetSelection() > 1:
                    scores, loads, eigs, _ = \
                        chemtrics.cva(xdata, self.data['class'][:, 0],
                                      self.spnDfaDfs.GetValue())
                else:
                    scores, _, eigs, loads = \
                        chemtrics.cva(xdata, self.data['class'][:, 0],
                                      self.spnDfaDfs.GetValue(),
                                      loads[0:self.spnDfaPcs.GetValue(), :])

            elif self.cbDfaXval.GetValue():
                if self.cbxData.GetSelection() > 1:
                    # run dfa
                    scores, loads, eigs = \
                        chemtrics.dfa_xvalraw(xdata, self.data['class'][:, 0],
                                              self.data['validation'],
                                              self.spnDfaDfs.GetValue())

                elif self.cbxData.GetSelection() == 0:
                    # run pc-dfa
                    if self.data['niporsvd'] in ['nip']:
                        scores, loads, eigs = \
                            chemtrics.dfa_xval_pca(xvaldata, 'NIPALS',
                                                   self.spnDfaPcs.GetValue(),
                                                   self.data['class'][:, 0],
                                                   self.data['validation'],
                                                   self.spnDfaDfs.GetValue(),
                                                   ptype=self.data['pcatype'])

                    elif self.data['niporsvd'] in ['svd']:
                        scores, loads, eigs = \
                            chemtrics.dfa_xval_pca(xvaldata, 'SVD',
                                                   self.spnDfaPcs.GetValue(),
                                                   self.data['class'][:, 0],
                                                   self.data['validation'],
                                                   self.spnDfaDfs.GetValue(),
                                                   ptype=self.data['pcatype'])

                elif self.cbxData.GetSelection() == 1:
                    # run pls-dfa
                    scores, loads, eigs = \
                        chemtrics.dfa_xval_pls(self.data['plst'],
                                               self.data['plsloads'],
                                               self.spnDfaPcs.GetValue(),
                                               self.data['class'][:, 0],
                                               self.data['validation'],
                                               self.spnDfaDfs.GetValue())

            self.data['dfscores'] = scores
            self.data['dfloads'] = loads
            self.data['dfeigs'] = eigs

            # plot dfa results
            self.plot_dfa()

        except Exception as error:
            error_box(self, '%s' % str(error))
            raise

    def on_exp_dfa(self, _):
        dlg = wx.FileDialog(self, "Choose a file", ".", "",
                            "Any files (*.*)|*.*", wx.SAVE)
        try:
            if dlg.ShowModal() == wx.ID_OK:
                saveFile = dlg.GetPath()
                scores_txt = np.array2string(self.data['dfscores'], separator='\t')
                loads_txt = np.array2string(self.data['dfloads'], separator='\t')
                eigs_txt = np.array2string(self.data['dfeigs'], separator='\t')

                out = '#DISCRIMINANT_FUNCTION_SCORES\n' + scores_txt + '\n' + \
                      '#DISCRIMINANT_FUNCTION_LOADINGS\n' + loads_txt + '\n' + \
                      '#EIGENVALUES\n' + eigs_txt

                f = open(saveFile, 'w')
                f.write(out)
                f.close()
        finally:
            dlg.Destroy()

    def on_spn_dfa_score1(self, _):
        self.plot_dfa()
        SetButtonState(self.spnDfaScore1.GetValue(),
                       self.spnDfaScore2.GetValue(),
                       self.parent.prnt.prnt.tbMain)

    def on_spn_dfa_score2(self, event):
        self.plot_dfa()
        SetButtonState(self.spnDfaScore1.GetValue(),
                       self.spnDfaScore2.GetValue(),
                       self.parent.prnt.prnt.tbMain)

    def plot_dfa(self):
        # plot scores
        plotScores(self.parent.plcDFAscores, self.data['dfscores'],
                   cl=self.data['class'][:, 0],
                   labels=self.data['label'],
                   validation=self.data['validation'],
                   col1=self.spnDfaScore1.GetValue() - 1,
                   col2=self.spnDfaScore2.GetValue() - 1,
                   title='DFA Scores',
                   xLabel='t[' + str(self.spnDfaScore1.GetValue()) + ']',
                   yLabel='t[' + str(self.spnDfaScore2.GetValue()) + ']',
                   xval=self.cbDfaXval.GetValue(),
                   symb=self.parent.prnt.prnt.tbMain.tbSymbols.GetValue(),
                   text=self.parent.prnt.prnt.tbMain.tbPoints.GetValue(),
                   pconf=self.parent.prnt.prnt.tbMain.tbConf.GetValue(),
                   usecol=[], usesym=[])

        # plot loadings
        if self.cbxData.GetSelection() == 0:
            label = 'PC-DFA Loadings'
        else:
            label = 'DFA Loadings'

        if self.spnDfaScore1.GetValue() != self.spnDfaScore2.GetValue():
            plotLoads(self.parent.plcDfaLoadsV, self.data['dfloads'],
                      xaxis=self.data['indlabels'],
                      col1=self.spnDfaScore1.GetValue() - 1,
                      col2=self.spnDfaScore2.GetValue() - 1, title=label,
                      xLabel='w[' + str(self.spnDfaScore1.GetValue()) + ']',
                      yLabel='w[' + str(self.spnDfaScore2.GetValue()) + ']',
                      type=self.parent.prnt.prnt.tbMain.GetLoadPlotIdx(),
                      usecol=[], usesym=[])

        else:
            idx = self.spnDfaScore1.GetValue() - 1
            plotLine(self.parent.plcDfaLoadsV,
                     np.transpose(self.data['dfloads']),
                     xaxis=self.data['xaxis'], tit=label, rownum=idx,
                     xLabel='Variable', yLabel='w[' + str(idx + 1) + ']',
                     wdth=1, ledge=[], type='single')

        # calculate and plot hierarchical clustering using euclidean distance
        # get average df scores for each class
        mS, mSn = [], []
        for each in np.unique(self.data['class'][:, 0]):
            mS.append(np.mean(
                self.data['dfscores'][self.data['class'][:, 0] == each, :], 0))
            mSn.append(
                self.data['label'][_index(self.data['class'][:, 0], each)[0]])

        tree = cluster.treecluster(data=mS, method='m', dist='e')
        tree, order = self.parent.prnt.prnt.plCluster.titleBar.treestructure(
            tree,
            np.arange(len(tree) + 1))
        self.parent.prnt.prnt.plCluster.titleBar.drawTree(
            self.parent.plcDfaCluster,
            tree, order, mSn, tit='Hierarchical Cluster Analysis',
            xL='Euclidean Distance', yL='Sample')

        # Plot eigs
        self.DrawDfaEig = plotLine(self.parent.plcDFAeigs, self.data['dfeigs'],
                                   xaxis=np.arange(1, self.data['dfeigs'].shape[
                                       1] + 1)[:, nax], rownum=0,
                                   tit='Eigenvalues',
                                   xLabel='Discriminant Function',
                                   yLabel='Eigenvalues', wdth=3, type='single',
                                   ledge=[])

        # make sure ctrls enabled
        self.spnDfaScore1.Enable(True)
        self.spnDfaScore2.Enable(True)
        self.btnExpDfa.Enable(True)

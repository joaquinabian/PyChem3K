# .-----------------------------------------------------------------------------
# Name:        dfa.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2007/05/22
# RCS-ID:      $Id: dfa.py, v 1.16 2009/02/26 22:19:46 rmj01 Exp $
# Copyright:   (c) 2006
# Licence:     GNU General Public Licence
# -----------------------------------------------------------------------------

import os
import numpy as np
from numpy import newaxis as nax
from Bio.Cluster import treecluster

import wx
import wx.lib.buttons
import wx.lib.agw.buttonpanel as bp
from wx.lib.stattext import GenStaticText
from wx.lib.anchors import LayoutAnchors
from wx.lib.plot import PolyLine
from wx.lib.plot import PlotGraphics

from commons import error_box
from mva import chemometrics as chemtrics
# noinspection PyProtectedMember
from mva.chemometrics import _index
from pca import plot_line
from pca import plot_scores
from pca import plot_loads
from pca import set_btn_state
from pca import MyPlotCanvas

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

# To remove inspection unused. Used on exec
_ = PlotGraphics

class Dfa(wx.Panel):
    """Discriminant function analysis.

    """
    def __init__(self, parent, id_, pos, size, style, name):
        """"""
        wx.Panel.__init__(self, id=wxID_DFA, name='Dfa', parent=parent,
                          pos=(47, 118), size=(796, 460),
                          style=wx.TAB_TRAVERSAL)

        _, _, _, _, _ = id_, pos, size, style, name

        self.parent = parent
        self._init_ctrls()
        self._init_sizers()

    def _init_ctrls(self):
        """"""
        self.SetClientSize((788, 426))
        self.SetToolTip('')
        self.SetAutoLayout(True)

        self.plcDFAscores = MyPlotCanvas(id_=-1, name='plcDFAscores',
                                         parent=self, pos=(0, 24),
                                         size=(24, 20), style=0,
                                         toolbar=self.parent.parent.tbMain)
        self.plcDFAscores.fontSizeTitle = 10
        self.plcDFAscores.fontSizeAxis = 8
        self.plcDFAscores.enableZoom = True
        self.plcDFAscores.enableLegend = True
        self.plcDFAscores.SetToolTip('')
        self.plcDFAscores.SetAutoLayout(True)
        self.plcDFAscores.SetConstraints(
            LayoutAnchors(self.plcDFAscores, True, True, True, True))
        self.plcDFAscores.fontSizeLegend = 8

        self.plcDfaLoadsV = MyPlotCanvas(id_=-1, name='plcDfaLoadsV',
                                         parent=self, pos=(-5, 24),
                                         size=(24, 20), style=0,
                                         toolbar=self.parent.parent.tbMain)
        self.plcDfaLoadsV.fontSizeAxis = 8
        self.plcDfaLoadsV.fontSizeTitle = 10
        self.plcDfaLoadsV.enableZoom = True
        self.plcDfaLoadsV.enableLegend = True
        self.plcDfaLoadsV.SetToolTip('')
        self.plcDfaLoadsV.SetAutoLayout(True)
        self.plcDfaLoadsV.SetConstraints(
            LayoutAnchors(self.plcDfaLoadsV, True, True, True, True))
        self.plcDfaLoadsV.fontSizeLegend = 8

        self.plcDFAeigs = MyPlotCanvas(id_=-1, name='plcDFAeigs', parent=self,
                                       pos=(483, 214), size=(305, 212), style=0,
                                       toolbar=self.parent.parent.tbMain)
        self.plcDFAeigs.fontSizeAxis = 8
        self.plcDFAeigs.fontSizeTitle = 10
        self.plcDFAeigs.enableZoom = True
        self.plcDFAeigs.SetToolTip('')
        self.plcDFAeigs.SetAutoLayout(True)
        self.plcDFAeigs.SetConstraints(LayoutAnchors(self.plcDFAeigs, False,
                                                     True, False, True))
        self.plcDFAeigs.fontSizeLegend = 8

        self.plcDfaCluster = MyPlotCanvas(id_=-1, name='plcDfaCluster',
                                          parent=self, pos=(176, 214),
                                          size=(305, 212), style=0,
                                          toolbar=self.parent.parent.tbMain)
        self.plcDfaCluster.fontSizeAxis = 8
        self.plcDfaCluster.fontSizeTitle = 10
        self.plcDfaCluster.enableZoom = True
        self.plcDfaCluster.enableLegend = False
        self.plcDfaCluster.SetToolTip('')
        self.plcDfaCluster.SetAutoLayout(True)
        self.plcDfaCluster.xSpec = 'none'
        self.plcDfaCluster.ySpec = 'none'
        self.plcDfaCluster.SetConstraints(
            LayoutAnchors(self.plcDfaCluster, True, True, False, True))
        self.plcDfaCluster.fontSizeLegend = 8

        self.titleBar = TitleBar(self, id_=-1,
                                 text="Discriminant Function Analysis",
                                 style=bp.BP_USE_GRADIENT,
                                 alignment=bp.BP_ALIGN_LEFT)

    def _init_sizers(self):
        """"""
        self.grsDfa = wx.GridSizer(cols=2, hgap=2, rows=2, vgap=2)
        self.bxsDfa1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bxsDfa2 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_bxs_dfa1(self.bxsDfa1)
        self._init_coll_bxs_dfa2(self.bxsDfa2)
        self._init_coll_grs_dfa(self.grsDfa)

        self.SetSizer(self.bxsDfa1)


    def _init_coll_grs_dfa(self, parent):
        # generated method, don't edit

        parent.Add(self.plcDFAscores, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.plcDfaLoadsV, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.plcDfaCluster, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.plcDFAeigs, 0, border=0, flag=wx.EXPAND)

    def _init_coll_bxs_dfa1(self, parent):
        # generated method, don't edit

        parent.Add(self.bxsDfa2, 1, border=0, flag=wx.EXPAND)

    def _init_coll_bxs_dfa2(self, parent):
        # generated method, don't edit

        parent.Add(self.titleBar, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.grsDfa, 1, border=0, flag=wx.EXPAND)

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

        # TODO: Check what curve is for
        # noinspection PyUnusedLocal,PyTypeChecker
        curve = PolyLine([[0, 0], [1, 1]], colour='white',
                         width=1, style=wx.PENSTYLE_TRANSPARENT)

        for each in objects.keys():
            cmd = ('self.%s.Draw(PlotGraphics([curve], '
                   'objects["%s"][0], objects["%s"][1], objects["%s"][2]))')
            exec(cmd % (each, each, each, each), locals(), globals())


class TitleBar(bp.ButtonPanel):
    """"""
    def __init__(self, parent, id_, text, style, alignment):
        """"""
        bp.ButtonPanel.__init__(self, parent=parent, id=-1,
                                text="Discriminant Function Analysis",
                                agwStyle=bp.BP_USE_GRADIENT,
                                alignment=bp.BP_ALIGN_LEFT)

        _, _, _, _ = id_, text, style, alignment
        self._init_btnpanel_ctrls()
        self.parent = parent
        self.data = None
        self.draw_dfa_eig = None
        self.create_buttons()

    def _init_btnpanel_ctrls(self):
        """"""
        chcs = ['PC Scores', 'PLS Scores', 'Raw spectra', 'Processed spectra']
        self.cbxData = wx.Choice(choices=chcs, id=-1, name='cbxData',
                                 parent=self, pos=(118, 21),
                                 size=(100, 23), style=0)

        self.cbxData.SetSelection(0)
        self.Bind(wx.EVT_CHOICE, self.on_cbx_data, id=self.cbxData.GetId())

        bmp = wx.Bitmap(os.path.join('bmp', 'run.png'), wx.BITMAP_TYPE_PNG)
        self.btnRunDfa = bp.ButtonInfo(self, -1, bmp, kind=wx.ITEM_NORMAL,
                                       shortHelp='Run DFA',
                                       longHelp='Run Discriminant Function Analysis')
        self.btnRunDfa.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.on_run_dfa, id=self.btnRunDfa.GetId())

        self.spnDfaPcs = wx.SpinCtrl(id=-1, initial=1, max=100, min=3,
                                     name='spnDfaPcs', parent=self,
                                     pos=(104, 104),
                                     size=(46, 23),
                                     style=wx.SP_ARROW_KEYS)
        self.spnDfaPcs.SetValue(3)
        self.spnDfaPcs.SetToolTip('')

        self.spnDfaDfs = wx.SpinCtrl(id=-1, initial=1, max=100, min=2,
                                     name='spnDfaDfs', parent=self,
                                     pos=(57, 168),
                                     size=(46, 23),
                                     style=wx.SP_ARROW_KEYS)
        self.spnDfaDfs.SetValue(2)
        self.spnDfaDfs.SetToolTip('')

        self.cbDfaXval = wx.CheckBox(id=-1, label='',
                                     name='cbDfaXval', parent=self,
                                     pos=(16, 216),
                                     size=(14, 13), style=0)
        self.cbDfaXval.SetValue(False)
        self.cbDfaXval.SetToolTip('')

        bmp = wx.Bitmap(os.path.join('bmp', 'export.png'), wx.BITMAP_TYPE_PNG)
        self.btnExpDfa = bp.ButtonInfo(self, -1, bmp, kind=wx.ITEM_NORMAL,
                                       shortHelp='Export DFA Results',
                                       longHelp='Export DFA Results')
        self.btnExpDfa.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.on_exp_dfa, id=self.btnExpDfa.GetId())

        self.spnDfaScore1 = wx.SpinCtrl(id=-1, initial=1, max=100, min=1,
                                        name='spnDfaScore1', parent=self,
                                        pos=(199, 4), size=(46, 23),
                                        style=wx.SP_ARROW_KEYS)
        self.spnDfaScore1.SetToolTip('')
        self.spnDfaScore1.Enable(0)
        self.spnDfaScore1.Bind(wx.EVT_SPINCTRL, self.on_spn_dfa_score1,
                               id=-1)

        self.spnDfaScore2 = wx.SpinCtrl(id=-1, initial=1, max=100, min=1,
                                        name='spnDfaScore2', parent=self,
                                        pos=(287, 4), size=(46, 23),
                                        style=wx.SP_ARROW_KEYS)
        self.spnDfaScore2.SetToolTip('')
        self.spnDfaScore2.Enable(0)
        self.spnDfaScore2.Bind(wx.EVT_SPINCTRL, self.on_spn_dfa_score2,
                               id=-1)

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

    # noinspection PyPep8Naming
    def SetProperties(self):
        """Sets the colours for the two demos.

        Called only if the user didn't modify the colours and sizes
        using the Settings Panel

        """
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
        print('in DFA ln 325, data: ', data)

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
        xdata, loads, xvaldata = None, None, None
        scores, eigs = None, None
        tbar = self.parent.parent.parent.plPca.titleBar
        klass = self.data['class'][:, 0]
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
            if tbar.cbxData.GetSelection() == 0:
                xvaldata = self.data['rawtrunc']
            elif tbar.cbxData.GetSelection() == 1:
                xvaldata = self.data['proctrunc']

            # select pca method
            if tbar.cbxPcaType.GetSelection() == 0:
                self.data['niporsvd'] = 'nip'
            elif tbar.cbxPcaType.GetSelection() == 1:
                self.data['niporsvd'] = 'svd'

            # check appropriate number of pcs/dfs
            if self.spnDfaPcs.GetValue() <= self.spnDfaDfs.GetValue():
                self.spnDfaDfs.SetValue(self.spnDfaPcs.GetValue() - 1)

            # check for pca preproc method
            if tbar.cbxPreprocType.GetSelection() == 0:
                self.data['pcatype'] = 'covar'
            elif tbar.cbxPreprocType.GetSelection() == 1:
                self.data['pcatype'] = 'corr'

            # reset controls
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
                        chemtrics.cva(xdata, klass, self.spnDfaDfs.GetValue())
                else:
                    scores, _, eigs, loads = \
                        chemtrics.cva(xdata, klass, self.spnDfaDfs.GetValue(),
                                      loads[0:self.spnDfaPcs.GetValue(), :])

            elif self.cbDfaXval.GetValue():
                if self.cbxData.GetSelection() > 1:
                    # run dfa
                    scores, loads, eigs = \
                        chemtrics.dfa_xval_raw(xdata, klass,
                                               self.data['validation'],
                                               self.spnDfaDfs.GetValue())

                elif self.cbxData.GetSelection() == 0:
                    # run pc-dfa
                    if self.data['niporsvd'] in ['nip']:
                        scores, loads, eigs = \
                            chemtrics.dfa_xval_pca(xvaldata, 'NIPALS',
                                                   self.spnDfaPcs.GetValue(),
                                                   klass,
                                                   self.data['validation'],
                                                   self.spnDfaDfs.GetValue(),
                                                   ptype=self.data['pcatype'])

                    elif self.data['niporsvd'] in ['svd']:
                        scores, loads, eigs = \
                            chemtrics.dfa_xval_pca(xvaldata, 'SVD',
                                                   self.spnDfaPcs.GetValue(),
                                                   klass,
                                                   self.data['validation'],
                                                   self.spnDfaDfs.GetValue(),
                                                   ptype=self.data['pcatype'])

                elif self.cbxData.GetSelection() == 1:
                    # run pls-dfa
                    scores, loads, eigs = \
                        chemtrics.dfa_xval_pls(self.data['plst'],
                                               self.data['plsloads'],
                                               self.spnDfaPcs.GetValue(),
                                               klass,
                                               self.data['validation'],
                                               self.spnDfaDfs.GetValue())

            self.data['dfscores'] = scores
            self.data['dfloads'] = loads
            self.data['dfeigs'] = eigs

            # plot dfa results
            self.plot_dfa()

        except TypeError as error:
            error_box(self, '%s' % str(error))
            raise

    def on_exp_dfa(self, _):
        dlg = wx.FileDialog(self, "Choose a file", ".", "",
                            "Any files (*.*)|*.*", wx.FD_SAVE)
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
        set_btn_state(self.spnDfaScore1.GetValue(),
                      self.spnDfaScore2.GetValue(),
                      self.parent.prnt.prnt.tbMain)

    def on_spn_dfa_score2(self, _):
        self.plot_dfa()
        set_btn_state(self.spnDfaScore1.GetValue(),
                      self.spnDfaScore2.GetValue(),
                      self.parent.parent.prnt.tbMain)

    def plot_dfa(self):
        # plot scores
        tb_main = self.parent.prnt.parent.tbMain
        plot_scores(self.parent.plcDFAscores, self.data['dfscores'],
                    cl=self.data['class'][:, 0],
                    labels=self.data['label'],
                    validation=self.data['validation'],
                    col1=self.spnDfaScore1.GetValue() - 1,
                    col2=self.spnDfaScore2.GetValue() - 1,
                    title='DFA Scores',
                    xLabel='t[' + str(self.spnDfaScore1.GetValue()) + ']',
                    yLabel='t[' + str(self.spnDfaScore2.GetValue()) + ']',
                    xval=self.cbDfaXval.GetValue(),
                    symb=tb_main.tbSymbols.GetValue(),
                    text=tb_main.tbPoints.GetValue(),
                    pconf=tb_main.tbConf.GetValue(),
                    usecol=[], usesym=[])

        # plot loadings
        if self.cbxData.GetSelection() == 0:
            label = 'PC-DFA Loadings'
        else:
            label = 'DFA Loadings'

        if self.spnDfaScore1.GetValue() != self.spnDfaScore2.GetValue():
            plot_loads(self.parent.plcDfaLoadsV, self.data['dfloads'],
                       xaxis=self.data['indlabels'],
                       col1=self.spnDfaScore1.GetValue() - 1,
                       col2=self.spnDfaScore2.GetValue() - 1, title=label,
                       xLabel='w[' + str(self.spnDfaScore1.GetValue()) + ']',
                       yLabel='w[' + str(self.spnDfaScore2.GetValue()) + ']',
                       type=tb_main.get_load_plot_idx(),
                       usecol=[], usesym=[])

        else:
            idx = self.spnDfaScore1.GetValue() - 1
            plot_line(self.parent.plcDfaLoadsV,
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

        tree = treecluster(data=mS, method='m', dist='e')
        tree, order = self.parent.prnt.parent.plCluster.titleBar.treestructure(
            tree,
            np.arange(len(tree) + 1))
        self.parent.prnt.parent.plCluster.titleBar.draw_tree(
            self.parent.plcDfaCluster,
            tree, order, mSn, tit='Hierarchical Cluster Analysis',
            xL='Euclidean Distance', yL='Sample')

        # Plot eigs
        self.draw_dfa_eig = plot_line(self.parent.plcDFAeigs, self.data['dfeigs'],
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

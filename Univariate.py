# -----------------------------------------------------------------------------
# Name:        Univariate.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2007/05/22
# RCS-ID:      $Id: Univariate.py,v 1.2 2009/02/26 22:19:47 rmj01 Exp $
# Copyright:   (c) 2006
# Licence:     GNU General Public Licence
# ---------------------------------------------------------------------------

import wx
import wx.lib.buttons
from wx.lib.plot import PolyMarker, PlotGraphics, PolyLine
import wx.lib.stattext
import wx.lib.agw.buttonpanel as bp
from wx.lib.anchors import LayoutAnchors

import numpy as np
import scipy as sp
import scipy.stats
import string, copy
import os

from numpy import newaxis as nax
from Pca import BoxPlot
from Pca import plotScores
from Pca import PlotPlsModel
from Pca import SetButtonState
from Pca import MyPlotCanvas
from mva.process import meancent
from mva.process import scale01

class Univariate(wx.Panel):
    # partial least squares regression
    
    def _init_coll_bxsPls2_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.titleBar, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.grsPls1, 1, border=0, flag=wx.EXPAND)

    def _init_coll_bxsPls1_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.bxsPls2, 1, border=0, flag=wx.EXPAND)
    
    def _init_coll_grsPls1_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.plcBoxplot, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.plcRoc, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.nbUniRes, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.plcPsumm, 0, border=0, flag=wx.EXPAND)

    def _init_sizers(self):
        # generated method, don't edit
        self.grsPls1 = wx.GridSizer(cols=2, hgap=2, rows=2, vgap=2)
        
        self.bxsPls1 = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.bxsPls2 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_grsPls1_Items(self.grsPls1)
        self._init_coll_bxsPls1_Items(self.bxsPls1)
        self._init_coll_bxsPls2_Items(self.bxsPls2)
        
        self.SetSizer(self.bxsPls1)
    
    def _init_class_sizers(self):
        for item in self.grsPls1.GetChildren():
            self.grsPls1.Detach(item.GetWindow())
        
        # self.grsPls1.Clear()
        self.grsPls1.DeleteWindows()
        
        self.grsPls1.SetCols(2)
        
        self.plcRoc.Show(True)
        self.plcPsumm.Show(True)
        
        self.grsPls1.Add(self.plcBoxplot, 0, border=0, flag=wx.EXPAND)
        self.grsPls1.Add(self.plcRoc, 0, border=0, flag=wx.EXPAND)
        self.grsPls1.Add(self.nbUniRes, 0, border=0, flag=wx.EXPAND)
        self.grsPls1.Add(self.plcPsumm, 0, border=0, flag=wx.EXPAND)
        
        self.Reset()
        
        self.grsPls1.Layout()
        
    def _init_corr_sizers(self):
        for item in self.grsPls1.GetChildren():
            self.grsPls1.Detach(item.GetWindow())
        
        # self.grsPls1.Clear()
        self.grsPls1.DeleteWindows()
        
        self.grsPls1.SetCols(1)
        
        self.plcRoc.Show(False)
        self.plcPsumm.Show(False)
        
        self.grsPls1.Add(self.plcBoxplot, 0, border=0, flag=wx.EXPAND)
        self.grsPls1.Add(self.nbUniRes, 0, border=0, flag=wx.EXPAND)
        
        self.Reset()
        
        self.grsPls1.Layout()
        
    def _init_coll_nbUniRes_Pages(self, parent):
        # generated method, don't edit

        parent.AddPage(imageId=-1, page=self.plcScatter, select=True,
                       text='Scatter Plot')
        parent.AddPage(imageId=-1, page=self.txtResTable, select=False,
                       text='Results Table')

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=-1, name='Univariate', parent=prnt,
                          pos=wx.Point(84, 70), size=wx.Size(796, 460),
                          style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(788, 426))
        self.SetAutoLayout(True)
        self.SetToolTip('')
        self.prnt = prnt

        self.plcBoxplot = MyPlotCanvas(id=-1, name='plcBoxplot',
                                       parent=self, pos=wx.Point(0, 0), size=wx.Size(302, 246),
                                       style=0, toolbar=self.prnt.parent.tbMain)
        self.plcBoxplot.fontSizeAxis = 8
        self.plcBoxplot.fontSizeTitle = 10
        self.plcBoxplot.enableZoom = True
        self.plcBoxplot.SetToolTip('')
        self.plcBoxplot.enableLegend = True
        self.plcBoxplot.fontSizeLegend = 8
        self.plcBoxplot.SetAutoLayout(True)
        self.plcBoxplot.SetConstraints(
            LayoutAnchors(self.plcBoxplot, True, True, True, True))
        
        self.plcPsumm = MyPlotCanvas(id=-1, name='plcPsumm',
                                     parent=self, pos=wx.Point(0, 0), size=wx.Size(302, 246),
                                     style=0, toolbar=self.prnt.parent.tbMain)
        self.plcPsumm.fontSizeAxis = 8
        self.plcPsumm.fontSizeTitle = 10
        self.plcPsumm.enableZoom = True
        self.plcPsumm.SetToolTip('')
        self.plcPsumm.enableLegend = True
        self.plcPsumm.fontSizeLegend = 8
        self.plcPsumm.SetAutoLayout(True)
        # self.plcPsumm.set_log_scale((True,False))
        self.plcPsumm.SetConstraints(LayoutAnchors(self.plcPsumm, True,
              True, True, True))
        
        self.plcRoc = MyPlotCanvas(id=-1, name='plcRoc',
                                   parent=self, pos=wx.Point(0, 0), size=wx.Size(302, 246),
                                   style=0, toolbar=self.prnt.parent.tbMain)
        self.plcRoc.fontSizeAxis = 8
        self.plcRoc.fontSizeTitle = 10
        self.plcRoc.enableZoom = True
        self.plcRoc.SetToolTip('')
        self.plcRoc.enableLegend = True
        self.plcRoc.fontSizeLegend = 8
        self.plcRoc.SetAutoLayout(True)
        self.plcRoc.SetConstraints(LayoutAnchors(self.plcRoc, True,
                                                 True, True, True))
        
        self.nbUniRes = wx.Notebook(id=-1, name='nbUniRes', parent=self,
              pos=wx.Point(176, 274), size=wx.Size(310, 272),
              style=wx.NB_BOTTOM)
        self.nbUniRes.SetToolTip('')
        self.nbUniRes.SetAutoLayout(True)
        self.nbUniRes.SetConstraints(LayoutAnchors(self.nbUniRes, True,
                                                   True, True, True))

        self.plcScatter = MyPlotCanvas(id=-1, name='plcScatter',
                                       parent=self.nbUniRes, pos=wx.Point(0, 0), size=wx.Size(302, 246),
                                       style=0, toolbar=self.prnt.parent.tbMain)
        self.plcScatter.fontSizeAxis = 8
        self.plcScatter.fontSizeTitle = 10
        self.plcScatter.enableZoom = True
        self.plcScatter.SetToolTip('')
        self.plcScatter.enableLegend = True
        self.plcScatter.fontSizeLegend = 8
        self.plcScatter.SetAutoLayout(True)
        self.plcScatter.SetConstraints(
            LayoutAnchors(self.plcScatter, True, True, True, True))
        
        self.txtResTable = wx.TextCtrl(
            id=-1, name='txtResTable', parent=self.nbUniRes,
            pos=wx.Point(0, 0), size=wx.Size(200, 200),
            style=wx.TE_DONTWRAP | wx.HSCROLL | wx.TE_READONLY |
            wx.SUNKEN_BORDER | wx.TE_MULTILINE | wx.VSCROLL,
            value='')
        self.txtResTable.SetToolTip('')
        self.txtResTable.SetConstraints(
            LayoutAnchors(self.txtResTable, True, True, True, True))
              
        self.titleBar = TitleBar(self, id=-1, text="Univariate Tests",
                                 style=bp.BP_USE_GRADIENT,
                                 alignment=bp.BP_ALIGN_LEFT)
        
        self._init_coll_nbUniRes_Pages(self.nbUniRes)
        
        self._init_sizers()

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)
    
    def Reset(self):
        # reset plots
        objects = {
            'plcBoxplot': ['Boxplot or Regression Curve', 'Group/Actual', 'Value'],
            'plcPsumm': ['p-value vs. Receiver Operating Characteristic', 'p-value', 'Area Under ROC'],
            'plcRoc': ['Receiver Operating Characteristic', 'False positive', 'True positive'],
            'plcScatter': ['Scatter Plot or Regression Summary', 'Group/R', 'Value']
        }

        curve = wx.lib.plot.PolyLine([[0, 0], [1, 1]], colour='white', width=1,
                                     style=wx.TRANSPARENT)
        
        # set to udef by boxplot function
        self.plcBoxplot.xSpec = 'min'
        
        for each in objects:
            exec('self.' + each + '.Draw(wx.lib.plot.PlotGraphics([curve],' +
                 'objects["' + each + '"][0],' +
                 'objects["' + each + '"][1],' +
                 'objects["' + each + '"][2]))'
                 )
        
        # reset textbox
        self.txtResTable.SetValue('Results Table')
            
class TitleBar(bp.ButtonPanel):
    def _init_btnpanel_ctrls(self, prnt):
        bp.ButtonPanel.__init__(self, parent=prnt, id=-1,
                                text="Univariate Tests",
                                agwStyle=bp.BP_USE_GRADIENT,
                                alignment=bp.BP_ALIGN_LEFT)
        
        self.cbxData = wx.Choice(choices=['Raw spectra', 'Processed spectra'],
                                 id=-1, name='cbxData', parent=self,
                                 pos=wx.Point(118, 21), size=wx.Size(90, 23),
                                 style=0)
        self.cbxData.SetSelection(0)
        
        self.cbxVariable = wx.Choice(choices=['Variables'], id=-1,
                                     name='cbxVariable', parent=self,
                                     pos=wx.Point(118, 21),
                                     size=wx.Size(90, 23), style=0)
        self.cbxVariable.SetSelection(0)
        
        self.cbxTest = wx.Choice(choices=['ANOVA', 'Kruskal-Wallis',
                                          'Correlation Coeff.'],
                                 id=-1, name='cbxTest', parent=self,
                                 pos=wx.Point(75, 21),
                                 size=wx.Size(90, 23), style=0)

        self.cbxTest.Bind(wx.EVT_CHOICE, self.OnCbxTest, id=-1)
        self.cbxTest.SetSelection(0)

        bmp = wx.Bitmap(os.path.join('bmp', 'run.png'), wx.BITMAP_TYPE_PNG)
        self.btnRunTest = bp.ButtonInfo(self, -1, bmp, kind=wx.ITEM_NORMAL,
                                        shortHelp='Run Test',
                                        longHelp='Run Test')
        self.btnRunTest.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.OnBtnRunTestButton, id=self.btnRunTest.GetId())
        
    def __init__(self, parent, id, text, style, alignment):
        
        self._init_btnpanel_ctrls(parent)
        
        self.parent = parent
                                           
        self.CreateButtons()
    
    def CreateButtons(self):
        self.Freeze()
        
        self.SetProperties()
                    
        self.AddControl(self.cbxData)
        self.AddControl(self.cbxVariable)
        self.AddControl(self.cbxTest)
        self.AddSeparator()
        self.AddButton(self.btnRunTest)
        
        self.Thaw()

        self.DoLayout()
    
    def get_data(self, data):
        self.data = data
        
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
    
    def Roc(self, group, x):
        """Receiver operating characteristic (ROC)
        
        group = column vector of 0's & 1's, where 1 represents 
                the positive class
        
        x     = column vector of classification scores
        
        """
        # sort by classifier output
        idx = sp.argsort(-x, 0)
        group = group[sp.reshape(idx, (len(idx),))][:, nax]
        
        # compute true positive and false positive rates
        rgrp = sp.ones(group.shape)
        rgrp[sp.nonzero(group)[0]] = 0
        
        tp = sp.cumsum(group) / sp.sum(group)
        fp = sp.cumsum(rgrp) / sp.sum(rgrp)
        
        tp = sp.concatenate(([[0]], tp[:, nax], [[1]]), 0)
        fp = sp.concatenate(([[0]], fp[:, nax], [[1]]), 0)
        
        return tp, fp
    
    def RocArea(self, tp, fp):
        """Area under roc curve
        """
        n = len(tp)
        
        return sp.sum((fp[2:n] - fp[1:n-1]) * (tp[2:n] + tp[1:n-1])) / 2
    
    def OnBtnRunTestButton(self, event):
        # run the analysis
        self.RunUnivariate()
        
    def RunUnivariate(self):
        # ANOVA or KW
        if self.cbxTest.GetSelection() < 2:
            if (self.data['utest'] is None) | (self.data['utest'] != [self.cbxTest.GetSelection(),
                  self.cbxData.GetSelection()]) is True:
                vr = range(self.cbxVariable.GetCount())
            else:
                cbx_value = self.cbxVariable.GetSelection()
                vr = range(cbx_value, cbx_value + 1)
                
            # prepare data
            uG = sp.unique(np.array(self.data['label']))
            p_aur = [[]]*len(uG)

            # plotting colours
            colours = ['black', 'blue', 'red', 'cyan', 'green']
            for variable in vr:
                # report to status bar
                self.parent.prnt.parent.sbMain.SetStatusText('Calculating ' +
                                                           self.data['indlabels'][variable], 0)
                
                # get column
                if self.cbxData.GetSelection() == 0:
                    x = sp.take(self.data['rawtrunc'], [variable], 1)
                elif self.cbxData.GetSelection() == 1:
                    x = sp.take(self.data['proctrunc'], [variable], 1)
                
                print('*** x ***')
                print(type(x))
                print(x)
                print('*** uG ***')
                print(uG)
                print('*** data ***')
                print(type(self.data))
                print(self.data)
                print('**********')

                # gather data
                grp_list = ''
                for item in uG:
                    grp_list = grp_list + 'x[sp.array(self.data["label"])==' + item + '],'
                
                # apply test!!!!!!!!!!!!!!!!!!
                if self.cbxTest.GetSelection() == 0:
                    # run anova
                    groups = grp_list[0:len(grp_list) - 1]
                    print('groups : ', groups)
                    f = 0
                    exec('f, p = sp.stats.f_oneway(' + groups + ')')

                    print('-> ', f)
                    print('-> ', p)

                    p = p[0]
                elif self.cbxTest.GetSelection() == 1:
                    # run kruskal-wallis (non-parametric anova)
                    exec('h, p = sp.stats.kruskal(' + grp_list[0:len(grp_list)-1] + ')')
                
                # save some stuff for plotting
                if variable == self.cbxVariable.GetSelection():
                    plotx,self.data['plotp'] = x, p
                
                # plot roc vs. p for small p, big r
                # filter by bonferroni corrected p-value:
                if p < (.05 / self.cbxVariable.GetCount()):
                    colCount = 0
                    for each in range(len(uG)):
                        # create class structure for roc,
                        # +1 for most group with most +ve values
                        y = np.zeros(x.shape)
                        y[np.array(self.data['label']) == uG[each]] = 1
                        if sp.mean(x[y == 1]) < sp.mean(x[y == 0]):
                            y = sp.ones(x.shape)
                            y[np.array(self.data['label']) == uG[each]] = 0
                        
                        # calculate roc
                        tp,fp = self.Roc(y, x)
                        r = self.RocArea(tp,fp)
                        
                        if r > .75:
                            # list of coords for plotting
                            aslice = copy.deepcopy(p_aur[each])
                            aslice.append([each, np.log(p), r,
                                           colours[colCount],
                                           self.cbxVariable.GetString(variable)]
                                          )
                            p_aur[each] = aslice
                        # colour index
                        colCount += 1
                        if colCount == len(colours):
                            colCount = 0
            exit()
            # create results array
            plotSum = False
            if (self.data['utest'] is None) | (self.data['utest'] != [self.cbxTest.GetSelection(),
                self.cbxData.GetSelection()]) is True:
                self.data['p_aur'] = sp.zeros((1, 5))
                for each in p_aur:
                    if len(each) > 0:
                        self.data['p_aur'] = sp.concatenate((self.data['p_aur'],
                                                        sp.array(each)), 0)
                self.data['p_aur'] = self.data['p_aur'][1:len(self.data['p_aur']), :]
                plotSum = True
            
            # plot results
            self.PlotResults(plotx,p,uG,colours=colours,psum=plotSum)
            
            # save test used
            # self.data['utest'] = [self.cbxTest.GetSelection(),self.cbxData.GetSelection()]

        # corr coef
        else:
            r = []
            if (self.data['utest'] is None) | (self.data['utest'] != [self.cbxTest.GetSelection(),
                  self.cbxData.GetSelection()]) is True:
                vr = range(self.cbxVariable.GetCount())
            else:
                vr = range(self.cbxVariable.GetSelection(),
                           self.cbxVariable.GetSelection() + 1)
            
            for variable in vr:
                # report to status bar
                self.parent.prnt.prnt.sbMain.SetStatusText('Calculating ' + \
                                                           self.data['indlabels'][variable], 0)
                
                # get column
                if self.cbxData.GetSelection() == 0:
                    x = sp.take(self.data['rawtrunc'], [variable], 1)
                    xsel = 'raw'
                elif self.cbxData.GetSelection() == 1:
                    x = sp.take(self.data['proctrunc'], [variable], 1)
                    xsel = 'proc'
                    
                # calculate correlation coefficient
                r.append(sp.corrcoef(sp.reshape(x, (len(x),)),
                                     self.data['class'][:, 0])[0, 1])
                
            # plot regression line
            points = wx.lib.plot.PolyMarker(sp.transpose([self.data['class'][:, 0],
                  sp.reshape(sp.take(self.data[xsel + 'trunc'],
                  [self.cbxVariable.GetSelection()],1),(len(self.data[xsel + 'trunc']),))]),
                  marker = 'square', fillstyle=wx.TRANSPARENT, colour='black', size=2)
            pfit = sp.polyfit(self.data['class'][:,0], sp.reshape(sp.take(self.data[xsel + 'trunc'],
                  [self.cbxVariable.GetSelection()],1), (len(self.data[xsel + 'trunc']),)), 1)
            pval = sp.polyval(pfit, sp.sort(self.data['class'][:, 0]))
            linear = wx.lib.plot.PolyLine(sp.transpose([sp.sort(self.data['class'][:, 0]),
                                                        pval[:, nax]]), colour='black')
            if len(r) > 1:
                self.data['plotp'] = r[self.cbxVariable.GetSelection()]
            else:
                self.data['plotp'] = r[0]

            if self.data['plotp'] < 0:
                coords = [[.75 * max(self.data['class'][:, 0]),
                           .75 * max(sp.take(self.data[xsel + 'trunc'],
                                     [self.cbxVariable.GetSelection()], 1))]]
            else:
                coords = [[.05*min(self.data['class'][:,0]),.75*min(sp.take(self.data[xsel + 'trunc'],
                  [self.cbxVariable.GetSelection()],1))]]
            if pfit[1] < 0:
                lineq = 'y = ' + '%.2f' % pfit[0] + 'x ' + '%.2f' %pfit[1] + \
                      '; R = ' + '%.2f' % self.data['plotp']
            else:
                lineq = 'y = ' + '%.2f' % pfit[0] + 'x + ' + '%.2f' %pfit[1] + \
                      ';R = ' + '%.2f' % self.data['plotp']
            eq = PolyMarker(coords, labels = lineq, marker = 'text')
            self.parent.plcBoxplot.Draw(PlotGraphics([points, linear, eq],
                  title = 'Linear Regression', xLabel = 'Actual Value', 
                  yLabel = self.cbxVariable.GetStringSelection()))
            
            if len(r) > 1:
                # plot +ve/-ve average spectrum, scaled with r
                xaxis = self.data['xaxis']
                rplot = PolyLine(sp.transpose([sp.reshape(xaxis,
                      (len(xaxis),)),sp.array(r)]), colour='blue',
                      legend='Correlation Coefficient')

                applot = PolyLine(sp.transpose([sp.reshape(xaxis,
                                                (len(xaxis), )),
                                                sp.reshape(scale01(sp.mean(self.data[xsel + 'trunc'],
                                                                           axis=0)[nax, :]),
                                                           (len(self.data['xaxis']), ))]),
                                  colour='black',
                                              legend='Average spectrum (+ve)')
                anplot = PolyLine(sp.transpose([sp.reshape(self.data['xaxis'],
                      (len(self.data['xaxis']),)), -sp.reshape(scale01(sp.mean(self.data[xsel + 'trunc'],
                      axis=0)[nax, :]), (len(self.data['xaxis']),))]), colour='red',
                                              legend='Average spectrum (-ve)')
                self.parent.plcScatter.Draw(
                    PlotGraphics([rplot, applot, anplot], title='R-Summary',
                                 xLabel ='Arbitrary',
                                 yLabel='Intensity (a.u.) / R'))
                
        # save test used
        self.data['utest'] = [self.cbxTest.GetSelection(),self.cbxData.GetSelection()]
            
    def PlotResults(self, x, p, ugrp, colours, psum=False):
        # boxplot
        BoxPlot(self.parent.plcBoxplot, x, self.data['label'], xLabel='Groups',
                yLabel=self.cbxVariable.GetStringSelection(),
                title='Box and Whisker Plot: p = ' + '%.2g' % p)
        
        # scatter plot
        plotScores(self.parent.plcScatter, x, cl=self.data['class'][:, 0],
                   labels=self.data['label'],
                   validation=self.data['validation'],
                   col1=0, col2=0, title='Scatter Plot',
                   xLabel='Group', yLabel='Value',
                   xval=False, pconf=False, symb=None, text=True,
                   usecol=[], usesym=[])
        
        # roc curve
        colCount = 0
        rocPlot = []
        for each in range(len(ugrp)):
            # create class structure, +1 for most group with most +ve values
            y = np.zeros(x.shape)
            y[np.array(self.data['label']) == ugrp[each]] = 1
            if sp.mean(x[y == 1]) < sp.mean(x[y == 0]):
                y = np.ones(x.shape)
                y[np.array(self.data['label']) == ugrp[each]] = 0
            
            # calculate roc
            tp, fp = self.Roc(y, x)
            
            # calculate roc convex hull
            ch = self.convex_hull(sp.transpose(np.concatenate((fp, tp), 1)))
            
            # plot roc
            area1 = self.RocArea(tp, fp)
            area2 = self.RocArea(ch[:, 1][:, nax], ch[:, 0][:, nax])
            rocPlot.append(PolyLine(
                np.concatenate((fp, tp), 1),
                legend='%s: Area = %.2f (%.2f)' % (ugrp[each], area1, area2),
                colour=wx.Colour(colours[colCount])))
            
            # plot roc ch
            rocPlot.append(PolyLine(
                ch, style=wx.SHORT_DASH, colour=wx.Colour(colours[colCount])))
            
            # colour index
            colCount += 1
            if colCount == len(colours):
                colCount = 0
                
        # set legend option
        if len(ugrp) > 2:
            self.parent.plcRoc.enableLegend = True
        else:
            self.parent.plcRoc.enableLegend = False
        
        # draw roc
        self.parent.plcRoc.Draw(PlotGraphics(rocPlot,
                                             title='Receiver Operating Characteristic',
                                             xLabel='False Positive',
                                             yLabel='True Positive'))
        
        # plot p-value vs. area under roc
        if psum:
            pRoc = []
            chkSum = 0
            for each in range(len(ugrp)):
                aslice = self.data['p_aur'][sp.asarray(self.data['p_aur'][:, 0],
                                                       dtype='i') == each, :]
                if len(aslice) > 0:
                    pRoc.append(PolyMarker(sp.asarray(slice[:, 1:3],
                                                      dtype='float64'),
                                           marker='circle',
                                           colour=wx.Colour(slice[0, 3]),
                                           fillcolour=wx.Colour(slice[0, 3]),
                                           size=1, legend=ugrp[each]))

                    pRoc.append(PolyMarker(sp.asarray(aslice[:, 1:3],
                                                      dtype='float64'),
                                           marker='text',
                                           labels=slice[:, 4],
                                           colour=wx.Colour(aslice[0, 3])))
                chkSum += len(aslice)
            #
            if chkSum > 0:
                self.parent.plcPsumm.Draw(PlotGraphics(pRoc,
                                                       title='p-value vs. Area under ROC',
                                                       xLabel='log(p)',
                                                       yLabel='Area under ROC'))

    def _angle_to_point(self, point, centre):
        """calculate angle in 2-D between points and x axis"""
        delta = point - centre
        res = np.arctan(delta[1] / delta[0])
        if delta[0] < 0:
            res += np.pi
        return res
    
    def area_triangle(self, p1, p2, p3):
        """calculate area of any triangle given co-ordinates of the corners"""
        return np.linalg.norm(np.cross((p2 - p1), (p3 - p1))) / 2

    def convex_hull(self, points):
        """Calculate subset of points that make a convex hull around points
        
        Taken from Scipy cookbook
        (https://scipy.github.io/old-wiki/pages/Cookbook/Finding_Convex_Hull.html)
        
        Recursively eliminates points that lie inside two neighbouring points 
        until only convex hull is remaining.
        
        :Parameters:
            points : ndarray (2 x m)
                array of points for which to find hull
            
        :Returns:
            hull_points : ndarray (2 x n)
                convex hull surrounding points
        """
        n_pts = points.shape[1]
        assert(n_pts > 5)
        centre = points.mean(1)
        angles = np.apply_along_axis(self._angle_to_point, 0, points, centre)
        pts_ord = points[:, angles.argsort()]
        pts = [x[0] for x in zip(pts_ord.transpose())]
        prev_pts = len(pts) + 1
        k = 0
        while prev_pts > n_pts:
            prev_pts = n_pts
            n_pts = len(pts)
            i = -2
            while i < (n_pts - 2):
                Aij = self.area_triangle(centre, pts[i], pts[(i + 1) % n_pts])
                Ajk = self.area_triangle(centre, pts[(i + 1) % n_pts],
                                         pts[(i + 2) % n_pts])
                Aik = self.area_triangle(centre, pts[i], pts[(i + 2) % n_pts])
                if Aij + Ajk <= Aik:
                    del pts[i+1]
                i += 1
                n_pts = len(pts)
            k += 1
        pts = sp.sort(np.asarray(pts), 0)
        
        return pts
    
    def OnCbxTest(self, event):
        # change page layout
        if self.cbxTest.GetSelection() == 2:
            self.parent._init_corr_sizers()
        else:
            self.parent._init_class_sizers()
            
            
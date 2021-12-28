# -----------------------------------------------------------------------------
# Name:        plsr.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2007/05/22
# RCS-ID:      $Id: plsr.py, v 1.16 2009/02/26 22:19:47 rmj01 Exp $
# Copyright:   (c) 2006
# Licence:     GNU General Public Licence
# -----------------------------------------------------------------------------

import os
import numpy as np
from numpy import newaxis as nax

import wx
import wx.lib.buttons
import wx.lib.agw.buttonpanel as bp
from wx.lib.anchors import LayoutAnchors
from wx.lib.plot import PlotGraphics, PolyLine
from wx.lib.plot import PolyMarker
from wx.lib.stattext import GenStaticText

import mva.chemometrics as chemtrics
from pca import plot_line
from pca import plot_loads
from pca import MyPlotCanvas
from pca import plot_pls_model
from commons import error_box

[wxID_PLSR, wxID_PLSRBTNEXPPLS, wxID_PLSRBTNGOTOGADPLS, wxID_PLSRBTNGOTOGAPLS, 
 wxID_PLSRBTNRUNFULLPLS, wxID_PLSRNBFULLPLS, wxID_PLSRPLCPLSERROR, 
 wxID_PLSRPLCPLSHETERO, wxID_PLSRPLCPLSLOADING, wxID_PLSRPLCPLSMODEL, 
 wxID_PLSRPLPLSLOADS, wxID_PLSRRBPLSUSEPROC, wxID_PLSRRBPLSUSERAW, 
 wxID_PLSRSASHWINDOW8, wxID_PLSRSPNPLSFACTOR, wxID_PLSRSPNPLSMAXFAC, 
 wxID_PLSRSTATICTEXT10, wxID_PLSRSTATICTEXT14, wxID_PLSRSTATICTEXT15, 
 wxID_PLSRSTUSE, wxID_PLSRTXTPLSSTATS, 
 ] = [wx.NewId() for _init_ctrls in range(21)]


class Plsr(wx.Panel):
    # partial least squares regression
    def __init__(self, parent, id_, pos, size, style, name):
        wx.Panel.__init__(self, id=wxID_PLSR, name='Plsr', parent=parent,
                          pos=(84, 70), size=(796, 460),
                          style=wx.TAB_TRAVERSAL)

        _, _, _, _, _ = id_, pos, size, style, name

        self.parent = parent
        self._init_ctrls()
        self._init_sizers()

    def _init_ctrls(self):
        """"""
        self.SetClientSize((788, 426))
        self.SetAutoLayout(True)
        self.SetToolTip('')

        self.nb_full_pls = wx.Notebook(id=-1, name='nbFullPls', parent=self,
                                       pos=(176, 274),
                                       size=(310, 272),
                                       style=wx.NB_BOTTOM)
        self.nb_full_pls.SetToolTip('')
        self.nb_full_pls.SetAutoLayout(True)
        self.nb_full_pls.SetConstraints(
            LayoutAnchors(self.nb_full_pls, True, True, True, True))
        # self.nbFullPls.SetTabSize((40, 15))

        self.nb_pls_preds = wx.Notebook(id=-1, name='nbPlsPreds', parent=self,
                                        pos=(176, 274),
                                        size=(310, 272),
                                        style=wx.NB_BOTTOM)
        self.nb_pls_preds.SetToolTip('')
        self.nb_pls_preds.SetAutoLayout(True)
        self.nb_pls_preds.SetConstraints(
            LayoutAnchors(self.nb_pls_preds, True, True, True, True))
        # self.nbPlsPreds.SetTabSize((0, 1))
        self.nb_pls_preds.parent = self

        self.plcPLSerror = MyPlotCanvas(id_=-1, name='plcPLSerror',
                                        parent=self.nb_full_pls, pos=(0, 0),
                                        size=(302, 246), style=0,
                                        toolbar=self.parent.parent.tbMain)
        self.plcPLSerror.fontSizeAxis = 8
        self.plcPLSerror.fontSizeTitle = 10
        self.plcPLSerror.enableZoom = True
        self.plcPLSerror.SetToolTip('')
        self.plcPLSerror.enableLegend = True
        self.plcPLSerror.fontSizeLegend = 8
        self.plcPLSerror.SetAutoLayout(True)
        self.plcPLSerror.SetConstraints(
            LayoutAnchors(self.plcPLSerror, True, True, True, True))

        self.plcPlsStats = MyPlotCanvas(id_=-1, name='plcPlsStats',
                                        parent=self.nb_full_pls,
                                        pos=(176, 0), size=(310, 272), style=0,
                                        toolbar=self.parent.parent.tbMain)
        self.plcPlsStats.xSpec = 'none'
        self.plcPlsStats.ySpec = 'none'
        self.plcPlsStats.SetAutoLayout(True)
        self.plcPlsStats.enableZoom = True
        self.plcPlsStats.SetConstraints(
            LayoutAnchors(self.plcPlsStats, True, True, True, True))
        self.plcPlsStats.SetFont(
            wx.Font(6, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_NORMAL, False, 'Courier New'))
        self.plcPlsStats.SetToolTip('')

        self.plc_pred_pls1 = MyPlotCanvas(id_=-1, name='plcPredPls1',
                                          parent=self.nb_pls_preds, style=0,
                                          pos=(176, 0), size=(310, 272),
                                          toolbar=self.parent.parent.tbMain)
        self.plc_pred_pls1.fontSizeTitle = 10
        self.plc_pred_pls1.fontSizeAxis = 8
        self.plc_pred_pls1.enableZoom = True
        self.plc_pred_pls1.SetToolTip('')
        self.plc_pred_pls1.enableLegend = True
        self.plc_pred_pls1.fontSizeLegend = 8
        self.plc_pred_pls1.SetAutoLayout(True)
        self.plc_pred_pls1.SetConstraints(
            LayoutAnchors(self.plc_pred_pls1, True, True, True, True))

        self.plcPlsHetero = MyPlotCanvas(id_=-1, name='plcPlsHetero',
                                         parent=self, pos=(488, 274),
                                         size=(310, 272),
                                         style=0,
                                         toolbar=self.parent.parent.tbMain)
        self.plcPlsHetero.fontSizeAxis = 8
        self.plcPlsHetero.fontSizeTitle = 10
        self.plcPlsHetero.enableZoom = True
        self.plcPlsHetero.SetToolTip('')
        self.plcPlsHetero.enableLegend = True
        self.plcPlsHetero.fontSizeLegend = 8
        self.plcPlsHetero.SetAutoLayout(True)
        self.plcPlsHetero.SetConstraints(
            LayoutAnchors(self.plcPlsHetero, True, True, True, True))

        self.plc_pls_load = MyPlotCanvas(id_=-1, name='plcPLSloading',
                                         parent=self, pos=(0, 24),
                                         size=(330, 292), style=0,
                                         toolbar=self.parent.parent.tbMain)
        self.plc_pls_load.fontSizeTitle = 10
        self.plc_pls_load.fontSizeAxis = 8
        self.plc_pls_load.enableZoom = True
        self.plc_pls_load.enableLegend = True
        self.plc_pls_load.SetToolTip('')
        self.plc_pls_load.fontSizeLegend = 8
        self.plc_pls_load.SetAutoLayout(True)
        self.plc_pls_load.SetConstraints(
            LayoutAnchors(self.plc_pls_load, True, True, True, True))

        self.titleBar = TitleBar(self, id_=-1,
                                 text="Partial Least Squares Regression",
                                 style=bp.BP_USE_GRADIENT,
                                 alignment=bp.BP_ALIGN_LEFT)

        self._init_coll_nb_full_pls_pages(self.nb_full_pls)
        self._init_coll_nb_pls_preds_pages(self.nb_pls_preds)

    def _init_sizers(self):
        # generated method, don't edit
        self.grsPls1 = wx.GridSizer(cols=2, hgap=2, rows=2, vgap=2)
        self.bxsPls1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bxsPls2 = wx.BoxSizer(orient=wx.VERTICAL)

        self.grsPls1.Add(self.nb_pls_preds, 0, border=0, flag=wx.EXPAND)
        self.grsPls1.Add(self.plc_pls_load, 0, border=0, flag=wx.EXPAND)
        self.grsPls1.Add(self.nb_full_pls, 0, border=0, flag=wx.EXPAND)
        self.grsPls1.Add(self.plcPlsHetero, 0, border=0, flag=wx.EXPAND)
        self.bxsPls1.Add(self.bxsPls2, 1, border=0, flag=wx.EXPAND)
        self.bxsPls2.Add(self.titleBar, 0, border=0, flag=wx.EXPAND)
        self.bxsPls2.Add(self.grsPls1, 1, border=0, flag=wx.EXPAND)

        self.SetSizer(self.bxsPls1)

    def _init_coll_nb_full_pls_pages(self, parent):
        """"""
        parent.AddPage(imageId=-1, page=self.plcPLSerror,
                       select=True, text='PLS Error')
        parent.AddPage(imageId=-1, page=self.plcPlsStats,
                       select=False, text='OLS Results ')
    
    def _init_coll_nb_pls_preds_pages(self, parent):
        """"""
        parent.AddPage(imageId=-1, page=self.plc_pred_pls1,
                       select=True, text='dummy')

    # noinspection PyPep8Naming
    def Reset(self):
        self.titleBar.spnPLSfactor1.Enable(0)
        self.titleBar.spnPLSfactor2.Enable(0)
        self.titleBar.spnPLSfactor1.SetValue(1)
        self.titleBar.spnPLSfactor2.SetValue(2)
        
        # delete multiple scores plots
        self.plc_pred_pls1.parent.SetSelection(0)
        self.plc_pred_pls1.parent.SetPageText(0, '')
        # self.plcPredPls1.prnt.SetTabSize((0, 1))
        for page in range(self.plc_pred_pls1.parent.GetPageCount() - 1, 0, -1):
            self.plc_pred_pls1.parent.DeletePage(page)
        
        objects = {
            'plcPLSerror': ['RMS Error', 'Latent Variable', 'RMS Error'],
            'plc_pred_pls1': ['PLS Predictions', 'Actual', 'Predicted'],
            'plcPlsHetero': ['Residuals vs. Predicted Values', 'Predicted',
                             'Residuals'],
            'plc_pls_load': ['PLS Loading', 'w*c[1]', 'w*c[2]']}

        # noinspection PyTypeChecker, PyUnusedLocal
        curve = PolyLine([[0, 0], [1, 1]], colour='white',
                         width=1, style=wx.PENSTYLE_TRANSPARENT)
        
        for each in objects:
            exec('self.' + each + '.Draw(PlotGraphics([curve], ' +
                 'objects["' + each + '"][0], ' +
                 'objects["' + each + '"][1], ' +
                 'objects["' + each + '"][2]))')


class TitleBar(bp.ButtonPanel):
    """"""
    def __init__(self, parent, id_, text, style, alignment):
        """"""
        bp.ButtonPanel.__init__(self, parent=parent, id=-1,
                                text="Partial Least Squares Regression",
                                agwStyle=bp.BP_USE_GRADIENT,
                                alignment=bp.BP_ALIGN_LEFT)

        _, _, _, _ = id_, text, style, alignment
        self.parent = parent
        self.plsError = None
        self.data = None

        self._init_btnpanel_ctrls()
        self.create_btns()

    def _init_btnpanel_ctrls(self):
        """"""
        self.cbxData = wx.Choice(choices=['Raw spectra', 'Processed spectra'],
                                 id=-1, name='cbxData', parent=self,
                                 pos=(118, 21),
                                 size=(90, 23), style=0)
        self.cbxData.SetSelection(0)
        
        self.cbxType = wx.Choice(choices=['PLSR', 'PLS-DA'], id=-1,
                                 name='cbxType', parent=self,
                                 pos=(75, 21),
                                 size=(50, 23), style=0)
        self.cbxType.SetSelection(0)

        choices = ['Correlation matrix', 'Covariance matrix']
        self.cbxPreprocType = wx.Choice(choices=choices, id=-1,
                                        name='cbxPreprocType', parent=self,
                                        pos=(118, 23),
                                        size=(110, 23), style=0)
        self.cbxPreprocType.SetSelection(0)
                                
        self.spnPLSmaxfac = wx.SpinCtrl(id=-1, initial=2, max=100, min=1,
                                        name='spnPLSmaxfac', parent=self,
                                        pos=(54, 72),
                                        size=(54, 23),
                                        style=wx.SP_ARROW_KEYS)
        self.spnPLSmaxfac.SetValue(1)
        self.spnPLSmaxfac.SetToolTip('')

        bmp = wx.Bitmap(os.path.join('bmp', 'run.png'), wx.BITMAP_TYPE_PNG)
        self.btnRunFullPls = bp.ButtonInfo(self, -1, bmp, kind=wx.ITEM_NORMAL,
                                           shortHelp='Run PLS',
                                           longHelp='Run Partial Least Squares')
        self.btnRunFullPls.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.on_btn_run_full_pls, id=self.btnRunFullPls.GetId())
        
        self.spnPLSfactor1 = wx.SpinCtrl(id=-1, initial=1, max=100, min=1,
                                         name='spnPLSfactor1', parent=self,
                                         pos=(228, 4),
                                         size=(46, 23),
                                         style=wx.SP_ARROW_KEYS)
        self.spnPLSfactor1.SetToolTip('')
        self.spnPLSfactor1.Enable(0)
        self.spnPLSfactor1.Bind(wx.EVT_SPINCTRL,
                                self.on_spn_pl_sfactor1, id=-1)
        
        self.spnPLSfactor2 = wx.SpinCtrl(id=-1, initial=2, max=100, min=1,
                                         name='spnPLSfactor2', parent=self,
                                         pos=(228, 4),
                                         size=(46, 23),
                                         style=wx.SP_ARROW_KEYS)
        self.spnPLSfactor2.SetToolTip('')
        self.spnPLSfactor2.Enable(0)
        self.spnPLSfactor2.Bind(wx.EVT_SPINCTRL,
                                self.on_spn_pl_sfactor2, id=-1)

        bmp = wx.Bitmap(os.path.join('bmp', 'export.png'), wx.BITMAP_TYPE_PNG)
        self.btnExpPls = bp.ButtonInfo(self, -1, bmp, kind=wx.ITEM_NORMAL,
                                       shortHelp='Export PLS Results',
                                       longHelp='Export PLS Results')
        self.btnExpPls.Enable(False)
        self.Bind(wx.EVT_BUTTON,
                  self.on_btn_exp_pls, id=self.btnExpPls.GetId())

    def create_btns(self):
        self.Freeze()
        self.SetProperties()
                    
        self.AddControl(self.cbxData)
        self.AddControl(self.cbxType)
        self.AddControl(self.cbxPreprocType)
        self.AddControl(GenStaticText(self, -1, 'Max. factors', style=wx.TRANSPARENT_WINDOW))
        self.AddControl(self.spnPLSmaxfac)
        self.AddSeparator()
        self.AddControl(GenStaticText(self, -1, 'PLS factor', style=wx.TRANSPARENT_WINDOW))
        self.AddControl(self.spnPLSfactor1)
        self.AddControl(GenStaticText(self, -1, ' vs. ', style=wx.TRANSPARENT_WINDOW))
        self.AddControl(self.spnPLSfactor2)
        self.AddSeparator()
        self.AddButton(self.btnRunFullPls)
        self.AddSeparator()
        self.AddButton(self.btnExpPls)
        
        self.Thaw()
        self.DoLayout()
    
    def get_data(self, data):
        self.data = data

    # noinspection PyPep8Naming
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
    
    def on_btn_run_full_pls(self, _):
        self.run_pls()
    
    def on_spn_pl_sfactor1(self, _):
        self.plot_pls_scores()
        self.plot_pls_loads()
    
    def on_spn_pl_sfactor2(self, _):
        self.plot_pls_scores()
        self.plot_pls_loads()
    
    def on_btn_exp_pls(self, _):
        dlg = wx.FileDialog(self, "Choose a file", ".", "", 
                            "Any files (*.*)|*.*", wx.FD_SAVE)
        try:
            # here
            if dlg.ShowModal() == wx.ID_OK:
                saveFile = dlg.GetPath()
                # prepare prediction output
                pred = np.concatenate(
                    (np.array(self.data['validation'])[:, nax],
                     self.data['class'], self.data['plspred']), 1)
                
                out = '#PARTIAL_LEAST_SQUARES_PREDICTIONS\nValidation\t'
                klass_range = self.data['class'].shape[1]
                for i in range(klass_range):
                    out = out + 'Y' + str(i) + '\t'
                for i in range(klass_range):
                    out = out + 'P' + str(i) + '\t'
                    
                out = out + '\n' + np.array2string(np.array(pred), col_sep='\t') + '\n' +\
                    '#PARTIAL_LEAST_SQUARES_LOADINGS\n' +\
                    np.array2string(self.data['plsloads'], col_sep='\t') + '\n' +\
                    '#NUMBER_OF_PLS_FACTORS\n' + str(self.data['plsfactors']+1) + '\n' +\
                    '#ROOT_MEAN_SQUARED_ERROR_OF_CALIBRATION\n' + str(self.data['rmsec']) + '\n' +\
                    '#ROOT_MEAN_SQUARED_ERROR_OF_CROSS_VALIDATION\n' + str(self.data['rmsepc']) + '\n' +\
                    '#ROOT_MEAN_SQUARED_ERROR_FOR_INDEPENDENT_TEST_SAMPLES\n' + str(self.data['rmsept']) + '\n' +\
                    '#PARTIAL_PREDICTION\n' + np.array2string(self.data['partial_pred'], col_sep='\t') + '\n' +\
                    '#SPECTRAL SCORES\n' + np.array2string(self.data['plst'], col_sep='\t')
                with open(saveFile, 'w') as f:
                    f.write(out)

        except Exception as error:
            error_box(self, '%s' % str(error))
            raise
        finally:
            dlg.Destroy()

    # noinspection PyProtectedMember
    def run_pls(self):
        klass = self.data['class']
        xdata = None
        try:
            # Get X
            if self.cbxData.GetSelection() == 0:
                xdata = self.data['rawtrunc']
            elif self.cbxData.GetSelection()  == 1:
                xdata = self.data['proctrunc']
                
            # save preproc type
            self.data['plstype'] = self.cbxType.GetSelection()
            
            # create false pls2 constituent array for pls-da classification
            if self.cbxType.GetSelection() == 1:
                self.data['pls_class'] = -np.ones((len(klass[:, 0]), len(np.unique(klass[:, 0]))))
                uCnt = 0
                for each in np.unique(klass[:, 0]):
                    idx = chemtrics._index(klass[:, 0], each)
                    self.data['pls_class'][idx, uCnt] = np.ones((len(idx), ))
                    uCnt += 1
                
            else:
                self.data['pls_class'] = klass
            
            # Run PLS
            pls_output = chemtrics.pls(xdata, self.data['pls_class'],
                                       self.data['validation'],
                                       self.spnPLSmaxfac.GetValue(),
                                       stb=self.parent.parent.sbMain,
                                       typex=self.cbxPreprocType.GetSelection())
            
            self.data['plsloads'] = pls_output['W']
            self.data['plst'] = pls_output['plsscores']
            self.data['plsfactors'] = pls_output['facs']
            self.data['plspred'] = pls_output['predictions']
            self.data['rmsec'] = pls_output['rmsec']
            self.data['rmsepc'] = pls_output['rmsepc']
            self.data['rmsept'] = pls_output['rmsept']
            self.data['RMSEC'] = pls_output['RMSEC']
            self.data['RMSEPC'] = pls_output['RMSEPC']
            self.data['RMSEPT'] = pls_output['RMSEPT']
            self.data['partial_pred'] = np.transpose(pls_output['b'])

            # plot pls error
            plot_line(self.parent.plcPLSerror,
                      np.concatenate((np.array(self.data['rmsec'])[nax, :],
                                     np.array(self.data['rmsepc'])[nax, :]), 0),
                      xaxis=np.arange(1, len(self.data['rmsec'])+1)[:, nax],
                      rownum=0, tit='Root Mean Squared Error',
                      xLabel='Latent variable', yLabel='RMS Error', type='multi',
                      ledge=['Trn Err', 'Tst Err'], wdth=3)
            
            # plot predicted vs. residuals for train and validation
            trnPlot, valPlot = np.zeros((1, 2)), np.zeros((1, 2))
            npklass = np.array(klass[:, 0])[:, nax]
            validation = self.data['validation']
            validation_idx0 = chemtrics._index(validation, 0)
            validation_idx1 = chemtrics._index(validation, 1)
            plspred = self.data['plspred']

            for p in range(plspred.shape[1]):
                trnData = np.take(plspred[:, p][:, nax],
                                  validation_idx0, axis=0)
                
                trnPlot = np.concatenate(
                    (trnPlot,
                     np.concatenate(
                        (trnData,
                         trnData-np.take(npklass, validation_idx0, 0)), 1)
                     ), 0)
                
                valData = np.take(plspred[:, p][:, nax],
                                  validation_idx1, axis=0)
                      
                valPlot = np.concatenate(
                    (valPlot,
                     np.concatenate(
                         (valData,
                          valData-np.take(npklass, validation_idx1, 0)), 1)
                     ), 0)

            # noinspection PyTypeChecker
            trnObj = PolyMarker(trnPlot[1:len(trnPlot), :], legend='Train',
                                colour='black', marker='square', size=1.25,
                                fillstyle=wx.BRUSHSTYLE_TRANSPARENT)

            # noinspection PyTypeChecker
            valObj = PolyMarker(valPlot[1:len(valPlot), :], legend='Val.',
                                colour='red', marker='circle', size=1.25,
                                fillstyle=wx.BRUSHSTYLE_TRANSPARENT)
            
            PlsHeteroPlot = PlotGraphics([trnObj, valObj],
                                         'Residuals v. Predicted Values',
                                         'Predicted', 'Residuals')
            
            self.parent.plcPlsHetero.draw(PlsHeteroPlot)
            
            # Set max fac for loadings plot
            self.spnPLSfactor1.Enable(1)
            self.spnPLSfactor2.Enable(1)
            self.spnPLSfactor1.SetRange(1, self.spnPLSmaxfac.GetValue())
            self.spnPLSfactor2.SetRange(1, self.spnPLSmaxfac.GetValue())
            self.spnPLSfactor1.SetValue(1)
            self.spnPLSfactor2.SetValue(2)
            
            # plot pls model
            # self.parent.parent.
            self.parent.plc_pred_pls1 = plot_pls_model(
                self.parent.plc_pred_pls1,
                model='full', tbar=self.parent.parent.tbMain,
                cL=klass, scores=self.data['plst'],
                predictions=self.data['plspred'],
                validation=self.data['validation'],
                RMSEPT=self.data['RMSEPT'], factors=self.data['plsfactors'],
                type=self.data['plstype'], col1=0, col2=1,
                label=self.data['label'],
                symbols=self.parent.parent.tbMain.tbSymbols.GetValue(),
                usetxt=self.parent.parent.tbMain.tbPoints.GetValue(),
                usecol=[], usesym=[], errplot=False,
                plScL=self.data['pls_class'])
            
            # draw PLS loadings
            self.plot_pls_loads()
            
            # for pls export
            self.plsError = np.concatenate(
                (np.reshape(self.data['rmsec'], (1, len(self.data['rmsec']))),
                 np.reshape(self.data['rmsepc'], (1, len(self.data['rmsepc'])))
                 ), 0)
            
            # Do OLS on results
            self.do_ols(self.parent.plcPlsStats, self.data['plspred'],
                        klass[:, 0], self.data['validation'],
                        self.data['RMSEC'], self.data['RMSEPC'],
                        self.data['RMSEPT'])
            
            # allow results export
            self.btnExpPls.Enable(1)
                        
        except AttributeError as error:
            error_box(self, '%s' % str(error))
            raise

    # noinspection PyProtectedMember, PyMethodMayBeStatic
    def do_ols(self, writeto, predictions, labels, mask, rmsec, rmsecv, rmset):
        # Do least squares regression on PLS results
        n0, n1, n2 = [], [], []
        for i in range(len(labels)):
            if mask[i] == 0:
                n0.append(labels[i])
            elif mask[i] == 1:
                n1.append(labels[i])
            else:
                n2.append(labels[i])
        
        predy = np.take(predictions, chemtrics._index(mask, 0), axis=0)
        trngrad, trnyi, trnmserr, trnrmserr, trngerr, trnierr = chemtrics.ols(n0, predy)
        
        predyv = np.take(predictions, chemtrics._index(mask, 1), axis=0)
        cvgrad, cvyi, cvmserr, cvrmserr, cvgerr, cvierr = chemtrics.ols(n1, predyv)
        
        if max(mask) == 2:
            predyt = np.take(predictions, chemtrics._index(mask, 2), axis=0)
            tstgrad, tstyi, tstmserr, tstrmserr, tstgerr, tstierr = chemtrics.ols(n2, predyt)
        else:
            tstgrad, tstyi, tstmserr, tstrmserr, tstgerr, tstierr = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            
        # Write to textctrl
        # noinspection PyListCreation
        write = []
        write.append(PolyMarker(np.array([[0, 12]]), marker='text',
                                labels='Root mean squared error'))
        
        write.append(PolyMarker(np.array([[0, 10.5]]), marker='text',
                                labels='Calibration'))
        write.append(PolyMarker(np.array([[12, 10.5]]), marker='text',
                                labels='Validation'))
        write.append(PolyMarker(np.array([[24, 10.5]]), marker='text',
                                labels='Test'))
        write.append(PolyLine([[0, 9.5], [8, 9.5]]))
        write.append(PolyLine([[12, 9.5], [20, 9.5]]))
        write.append(PolyLine([[24, 9.5], [32, 9.5]]))
        write.append(PolyMarker(np.array([[0, 9]]), marker='text',
                                labels='% .2f' % rmsec))
        write.append(PolyMarker(np.array([[12, 9]]), marker='text',
                                labels='% .2f' % rmsecv))
        if max(mask) > 1:
            write.append(PolyMarker(np.array([[24, 9]]), marker='text',
                                    labels='% .2f' % rmset))
        
        write.append(PolyMarker(np.array([[0, 7.5]]), marker='text',
                                labels='Least Squares Regression'))
        
        # write.append(PolyMarker(np.array([[0, 6]]), marker='text',
        #                         labels='Coefficient'))
        # write.append(PolyMarker(np.array([[12, 6]]), marker='text',
        #                         labels='Standard Error'))
        # write.append(PolyLine([[0, 5], [8, 5]]))
        # write.append(PolyLine([[12, 5], [20, 5]]))
        # write.append(PolyMarker(np.array([[0, 4.5]]), marker='text',
        #                         labels='%.2f' %trngerr))
        # write.append(PolyMarker(np.array([[12, 4.5]]), marker='text',
        #                         labels='%.2f' %trnierr[0]))
        # train
        write.append(PolyMarker(np.array([[0, 6]]), marker='text',
                                labels='Train Intercept (Error)'))
        write.append(PolyMarker(np.array([[12, 6]]), marker='text',
                                labels='Train Slope (Error)'))
        write.append(PolyLine([[0, 5], [8, 5]]))
        write.append(PolyLine([[12, 5], [20, 5]]))
        write.append(PolyMarker(np.array([[0, 4.5]]), marker='text',
                                labels='%.2f (%.2f)' % (trnyi[0], trnierr[0])))
        write.append(PolyMarker(np.array([[12, 4.5]]), marker='text',
                                labels='%.2f (%.2f)' % (trngrad[0], trngerr)))

        # cross-validation
        write.append(PolyMarker(np.array([[0, 3]]), marker='text',
                                labels='Val. Intercept (Error)'))
        write.append(PolyMarker(np.array([[12, 3]]), marker='text',
                                labels='Val. Slope (Error)'))
        write.append(PolyLine([[0, 2], [8, 2]]))
        write.append(PolyLine([[12, 2], [20, 2]]))
        write.append(PolyMarker(np.array([[0, 1.5]]), marker='text',
                                labels='%.2f (%.2f)' % (cvyi[0], cvierr[0])))
        write.append(PolyMarker(np.array([[12, 1.5]]), marker='text',
                                labels='%.2f (%.2f)' % (cvgrad[0], cvgerr)))
        
        # test
        if max(mask) > 1:
            write.append(PolyMarker(np.array([[0, 0]]), marker='text',
                                    labels='Test Intercept (Error)'))
            write.append(PolyMarker(np.array([[12, 0]]), marker='text',
                                    labels='Test Slope (Error)'))
            write.append(PolyLine([[0, -1], [8, -1]]))
            write.append(PolyLine([[12, -1], [20, -1]]))
            write.append(PolyMarker(np.array([[0, -1.5]]), marker='text',
                                    labels='%.2f' % tstyi[0] + ' (' + '%.2f' % tstierr[0] + ')'))
            write.append(PolyMarker(np.array([[12, -1.5]]), marker='text',
                                    labels='%.2f' % tstgrad[0] + ' (' + '%.2f' % tstgerr + ')'))
                                
        # filler
        write.append(PolyMarker(np.array([[0, -3]]),
                                marker='text', labels=''))
                                    
        write = PlotGraphics(write)
        
        writeto.draw(write)
        
    def plot_pls_loads(self):
        # Plot loadings
        if self.spnPLSfactor1.GetValue() != self.spnPLSfactor2.GetValue():
            plot_loads(self.parent.plc_pls_load, self.data['plsloads'],
                       xaxis=self.data['indlabels'],
                       col1=self.spnPLSfactor1.GetValue()-1,
                       col2=self.spnPLSfactor2.GetValue()-1,
                       title='PLS Loadings',
                       xLabel='w*c[%i]' % self.spnPLSfactor1.GetValue(),
                       yLabel='w*c[%i]' % self.spnPLSfactor2.GetValue(),
                       type=self.parent.prnt.prnt.tbMain.get_load_plot_idx(),
                       usecol=[], usesym=[])
        else:
            idx = self.spnPLSfactor1.GetValue()-1
            plot_line(self.parent.plc_pls_load,
                      np.transpose(self.data['plsloads']),
                      xaxis=self.data['xaxis'], tit='PLS Loadings', rownum=idx,
                      type='single', xLabel='Variable',
                      yLabel='w*c[' + str(idx+1) + ']', wdth=1, ledge=[])
        
    def plot_pls_scores(self):
        """Plot scores for pls-da.

        """
        if self.data['plstype'] == 1:
            tb_main = self.parent.prnt.parent.tbMain
            self.parent.plc_pred_pls1 = \
                plot_pls_model(self.parent.plc_pred_pls1, model='full',
                               tbar=tb_main,
                               cL=self.data['class'], scores=self.data['plst'],
                               predictions=None,
                               label=self.data['label'],
                               validation=self.data['validation'],
                               RMSEPT=None, factors=None, type=1,
                               col1=self.spnPLSfactor1.GetValue()-1,
                               col2=self.spnPLSfactor2.GetValue()-1,
                               symbols=tb_main.tbSymbols.GetValue(),
                               usetxt=tb_main.tbPoints.GetValue(),
                               usecol=[], usesym=[], plScL=self.data['pls_class'])
                

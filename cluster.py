# -----------------------------------------------------------------------------
# Name:        cluster.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2007/05/22
# RCS-ID:      $Id: cluster.py, v 1.12 2009/02/26 22:19:46 rmj01 Exp $
# Copyright:   (c) 2006
# Licence:     GNU General Public Licence
# -----------------------------------------------------------------------------

import os
import numpy as np

import wx
import wx.lib.buttons
import wx.lib.agw.buttonpanel as bp
import wx.lib.agw.foldpanelbar as fpb
from wx.lib.anchors import LayoutAnchors
from wx.lib.plot.polyobjects import PolyLine, PlotGraphics
# from wx.lib.plot.polyobjects import PolyMarker

from commons import error_box
from commons import PolyMarker

from Bio.Cluster import kcluster, treecluster
from Bio.Cluster import distancematrix, clustercentroids
from Bio.Cluster import kmedoids

from pca import MyPlotCanvas

[wxID_CLUSTER, ] = [wx.NewId() for _init_ctrls in range(1)]

[wxID_SELFUN, wxID_SELFUNCBAVLINK, wxID_SELFUNCBCENTLINK, 
 wxID_SELFUNCBMAXLINK, wxID_SELFUNCBSINGLELINK, wxID_SELFUNCBUSECLASS, 
 wxID_SELFUNRBABSCORR, wxID_SELFUNRBABSUNCENTCORR, wxID_SELFUNRBCITYBLOCK, 
 wxID_SELFUNRBCORRELATION, wxID_SELFUNRBEUCLIDEAN, wxID_SELFUNRBHARMONICEUC, 
 wxID_SELFUNRBHCLUSTER, wxID_SELFUNRBKENDALLS, wxID_SELFUNRBKMEANS, 
 wxID_SELFUNRBKMEDIAN, wxID_SELFUNRBKMEDOIDS, wxID_SELFUNRBPLOTCOLOURS, 
 wxID_SELFUNRBPLOTNAME, wxID_SELFUNRBSPEARMANS, wxID_SELFUNRBUNCENTREDCORR, 
 wxID_SELFUNSPNNOPASS, wxID_SELFUNSTATICBOX1, wxID_SELFUNSTATICBOX2, 
 wxID_SELFUNSTNOPASS, 
 ] = [wx.NewId() for _init_selfun_ctrls in range(25)]


class Cluster(wx.Panel):
    """"""
    def __init__(self, parent, id_, pos, size, style, name):
        """"""
        _, _, _, _, _ = id_, pos, size, style, name

        wx.Panel.__init__(self, id=wxID_CLUSTER, name='Cluster', parent=parent,
                          pos=wx.Point(72, 35), size=wx.Size(907, 670),
                          style=wx.TAB_TRAVERSAL)

        self._init_ctrls(parent)
        self.parent = parent

    def _init_coll_bxs_clust1_items(self, parent):
        """ """

        parent.Add(self.bxsClust2, 1, border=0, flag=wx.EXPAND)

    def _init_coll_bxs_clust2_items(self, parent):
        """"""
        parent.Add(self.titleBar, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.Splitter, 1, border=0, flag=wx.EXPAND)

    def _init_cluster_sizers(self):
        """"""
        self.bxsClust1 = wx.BoxSizer(orient=wx.HORIZONTAL)
        self.bxsClust2 = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_bxs_clust1_items(self.bxsClust1)
        self._init_coll_bxs_clust2_items(self.bxsClust2)
        
        self.SetSizer(self.bxsClust1)
    
    def _init_ctrls(self, prnt):
        """ """
        self.SetToolTip('')
        self.SetAutoLayout(True)
        self.prnt = prnt
        
        self.Splitter = wx.SplitterWindow(id=-1, name='Splitter', parent=self,
                                          pos=wx.Point(16, 24),
                                          size=wx.Size(272, 168),
                                          style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        self.Splitter.SetAutoLayout(True)
        self.Splitter.Bind(wx.EVT_SPLITTER_DCLICK, self.on_splitter_dclick)
        
        self.p1 = wx.Panel(self.Splitter)
        self.p1.SetAutoLayout(True)
        self.p1.Show(True)
        
        self.optDlg = SelFun(self.Splitter)
        
        self.plcCluster = MyPlotCanvas(id_=-1, name='plcCluster', parent=self.p1,
                                       pos=wx.Point(0, 0),
                                       size=wx.Size(200, 200),
                                       style=wx.SUNKEN_BORDER,
                                       toolbar=self.prnt.parent.tbMain)
        self.plcCluster.SetToolTip('')
        self.plcCluster.enableZoom = True
        self.plcCluster.fontSizeTitle = 12
        self.plcCluster.fontSizeAxis = 12
        self.plcCluster.xSpec = 'none'
        self.plcCluster.ySpec = 'none'
        self.plcCluster.SetConstraints(
            LayoutAnchors(self.plcCluster, True, True, True, True))
        
        self.txtCluster = wx.TextCtrl(
            id=-1, name='txtCluster', parent=self.p1,
            pos=wx.Point(0, 0), size=wx.Size(200, 200),
            style=wx.TE_DONTWRAP | wx.HSCROLL | wx.TE_READONLY |
            wx.SUNKEN_BORDER | wx.TE_MULTILINE | wx.VSCROLL,
            value='')
        self.txtCluster.SetToolTip('')
        self.txtCluster.SetConstraints(
            LayoutAnchors(self.txtCluster, True, True, True, True))
        self.txtCluster.Show(False)
        
        self.titleBar = TitleBar(self, id_=-1, text="Cluster Analysis",
                                 style=bp.BP_USE_GRADIENT,
                                 alignment=bp.BP_ALIGN_LEFT)
        
        self.Splitter.SplitVertically(self.optDlg, self.p1, 1)
        self.Splitter.SetMinimumPaneSize(1)
        
        self._init_cluster_sizers()

    def reset(self):
        """"""
        # noinspection PyTypeChecker
        curve = PolyLine([[0, 0], [1, 1]], colour='white', width=1,
                         style=wx.PENSTYLE_TRANSPARENT)
        curve = PlotGraphics([curve], 'Hierarchical Cluster Analysis', '', '')

        self.plcCluster.Draw(curve)
        
    def on_splitter_dclick(self, _):
        if self.Splitter.GetSashPosition() <= 5:
            self.Splitter.SetSashPosition(250)
        else:
            self.Splitter.SetSashPosition(1)
        
    
class TitleBar(bp.ButtonPanel):
    """"""
    def __init__(self, parent, id_, text, style, alignment):
        """"""
        bp.ButtonPanel.__init__(self, parent=parent, id=-1,
                                text="Cluster Analysis",
                                agwStyle=bp.BP_USE_GRADIENT,
                                alignment=bp.BP_ALIGN_LEFT)

        _, _, _, _ = id_, text, style, alignment
        self._init_btnpanel_ctrls()
        self.create_btns()
        self.parent = parent
        self.data = None
        self.clusterid = None

    def _init_btnpanel_ctrls(self):
        """ """
        choices = ['Raw spectra', 'Processed spectra', 'PC Scores', 'DF Scores']
        self.cbxData = wx.Choice(choices=choices, id=-1, name='cbxData',
                                 parent=self, pos=wx.Point(118, 21),
                                 size=wx.Size(100, 23), style=0)
        self.cbxData.SetSelection(0)
        
        bmp = wx.Bitmap(os.path.join('bmp', 'run.png'), wx.BITMAP_TYPE_PNG)
        self.btnRunClustering = bp.ButtonInfo(self, -1, bmp,
                                              kind=wx.ITEM_NORMAL,
                                              shortHelp='Run Cluster Analysis',
                                              longHelp='Run Cluster Analysis')
        self.btnRunClustering.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.on_btn_run_cluster,
                  id=self.btnRunClustering.GetId())

        bmp = wx.Bitmap(os.path.join('bmp', 'export.png'), wx.BITMAP_TYPE_PNG)
        self.btnExportCluster = bp.ButtonInfo(self, -1, bmp,
                                              kind=wx.ITEM_NORMAL,
                                              shortHelp='Export Cluster Results',
                                              longHelp='Export Cluster Results')
        self.btnExportCluster.Enable(False)
        self.Bind(wx.EVT_BUTTON, self.on_btn_export_cluster,
                  id=self.btnExportCluster.GetId())

        bmp = wx.Bitmap(os.path.join('bmp', 'params.png'), wx.BITMAP_TYPE_PNG)
        self.setParams = bp.ButtonInfo(self, -1, bmp,
                                       kind=wx.ITEM_NORMAL,
                                       shortHelp='Clustering Options',
                                       longHelp='Clustering Options')
        self.Bind(wx.EVT_BUTTON, self.on_btn_set_params,
                  id=self.setParams.GetId())

    def create_btns(self):
        self.Freeze()
        self.SetProperties()
        
        self.AddControl(self.cbxData) 
        self.AddSeparator()           
        self.AddButton(self.setParams)
        self.AddSeparator()
        self.AddButton(self.btnRunClustering)
        self.AddSeparator()
        self.AddButton(self.btnExportCluster)
        
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

    # noinspection PyMethodMayBeStatic
    def on_btn_export_cluster(self, event):
        event.Skip()
    
    def on_btn_set_params(self, _):
        if self.parent.splitter.GetSashPosition() <= 5:
            self.parent.splitter.SetSashPosition(250)
        else:
            self.parent.splitter.SetSashPosition(1)
        
    def on_btn_run_cluster(self, _):
        self.run_cluster()
    
    def run_cluster(self):
        # hierarchical cluster analysis
        klass = self.data['class'][:, 0]
        opt = self.parent.optDlg
        xdata = None
        seldist = ''
        hmeth = ''

        try:
            # get x-data
            if self.cbxData.GetSelection() == 0:
                xdata = self.data['rawtrunc']
            elif self.cbxData.GetSelection() == 1:
                xdata = self.data['proctrunc']
            elif self.cbxData.GetSelection() == 2:
                xdata = self.data['pcscores']
            elif self.cbxData.GetSelection() == 3:
                xdata = self.data['dfscores']
            
            # get distance measure
            if opt.rbEuclidean.GetValue():
                seldist = 'e'
            elif opt.rbCorrelation.GetValue():
                seldist = 'c'
            elif opt.rbAbsCorr.GetValue():
                seldist = 'a'
            elif opt.rbUncentredCorr.GetValue():
                seldist = 'u'
            elif opt.rbAbsUncentCorr.GetValue():
                seldist = 'x'
            elif opt.rbSpearmans.GetValue():
                seldist = 's'
            elif opt.rbKendalls.GetValue():
                seldist = 'k'
            elif opt.rbCityBlock.GetValue():
                seldist = 'b'
            
            # run clustering
            if opt.rbKmeans.GetValue():
                if opt.spnNoPass.GetValue() == 1:
                    stid = (np.array(klass, 'i')-1).tolist()
                    self.clusterid, error, nfound = \
                        kcluster(xdata,
                                 nclusters=len(np.unique(self.data['class'])),
                                 transpose=0, npass=1, method='a', dist=seldist,
                                 initialid=stid)
                else:
                    self.clusterid, error, nfound = \
                        kcluster(xdata,
                                 nclusters=len(np.unique(klass)),
                                 transpose=0, npass=opt.spnNoPass.GetValue(),
                                 method='a', dist=seldist)
                                                                
                self.parent.plcCluster.Show(False)
                self.parent.txtCluster.Show(True)
                
                centroids, mask = clustercentroids(xdata,
                                                   clusterid=self.clusterid,
                                                   method='a', transpose=0)
        
                self.report_partitioning(self.parent.txtCluster, self.clusterid,
                                         error, nfound, 'K-means Summary',
                                         centroids)
                
            elif opt.rbKmedian.GetValue() is True:
                if opt.spnNoPass.GetValue() == 1:
                    stid = (np.array(klass, 'i')-1).tolist()
                    self.clusterid, error, nfound = \
                        kcluster(xdata,
                                 nclusters=len(np.unique(klass)),
                                 npass=1, method='m', dist=seldist,
                                 initialid=stid)
                else:
                    self.clusterid, error, nfound = \
                        kcluster(xdata,
                                 nclusters=len(np.unique(klass)),
                                 npass=opt.spnNoPass.GetValue(),
                                 method='m', dist=seldist)
                
                self.parent.plcCluster.Show(False)
                self.parent.txtCluster.Show(True)
                
                centroids, mask = clustercentroids(
                    xdata, mask=np.ones(xdata.shape),
                    clusterid=self.clusterid, method='m', transpose=0)
                
                self.report_partitioning(self.parent.txtCluster, self.clusterid,
                                         error, nfound, 'K-medians Summary',
                                         centroids)
            
            elif opt.rbKmedoids.GetValue() is True:
                # generate distance matrix
                distance = distancematrix(xdata, transpose=0, dist=seldist)
                
                if opt.spnNoPass.GetValue() == 1:
                    stid = (np.array(klass, 'i')-1).tolist()
                    self.clusterid, error, nfound = \
                        kmedoids(distance, nclusters=len(np.unique(klass)),
                                 npass=1, initialid=stid)
                else:
                    self.clusterid, error, nfound = \
                        kmedoids(distance, nclusters=len(np.unique(klass)),
                                 npass=opt.spnNoPass.GetValue())
                
                # rename cluster ids
                for i in range(len(self.clusterid)):
                    self.clusterid[i] = klass[self.clusterid[i]]-1
                
                self.parent.plcCluster.Show(False)
                self.parent.txtCluster.Show(True)
                
                self.report_partitioning(self.parent.txtCluster, self.clusterid,
                                         error, nfound, 'K-medoids Summary')
                
            elif opt.rbHcluster.GetValue():
                # get clustering method
                if opt.rbSingleLink.GetValue():
                    hmeth = 's'
                elif opt.rbMaxLink.GetValue():
                    hmeth = 'm'
                elif opt.rbAvLink.GetValue():
                    hmeth = 'a'
                elif opt.rbCentLink.GetValue():
                    hmeth = 'c'
                    
                # run hca
                tree = treecluster(data=xdata, method=hmeth, dist=seldist)
                
                # scale tree
                tree.scale()
                
                # divide into clusters
# #                tree.cut(len(np.unique(klass)))
                
                # determine tree structure
                self.data['tree'], self.data['order'] = \
                    self.treestructure(tree, np.arange(len(tree)+1))
                      
                # draw tree
                self.draw_tree(self.parent.plcCluster, self.data['tree'],
                               self.data['order'], self.data['label'])

                self.parent.plcCluster.Show(True)
                self.parent.txtCluster.Show(False)
                    
                #   enable export
                #   if opt.rbHcluster.GetValue() is True:
                #       self.btnExportCluster.Enable(1)
                #   else:
                #   self.btnExportCluster.Enable(0)
        except Exception as error:
            error_box(self, '%s' % str(error))
            raise

    def treestructure(self, tree, order):
        # determine hierarchical tree structure
        clusters, nodedist = [], []
        nodes = tree[:]
        
        for i in range(len(tree)):
            clusters.append([nodes[i].left, nodes[i].right])
            nodedist.append([nodes[i].distance])
        
        nnodes = len(tree)
        
        nodeid = np.zeros((nnodes, 4), 'd')
        nodecounts = np.zeros(nnodes)
        nodeorder = np.zeros(nnodes, 'd')
        nodedist = np.array(nodedist)
        for nodeindex in range(nnodes):
            min1 = clusters[nodeindex][0]
            min2 = clusters[nodeindex][1]
            nodeid[nodeindex, 0] = nodeindex
            if min1 < 0:
                index1 = -min1-1
                order1 = nodeorder[index1]
                counts1 = nodecounts[index1]
                nodeid[nodeindex, 1] = min1
            else:
                order1 = order[min1]
                counts1 = 1
                nodeid[nodeindex, 1] = min1
            if min2 < 0:
                index2 = -min2-1
                order2 = nodeorder[index2]
                counts2 = nodecounts[index2]
                nodeid[nodeindex, 2] = min2
            else:
                order2 = order[min2]
                counts2 = 1
                nodeid[nodeindex, 2] = min2
            nodeid[nodeindex, 3] = nodedist[nodeindex]
            nodecounts[nodeindex] = counts1 + counts2
            nodeorder[nodeindex] = \
                (counts1*order1+counts2*order2) / (counts1+counts2)
        
        # Now set up order based on the tree structure
        index = self.treeindex(clusters, nodedist, order)
        
        return nodeid, index

    def treeindex(self, clusters, linkdist, order):
        """"""
        nnodes = len(clusters)
        nodecounts = np.zeros(nnodes)
        nodeorder = np.zeros(nnodes, 'd')
        nodedist = np.array(linkdist)
        for nodeindex in range(nnodes):
            min1 = clusters[nodeindex][0]
            min2 = clusters[nodeindex][1]
            if min1 < 0:
                index1 = -min1 - 1
                order1 = nodeorder[index1]
                counts1 = nodecounts[index1]
                nodedist[nodeindex] = max(nodedist[nodeindex], nodedist[index1])
            else:
                order1 = order[min1]
                counts1 = 1

            if min2 < 0:
                index2 = -min2 - 1
                order2 = nodeorder[index2]
                counts2 = nodecounts[index2]
                nodedist[nodeindex] = max(nodedist[nodeindex], nodedist[index2])
            else:
                order2 = order[min2]
                counts2 = 1
            nodecounts[nodeindex] = counts1 + counts2
            nodeorder[nodeindex] = (counts1 * order1 + counts2 * order2) / (
                        counts1 + counts2)
        # Now set up order based on the tree structure
        index = self.treesort(order, nodeorder, nodecounts, clusters)
        return index

    # noinspection PyMethodMayBeStatic
    def treesort(self, order, nodeorder, nodecounts, NodeElement):
        nNodes = len(NodeElement)
        nElements = nNodes + 1
        neworder = np.zeros(nElements, 'd')
        clusterids = list(range(nElements))
        for i in range(nNodes):
            i1 = NodeElement[i][0]
            i2 = NodeElement[i][1]
            if i1 < 0:
                order1 = nodeorder[-i1 - 1]
                count1 = nodecounts[-i1 - 1]
            else:
                order1 = order[i1]
                count1 = 1
            if i2 < 0:
                order2 = nodeorder[-i2 - 1]
                count2 = nodecounts[-i2 - 1]
            else:
                order2 = order[i2]
                count2 = 1
            # If order1 and order2 are equal, their order is determined
            # by the order in which they were clustered
            if i1 < i2:
                if order1 < order2:
                    increase = count1
                else:
                    increase = count2
                for j in range(nElements):
                    clusterid = clusterids[j]
                    if clusterid == i1 and order1 >= order2:
                        neworder[j] += increase
                    if clusterid == i2 and order1 < order2:
                        neworder[j] += increase
                    if clusterid == i1 or clusterid == i2:
                        clusterids[j] = -i - 1
            else:
                if order1 <= order2:
                    increase = count1
                else:
                    increase = count2
                for j in range(nElements):
                    clusterid = clusterids[j]
                    if clusterid == i1 and order1 > order2:
                        neworder[j] += increase
                    if clusterid == i2 and order1 <= order2:
                        neworder[j] += increase
                    if clusterid == i1 or clusterid == i2:
                        clusterids[j] = -i - 1
        return np.argsort(neworder)

    # noinspection PyTypeChecker, PyMethodMayBeStatic
    def draw_tree(self, canvas, tree, order, labels, tit='', xL='', yL=''):
        """      """
        # colourList = ['BLUE', 'BROWN', 'CYAN', 'GREY', 'GREEN', 'MAGENTA',
        #               'ORANGE', 'PURPLE', 'VIOLET']

        # TODO: Reactivate labels when PolyMarker get fixed
        _ = labels
        # set font size
        font_size = 8

        canvas.font_size_axis = font_size
        canvas.enable_legend = False
        
        # do level 1
        # List, Cols, ccount = [], [], 0
        # for i in range(len(tree)):
        #     if self.data['class'][:, 0][i] not in List:
        #        List.append(self.data['class'][:, 0][i])
        #        Cols.append(colourList[ccount])
        #        ccount += 1
        #        if ccount == len(colourList):
        #            ccount = 0
        # minx = 0
        # if self.parent.optDlg.rbPlotColours.GetValue() is True:
        #     pass
        #     canvas.enable_legend(1)
        #     Line, List, Nlist, Store = [], [], [], {}
        #     count = 0
        #     for i in range(len(order)):
        #         idn = int(self.data['class'][:, 0][order[i]])
        #         # plot names
        #         if idn in List:
        #            Store[str(idn)] = np.concatenate((Store[str(idn)], [[0, count]]), 0)
        #         else:
        #            Store[str(idn)] = [[0, count]]
        #            List.append(self.data['class'][:, 0][order[i]])
        #            Nlist.append(self.data['label'][order[i]])
        #        count += 2
        #
        #     canvas.SetLegendItems(len(Store))
        #     for i in range(1, len(Store)+1):
        #         Line.append(PolyMarker(Store[str(i)], marker='square', size=font_size,
        #         colour=Cols[i-1], legend=Nlist[i-1]))

        # elif self.parent.optDlg.rbPlotName.GetValue() is True:

        # TODO: Create a new class PolyMaker inheriting from wx PolyMaker and
        #       try to implement method _text and class _attributes 'labels' as
        #       in pychem_305g/plot.py/PolyMarker
        Line = []
        count = 0
        for i in range(len(order)):
            Line.append(PolyMarker(np.array([[0, count], [0, count]]),
                                   marker='text'))
            #                       labels=[labels[int(order[i])],
            #                       labels[int(order[i])]]))
            count += 2
                
        # plot distances
        # TODO: Implement attribute 'labels' in PolyMarker
        Line.append(PolyMarker(np.array([[0, -2]]), marker='text'))   # , labels='0'))
        Line.append(PolyMarker(np.array([[max(tree[:, 3]), -2]]),
                               marker='text'))                        # , labels='% .2f' % max(tree[:, 3])))
        # TODO: idx is not used !!
        # noinspection PyUnusedLocal
        idx = np.reshape(np.arange(len(tree)+1), (len(tree)+1, ))
        Nodes = {}
        y1, y2 = None, None
        for i in range(len(tree)):
            # just samples
            if tree[i, 1] >= 0:
                if tree[i, 2] >= 0:
                    # sample 1
                    x1 = 0
                    x2 = tree[i, 3]
                    pos = order == int(tree[i, 1])
                    pos = pos.tolist()
                    for iix in range(len(pos)):
                        if pos[iix] == 1:
                            y1 = iix*2
                    Line.append(PolyLine(np.array([[x1, y1], [x2, y1]]),
                                         colour='black', width=1.5,
                                         style=wx.PENSTYLE_SOLID))
                    # sample 2
                    pos = order == int(tree[i, 2])
                    pos = pos.tolist()
                    for iix in range(len(pos)):
                        if pos[iix] == 1:
                            y2 = iix*2
                    Line.append(PolyLine(np.array([[x1, y2], [x2, y2]]),
                                         colour='black', width=1.5,
                                         style=wx.PENSTYLE_SOLID))
                    # connect
                    Line.append(PolyLine(np.array([[x2, y1], [x2, y2]]),
                                         colour='black', width=1.5,
                                         style=wx.PENSTYLE_SOLID))
                    # save node coord
                    Nodes[str((tree[i, 0]+1)*-1)] = (x2, (y1+y2)/2)
        
        for i in range(len(tree)):
            # nodes & samples
            if tree[i, 1] >= 0:
                if tree[i, 2] < 0:
                    if str(tree[i, 2]) in Nodes:
                        # sample first
                        x1 = 0
                        x2 = tree[i, 3]
                        pos = order == int(tree[i, 1])
                        pos = pos.tolist()
                        for iix in range(len(pos)):
                            if pos[iix] == 1:
                                y1 = iix*2
                        Line.append(PolyLine(np.array([[x1, y1], [x2, y1]]),
                                             colour='black', width=1.5,
                                             style=wx.PENSTYLE_SOLID))
                        # node next
                        if str(tree[i, 2]) in Nodes:
                            x1 = Nodes[str(tree[i, 2])][0]
                            x2 = tree[i, 3]
                            y2 = Nodes[str(tree[i, 2])][1]
                            Line.append(PolyLine(np.array([[x1, y2], [x2, y2]]),
                                                 colour='black', width=1.5,
                                                 style=wx.PENSTYLE_SOLID))
                        # connect
                        Line.append(PolyLine(np.array([[x2, y1], [x2, y2]]),
                                             colour='black', width=1.5,
                                             style=wx.PENSTYLE_SOLID))
                        # save node coord
                        Nodes[str((tree[i, 0]+1)*-1)] = (x2, (y1+y2)/2)
                
            if tree[i, 1] < 0:
                if tree[i, 2] >= 0:
                    if str(tree[i, 1]) in Nodes:
                        # sample first
                        x1 = 0
                        x2 = tree[i, 3]
                        pos = order == int(tree[i, 2])
                        pos = pos.tolist()
                        for iix in range(len(pos)):
                            if pos[iix] == 1:
                                y1 = iix*2
                        Line.append(PolyLine(np.array([[x1, y1], [x2, y1]]),
                                             colour='black', width=1.5,
                                             style=wx.PENSTYLE_SOLID))
                        # node next
                        if str(tree[i, 1]) in Nodes:
                            x1 = Nodes[str(tree[i, 1])][0]
                            x2 = tree[i, 3]
                            y2 = Nodes[str(tree[i, 1])][1]
                            Line.append(PolyLine(np.array([[x1, y2], [x2, y2]]),
                                                 colour='black', width=1.5,
                                                 style=wx.PENSTYLE_SOLID))
                        # connect
                        Line.append(PolyLine(np.array([[x2, y1], [x2, y2]]),
                                             colour='black', width=1.5,
                                             style=wx.PENSTYLE_SOLID))
                        # save node coord
                        Nodes[str((tree[i, 0]+1)*-1)] = (x2, (y1+y2)/2)
            
            if tree[i, 1] < 0:
                if tree[i, 2] < 0:
                    # nodes and nodes
                    # n1
                    x1 = Nodes[str(tree[i, 1])][0]
                    x2 = tree[i, 3]
                    y1 = Nodes[str(tree[i, 1])][1]
                    Line.append(PolyLine(np.array([[x1, y1], [x2, y1]]),
                                         colour='black', width=1.5,
                                         style=wx.PENSTYLE_SOLID))
                    # n2
                    x1 = Nodes[str(tree[i, 2])][0]
                    x2 = tree[i, 3]
                    y2 = Nodes[str(tree[i, 2])][1]
                    Line.append(PolyLine(np.array([[x1, y2], [x2, y2]]),
                                         colour='black', width=1.5,
                                         style=wx.PENSTYLE_SOLID))
                    # connect
                    Line.append(PolyLine(np.array([[x2, y1], [x2, y2]]),
                                         colour='black', width=1.5,
                                         style=wx.PENSTYLE_SOLID))
                    # save node coord
                    Nodes[str((tree[i, 0]+1)*-1)] = (x2, (y1+y2)/2)
                        
        canvas.draw(PlotGraphics(Line, title=tit, xLabel=xL, yLabel=yL))
                
    def report_partitioning(self, textctrl, clusterid,
                            error, nfound, title, centroids=None):
        """"""
        _ = clusterid
        # report summary
        hphn20 = '-' * 23
        hphn10 = '-' * 10
        summary = ''.join((title, '\n', hphn20, '\n\n',
                           'No. clusters\t\tError\t\tNo. optimal soln.\n',
                           hphn20, '\t\t', hphn10, '\t\t', hphn20, '\n',
                           str(max(self.clusterid)+1), '\t\t\t',
                           '% .2f' % error, '\t\t', str(nfound)))
        
        # cluster centres
        if centroids is not None:
            if centroids.shape[1] < 40:
                centres = '\n\nCluster centres\n%s\n\nCluster/X var.' % hphn20
                for i in range(centroids.shape[1]):
                    centres = ''.join((centres, '\t', str(i+1)))
                centres = ''.join((centres, '\n'))
                for i in range(centroids.shape[0]):
                    for j in range(centroids.shape[1]):
                        if j == 0:
                            centres = '\t%s\t%i\t\t%.2f' % (centres, i+1, centroids[i, j])
                        elif 0 < j < centroids.shape[1]-1:
                            centres = '%s%.2f\t' % (centres, centroids[i, j])
                        else:
                            centres = '%s%.2f\n' % (centres, centroids[i, j])
            else:
                centres = '\n\n'
        else:
            centres = '\n\n'
        
        # confusion matrix
        confmat = '\n\nResults confusion matrix\n%s\n\nExp./Pred.' % hphn20

        klass = self.data['class'][:, 0]
        max_klass = int(max(klass))

        for i in range(max_klass):
            confmat = ''.join((confmat, '\t', str(i+1)))
        confmat = ''.join((confmat, '\n'))
        
        confarr = np.zeros((max_klass, max_klass))
        for row in range(len(klass)):
            if klass[row] == self.clusterid[row]+1:
                confarr[self.clusterid[row], self.clusterid[row]] = \
                    confarr[self.clusterid[row], self.clusterid[row]]+1
            else:
                confarr[int(klass[row])-1, self.clusterid[row]] = \
                    confarr[int(klass[row])-1, self.clusterid[row]]+1
        
        for i in range(confarr.shape[0]):
            for j in range(confarr.shape[1]):
                if j == 0:
                    confmat = '%s%i\t\t%s'  % (confmat, i+1, confarr[i, j])
                else:
                    confmat = '%s\t%s' % (confmat, confarr[i, j])
            confmat = ''.join((confmat, '\n'))
                
        report = ''.join((summary, centres, confmat))
        
        textctrl.SetValue(report)

class SelFun(fpb.FoldPanelBar):
    """"""
    def __init__(self, parent):
        fpb.FoldPanelBar.__init__(self, parent, -1, pos=wx.DefaultPosition,
                                  size=wx.DefaultSize,
                                  agwStyle=fpb.FPB_SINGLE_FOLD)

        self._init_selfun_ctrls()

        self.Expand(self.clustType)
        self.Expand(self.distType)
        self.Expand(self.linkType)

    def _init_coll_gbs_cluster_method(self, parent):
        parent.Add(self.rbKmeans, (0, 0), flag=wx.EXPAND, span=(1, 2))
        parent.Add(self.rbKmedian, (1, 0), flag=wx.EXPAND, span=(1, 2))
        parent.Add(self.rbKmedoids, (2, 0), flag=wx.EXPAND, span=(1, 2))
        parent.Add(self.rbHcluster, (3, 0), flag=wx.EXPAND, span=(1, 2))
        parent.Add(wx.StaticText(self.methPnl, -1, 'No. iterations',
                   style=wx.ALIGN_LEFT), (4, 0), flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.spnNoPass, (4, 1), flag=wx.EXPAND, span=(1, 1))
        # parent.AddSpacer(8)
        # parent.AddSpacer(wx.Size(8, 8), (5, 0), flag=wx.EXPAND, span=(2, 2))
        # parent.AddSpacer((8, 8), (5, 0), flag=wx.EXPAND, span=(2, 2))
        # parent.AddSpacer(8, (5, 0), flag=wx.EXPAND, span=(2, 2))
    
    def _init_coll_gbs_link_method(self, parent):
        parent.Add(self.rbSingleLink, (0, 0), flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.rbMaxLink, (1, 0), flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.rbAvLink, (2, 0), flag=wx.EXPAND,  span=(1, 1))
        parent.Add(self.rbCentLink, (3, 0), flag=wx.EXPAND, span=(1, 1))
        # parent.AddSpacer(8)
        # parent.AddSpacer(wx.Size(8, 8), (5, 0), flag=wx.EXPAND, span=(2, 2))
    
    def _init_coll_gbs_distance_measure(self, parent):
        parent.Add(self.rbAbsUncentCorr, (0, 0), flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.rbAbsCorr, (1, 0), flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.rbCityBlock, (2, 0), flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.rbCorrelation, (3, 0), flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.rbEuclidean, (4, 0), flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.rbKendalls, (5, 0), flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.rbSpearmans, (6, 0), flag=wx.EXPAND, span=(1, 1))
        parent.Add(self.rbUncentredCorr, (7, 0), flag=wx.EXPAND, span=(1, 1))
        # parent.AddSpacer(8)
        # parent.AddSpacer(wx.Size(8, 8), (5, 0), flag=wx.EXPAND, span=(2, 2))
              
    def _init_selparam_sizers(self):
        self.gbsClusterMethod = wx.GridBagSizer(5, 5)
        self.gbsLinkageMethod = wx.GridBagSizer(5, 5)
        self.gbsDistanceMeasure = wx.GridBagSizer(5, 5)
        
        self._init_coll_gbs_cluster_method(self.gbsClusterMethod)
        self._init_coll_gbs_link_method(self.gbsLinkageMethod)
        self._init_coll_gbs_distance_measure(self.gbsDistanceMeasure)
        
        self.gbsClusterMethod.AddGrowableCol(0)
        self.gbsClusterMethod.AddGrowableCol(1)
        self.gbsLinkageMethod.AddGrowableCol(0)
        self.gbsDistanceMeasure.AddGrowableCol(0)
        
        self.clustType.SetSizer(self.gbsClusterMethod)
        self.linkType.SetSizer(self.gbsLinkageMethod)
        self.distType.SetSizer(self.gbsDistanceMeasure)
        
    def _init_selfun_ctrls(self):

        self.SetConstraints(LayoutAnchors(self, True, True, True, True))
        self.SetAutoLayout(True)
        
        icons = wx.ImageList(16, 16)
        icons.Add(wx.Bitmap(os.path.join('bmp', 'arrown.png'), wx.BITMAP_TYPE_PNG))
        icons.Add(wx.Bitmap(os.path.join('bmp', 'arrows.png'), wx.BITMAP_TYPE_PNG))
        
        self.clustType = self.AddFoldPanel("Cluster method", collapsed=True, 
                                           foldIcons=icons)
        
        self.distType = self.AddFoldPanel("Distance measure", 
                                          collapsed=True, foldIcons=icons)
        
        self.linkType = self.AddFoldPanel("Linkage method (HCA)", 
                                          collapsed=True, foldIcons=icons)
        
        self.methPnl = wx.Panel(id=-1, name='methPnl', parent=self.clustType,
                                pos=wx.Point(0, 0), size=wx.Size(200, 220),
                                style=wx.TAB_TRAVERSAL)
        self.methPnl.SetToolTip('')
        
        self.distPnl = wx.Panel(id=-1, name='distPnl', parent=self.distType,
                                pos=wx.Point(0, 0), size=wx.Size(200, 290),
                                style=wx.TAB_TRAVERSAL)
        self.distPnl.SetToolTip('')     
        
        self.linkPnl = wx.Panel(id=-1, name='linkPnl', parent=self.linkType,
                                pos=wx.Point(0, 0), size=wx.Size(200, 150),
                                style=wx.TAB_TRAVERSAL)
        self.linkPnl.SetToolTip('')        
        
        self.rbKmeans = wx.RadioButton(id=-1, label='k-means clustering',
                                       name='rbKmeans', parent=self.methPnl,
                                       pos=wx.Point(16, 48),
                                       size=wx.Size(128, 21), style=wx.RB_GROUP)
        self.rbKmeans.SetValue(True)
        self.rbKmeans.SetToolTip('')
        
        self.rbKmedian = wx.RadioButton(id=-1, label='k-medians clustering',
                                        name='rbKmedian', parent=self.methPnl,
                                        pos=wx.Point(16, 24),
                                        size=wx.Size(128, 21), style=0)
        self.rbKmedian.SetValue(False)
        self.rbKmedian.SetToolTip('')
        
        self.rbKmedoids = wx.RadioButton(id=-1, label='k-medoids clustering',
                                         name='rbKmedoids', parent=self.methPnl,
                                         pos=wx.Point(16, 72),
                                         size=wx.Size(120, 21), style=0)
        self.rbKmedoids.SetToolTip('')
        self.rbKmedoids.SetValue(False)
        
        self.rbHcluster = wx.RadioButton(id=-1, label='Hierarchical clustering',
                                         name='rbHcluster', parent=self.methPnl,
                                         pos=wx.Point(16, 96),
                                         size=wx.Size(152, 21), style=0)
        self.rbHcluster.SetToolTip('')
        self.rbHcluster.SetValue(True)
        
        self.rbSingleLink = wx.RadioButton(id=-1, label='Single linkage',
                                           name='rbSingleLink',
                                           parent=self.linkPnl,
                                           pos=wx.Point(168, 144),
                                           size=wx.Size(88, 21),
                                           style=wx.RB_GROUP)
        self.rbSingleLink.SetValue(True)
        self.rbSingleLink.SetToolTip('')
        
        self.rbMaxLink = wx.RadioButton(id=-1, label='Maximum linkage',
                                        name='rbMaxLink', parent=self.linkPnl,
                                        pos=wx.Point(40, 144),
                                        size=wx.Size(104, 21), style=0)
        self.rbMaxLink.SetValue(False)
        self.rbMaxLink.SetToolTip('')
        
        self.rbAvLink = wx.RadioButton(id=-1, label='Average linkage',
                                       name='rbAvLink', parent=self.linkPnl,
                                       pos=wx.Point(40, 120),
                                       size=wx.Size(96, 21), style=0)
        self.rbAvLink.SetValue(False)
        self.rbAvLink.SetToolTip('')
        
        self.rbCentLink = wx.RadioButton(id=-1, label='Centroid linkage',
                                         name='rbCentLink', parent=self.linkPnl,
                                         pos=wx.Point(168, 120),
                                         size=wx.Size(96, 21), style=0)
        self.rbCentLink.SetValue(False)
        self.rbCentLink.SetToolTip('')
        
        self.rbEuclidean = wx.RadioButton(id=-1, label='Euclidean',
                                          name='rbEuclidean',
                                          parent=self.distPnl,
                                          pos=wx.Point(16, 304),
                                          size=wx.Size(136, 21),
                                          style=wx.RB_GROUP)
        self.rbEuclidean.SetValue(True)
        self.rbEuclidean.SetToolTip('')
        
        self.rbCorrelation = wx.RadioButton(id=-1, label='Correlation',
                                            name='rbCorrelation',
                                            parent=self.distPnl,
                                            pos=wx.Point(16, 280),
                                            size=wx.Size(136, 21), style=0)
        self.rbCorrelation.SetValue(False)
        self.rbCorrelation.SetToolTip('')
        
        self.rbAbsCorr = wx.RadioButton(id=-1,
                                        label='Absolute value of correlation',
                                        name='rbAbsCorr', parent=self.distPnl,
                                        pos=wx.Point(16, 232),
                                        size=wx.Size(184, 21), style=0)
        self.rbAbsCorr.SetValue(False)
        self.rbAbsCorr.SetToolTip('')
        
        self.rbUncentredCorr = wx.RadioButton(id=-1,
                                              label='Uncentred correlation',
                                              name='rbUncentredCorr',
                                              parent=self.distPnl,
                                              pos=wx.Point(16, 400),
                                              size=wx.Size(136, 21), style=0)
        self.rbUncentredCorr.SetValue(False)
        self.rbUncentredCorr.SetToolTip('')
        
        self.rbAbsUncentCorr = wx.RadioButton(id=-1,
                                              label='Absolute uncentred correlation',
                                              name='rbAbsUncentCorr',
                                              parent=self.distPnl,
                                              pos=wx.Point(16, 208),
                                              size=wx.Size(176, 21), style=0)
        self.rbAbsUncentCorr.SetValue(False)
        self.rbAbsUncentCorr.SetToolTip('')
        
        self.rbSpearmans = wx.RadioButton(id=-1,
                                          label='Spearmans rank correlation',
                                          name='rbSpearmans',
                                          parent=self.distPnl,
                                          pos=wx.Point(16, 376),
                                          size=wx.Size(168, 21), style=0)
        self.rbSpearmans.SetValue(False)
        self.rbSpearmans.SetToolTip('')
        
        self.rbKendalls = wx.RadioButton(id=-1, label='Kendalls rho',
                                         name='rbKendalls', parent=self.distPnl,
                                         pos=wx.Point(16, 352),
                                         size=wx.Size(136, 21), style=0)
        self.rbKendalls.SetValue(False)
        self.rbKendalls.SetToolTip('')
        
        self.rbCityBlock = wx.RadioButton(id=-1, label='City-block distance',
                                          name='rbCityBlock',
                                          parent=self.distPnl,
                                          pos=wx.Point(16, 256),
                                          size=wx.Size(136, 21), style=0)
        self.rbCityBlock.SetValue(False)
        self.rbCityBlock.SetToolTip('')
        
        # self.cbUseClass = wx.CheckBox(id_=-1, label='Use class structure',
        #       name='cbUseClass', parent=self.methPnl, pos=wx.Point(16, 448),
        #       size=wx.Size(112, 21), style=0)
        # self.cbUseClass.SetValue(True)
        # self.cbUseClass.SetToolTip('')
        # self.cbUseClass.Bind(wx.EVT_CHECKBOX, self.on_ckbx_use_class, id_=-1)
        
        self.spnNoPass = wx.SpinCtrl(id=-1, initial=1, max=1000, min=1,
                                     name='spnNoPass', parent=self.methPnl,
                                     pos=wx.Point(200, 444),
                                     size=wx.Size(80, 23),
                                     style=wx.SP_ARROW_KEYS)
        self.spnNoPass.SetValue(1)
        self.spnNoPass.SetToolTip('')
        self.spnNoPass.SetRange(1, 1000)
        
        self.spnNumClass = wx.SpinCtrl(id=-1, initial=1, max=1000, min=1,
                                       name='spnNumClass', parent=self.methPnl,
                                       pos=wx.Point(200, 444),
                                       size=wx.Size(80, 23),
                                       style=wx.SP_ARROW_KEYS)
        self.spnNumClass.SetValue(1)
        self.spnNumClass.SetToolTip('')
        self.spnNumClass.SetRange(1, 1000)
        
        self.rbPlotName = wx.RadioButton(id=-1, label='Plot using labels',
                                         name='rbPlotName', parent=self.distPnl,
                                         pos=wx.Point(16, 480),
                                         size=wx.Size(104, 21),
                                         style=wx.RB_GROUP)
        self.rbPlotName.SetValue(True)
        self.rbPlotName.SetToolTip('')
        self.rbPlotName.Show(False)
        
        self.rbPlotColours = wx.RadioButton(id=-1, label='Plot using colours',
                                            name='rbPlotColours',
                                            parent=self.distPnl,
                                            pos=wx.Point(144, 480),
                                            size=wx.Size(104, 21), style=0)
        self.rbPlotColours.SetValue(False)
        self.rbPlotColours.SetToolTip('')
        self.rbPlotColours.Show(False)
        
        self.AddFoldPanelWindow(self.clustType, self.methPnl, fpb.FPB_ALIGN_WIDTH)
        self.AddFoldPanelWindow(self.distType, self.distPnl, fpb.FPB_ALIGN_WIDTH)
        self.AddFoldPanelWindow(self.linkType, self.linkPnl, fpb.FPB_ALIGN_WIDTH)
        
        self._init_selparam_sizers()
        
    # noinspection PyUnresolvedReferences
    def on_ckbx_use_class(self, _):
        """"""
        # TODO: Definition of cbUseClass was commented above. This will crash
        if self.cbUseClass.GetValue() is False:
            self.spnNoPass.Enable(True)
        else:
            self.spnNoPass.Enable(False)
            

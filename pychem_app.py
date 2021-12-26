#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Name:        PyChem.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2007/05/22
# RCS-ID:      $Id: pychem_app.py,v 1.12 2009/02/25 19:45:42 rmj01 Exp $
# Copyright:   (c) 2007
# Licence:     GNU General Public Licence
# -----------------------------------------------------------------------------

import wx
import pychem_main
# import psyco, pychemaui

modules = {'Cluster': [0, '', 'cluster.py'],
           'Dfa': [0, '', 'dfa.py'],
           'Ga': [0, '', 'ga.py'],
           'Pca': [0, '', 'pca.py'],
           'Plsr': [0, '', 'plsr.py'],
           # 'pychemaui': [1, 'Main frame of Application', 'pychemaui.py'],
           'PyChemMain': [1, 'Main frame of Application', 'pychem_main.py'],
           'Univariate': [0, '', 'univariate.py'],
           'chemometrics': [0, '', 'mva/chemometrics.py'],
           'expSetup': [0, '', 'exp_setup.py'],
           'fitfun': [0, '', 'mva/fitfun.py'],
           'genetic': [0, '', 'mva/genetic.py'],
           'plotSpectra': [0, '', 'plot_spectra.py'],
           'process': [0, '', 'mva/process.py']}

class PyChemApp(wx.App):
    """"""
    def OnInit(self):
        # create splash object
        # bmp = wx.Image(os.path.join('bmp', 'pychemsplash.png')).ConvertToBitmap()
        # splash = wx.SplashScreen(bmp,wx.SPLASH_CENTRE_ON_SCREEN,
        #              5000, None, id_=-1)
        # self.SetTopWindow(splash)
        # time.sleep(2)
        # start pychem
        # psyco.full()
        # self.main = pychemaui.create(None)

        # noinspection PyAttributeOutsideInit
        self.main = pychem_main.create(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        # splash.Destroy()
        return True
        
def main():
    application = PyChemApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()

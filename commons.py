import wx
import wx.lib.plot
import numpy as np


class PolyMarker(wx.lib.plot.polyobjects.PolyMarker):
    """Inherits from  wx PolyMaker to add labels

    """
    _attributes = {'colour': 'black',
                   'width': 1,
                   'size': 2,
                   'fillcolour': None,
                   'fillstyle': wx.BRUSHSTYLE_SOLID,
                   'marker': 'circle',
                   'legend': '',
                   'labels': None,
                   'text_colour': 'black'}

    def __init__(self, points, **attr):
        super(wx.lib.plot.polyobjects.PolyMarker, self).__init__(points, attr)

    def _text(self, dc, coords, size=1):
        """Added by rmj 14.05.07"""
        dc.SetTextForeground(self.attributes['text_colour'])
        dc.DrawTextList(self.attributes['labels'], coords)


def error_box(window, error):
    """"""
    msg = 'The following error occured:\n\n %s' % error
    dlg = wx.MessageDialog(window, msg, 'Error!', wx.OK | wx.ICON_ERROR)
    try:
        dlg.ShowModal()
    finally:
        dlg.Destroy()


def get_rx(rxa, rxb, ptype='covar'):
    """"""
    lrxb = len(rxb)
    mrxb = np.mean(rxb, 0)
    srxa = rxa.shape[1]

    # ptype = 'covar'
    rxb = rxb - np.resize(mrxb, (lrxb, srxa))

    if ptype not in ['covar']:
        rxb = rxb / np.resize(np.std(rxb, 0), (lrxb, srxa))

    return rxb


def test():
    data = np.array([[1], [4]])
    data = np.reshape(data, len(data), )
    print(data)
    data = data.tolist()
    print(type(data))
    print(data)
    for i in data:
        print(i)

test()

import wx
import numpy as np

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

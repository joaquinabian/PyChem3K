# -----------------------------------------------------------------------------
# Name:        fitfun.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2006/06/20
# RCS-ID:      $Id: fitfun.py, v 1.6 2009/01/13 16:26:55 rmj01 Exp $
# Copyright:   (c) 2006
# Licence:     GNU General Public License
# Description: Fitness functions for use in genetic algorithm optimisation
# -----------------------------------------------------------------------------

import scipy as sp
import numpy as np
from numpy import newaxis as nax

from mva.chemometrics import cva, pls
from mva.chemometrics import _split
from mva.chemometrics import _slice
from mva.chemometrics import _index
from mva.chemometrics import _put
from mva.chemometrics import _flip
from mva.chemometrics import _bw
from mva.genetic import _remdup
from mva.process import meancent


def _group(x, mrep):
    grp = []
    for n in range(1, x.shape[0]/mrep+1, 1):
        for cnt in range(0, mrep, 1):
            grp.append(n)
    return np.reshape(np.asarray(grp, 'i'), (len(grp), 1))


# noinspection PyUnreachableCode
def call_dfa(chrom, xdata, DFs, mask, data):
    """Runs DFA on subset of variables from "xdata" as 
    defined by "chrom" and returns a vector of fitness 
    scores to be fed back into the GA
    """
    Y = []
    for x in range(len(chrom)):
        if _remdup(chrom[x]) == 0:
            # extract vars from xdata
            aslice = meancent(_slice(xdata, chrom[x]))
            collate = 0
            for nF in range(mask.shape[1]):
                # split in to training and test
                (tr_slice, cv_slice, ts_slice,
                 tr_grp, cv_grp, ts_grp,
                 tr_nm, cv_nm, ts_nm) = \
                    _split(aslice, data['class'][:, 0], mask[:, nF].tolist(),
                           data['label'])

                try:
                    u, v, eigs, dummy = cva(tr_slice, tr_grp, DFs)
                    projU = np.dot(cv_slice, v)
                    u = np.concatenate((u, projU), 0)
                    group2 = np.concatenate((tr_grp, cv_grp), 0)
            
                    B, W = _bw(u, group2)
                    L, A = sp.linalg.eig(B, W)
                    # TODO: check why 'order' is not used
                    # noinspection PyUnusedLocal
                    order = _flip(np.argsort(np.reshape(L.real, (len(L), ))))
                    Ls = _flip(np.sort(L.real))
                    eigval = Ls[0:DFs]
                    
                    collate += sum(eigval)
                # TODO: remove raise after catching error
                except ValueError:
                    raise
                    continue
                
            if collate != 0:
                Y.append(float(mask.shape[1])/collate)
            else:
                Y.append(10.0**5)
        else:
            Y.append(10.0**5)
            
    return np.array(Y)[:, nax]


def rerun_dfa(chrom, xdata, mask, groups, names, DFs):
    """Run DFA in min app"""
    # extract vars from xdata
    aslice = meancent(_slice(xdata, chrom))
    
    # split in to training and test
    tr_slice, cv_slice, ts_slice, tr_grp, cv_grp, ts_grp, tr_nm, cv_nm, ts_nm = \
        _split(aslice, groups, mask, names)
    
    # get indexes
    idx = np.arange(xdata.shape[0])[:, nax]
    tr_idx = np.take(idx, _index(mask, 0), 0)
    cv_idx = np.take(idx, _index(mask, 1), 0)
    ts_idx = np.take(idx, _index(mask, 2), 0)
    
    # model DFA on training samples
    u, v, eigs, dummy = cva(tr_slice, tr_grp, DFs)
    
    # project xval and test samples
    projUcv = np.dot(cv_slice, v)
    projUt = np.dot(ts_slice, v)
    
    uout = np.zeros((xdata.shape[0], DFs), 'd')
    _put(uout, np.reshape(tr_idx, (len(tr_idx), )).tolist(), u)
    _put(uout, np.reshape(cv_idx, (len(cv_idx), )).tolist(), projUcv)
    _put(uout, np.reshape(ts_idx, (len(ts_idx), )).tolist(), projUt)
    
    return uout, v, eigs

# noinspection PyUnreachableCode
def call_pls(chrom, xdata, factors, mask, data):
    """Runs pls on a subset of X-variables"""
    scores = []
    
    for i in range(chrom.shape[0]):
        if _remdup(chrom[i]) == 0:
            # extract vars from xdata
            aslice = np.take(xdata, chrom[i, :].tolist(), 1)
            collate = 0
            for nF in range(mask.shape[1]):
                # split in to training and test
                try:
                    pls_output = pls(aslice, data['class'][:, 0][:, nax], mask[:, nF].tolist(), factors)
                    
                    if min(pls_output['rmsec']) <= min(pls_output['rmsepc']):
                        collate += pls_output['RMSEPC']
                    else:
                        collate += 10.0**5
                # TODO: remove raise after catching error
                except ValueError:
                    raise
                    collate = 0
                
            if collate != 0:
                scores.append(collate/mask.shape[1])
            else:
                scores.append(10.0**5)
        else:
            scores.append(10.0**5)
            
    return np.asarray(scores)[:, nax]

def rerun_pls(chrom, xdata, groups, mask, factors):
    """rerun pls on a subset of X-variables"""
    
    aslice = np.take(xdata, chrom, 1)
    
    return pls(aslice, groups, mask, factors)


if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    import fitfun
    import doctest
    doctest.testmod(fitfun, verbose=True)

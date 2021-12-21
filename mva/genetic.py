# -----------------------------------------------------------------------------
# Name:        genetic.py
# Purpose:     
#
# Author:      Roger Jarvis
#
# Created:     2006/06/20
# RCS-ID:      $Id: genetic.py, v 1.3 2009/01/13 16:26:55 rmj01 Exp $
# Copyright:   (c) 2006
# Licence:     GNU General Public License
# Description: A simple genetic algorithm for Python
# -----------------------------------------------------------------------------

import copy
import scipy as sp
import numpy as np
# from mva.chemometrics import _slice
from mva.chemometrics import _flip

def _sortrows(a, i=0):
    """Sort rows of "a" in ascending order by column i
    """
    keep = copy.deepcopy(a)
    ind, add, c = [], max(a[:, i])+10, 0
    for n in range(0, a.shape[0], 1):
        ind.append(np.argsort(a[:, i])[0])
        a[ind[n], i] = add
    for x in ind:
        a[c] = keep[x]
        c += 1
    return a


def _remdup(a, amax=None):
    """Remove duplicates from vector a
    """
    np.sort(a)
    flag = 0
    for x in range(1, len(a)):
        if (a[x-1]+1) - (a[x]+1) == 0:
            flag = 1
    return flag

def _unique(a):
    id = []
    for count in range(a.shape[0]):
        chk = 0
        ordx = np.sort(a[count])
        for i in range(1, len(ordx)):
            if ordx[i-1] == ordx[i]:
                chk = 1
        if chk == 0:
            id.append(count)
    return id

def crtpop(ni, nv, prec):
    """Create a random population array of size
    ni by nv in the range 0:preci-1.  Use prec = 2
    to create binary string
    """
    pop = np.around(np.rand(ni, nv)*(prec-1))
    
    return pop


def rank(chrom, score):
    """Linear ranking of individuals between
    0 (worst) and 2 (best)
    """
    order = _sortrows(np.concatenate((score, chrom), 1))

    ranksc = np.zeros((chrom.shape[0], 1), 'd')
    for x in range(1, len(score), 1):
        ranksc[x] = 2*(float(x)/(chrom.shape[0]-1)) 
    ranksc = _flip(ranksc)

    chrom = np.array(order[:, 1:order.shape[1]])
    scores = np.reshape(order[:, 0], (order.shape[0], 1))

    return ranksc, chrom, scores
    

def select(ranksc, chrom, N):
    """Stochastic universal sampling
    N is the generation gap (i.e. a real number between 0 and 1)
    """
    N = round(chrom.shape[0]*N)
    cumsum = np.cumsum(ranksc, 0)
    susrange = np.rand(N, 1)*max(max(cumsum))
    
    sel = []
    for each in susrange:
        qcount, q0 = 0, cumsum[0]
        for q in cumsum:
            if q0 < each < q:
                sel.append(qcount)
            qcount += 1
            q0 = q
    nchrom = np.take(chrom, sel, 0)
    
    return nchrom


def xover(chrom, N, p):
    """Single point crossover with probability N, precision p
    """
    N = round(chrom.shape[0]*N)
    index1 = np.arange(chrom.shape[0])
    index2 = np.unique(np.around(sp.rand(chrom.shape[0], )*chrom.shape[0]))[0:chrom.shape[0]/2]
    sel1, sel2 = [], []
    for i in range(len(index1)):
        if index1[i] not in index2:
            sel1.append(index1[i])
        else:
            sel2.append(index1[i])
    select1 = sel1[0:min([int(round(len(sel1)*N)), int(round(len(sel2)*N))])]
    select2 = sel2[0:min([int(round(len(sel1)*N)), int(round(len(sel2)*N))])]
    
    # set xover points
    xoverpnt = np.around(sp.rand(len(select1), )*(chrom.shape[1]-1))
    
    # perform xover
    nchrom = copy.deepcopy(chrom)
    for i in range(len(select1)):
        try:
            slice1 = chrom[select1[i], 0:int(xoverpnt[i])]
            slice2 = chrom[select2[i], 0:int(xoverpnt[i])]
            nchrom[select2[i], 0:int(xoverpnt[i])] = slice1
            nchrom[select1[i], 0:int(xoverpnt[i])] = slice2
        except ValueError:
            nchrom = nchrom
            raise
    
    return nchrom


def mutate(chrom, N, p):
    """Mutation with probability N and precision p
    """
    index = []

    for x in range(int(np.around(chrom.shape[0]*chrom.shape[1]*N))):
        index.append((int(np.around(sp.rand(1, )[0]*(chrom.shape[0]-1))),
                      int(np.around(sp.rand(1, )[0]*(chrom.shape[1]-1)))))

    for x in index:
        if p == 1:
            if chrom[x] == 1:
                chrom[x] = 0
            else:
                chrom[x] = 1
        else:
            chrom[x] = int(np.around(sp.rand(1, )[0]*(p-1)))
    
    return chrom


def reinsert(ch, selch, chsc, selsc):
    """Reinsert evolved population into original pop
    retaining the best individuals
    """
    newChrom = np.concatenate((ch, selch), 0)
    newScore = np.concatenate((chsc, selsc), 0)
    
    # select only unique chroms - can be removed
    uid = []
    for i in range(len(newChrom)):
        if len(np.unique(newChrom[i, :])) == ch.shape[1]:
            uid.append(i)
    newScore = np.take(newScore, uid, 0)
    newChrom = np.take(newChrom, uid, 0)
    
    idx = np.argsort(newScore, 0)[:, 0].tolist()
    idx = idx[0:ch.shape[0]]
    
    newChrom = np.take(newChrom, idx, 0)
    newScore = np.take(newScore, idx, 0)
    
    return newChrom, newScore


if __name__ == "__main__":
    # noinspection PyUnresolvedReferences
    import genetic
    import doctest
    doctest.testmod(genetic, verbose=True)

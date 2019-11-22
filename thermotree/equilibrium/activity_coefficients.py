#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 08:58:41 2018

@author: Yoel Rene Cortes-Pena
"""
from math import exp
import numpy as np
from .unifac_data import DOUFSG, DOUFIP2016, UFIP, UFSG
from numba import njit

__all__ = ('GroupActivityCoefficients', 'DortmundActivityCoefficients')

# %% Utilities

def chemgroup_array(chemgroups, index):
    M = len(chemgroups)
    N = len(index)
    array = np.zeros((M, N))
    for i, groups in enumerate(chemgroups):
        for group, count in groups.items():
            array[i, index[group]] = count
    return array

def masked_psis(cQfs, psis, indices):
    masked_psis = np.zeros_like(psis, dtype=float)
    for index in indices:
        for i in index:
            masked_psis[i, index] = psis[index, i]
    return masked_psis

# %% Activity Coefficients

class GroupActivityCoefficients:
    __slots__ = ('_chemgroups', '_rs', '_qs', '_indices',
                 '_Qs', '_chem_Qfractions',
                 '_interactions', '_chemicals')
    _cached = {}
    def __init__(self, chemicals):
        self.chemicals = chemicals
        
    @property
    def chemicals(self):
        return self._chemicals
    
    @chemicals.setter
    def chemicals(self, chemicals):
        chemicals = tuple(chemicals)
        if chemicals in self._cached:
            (self._rs, self._qs, self._Qs, self._chemgroups,
            self._chem_Qfractions, self._interactions, self._indices) = self._cached[chemicals]
        else:
            chemgroups = [s.UNIFAC_Dortmund for s in chemicals]
            all_groups = set()
            for groups in chemgroups: all_groups.update(groups)
            index = {group:i for i,group in enumerate(all_groups)}
            chemgroups = chemgroup_array(chemgroups, index)
            all_subgroups = self.all_subgroups
            subgroups = [all_subgroups[i] for i in all_groups]
            main_group_ids = [i.main_group_id for i in subgroups]
            self._Qs = Qs = np.array([i.Q for i in subgroups])
            Rs = np.array([i.R for i in subgroups])
            self._rs = rs = chemgroups @ Rs
            self._qs = qs = chemgroups @ Qs
            self._chemgroups = chemgroups
            chem_Qs = Qs * chemgroups
            self._chem_Qfractions = cQfs = chem_Qs/chem_Qs.sum(1, keepdims=True)
            all_interactions = self.all_interactions
            self._interactions = [[None if i == j else all_interactions[i][j] for i in main_group_ids]
                                 for j in main_group_ids]
            rowindex = np.arange(len(all_groups), dtype=int)
            self._indices = indices = [rowindex[rowmask] for rowmask in cQfs != 0]
            self._cached[chemicals] = (rs, qs, Qs, chemgroups, cQfs,
                                       self._interactions, indices)
        self._chemicals = chemicals
        
    def __call__(self, xs, T):
        """Return UNIFAC coefficients.
        
        Parameters
        ----------
        xs : array_like
            Molar fractions
        T : float
            Temperature (K)
        
        """
        xs = np.asarray(xs)
        chemgroups = self._chemgroups
        weighted_counts = chemgroups.transpose() @ xs
        loggammacs = self.loggammacs(self._qs, self._rs, xs)
        Qs = self._Qs
        Q_fractions = Qs * weighted_counts 
        Q_fractions /= Q_fractions.sum()
        psis = np.array([[self.psi(T, d) if d else 1. for d in i]
                         for i in self._interactions])
        Q_psis = psis * Q_fractions
        lg1 = Q_psis.sum(1)
        lg2 = -(psis.transpose() / lg1) @ Q_fractions
        loggamma_groups = Qs * (1. - np.log(lg1) + lg2)
        cQfs = self._chem_Qfractions
        mpsis = masked_psis(cQfs, psis, self._indices)
        sum1 = cQfs @ mpsis
        sum1 = np.where(sum1==0, 1., sum1)
        fracs = - cQfs / sum1
        sum2 = (mpsis @ fracs.transpose()).transpose()
        chem_loggamma_groups = Qs*(1. - np.log(sum1) + sum2)
        loggammars = ((loggamma_groups - chem_loggamma_groups) * chemgroups).sum(1)
        return np.exp(loggammacs + loggammars)
    
    def __repr__(self):
        chemicals = ", ".join([i.ID for i in self.chemicals])
        return f"<{type(self).__name__}({chemicals})>"
    
    
class UNIFACActivityCoefficiencts(GroupActivityCoefficients):
    all_subgroups = UFSG
    all_interactions = UFIP
    
    @staticmethod
    @njit
    def loggammacs(qs, rs, xs):
        r_net = (xs*rs).sum()
        q_net = (xs*qs).sum()  
        Vs = rs/r_net
        Fs = qs/q_net
        Vs_over_Fs = Vs/Fs
        return 1. - Vs - np.log(Vs) - 5.*qs*(1. - Vs_over_Fs + np.log(Vs_over_Fs))
    
    @staticmethod
    def psi(T, a):
        return exp(-a/T)


class DortmundActivityCoefficients(GroupActivityCoefficients):
    __slots__ = ()
    all_subgroups = DOUFSG
    all_interactions = DOUFIP2016
    
    @staticmethod
    @njit
    def loggammacs(qs, rs, xs):
        r_net = (xs*rs).sum()
        q_net = (xs*qs).sum()
        rs_p = rs**0.75
        r_pnet = (rs_p*xs).sum()
        Vs = rs/r_net
        Fs = qs/q_net
        Vs_over_Fs = Vs/Fs
        Vs_p = rs_p/r_pnet
        return 1. - Vs_p + np.log(Vs_p) - 5.*qs*(1. - Vs_over_Fs + np.log(Vs_over_Fs))
    
    @staticmethod
    def psi(T, abc):
        a, b, c = abc
        return exp((-a/T - b - c*T)) 
    
    
    
# def UNIFAC(self, xs, T):
#     return UNIFAC_Coeffictients(self, xs, T, UFSG, UFIP, UNIFAC_psi, loggammacs_UNIFAC)

# def UNIFAC_LL(self, xs, T):
#     """For LLE"""
#     return UNIFAC_Coeffictients(self, xs, T, UFSG, UFLLIP, UNIFAC_psi, loggammacs_UNIFAC)

# def loggammacs_UNIFAC(qs, rs, xs):
#     rsxs = sum([ri*xi for ri, xi in zip(rs, xs)])
#     Vis = [ri/rsxs for ri in rs]
#     qsxs = sum([qi*xi for qi, xi in zip(qs, xs)])
#     Fis = [qi/qsxs for qi in qs]

#     loggammacs = [1. - Visi + log(Visi) - 5.*qsi*(1. - Visi/Fisi + log(Visi/Fisi))
#                   for Visi, Fisi, qsi in zip(Vis, Fis, qs)]
#     return loggammacs

# def UNIFAC_psi(T, subgroup1, subgroup2, subgroup_data, interaction_data):
#     try:
#         return exp(-interaction_data[subgroup_data[subgroup1].main_group_id] \
#                                     [subgroup_data[subgroup2].main_group_id]/T)
#     except:
#         return 1




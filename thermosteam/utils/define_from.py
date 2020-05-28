# -*- coding: utf-8 -*-
# BioSTEAM: The Biorefinery Simulation and Techno-Economic Analysis Modules
# Copyright (C) 2020, Yoel Cortes-Pena <yoelcortes@gmail.com>
# 
# This module is under the UIUC open-source license. See 
# github.com/BioSTEAMDevelopmentGroup/biosteam/blob/master/LICENSE.txt
# for license details.
"""
"""

__all__ = ('define_from',)

def _define_from(cls, other, names):
    getfield = getattr
    setfield = setattr
    for name in names: setfield(cls, name, getfield(other, name))
    return cls

def define_from(other, names):
    return lambda cls: _define_from(cls, other, names)
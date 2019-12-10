# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 23:02:53 2019

@author: yoelr
"""
__all__ = ('units_of_measure', 'ureg', '_Q', 'Units')

# %% Import unit registry

from pint import UnitRegistry
from pint.quantity import to_units_container
import os

# Set pint Unit Registry
ureg = UnitRegistry()
ureg.default_format = '~P'
ureg.load_definitions(os.path.dirname(os.path.realpath(__file__)) + '/units_of_measure.txt')
_Q = Quantity = ureg.Quantity
_Q._repr_latex_ = _Q._repr_html_ = \
_Q.__str__ = _Q.__repr__ = lambda self: self.__format__('')
del os, UnitRegistry

# %% Manage conversion factors

class Units:
    __slots__ = ('_units', '_units_container', '_dimensionality', '_factor_cache')
    _cache = {}
    def __new__(cls, units=""):
        cache = cls._cache
        if units in cache:
            return cache[units]
        else:
            self = super().__new__(cls)
            self._units = units
            self._units_container = to_units_container(units, ureg)
            self._dimensionality = ureg._get_dimensionality(self._units_container)
            self._factor_cache = {}
            cache[units] = self
            return self
    
    @property
    def units(self):
        return self._units
    
    @property
    def dimensionality(self):
        return self._dimensionality
    
    def to(self, units):
        cache = self._factor_cache
        if units in cache:
            factor = cache[units]
        else:
            cache[units] = factor = ureg.convert(1., self._units_container, units)
        return factor
    
    def __bool__(self):
        return bool(self._units)
    
    def __str__(self):
        return self._units
    
    def __repr__(self):
        return f"{type(self).__name__}({repr(self._units)})"

def get_dimensionality(units):
    return ureg._get_dimensionality(to_units_container(units, ureg))
    

# %% Units of measure

units_of_measure = {'MW': 'g/mol',
                    'T': 'K',
                    'Tm': 'K',
                    'Tb': 'K',
                    'Tt': 'K',
                    'Tc': 'K',
                    'P': 'Pa',
                    'Pc': 'Pa',
                    'Psat': 'Pa',
                    'Pt': 'K',
                    'V': 'm^3/mol',
                    'Vc': 'm^3/mol',
                    'Cp': 'J/mol/K',
                    'rho': 'kg/m^3', 
                    'rhoc': 'kg/m^3',
                    'nu': 'm^2/s',
                    'mu': 'Pa*s',
                    'sigma': 'N/m' ,
                    'kappa': 'W/m/K',
                    'alpha': 'm^2/s', 
                    'Hvap': 'J/mol',
                    'H': 'J/mol',  
                    'Hf':'J/mol', 
                    'Hc':'J/mol', 
                    'Hfus': 'J/mol', 
                    'Hsub': 'J/mol',
                    'S': 'J/mol', 
                    'G': 'J/mol', 
                    'U': 'J/mol', 
                    'A': 'J/mol',
                    'H_excess': 'J/mol', 
                    'S_excess': 'J/mol',
                    'R': 'J/mol/K',
                    'delta': 'Pa^0.5',
                    'epsilon': "",
}

definitions = {'MW': 'Molecular weight',
               'T': 'Temperature',
               'Tm': 'Melting point temperature',
               'Tb': 'Boiling point temperature',
               'Tt': 'Triple point temperature',
               'Tc': 'Critical point temperature',
               'P': 'Pressure',
               'Pc': 'Critical point pressure',
               'Psat': 'Saturated vapor pressure',
               'Pt': 'Triple point pressure',
               'V': 'Molar volume',
               'Vc': 'Critical point volume',
               'Cp': 'Molar heat capacity',
               'Cp.s': 'Molar heat capacity of a solid',
               'Cp.l': 'Molar heat capacity of a liquid',
               'Cp.g': 'Molar heat capacity of a gas',
               'rho': 'Density',
               'rhoc': 'Critical point density',
               'nu': 'Kinematic viscosity',
               'mu': 'Hydrolic viscosity',
               'sigma': 'Surface tension',
               'kappa': 'Thermal conductivity',
               'alpha': 'Thermal diffusivity',
               'Hvap': 'Heat of vaporization',
               'H': 'Enthalpy',
               'Hf': 'Heat of formation',
               'Hc': 'Heat of combustion', 
               'Hfus': 'Heat of fusion',
               'Hsub': 'Heat of sublimation',
               'S': 'Entropy',
               'G': 'Gibbs free energy',
               'U': 'Internal energy',
               'A': 'Helmholtz energy',
               'H_excess': 'Excess enthalpy',
               'S_excess': 'Excess entropy',
               'R': 'Universal gas constant',
               'Zc': 'Critical compressibility',
               'omega': 'Acentric factor',
               'delta': 'Solubility parameter',
               'epsilon': 'Relative permittivity',
}

types = {}
# Synonyms
for i, j in [('ω', 'omega')]:
    definitions[i] = definitions[j]
    if j in units_of_measure: units_of_measure[i] = units_of_measure[j]

# Phase properties
for var in ('Cp', 'H', 'S', 'V', 'kappa', 'H_excess', 'S_excess'):
    units = units_of_measure[var]
    definition = definitions[var].lower()
    for tag, phase in zip(('s', 'l', 'g'), ('Solid ', 'Liquid ', 'Gas ')):
        for tag in ('_' + tag, '.'+tag):
            phasevar = var + tag
            units_of_measure[phasevar] = units
            definitions[phasevar] = phase + definition

# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 04:26:20 2019

@author: yoelr
"""
from .units_of_measure import units_of_measure, definitions, types
from .utils import var_with_units, get_obj_values
from .autodoc import autodoc_functor
from inspect import signature
from numba.targets.registry import CPUDispatcher
from numba import njit

__all__ = ("Functor", "MixtureFunctor", 
           "TFunctor", "TPFunctor",
           "zTFunctor", "zTPFunctor",
           "functor", 'H', 'S', 'V', 'Cp', 'mu', 'kappa', 'sigma', 'delta', 'epsilon',
           'Psat', 'Hvap', 'display_asfunctor', 'functor_lookalike',
           'functor_matching_params', 'functor_base_and_params')

RegisteredArgs = set()
RegisteredFunctors = []

# %% Utilities

def functor_name(functor):
    return functor.__name__ if hasattr(functor, "__name__") else type(functor).__name__

def display_asfunctor(functor, var=None, name=None, show_var=True):
    name = name or functor_name(functor)
    info = f"{name}{str(signature(functor)).replace('self, ', '')}"
    var = var or (functor.var if hasattr(functor, 'var') else None)
    units = functor.units_of_measure if hasattr(functor, "units_of_measure") else units_of_measure
    if var:
        if show_var:
            info += f" -> " + var_with_units(var, units)
        else:
            u = units.get(var)
            if u: info += f" -> {u}"
    return info

def functor_lookalike(cls):
    cls.__repr__ = Functor.__repr__
    cls.__str__ = Functor.__str__
    return cls

def functor_matching_params(params):
    N_total = len(params)
    for base in RegisteredFunctors:
        args = base._args
        N = len(args)
        if N > N_total: continue
        if args == params[:N]: return base
    raise ValueError("could not match function signature to registered functors")

def functor_base_and_params(function):
    params = tuple(signature(function).parameters)
    base = functor_matching_params(params)
    return base, params[len(base._args):]


# %% Decorator
  
def functor(function=None, var=None, njitcompile=True, wrap=None,
            definitions=None, units_of_measure=None, math="", refs="",
            doc=None):
    if function:
        base, params = functor_base_and_params(function)
        if njitcompile and not isinstance(function, CPUDispatcher): 
            function = njit(function)
        dct = {'__slots__': (),
               'function': staticmethod(function),
               'params': params,
               'var': var}
        cls = type(function.__name__, (base,), dct)
        if units_of_measure:
            dct['units_of_measure'] = units_of_measure
        if definitions:
            dct['definitions'] = definitions
        if wrap: cls.wrapper(wrap)
        if doc:  cls.__doc__ = doc
        else: autodoc_functor(cls, base, math, refs)
        cls.__module__ = function.__module__
        return cls
    else:
        return lambda function: functor(function, var, njitcompile, wrap)


# %% Decorators
    
class FunctorFactory:
    __slots__ = ('var',)
   
    def __init__(self, var):
        self.var = var
    
    def __call__(self, function=None, njitcompile=True, wrap=None,
                 definitions=None, units_of_measure=None, math="", refs="",
                 doc=None):
        return functor(function, self.var, njitcompile, wrap,
                       definitions, units_of_measure, math, refs, doc)
    
    def s(self, function=None, njitcompile=True, wrap=None,
          definitions=None, units_of_measure=None, math="", refs="", doc=None):
        return functor(function, self.var + '.s', njitcompile, wrap,
                       definitions, units_of_measure, math, refs, doc)
    
    def l(self, function=None, njitcompile=True, wrap=None,
          definitions=None, units_of_measure=None, math="", refs="", doc=None):
        return functor(function, self.var + '.l', njitcompile, wrap,
                       definitions, units_of_measure, math, refs, doc)
    
    def g(self, function=None, njitcompile=True, wrap=None,
          definitions=None, units_of_measure=None, math="", refs="", doc=None):
        return functor(function, self.var + '.g', njitcompile, wrap,
                       definitions, units_of_measure, math, refs, doc)
    
    def __repr__(self):
        return f"{type(self).__name__}({repr(self.var)})"
    
H, S, Cp, V, kappa, mu, Psat, Hvap, sigma, delta, epsilon = [FunctorFactory(i) for i in
                                                             ('H', 'S', 'Cp', 'V', 'kappa',
                                                              'mu', 'Psat', 'Hvap',
                                                              'sigma', 'delta', 'epsilon')]


# %% Functors

class Functor: 
    __slots__ = ()
    units_of_measure = units_of_measure
    definitions = definitions
    types = types
    
    def __init_subclass__(cls, args=None, before=None, after=None):
        if args and not hasattr(cls, 'function'):
            args = tuple(args)
            assert args not in RegisteredArgs, f"abstract functor with args={args} already implemented"
            if before:
                index = RegisteredFunctors.index(before)
            elif after:
                index = RegisteredFunctors.index(after) + 1
            else:
                index = 0
            RegisteredFunctors.insert(index, cls)
            RegisteredArgs.add(args)
            cls._args = args
    
    def __str__(self):
        return display_asfunctor(self)
    
    def __repr__(self):
        return f"<{self}>"


class PureComponentFunctor(Functor):
    __slots__ = ('kwargs', 'data')
    
    def __init__(self, data, kwargs=None):
        if isinstance(data, dict):
            self.data = data
        elif hasattr(data, '__iter__'):
            self.data = data = dict(zip(self.params, data))
        else:
            self.data = data = dict(zip(self.params, get_obj_values(data, self.params)))
        self.kwargs = kwargs or (self.wrap(**data) if hasattr(self, 'wrap') else data)
    
    @classmethod
    def wrapper(cls, kwargs):
        cls.params = tuple(signature(kwargs).parameters)
        cls.wrap = staticmethod(kwargs)
        return cls
    
    def show(self):
        info = f"Functor: {display_asfunctor(self)}"
        data = self.data
        units = self.units_of_measure
        for key, value in data.items():
            if value is None:
                info += f"\n {key}: {value}"
                continue
            else:
                try:
                    info += f"\n {key}: {value:.5g}"
                except:
                    info += f"\n {key}: {value}"    
                else:
                    u = units.get(key) or units_of_measure.get(key)
                    if u: info += ' ' + u
        print(info)
        
    _ipython_display_ = show


class TFunctor(PureComponentFunctor, args=('T',)):
    __slots__ = ()
    
    def __call__(self, T, P=None):
        return self.function(T, **self.kwargs)


class TIntegralFunctor(PureComponentFunctor, args=('Ta', 'Tb')):
    __slots__ = ()
    
    def __call__(self, Ta, Tb, P=None):
        return self.function(Ta, Tb, **self.kwargs)

class PIntegralFunctor(PureComponentFunctor, args=('Pa', 'Pb', 'T')):
    __slots__ = ()
    
    def __call__(self, Pa, Pb, T):
        return self.function(Pa, Pb, T, **self.kwargs)


class TPFunctor(PureComponentFunctor, args=('T', 'P')):
    __slots__ = ()
    
    def __call__(self, T, P):
        return self.function(T, P, **self.kwargs)


class MixtureFunctor(Functor):
    __slots__ = ('kwargs', '_species')
    
    def __init__(self, species, kwargs=None):
        species = tuple(species)
        if kwargs:
            self._species = species
            self.kwargs = kwargs
        else:
            self.species = species
    
    @classmethod
    def wrap(cls, kwargs):
        cls.calculate_kwargs = staticmethod(kwargs)
        return cls
    
    @property
    def species(self):
        return self._species
    
    @species.setter
    def species(self, species):
        if species == self._species: return
        self._species = species = tuple(species)
        if species in self.cache:
            self.kwargs = self.cache[species]
        else:
            self.cache[species] = self.kwargs = self.calculate_kwargs(self.species)
            
    
class zTFunctor(MixtureFunctor, args=('z', 'T')): 
    __slots__ = ()
    
    def __init_subclass__(self):
        self.cache = {}
    
    def __call__(self, z, T, P=None):
        return self.function(z, T, **self.kwargs)
        

class zTPFunctor(MixtureFunctor, args=('z', 'T', 'P')):
    __slots__ = ()
    
    def __init_subclass__(self):
        self.cache = {}
    
    def __call__(self, z, T, P):
        return self.function(z, T, P, **self.kwargs)
    
    
    
    
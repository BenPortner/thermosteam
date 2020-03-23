# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 12:00:55 2019

@author: yoelr
"""
from .thermo_model_handle import TDependentModelHandle, TPDependentModelHandle

__all__ = ('HandleBuilder', 'TDependentHandleBuilder', 'TPDependentHandleBuilder')

class HandleBuilder:
    __slots__ = ('function',)
    
    def __init__(self, function):
        self.function = function

    def __call__(self, data):
        handle = self.Handle()
        self.function(handle, *data)
        return handle
        
    def __repr__(self):
        return f"<[{type(self).__name__}] {self.function.__name__}(data)>"
    
class TDependentHandleBuilder(HandleBuilder):
    Handle = TDependentModelHandle

class TPDependentHandleBuilder(HandleBuilder):
    Handle = TPDependentModelHandle
# -*- coding: utf-8 -*-
"""
Created on Mon May 11 17:03:14 2020

@author: yoelr
"""
import os
import json

__all__ = (
    'load_json',
    'RowData',
)

# %% Readers

class RowData:
    """
    Create a RowData object for fast data frame lookups by row.
    
    """
    __slots__ = ('index', 'values')
    
    def __init__(self, index, values=None):
        self.index = {key: i for i, key in enumerate(index)}
        self.values = values
    
    def __getitem__(self, row):
        return self.values[self.index[row]]
    
    def __contains__(self, row):
        return row in self.index   
    
def load_json(folder, json_file, hook=None):
    with open(os.path.join(folder, json_file)) as f:
        return json.loads(f.read(), object_hook=hook)
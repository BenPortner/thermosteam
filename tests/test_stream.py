# -*- coding: utf-8 -*-
# BioSTEAM: The Biorefinery Simulation and Techno-Economic Analysis Modules
# Copyright (C) 2020-2021, Yoel Cortes-Pena <yoelcortes@gmail.com>
# 
# This module is under the UIUC open-source license. See 
# github.com/BioSTEAMDevelopmentGroup/biosteam/blob/master/LICENSE.txt
# for license details.
"""
"""
import pytest
import thermosteam as tmo
from numpy.testing import assert_allclose

def test_vlle():
    tmo.settings.set_thermo(['Water', 'Ethanol', 'Octane'])
    s = tmo.Stream(None, Water=1, Ethanol=1, Octane=2, vlle=True, T=350)
    assert_allclose(s.mol, [1, 1, 2]) # mass balance
    assert_allclose(s.imol['l'] + s.imol['L'], [0.537583, 0.383255, 1.755296], rtol=5e-2)
    assert_allclose(s.imol['g'], [0.462, 0.617, 0.245], rtol=5e-2) # Convergence
    s = tmo.Stream(None, Water=1, Ethanol=1, Octane=2, vlle=True, T=300)
    assert set(s.phases) == set(['l', 'L']) # No gas phase
    assert_allclose(s.mol, [1, 1, 2]) # mass balance
    s = tmo.Stream(None, Water=1, Ethanol=1, Octane=2, vlle=True, T=360)
    assert set(s.phases) == set(['l', 'g']) # No second liquid phase
    assert_allclose(s.mol, [1, 1, 2]) # mass balance
    assert_allclose(s.imol['g'], [0.955, 0.95 , 0.734], rtol=1e-2) # Convergence
    s = tmo.Stream(None, Water=1, Ethanol=1, Octane=2, vlle=True, T=380)
    assert s.phases == ('g',) # Only one phase
    s = tmo.MultiStream(None, l=[('Water', 1), ('Ethanol', 1), ('Octane', 2)], vlle=True, T=380)
    assert s.phase == 'g' # Only one phase
    assert set(s.phases) == set(['L', 'l', 'g']) # All three phases can still be used
    
def test_critical():
    tmo.settings.set_thermo(['CO2', 'O2', 'CH4'])
    
    # Three components
    s = tmo.Stream(None, CO2=1, O2=1, CH4=2, vlle=True, T=350)
    assert s.phase == 'g'
    vapor_fraction = 0.5
    s.vle(V=vapor_fraction, P=101325)
    assert_allclose(s.vapor_fraction, vapor_fraction)
    assert_allclose(s.mol, [1, 1, 2])
    assert_allclose(s['g'].z_mol, [0.0006053116760182865, 0.43970244158393407, 0.5596922467400477], rtol=1e-2)
    
    bp = s.bubble_point_at_P()
    assert_allclose(bp.T, 102.62052288398583, rtol=1e-3)
    assert_allclose(bp.y, [3.803565920764843e-05, 0.7778539445712263, 0.222108019769566], rtol=1e-2)
    
    dp = s.dew_point_at_P()
    assert_allclose(dp.T, 164.2843303081629, rtol=1e-3)
    assert_allclose(dp.x, [0.9697130577019155, 0.0034114070277255068, 0.02687553527035907], rtol=1e-2)
    
    s = tmo.Stream(None, CO2=1, O2=1, CH4=2, vlle=True, T=80)
    s.phase == 'l'
    
    # Two components
    s = tmo.Stream(None, CO2=1, O2=1, vlle=True, T=350)
    assert s.phase == 'g'
    vapor_fraction = 0.5
    s.vle(V=vapor_fraction, P=101325)
    assert_allclose(s.vapor_fraction, vapor_fraction)
    assert_allclose(s.mol, [1, 1, 0])
    assert_allclose(s['g'].z_mol, [0.03330754277536625, 0.9666924572246337, 0.0], rtol=1e-2)
    
    bp = s.bubble_point_at_P()
    assert_allclose(bp.T, 97.37091146329703, rtol=1e-3)
    assert_allclose(bp.y, [2.614648198782934e-05, 0.999973853518012], rtol=1e-2)
    
    dp = s.dew_point_at_P()
    assert_allclose(dp.T, 173.64797757499818, rtol=1e-3)
    assert_allclose(dp.x, [0.9951836814710002, 0.004816318528999781], rtol=1e-2)
    
    s = tmo.Stream(None, CO2=1, O2=1, vlle=True, T=80)
    s.phase == 'l'

def test_stream():
    tmo.settings.set_thermo(['Water'], cache=True)
    stream = tmo.Stream(None, Water=1, T=300)
    assert [stream.chemicals.Water] == stream.available_chemicals
    assert_allclose(stream.epsilon, 77.744307)
    assert_allclose(stream.alpha * 1e6, 0.14330776454124503)
    assert_allclose(stream.nu, 8.799123532986536e-07)
    assert_allclose(stream.Pr, 6.14001869413997)
    assert_allclose(stream.Cn, 75.29555729396768)
    assert_allclose(stream.C, 75.29555729396768)
    assert_allclose(stream.Cp, 4.179538552493643)
    assert_allclose(stream.P_vapor, 3536.806752274638)
    assert_allclose(stream.mu, 0.0008766363688287887)
    assert_allclose(stream.kappa, 0.5967303492959747)
    assert_allclose(stream.rho, 996.2769195618362)
    assert_allclose(stream.V, 1.80826029854462e-05)
    assert_allclose(stream.H, 139.31398526921475)
    assert_allclose(stream.S, 70.46581776376684)
    assert_allclose(stream.sigma, 0.07168596252716256)
    assert_allclose(stream.z_mol, [1.0])
    assert_allclose(stream.z_mass, [1.0])
    assert_allclose(stream.z_vol, [1.0])
    assert not stream.source
    assert not stream.sink
    assert stream.main_chemical == 'Water'
    assert not stream.isfeed()
    assert not stream.isproduct()
    assert stream.vapor_fraction == 0.
    with pytest.raises(ValueError):
        stream.get_property('isfeed', 'kg/hr')
    with pytest.raises(ValueError):
        stream.set_property('invalid property', 10, 'kg/hr')
    with pytest.raises(ValueError):
        tmo.Stream(None, Water=1, units='kg')
    
    stream.mol = 0.
    stream.mass = 0.
    stream.vol = 0.
    
    with pytest.raises(AttributeError):
        stream.F_mol = 1.
    with pytest.raises(AttributeError):
        stream.F_mass = 1.
    with pytest.raises(AttributeError):
        stream.F_vol = 1.
        
    # Make sure energy balance is working correctly with mix_from and vle
    chemicals = tmo.Chemicals(['Water', 'Ethanol'])
    thermo = tmo.Thermo(chemicals)
    tmo.settings.set_thermo(thermo)
    s3 = tmo.Stream('s3', T=300, P=1e5, Water=10, units='kg/hr')
    s4 = tmo.Stream('s4', phase='g', T=400, P=1e5, Water=10, units='kg/hr')
    s_eq = tmo.Stream('s34_mixture')
    s_eq.mix_from([s3, s4])
    s_eq.vle(H=s_eq.H, P=1e5)
    H_sum = s3.H + s4.H
    H_eq = s_eq.H
    assert_allclose(H_eq, H_sum, rtol=1e-3)
    s_eq.vle(H=s3.H + s4.H, P=1e5)
    assert_allclose(s_eq.H, H_sum, rtol=1e-3)    
        
def test_multistream():
    tmo.settings.set_thermo(['Water', 'Ethanol'], cache=True)
    stream = tmo.MultiStream(None, l=[('Water', 1)], T=300)
    assert [stream.chemicals.Water] == stream.available_chemicals
    assert_allclose(stream.epsilon, 77.744307)
    assert_allclose(stream.alpha * 1e6, 1.4330776454124502e-01)
    assert_allclose(stream.nu, 8.799123532986536e-07)
    assert_allclose(stream.Pr, 6.14001869413997)
    assert_allclose(stream.Cn, 75.29555729396768)
    assert_allclose(stream.C, 75.29555729396768)
    assert_allclose(stream.Cp, 4.179538552493643)
    assert_allclose(stream.P_vapor, 3536.806752274638)
    assert_allclose(stream.mu, 0.0008766363688287887)
    assert_allclose(stream.kappa, 0.5967303492959747)
    assert_allclose(stream.rho, 996.2769195618362)
    assert_allclose(stream.V, 1.80826029854462e-05)
    assert_allclose(stream.H, 139.31398526921475)
    assert_allclose(stream.S, 70.465818)
    assert_allclose(stream.sigma, 0.07168596252716256)
    assert_allclose(stream.z_mol, [1.0, 0.])
    assert_allclose(stream.z_mass, [1.0, 0.])
    assert_allclose(stream.z_vol, [1.0, 0.])
    assert not stream.source
    assert not stream.sink
    assert stream.main_chemical == 'Water'
    assert not stream.isfeed()
    assert not stream.isproduct()
    assert stream.vapor_fraction == 0.
    assert stream.liquid_fraction == 1.
    assert stream.solid_fraction == 0.
    with pytest.raises(ValueError):
        stream.get_property('isfeed', 'kg/hr')
    with pytest.raises(ValueError):
        stream.set_property('invalid property', 10, 'kg/hr')
    with pytest.raises(ValueError):
        tmo.MultiStream(None, l=[('Water', 1)], units='kg')
    stream.empty()
    with pytest.raises(AttributeError):
        stream.mol = 1.
    with pytest.raises(AttributeError):
        stream.mass = 1.
    with pytest.raises(AttributeError):
        stream.vol = 1.
    with pytest.raises(AttributeError):
        stream.F_mol = 1.
    with pytest.raises(AttributeError):
        stream.F_mass = 1.
    with pytest.raises(AttributeError):
        stream.F_vol = 1.
        
    # Casting
    stream.as_stream()
    assert stream.phase == 'g' # Phase of an empty multi-stream defaults to stream.phases[0]
    assert type(stream) is tmo.Stream
    stream.phases = 'gl'
    assert stream.phases == ('g', 'l')
    stream.phases = 'gls'
    stream.phases == ('g', 'l', 's')
    stream.phases = 's'
    assert type(stream) is tmo.Stream
    assert stream.phase == 's'
    
    # Linking
    stream.phase = 'l'
    stream.phases = 'lg'
    other = stream.copy()
    stream.link_with(other)
    other.imol['l', 'Water'] = 10
    other.vle(V=0.5, P=2*101325)
    assert_allclose(other.mol, stream.mol)
    assert_allclose(other.T, stream.T)
    assert_allclose(other.P, stream.P)
    
    # Indexing
    assert_allclose(stream.imol['Water'], 10.)
    assert_allclose(stream.imol['Water', 'Ethanol'], [10., 0.])
    UndefinedChemical = tmo.exceptions.UndefinedChemical
    UndefinedPhase = tmo.exceptions.UndefinedPhase
    with pytest.raises(UndefinedChemical):
        stream.imol['Octanol']
    with pytest.raises(UndefinedChemical):
        stream.imol['l', 'Octanol']
    with pytest.raises(TypeError):
        stream.imol['l', ['Octanol', 'Water']]
    with pytest.raises(IndexError):
        stream.imol[None, 'Octanol']
    with pytest.raises(UndefinedPhase):
        stream.imol['s', 'Octanol']
    
    # Other
    stream = tmo.MultiStream(None, l=[('Water', 1)], T=300, units='g/s')
    assert stream.get_flow('g/s', 'Water') == stream.F_mass / 3.6 == 1.
    stream.empty()    

def test_mixture():
    tmo.settings.set_thermo(['Water'], cache=True)

    # test solve_T_at_xx
    T_expected = 298
    s5 = tmo.Stream('s5', T=T_expected, P=1e5, Water=1)
    Th = s5.mixture.solve_T_at_HP(phase=s5.phase, mol=s5.mol, H=s5.H, T_guess=s5.T, P=s5.P)
    assert_allclose(T_expected, Th, rtol=1e-3)
    Ts = s5.mixture.solve_T_at_SP(phase=s5.phase, mol=s5.mol, S=s5.S, T_guess=s5.T, P=s5.P)
    assert_allclose(T_expected, Ts, rtol=1e-3)
    pass
    
if __name__ == '__main__':
    test_stream()
    test_multistream()
    test_vlle()
    test_critical()
    test_mixture()
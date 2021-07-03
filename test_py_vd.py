# file: test_py_vd.py

import voltage_divider as vdr
import os
import pytest
from collections import namedtuple

"""
this is to investigate pytest which is simpler than unittest. The names of the
test methods is the same but self is not passed and subclassing TestCase is not 
required. For test fixtures to work, all named tuples used in testing need to be 
defined in the test file and namedtuples need to be imported: 
    from collections import namedtuples
If a fixture is needed in the fixture definition, it needs to be passed as an 
argument. 
See fixture resistorSet(...) below.
"""
DesignGoals = namedtuple("DesignGoals", "vin v2_hi v2_lo max_mw")
VD = namedtuple("VD", "Vin V1 V2 Deviance R1 R2 Pow1_mw Pow2_mw A2D")


#  --------- globals and test fixtures-----------------
v2_hi = vdr.v2_hi
v2_lo = vdr.v2_lo
max_mw = 250


@pytest.fixture
def path1():
    return os.getcwd() + '/quarter_watt.csv'


@pytest.fixture
def path2():
    return os.getcwd() + '/half_watt.csv'


@pytest.fixture
def resistorSet(path1):
    return vdr.load_resistor_set(path1)


@pytest.fixture
def design_goals():
    return DesignGoals(25.2, v2_hi, v2_lo, 250)

# -------------------tests---------------------------------


def test_fixture(design_goals):
    print("This is to test the test fixture: design_goals ")
    A = design_goals.vin == 25.2
    B = design_goals.v2_hi == vdr.v2_hi
    C = design_goals.v2_lo == vdr.v2_lo
    D = design_goals.max_mw == 250
    assert A and B and C and D


def test_compute(design_goals, path1):
    """
    ---Test end to end.Given vin and path1, ensure returns 5 or less vds
    """
    vds = vdr.compute(design_goals.vin, path1)
    l1 = len(vds)
    # print(f' Num candidates: {l1}')
    assert(0 <= l1 <= 5)  # replace with better test.


def test_find_choices(design_goals, resistorSet):
    """
   ---Ensure vds returned are sorted ascending by Deviance from target V2
   """
    # assert 6 == len(find_choices(design_goals, resistorSet))
    candidates = vdr.find_choices(design_goals, resistorSet)
    assert(candidates[0].Deviance <= candidates[1].Deviance)


def test_design_meets_specs(design_goals):
    """
    ---Ensure that good inputs Pass specs :
    """
    Pass = vdr.design_meets_specs(design_goals, 2000, 470)
    assert Pass


def test_design_meets_specs_2(design_goals):
    """
    ---Ensure bad inputs Fail specs :
    """
    Pass = vdr.design_meets_specs(design_goals, 200, 47)
    assert not Pass


def test_design_meets_specs_3(design_goals):
    """
    ---This is to check a bug in a gui run. Not a bug after all.
    """
    # r1=220000  r2=51000
    assert vdr.design_meets_specs(design_goals, 220000, 51000)


def test_get_max_mw(path1):
    """
    ---Ensures that the correct wattage is set from the path1 to the resistors.
    """
    assert vdr.get_max_mw(path1) == 250


def test_get_max_mw2(path2):
    """
    ---Ensures that the correct wattage is set from the path2 to the resistors.
    """
    assert vdr.get_max_mw(path2) == 500


def test_load_resistor_set(path1):
    """
    ---Ensures that the resistor set is loaded correctly given path1.
    """
    resistorSet = vdr.load_resistor_set(path1)
    assert isinstance(resistorSet, set) and len(resistorSet) == 37


def test_load_resistor_set2(path2):
    """
    ---Ensures that the resistor set is loaded correctly given path2.
    """
    resistorSet = vdr.load_resistor_set(path2)
    assert isinstance(resistorSet, set) and len(resistorSet) == 37


def test_build_voltage_divider(design_goals):
    """
    ---Tests that the namedtuple VD is returned correctly
     # VD = namedtuple("VD", "Vin V1 V2 Deviance R1 R2 Pow1_mw Pow2_mw A2D")
     # DesignGoals = namedtuple("DesignGoals", "vin v2_hi v2_lo max_mw")

    """
    vd = vdr.build_voltage_divider(design_goals, 2000, 470)

    assert vd.Vin == design_goals.vin and vd.V1 == 20.4 and vd.V2 == 4.8 and vd.Pow1_mw == 208 and vd.Pow2_mw == 48 and vd.A2D == 981  # noqa: E501

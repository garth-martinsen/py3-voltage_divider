# file: voltage_divider2.py

import re
from collections import namedtuple
import csv
import os

# ----------------namedtuples----------------------------------
VD = namedtuple("VD", "Vin V1 V2 Deviance R1 R2 Pow1_mw Pow2_mw A2D")
DesignGoals = namedtuple("DesignGoals", "vin v2_hi v2_lo max_mw")

# --------------global variables-------------------------------
v2_hi = 4.95  # a2d = 1012
v2_lo = 4.65  # a2d = 951
max_mw = 0   # set in process


def load_resistor_set(path):
    """
Loads the set of resistors available for use into a set. The best Combination
of two of these will be used in the selected voltage divider.
"""
    resistorSet = set()
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                # print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                resistorSet.add(int(row[0]))
                line_count += 1
        print(f'Loaded {line_count-1} resistors.')
        return resistorSet


def build_voltage_divider(design_goals, r1, r2):
    """
    Returns a VoltageDivider candidate. This function is only called
    if specs for power dissipation and design_goals are met for r1,r2,
    as determined by function design_meets_specs
    """
    fract = r2 / (r1 + r2)
    vin = design_goals.vin
    v1 = vin * (1 - fract)
    v2 = design_goals.vin * fract
    p1 = int(v1**2 / r1 * 1000 ) # mW
    p2 = int(v2**2 / r2 * 1000 ) # mW
    a2d = int(f'{v2/5*1023:.0f}')
    dev = design_goals.v2_hi - v2
    # size for display
    vin= float(f'{vin:.2f}')
    v1= float(f'{v1:.2f}')
    v2= float(f'{v2:.2f}')
    dev = float(f'{dev:.4f}')
    # VD = namedtuple("VD", "Vin V1 V2 Deviance R1 R2 Pow1_mw Pow2_mw A2D")
    return VD(vin, v1, v2, dev, r1, r2, p1, p2, a2d)


def get_max_mw(path):
    """
    returns 250 or 500 mw depending on the filename.
    If another set of resistors exist with different power ratings,
    A file should be created with a title reflecting the rating.
    """
    global max_mw
    q = re.findall('quarter', path)
    h = re.findall('half', path)
    if len(q) > 0:
        max_mw = 250
    elif len(h) > 0:
        max_mw = 500
    return max_mw


def design_meets_specs(design_goals, r1, r2):
    """
    A candidate consists of two resistors, r1,r2. There are many candidates,
    but only some meet the specs. This function is used to filter out 
    candidates that do not meet specs. Given the design_goals and r1,r2, this 
    function computes the fraction, then uses that and vin to compute V2, 
    power1, power2 and try these against specs. 
    Returns True if meets specs:
    """
    # print(f'Design Goals: {design_goals}')
    vin = design_goals.vin
    fraction = r2 / (r1 + r2)
    v2 = vin * fraction
    V2_Ok = design_goals.v2_lo <= v2 <= design_goals.v2_hi
    pow1_Ok = ((vin - v2)**2 / r1) * 1000 < design_goals.max_mw
    pow2_OK = (v2**2 / r2 * 1000) < design_goals.max_mw
    return V2_Ok and pow1_Ok and pow2_OK


def find_choices(design_goals, resistorSet):
    """
    Returns a sorted list of 5 VoltageDivider candidates that meet
    design_goals. Resistor pairs that do not meet specs are filtered out.
    Any of the choices returned could be selected,
    but the one with the smallest deviance from desired_v2 should be used 
    as the best design. 
    """

    # list comprehension is used to filter out non-compliant candidates
    choices = [build_voltage_divider(design_goals, r1, r2)
               for r1 in resistorSet
               for r2 in resistorSet
               if design_meets_specs(design_goals, r1, r2)]
    print(f'Sorting {len(choices)} choices')
    return sorted(list(choices), key=lambda vdr: vdr.Deviance)


def compute(Vin, path):
    """
    Entry point from GUI. Vin = input Voltage to be measured,  # noqa: E101
    path = path to the resistor set csv file. max_mw is computed from path.
    The desired V2 is v2_hi 
    so any value in range (4.65 < v2 < 4.95) meets specs. v2_hi and v2_lo
    are global variables so they are easily changed at the top of the script.
    Returns top 5 candidates
    """
    global v2_hi
    global v2_lo
    max_mw = get_max_mw(path)
    resistor_set = load_resistor_set(path)
    design_goals = DesignGoals(float(Vin), v2_hi, v2_lo, max_mw)
    choices = find_choices(design_goals, resistor_set)
    print(choices)
    # This is to fix a bug. If you ask for [0:5] and there are only 4 choices, you get a wonky candidate.
    len_choices=(len(choices))
    end = min(5,len_choices)
    return choices[0:end]

# --------------------unit testing-----------------------------
# path = '/Users/garth/Programming/python3/VD3/quarter_watt.csv'
path = os.getcwd() + '/resistors_quarter.csv';

# "DesignGoals", "vin v2_hi v2_lo max_mw")
design_goals = DesignGoals(25.25, v2_hi, v2_lo, 250)
resistorSet = load_resistor_set(path)


def test_compute():
    fd = compute(design_goals.vin, path)
    l1 = len(fd)
    #print(f' Num candidates: {l1}')
    assert(1 <= l1 <= 5)  # replace with better test. Changing tol value would break test.  # noqa: E501


def test_find_choices():
    """
    Ensure they are sorted
    """
    # assert 6 == len(find_choices(design_goals, resistorSet))
    candidates = find_choices(design_goals, resistorSet)
    assert candidates[0].Deviance < candidates[1].Deviance

    def test_find_choices_2():
        """
        bug when running with vd_gui.py, this VD should not meet specs. The r values are wonky
        VD(Vin=25.5, V1=20.7, V2=4.8, Deviance=0.1511, R1=220000, R2=51000, Pow1_mw=1, Pow2_mw=0, A2D=982)
        but it is returned as an acceptable VD candidate.
        """
        test_vd=VD(25.5, 20.7, 4.8, 0.1511, 220000, 51000, 1, 0, 982) 
        candidates = vdr.compute(25.25,path)   
        assert test_vd not in candidates


def test_load_resistor_set():
    """
    Ensure that the loaded resistors have the same count as the file.
    """
    resistorSet = load_resistor_set(path)
    # replace with better test. Adding a resistor value would break test.
    assert(len(resistorSet) == 37)


def test_design_meets_specs():
    """
    Ensure specs are tested: 
    v2_lo <= v2 <= v2_hi and p1 <= 250 mw and p2 <= 250 mw
    """
    Pass = design_meets_specs(design_goals, 2000, 470)
    assert Pass



def test_design_meets_specs_3():
    """
    This is to check for the bug in a gui run. this config is displayed as a candidate. Tracking this down.
    """
    # r1=22000  r2=51000 
    Pass = design_meets_specs(design_goals, 22000, 51000)
    assert (Pass)

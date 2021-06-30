# file: test_vd.py
import voltage_divider as vdr
import os
import unittest


# --------------------unit tests-----------------------------

class VoltageDividerTest(unittest.TestCase):

    # -------------------fixtures-------------------------------
    def setUp(self):
        # print('In setup()')
        self.max_mw = 250
        self.path = os.getcwd() + '/quarter_watt.csv'
        self.resistorSet = vdr.load_resistor_set(self.path)
        self.v2_hi = vdr.v2_hi
        self.v2_lo = vdr.v2_lo
        self.design_goals = vdr.DesignGoals(25.2, self.v2_hi, self.v2_lo, 250)

    def tearDown(self):
        # print('In tearDown()')
        del self.max_mw
        del self.path
        del self.resistorSet
        del self.v2_hi
        del self.v2_lo
        del self.design_goals

    """
    def test(self):
        self.assertTrue(True)
    """

    def test_compute(self):
        """
        ---Test end to end.Given vin and path, ensure returns 5 or less vds
        """
        fd = vdr.compute(self.design_goals.vin, self.path)
        l1 = len(fd)
        # print(f' Num candidates: {l1}')
        self.assertTrue(0 <= l1 <= 5)  # replace with better test.

    def test_find_choices(self):
        """
       ---Ensure vds returned are sorted ascending by Deviance from target V2
       """
        # assert 6 == len(find_choices(design_goals, resistorSet))
        candidates = vdr.find_choices(self.design_goals, self.resistorSet)
        self.assertTrue(candidates[0].Deviance <= candidates[1].Deviance)

    def test_design_meets_specs(self):
        """
        ---Ensure that good inputs Pass specs :
        """
        Pass = vdr.design_meets_specs(self.design_goals, 2000, 470)
        self.assertTrue(Pass)

    def test_design_meets_specs_2(self):
        """
        ---Ensure bad inputs Fail specs :
        """
        Pass = vdr.design_meets_specs(self.design_goals, 200, 47)
        self.assertFalse(Pass)

    def test_design_meets_specs_3(self):
        """
        ---This is to check a bug in a gui run. Not a bug after all.
        """
        # r1=220000  r2=51000
        Pass = vdr.design_meets_specs(self.design_goals, 220000, 51000)
        self.assertTrue(Pass)

    def test_get_max_mw(self):
        """
        ---Ensures that the correct wattage is set from the path.
        """
        self.assertTrue(vdr.get_max_mw(self.path) == 250)

    def test_load_resistor_set(self):
        """
        ---Ensures that the resistor set is loaded correctly given path.
        """
        resistorSet = vdr.load_resistor_set(self.path)
        self.assertTrue(isinstance(resistorSet, set)
                        and len(resistorSet) == 37)

    def test_build_voltage_divider(self):
        """
        ---Tests that the namedtuple VD is returned correctly
         # VD = namedtuple("VD", "Vin V1 V2 Deviance R1 R2 Pow1_mw Pow2_mw A2D")
         """
        vd = vdr.build_voltage_divider(self.design_goals, 2000, 470)
        # print(f'target V2: {vd.Deviance + vd.V2}')
        self.assertTrue(vd.Vin == self.design_goals.vin
                        and vd.V1 == 20.4
                        and vd.V2 == 4.8
                        and vd.Pow1_mw == 208
                        and vd.Pow2_mw == 48 and vd.A2D == 981
                        and 4.8 <= vd.Deviance + vd.V2 <= 5.0)


if __name__ == '__main__':
    unittest.main()

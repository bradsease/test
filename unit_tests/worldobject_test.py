"""
WorldObject unit tests.
"""
import unittest
import worldobject as obj
import numpy as np

class worldobjecttests(unittest.TestCase):
    """
    World object test class.
    """

    def setUp(self):
        self.worldobject = obj.WorldObject()

    def tearDown(self):
        del self.worldobject

class test_initialization(worldobjecttests):
    """
    Test world object initialization.
    """

    def test_types(self):
        """
        Test for correct attribute types
        """

        # Check types
        self.assertTrue(isinstance(self.worldobject.quaternion, np.ndarray),                      \
                                                                 "Incorrect quaternion data type.")
        self.assertTrue(isinstance(self.worldobject.angular_rate, np.ndarray),                    \
                                                               "Incorrect angular rate data type.")
        self.assertTrue(isinstance(self.worldobject.position, np.ndarray),                        \
                                                                   "Incorrect position data type.")
        self.assertTrue(isinstance(self.worldobject.velocity, np.ndarray),                        \
                                                                   "Incorrect velocity data type.")

class test_set_pointing_fcn(worldobjecttests):
    """
    Test set_pointing_fcn method.
    """

    def test_ode(self):
        """
        Test ODE input format.
        """

        # Create static "state" function
        fcn = lambda t, state: [0, 0, 0, 0, 0, 0, 0]

        # Set function
        self.worldobject.set_pointing_fcn(fcn, "ode")

        # Check properties
        self.assertEqual(self.worldobject.model_pointing, "on", "Incorrect modeling option.")
        self.assertEqual(self.worldobject.pointing_mode, "ode", "Incorrect pointing mode.")

        # Check function output
        test_result = self.worldobject.pointing_fcn(1)
        expected_result = np.hstack((self.worldobject.quaternion, self.worldobject.angular_rate))
        self.assertTrue(np.all(test_result == expected_result), "Incorrect function result.")

    def test_explicit(self):
        """
        Test explicit input format.
        """

        # Create "state" function
        fcn = lambda t: np.hstack((self.worldobject.quaternion, self.worldobject.angular_rate))

        # Set function
        self.worldobject.set_pointing_fcn(fcn, "explicit")

        # Check properties
        self.assertEqual(self.worldobject.model_pointing, "on", "Incorrect modeling option.")
        self.assertEqual(self.worldobject.pointing_mode, "explicit", "Incorrect pointing mode.")

        # Check function output
        test_result = self.worldobject.pointing_fcn(1)
        expected_result = np.hstack((self.worldobject.quaternion, self.worldobject.angular_rate))
        self.assertTrue(np.all(test_result == expected_result), "Incorrect function result.")

class test_set_pointing_preset(worldobjecttests):
    """
    Test set_pointing_preset method.
    """

    def test_kinematic_preset(self):
        """
        Test rigid body kinematic preset.
        """

        # Set preset
        self.worldobject.set_pointing_preset("kinematic")

        # Check function output
        test_result = self.worldobject.pointing_fcn(1)
        expected_result = np.hstack((self.worldobject.quaternion, self.worldobject.angular_rate))
        self.assertTrue(np.all(test_result == expected_result), "Incorrect function result.")

class test_set_integrator(worldobjecttests):
    """
    Test set_integrator method.
    """

    def test_set(self):
        """
        Test basic integrator set.
        """
        # Set integrator
        self.worldobject.set_integrator("vode", 1e-8, 1e-9)

        # Check properties
        self.assertEqual(self.worldobject.integrator, "vode", "Incorrect integrator.")
        self.assertEqual(self.worldobject.integrator_atol, 1e-8, "Incorrect absolute tolerance.")
        self.assertEqual(self.worldobject.integrator_rtol, 1e-9, "Incorrect relative tolerance.")

    def test_set_with_pointing_ode(self):
        """
        Test integrator set with a pointing ode that requires re-initialization.
        """

        # Create "state" function
        fcn = lambda t, state: [0, 0, 0, 0, 0, 0, 0]

        # Set function
        self.worldobject.set_pointing_fcn(fcn, "ode")

        # Set integrator
        self.worldobject.set_integrator("vode", 1e-8, 1e-9)

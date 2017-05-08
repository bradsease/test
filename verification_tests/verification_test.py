"""
StarCam verification tests.
"""
import unittest
import astraviso as av
import numpy as np

class verificationtests(unittest.TestCase):
    """
    Astra Viso verification tests.

    Requirements Verified
    ---------------------
    1) Objects along the boresight of the sensor must always appear in the image
       for when using the pinhole projection model, regardless of the pointing
       direction.
    2) An object aligned with the boresight must appear in the exact center of
       the image when using the pinhole model.
    3) An object aligned with the boresight of the sensor and moving along the
       x or y axis in intertial space must move along the same axis in the image
       when using the pinhole model. 
    4) An object aligned with the boresight of the sensor and moving along the
       z-axis in intertial space must not move in the image plane when using the
       pinhole model.

    Requirements Remaining
    ----------------------
    5) A positive camera rotation about the x or y axes must cause motion along
       the corresponding axis with opposite sign in the image plane when using
       the pinhole model.
    6) With the pinhole model, a positive rotation about the z axis shall cause
       counter-clockwise motion for objects in view but no motion for objects
       aligned with the boresight.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

class test_pointing_consistency(verificationtests):
    """
    Verify StarCam and WorldObject pointing consistency.
    """

    def test_random(self):
        """
        Test multiple randomly-generated orientations.

        Requirement(s) Verified: #1, #2
        """

        # Initial setup
        num_tests = 20
        cam = av.StarCam()
        cam.star_catalog.load_preset("random", 0)
        cam.set_noise_preset("off")

        # Speed-up hack for when integration accuracy is not important
        cam._StarCam__settings["integration_steps"] = 1

        # Iterate through test cases
        for idx in range(num_tests):

            # Generate random quaternion
            rand_quat = np.random.rand(4)
            rand_quat = rand_quat / np.linalg.norm(rand_quat)

            # Set up camera
            cam.set_pointing_preset("static", initial_quaternion=rand_quat)

            # Set up object
            obj = av.WorldObject()
            position = 10*cam.get_pointing(0, mode="dcm")[:,2]
            obj.set_position_preset("kinematic", initial_position=position,                        \
                                                               initial_velocity=np.array([0, 0, 0]))

            # Add object and generate image
            cam.add_worldobject(obj)
            image = cam.integrate(0, 1)

            # Verify requirement #1
            self.assertGreater(np.sum(image), 0, "Image must contain test object.")
            self.assertTrue(np.all(image >= 0), "Images must be strictly positive.")

            # Verify requirement #2
            correct_coord = (cam._StarCam__settings["resolution"] + 1)/2
            test_coord = np.hstack(cam.get_projection(obj.in_frame_of(cam, 1)))
            self.assertTrue(np.isclose(test_coord[0], correct_coord), "Coordinates must correspond \
                                                                 to the center of the image frame.")
            self.assertTrue(np.isclose(test_coord[1], correct_coord), "Coordinates must correspond \
                                                                 to the center of the image frame.")

    def test_drift_directions(self):
        """
        Verify worldobject drift along x, y, and z axes.

        Requirement(s) Verified: #3, #4
        """

        # Initial setup
        num_tests = 25
        cam = av.StarCam()
        cam.star_catalog.load_preset("random", 0)
        cam.set_noise_preset("off")

        # Speed-up hack for when integration accuracy is not important
        cam._StarCam__settings["integration_steps"] = 1

        # Set up object
        obj = av.WorldObject()
        position = np.array([0, 0, 1])
        velocity = np.array([0, 0, 0])
        obj.set_position_preset("kinematic", initial_position=position, initial_velocity=velocity)

        # Store reference coordinates
        cam.add_worldobject(obj)
        ref_coords = cam.get_projection(obj.in_frame_of(cam, 0))
        cam.delete_worldobject(0)

        # Set up +x test
        velocity = np.array([0.01, 0, 0])
        obj.set_position_preset("kinematic", initial_position=position, initial_velocity=velocity)

        # Verify +x result
        cam.add_worldobject(obj)
        test_coords = cam.get_projection(obj.in_frame_of(cam, 1))
        self.assertGreater(test_coords[0], ref_coords[0], "For x-axis motion, object must move     \
                                                                              in the +x direction.")

        # Set up -x axis test
        velocity = np.array([-0.01, 0, 0])
        obj.set_position_preset("kinematic", initial_position=position, initial_velocity=velocity)

        # Verify -x axis
        cam.add_worldobject(obj)
        test_coords = cam.get_projection(obj.in_frame_of(cam, 1))
        self.assertLess(test_coords[0], ref_coords[0], "For negative x-axis motion, object          \
                                                                     must move in the -x direction.")

        # Set up +y test
        velocity = np.array([0, 0.01, 0])
        obj.set_position_preset("kinematic", initial_position=position, initial_velocity=velocity)

        # Verify +y result
        cam.add_worldobject(obj)
        test_coords = cam.get_projection(obj.in_frame_of(cam, 1))
        self.assertGreater(test_coords[1], ref_coords[1], "For y-axis motion, object must move   \
                                                                              in the +y direction.")

        # Set up -y axis test
        velocity = np.array([0, -0.01, 0])
        obj.set_position_preset("kinematic", initial_position=position, initial_velocity=velocity)

        # Verify -y result
        cam.add_worldobject(obj)
        test_coords = cam.get_projection(obj.in_frame_of(cam, 1))
        self.assertLess(test_coords[1], ref_coords[1], "For negative y-axis motion, object          \
                                                                     must move in the -y direction.")

        # Set up +z test
        velocity = np.array([0, 0, 0.01])
        obj.set_position_preset("kinematic", initial_position=position, initial_velocity=velocity)

        # Verify +z result
        cam.add_worldobject(obj)
        test_coords = cam.get_projection(obj.in_frame_of(cam, 1))
        self.assertTrue(np.all(test_coords == ref_coords), "For z-axis motion, object must         \
                                                                                         not move.")

        # Set up -z axis test
        velocity = np.array([0, 0, -0.01])
        obj.set_position_preset("kinematic", initial_position=position, initial_velocity=velocity)

        # Verify -z result
        cam.add_worldobject(obj)
        test_coords = cam.get_projection(obj.in_frame_of(cam, 1))
        self.assertTrue(np.all(test_coords == ref_coords), "For z-axis motion, object must         \
                                                                                         not move.")

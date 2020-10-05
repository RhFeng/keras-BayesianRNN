import unittest
import numpy as np
from numpy.testing import assert_allclose
from theano import tensor as T
from keras.layers import normalization
from keras.models import Sequential


class TestBatchNormalization(unittest.TestCase):
    def setUp(self):
        self.input_1 = np.arange(10)
        self.input_2 = np.zeros(10)
        self.input_3 = np.ones((10))

        self.input_shapes = [np.ones((10, 10)), np.ones((10, 10, 10))]

    def test_setup(self):
        norm_m0 = normalization.BatchNormalization((10, 10))
        norm_m1 = normalization.BatchNormalization((10, 10), mode=1)

        # mode 3 does not exist
        self.assertRaises(Exception, normalization.BatchNormalization((10, 10), mode=3))

    def test_mode_0(self):
        model = Sequential()
        norm_m0 = normalization.BatchNormalization((10,))
        model.add(norm_m0)
        model.compile(loss='mse', optimizer='sgd')

        # centered on 5.0, variance 10.0
        X = np.random.normal(loc=5.0, scale=10.0, size=(1000, 10))
        model.fit(X, X, nb_epoch=5, verbose=0)
        norm_m0.input = X
        out = (norm_m0.get_output(train=True) - norm_m0.beta) / norm_m0.gamma

        self.assertAlmostEqual(out.mean().eval(), 0.0, places=1)
        self.assertAlmostEqual(out.std().eval(), 1.0, places=1)

    def test_mode_1(self):
        norm_m1 = normalization.BatchNormalization((10,), mode=1)
        norm_m1.init_updates()

        for inp in [self.input_1, self.input_2, self.input_3]:
            norm_m1.input = inp
            out = (norm_m1.get_output(train=True) - norm_m1.beta) / norm_m1.gamma
            self.assertAlmostEqual(out.mean().eval(), 0.0)
            if inp.std() > 0.:
                self.assertAlmostEqual(out.std().eval(), 1.0, places=2)
            else:
                self.assertAlmostEqual(out.std().eval(), 0.0, places=2)

    def test_shapes(self):
        """
        Test batch normalization with various input shapes
        """
        for inp in self.input_shapes:
            norm_m0 = normalization.BatchNormalization(inp.shape, mode=0)
            norm_m0.init_updates()
            norm_m0.input = inp
            out = (norm_m0.get_output(train=True) - norm_m0.beta) / norm_m0.gamma

            norm_m1 = normalization.BatchNormalization(inp.shape, mode=1)
            norm_m1.input = inp
            out = (norm_m1.get_output(train=True) - norm_m1.beta) / norm_m1.gamma

    def test_weight_init(self):
        """
        Test weight initialization
        """

        norm_m1 = normalization.BatchNormalization((10,), mode=1, weights=[np.ones(10), np.ones(10)])
        norm_m1.init_updates()

        for inp in [self.input_1, self.input_2, self.input_3]:
            norm_m1.input = inp
            out = (norm_m1.get_output(train=True) - np.ones(10)) / 1.
            self.assertAlmostEqual(out.mean().eval(), 0.0)
            if inp.std() > 0.:
                self.assertAlmostEqual(out.std().eval(), 1.0, places=2)
            else:
                self.assertAlmostEqual(out.std().eval(), 0.0, places=2)

        assert_allclose(norm_m1.gamma.eval(), np.ones(10))
        assert_allclose(norm_m1.beta.eval(), np.ones(10))

        # Weights must be an iterable of gamma AND beta.
        self.assertRaises(Exception, normalization.BatchNormalization((10,)), weights=np.ones(10))

    def test_config(self):
        norm = normalization.BatchNormalization((10, 10), mode=1, epsilon=0.1)
        conf = norm.get_config()
        conf_target = {"input_shape": (10, 10), "name": normalization.BatchNormalization.__name__,
                       "epsilon": 0.1, "mode": 1}

        self.assertDictEqual(conf, conf_target)


if __name__ == '__main__':
    unittest.main()

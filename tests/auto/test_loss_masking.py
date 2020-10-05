import numpy as np
import unittest
from keras.models import Sequential
from keras.layers.core import TimeDistributedDense, Masking


class TestLossMasking(unittest.TestCase):
    def test_loss_masking(self):
        X = np.array(
            [[[1, 1], [2, 1], [3, 1], [5, 5]],
             [[1, 5], [5, 0], [0, 0], [0, 0]]], dtype=np.int32)
        model = Sequential()
        model.add(Masking(mask_value=0))
        model.add(TimeDistributedDense(2, 1, init='one'))
        model.compile(loss='mse', optimizer='sgd')
        y = model.predict(X)
        loss = model.fit(X, 4*y, nb_epoch=1, batch_size=2, verbose=1).history['loss'][0]
        assert loss == 282.375


if __name__ == '__main__':
    print('Test loss masking')
    unittest.main()

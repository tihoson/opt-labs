import numpy as np
import numba as nb
from numba.experimental import jitclass


@jitclass([
    ('_data', nb.float64[:, :, :])
])
class Tensor3D:
    def __init__(self, data):
        self._data = data

    @staticmethod
    def from_zeroes(shape):
        return Tensor3D(np.zeros(shape, dtype=nb.float64))

    @property
    def shape(self):
        return self._data.shape

    @property
    def data(self):
        return self._data

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    def __add__(self, value: 'Tensor3D'):
        return Tensor3D(self._data + value.data)

    def __sub__(self, value: 'Tensor3D'):
        return Tensor3D(self._data - value.data)

    def __mul__(self, value: 'Tensor3D'):
        return Tensor3D(self._data * value.data)

    def __truediv__(self, value: 'Tensor3D'):
        return Tensor3D(self._data / value.data)


if __name__ == '__main__':
    a = Tensor3D.from_zeroes((3, 3, 3))
    print('--' * 20)
    print(a.data)

    b = Tensor3D(np.array([
        [[1, 1, 1], [1, 1, 1], [1, 1, 1]], 
        [[2, 2, 2], [2, 2, 2], [2, 2, 2]], 
        [[3, 3, 3], [3, 3, 3], [3, 3, 3]],
    ], dtype=np.float64))
    print('--' * 20)
    print(b.data)

    print('--' * 20)
    print((b / b).data)

    print('--' * 20)
    print((a + b).data)

    print('--' * 20)
    print((b * b).data)

    print('--' * 20)
    print((a - b).data)


import itertools
import matplotlib.pyplot as plt
import numpy as np
from os.path import join

plt.style.use(join('styles', 'my_style.mplstyle'))


def get_row_info(matrix, ind: int):
    row = matrix[:, ind]
    return row.max(), row.min(), np.unique(row)


def drawable(func):
    def wrapper_drawable(self, *args, **kwargs):
        if not self.draw_flag:
            print(
                "Невозможно отобразить график, т.к. некоторые данные не были загружены корректно"
            )
            return
        else:
            func(self, *args, **kwargs)
    return wrapper_drawable


class VizCase:
    def __init__(self, path='', verbose=False):
        plt.close('all')
        self.__dict__.clear()
        self.path = path
        self.t_index = 3
        self.draw_flag = False  # флаг, что параметры установлены верно и можно рисовать
        self.x, self.y, self.z = 0, 0, 0

        with open(path, 'r') as f:
            content = [line.strip() for line in f.readlines()]
            self.metadata = content[:3]
            self.data = np.loadtxt(content[3:])
            if verbose:
                print(self.metadata)

        for i, coord in enumerate(['x', 'y', 'z']):
            coord_max, coord_min, row = get_row_info(self.data, i)
            print(f'Интервал {coord}: [{coord_min}, {coord_max}]')
            if verbose:
                print(f'Все точки по {coord}: {row}')

    def set_variables(self, **kwargs):
        self.__dict__.update(kwargs)

        layer_raw = self.data[(self.data[:, 2] == self.z)]
        if not len(layer_raw):
            print(f"Координата z={self.z} не найдена в файле")
            self.draw_flag = False
            return
        else:
            self.draw_flag = True
        layer = layer_raw[:,
                (0, 1, self.t_index)]  # берем x, y и такое T, которое указано по индексу
        self.X = np.unique(layer[:, 0])
        self.Y = np.unique(layer[:, 1])
        self.T = layer[:, 2]

    @drawable
    def horizontal_slice(self, size=(20, 10)):
        T_matr = self.T.reshape((self.Y.size, self.X.size))

        figure = plt.figure(num=None, figsize=size, dpi=80, facecolor='w')
        plt.pcolormesh(self.X, self.Y, T_matr, shading='nearest', figure=figure, snap=True)

        plt.title(f'Горизонтальный срез. $z={self.z}$')
        plt.colorbar(shrink=.9, aspect=50)
        ax = plt.gca()
        ax.set_xticks(np.arange(0, 49, 5))
        ax.set_yticks(np.arange(0, 25, 2))
        ax.set_xlabel('$x$')
        ax.set_ylabel('$y$')
        plt.tight_layout()

    @drawable
    def vertical_slice(self, size=(12, 5)):
        nearx_ind = np.argmin([np.abs(_x - self.x) for _x in self.X])  # nearest x
        neary_ind = np.argmin([np.abs(_y - self.y) for _y in self.Y])  # nearest y
        nearx = self.X[nearx_ind]
        neary = self.Y[neary_ind]
        vert_data = self.data[((self.data[:, 0] == nearx) & (self.data[:, 1] == neary))]

        figure = plt.figure(num=None, figsize=size, dpi=80, facecolor='w')
        plt.plot(vert_data[:, 2], vert_data[:, 3], figure=figure, marker='.')
        plt.title(f'Вертикальный срез в точке ({nearx}, {neary})')
        ax = plt.gca()
        ax.set_xticks(np.arange(-16, 2.1, 2))
        ax.set_yticks(np.arange(-25, 5.1, 5))
        ax.set_xlabel('$z$')
        ax.set_ylabel('$t(z)$')
        plt.grid()
        plt.tight_layout()

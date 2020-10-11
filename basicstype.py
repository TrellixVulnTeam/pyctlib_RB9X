from functools import singledispatch, update_wrapper, wraps
from typing import Optional, List, Union
from collections import Counter
import torch
import numpy as np
from pyctlib.exceptionhandler import *
from pyctlib.override import override
from types import GeneratorType

def methoddispatch(func):
    dispatcher = singledispatch(func)
    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)
    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper

class _Vector_Dict(dict):

    def values(self):
        return vector(super().values())

    def keys(self):
        return vector(super().keys())

class vector(list):

    def filter(self, func=None):
        if func is None:
            return self
        return vector([a for a in self if func(a)])

    def map(self, func=None):
        if func is None:
            return self
        return vector([func(a) for a in self])

    def check_type(self, instance):
        return all(self.map(lambda x: isinstance(x, instance)))

    @methoddispatch
    def __mul__(self, other):
        if touch(lambda: self.check_type(tuple) and other.check_type(tuple)):
            return vector(zip(self, other)).map(lambda x: (*x[0], *x[1]))
        elif touch(lambda: self.check_type(tuple)):
            return vector(zip(self, other)).map(lambda x: (*x[0], x[1]))
        elif touch(lambda: other.check_type(tuple)):
            return vector(zip(self, other)).map(lambda x: (x[0], *x[1]))
        else:
            return vector(zip(self, other))

    @__mul__.register(int)
    def _(self, times: int):
        return vector(super().__mul__(times))

    @methoddispatch
    def __pow__(self, other):
        return vector([(i, j) for i in self for j in other])

    def __add__(self, other: list):
        return vector(super().__add__(other))

    def _transform(self, element, func=None):
        if not func:
            return element
        return func(element)

    @methoddispatch
    def __eq__(self, element):
        return self.map(lambda x: x == element)

    @__eq__.register(list)
    def _(self, other):
        return vector(zip(self, other)).map(lambda x: x[0] == x[1])

    @methoddispatch
    def __neq__(self, element):
        return self.map(lambda x: x != element)

    @__neq__.register(list)
    def _(self, other):
        return vector(zip(self, other)).map(lambda x: x[0] != x[1])

    @methoddispatch
    def __lt__(self, element):
        return self.map(lambda x: x < element)

    @__lt__.register(list)
    def _(self, other):
        return vector(zip(self, other)).map(lambda x: x[0] < x[1])

    @methoddispatch
    def __gt__(self, element):
        return self.map(lambda x: x > element)

    @__gt__.register(list)
    def _(self, other):
        return vector(zip(self, other)).map(lambda x: x[0] > x[1])

    @methoddispatch
    def __le__(self, element):
        return self.map(lambda x: x < element)

    @__le__.register(list)
    def _(self, other):
        return vector(zip(self, other)).map(lambda x: x[0] <= x[1])

    @methoddispatch
    def __ge__(self, element):
        return self.map(lambda x: x >= element)

    @__ge__.register(list)
    def _(self, other):
        return vector(zip(self, other)).map(lambda x: x[0] >= x[1])

    @methoddispatch
    def __getitem__(self, index):
        if isinstance(index, slice):
            return vector(super().__getitem__(index))
        return super().__getitem__(index)

    @__getitem__.register(list)
    def _(self, index_list):
        assert len(self) == len(index_list)
        return vector(zip(self, index_list)).filter(lambda x: x[1]).map(lambda x: x[0])

    def _hashable(self):
        return all(self.filter(lambda x: "__hash__" in x.__dir__()))

    def __hash__(self):
        if not self._hashable():
            raise Exception("not all elements in the vector is hashable, the index of first unhashable element is %d" % self.index(lambda x: "__hash__" not in x.__dir__()))
        else:
            return hash(tuple(self))

    def unique(self):
        if len(self) == 0:
            return vector([])
        hashable = self._hashable()
        explored = set() if hashable else list()
        pushfunc = explored.add if hashable else explored.append
        unique_elements = list()
        for x in self:
            if x not in explored:
                unique_elements.append(x)
                pushfunc(x)
        return vector(unique_elements)

    def count(self, descend=True):
        if len(self) == 0:
            return vector([])
        counter = Counter(self)
        count_vector = vector(counter.items())
        count_vector.sort(key=lambda x: x[1])
        if descend:
            return count_vector[::-1]
        return count_vector

    def index(self, element):
        try:
            if callable(element):
                for index in range(len(self)):
                    if element(self[index]):
                        return index
                return -1
            i = super().index(element)
            return i
        except Exception as e:
            return -1

    def max(self, key=None):
        if len(self) == 0:
            return None
        m_index = 0
        m_key = self._transform(self[0], key)
        for index in range(1, len(self)):
            i_key = self._transform(self[index], key)
            if i_key > m_key:
                m_key = i_key
                m_index = index
        return self[m_index], m_index


    def min(self, key=None):
        if len(self) == 0:
            return None
        m_index = 0
        m_key = self._transform(self[0], key)
        for index in range(1, len(self)):
            i_key = self._transform(self[index], key)
            if i_key < m_key:
                m_key = i_key
                m_index = index
        return self[m_index], m_index

    def sum(self):
        return self.reduce(lambda x, y: x + y)

    def group_by(self, key=lambda x: x[0]):
        result = _Vector_Dict()
        for x in self:
            k_x = key(x)
            if k_x not in result:
                result[k_x] = vector([x])
            else:
                result[k_x].append(x)
        return result

    def reduce(self, func):
        if len(self) == 0:
            return None
        temp = self[0]
        for x in self[1:]:
            temp = func(temp, x)
        return temp

    def flatten(self):
        return self.reduce(lambda x, y: x + y)

def raw_function(func):
    if "__func__" in func.__dir__():
        return func.__func__
    return func

def generator_wrapper(*args, **kwargs):
    if len(args) == 1 and callable(raw_function(args[0])):
        func = raw_function(args[0])
        @wraps(func)
        def wrapper(*args, **kwargs):
            return ctgenerator(func(*args, **kwargs))
        return wrapper
    else:
        raise TypeError("function is not callable")


class ctgenerator:

    @staticmethod
    def _generate(iterable):
        for x in iterable:
            yield x

    @override
    def __init__(self, generator):
        if "__iter__" in generator.__dir__():
            self.generator = ctgenerator._generate(generator)

    @__init__
    def _(self, generator: "ctgenerator"):
        self.generator = generator

    @__init__
    def _(self, generator: GeneratorType):
        self.generator = generator

    @generator_wrapper
    def map(self, func) -> "ctgenerator":
        for x in self.generator:
            yield func(x)

    @generator_wrapper
    def filter(self, func=None) -> "ctgenerator":
        for x in self.generator:
            if func(x):
                yield x

    def reduce(self, func, initial_value=None):
        if not initial_value:
            initial_value = next(self.generator)
        result = initial_value
        for x in self.generator:
            result = func(initial_value, x)
        return result

    def apply(self, func) -> None:
        for x in self.generator:
            func(x)

    def __iter__(self):
        for x in self.generator:
            yield x

    def __next__(self):
        return next(self.generator)

    def vector(self):
        return vector(self)

class moving_average:

    def __init__(self, lam=0.99, recorded=False):
        self._average = 0
        self.n = 0
        self._b = 0
        self._d = 0
        self.lam = lam
        self._recorded=recorded
        if recorded:
            self.history = vector()

    @methoddispatch
    def update(self, x: float):
        self._b = x + self._b * self.lam
        self._d = 1 + self._d * self.lam
        self._average = self._b / self._d
        if self._recorded:
            self.history.append(x)

    @update.register(torch.Tensor)
    def _(self, x):
        self.update(x.item())

    @update.register(np.ndarray)
    def _(self, x):
        self.update(x[0])

    @property
    def average(self):
        return self._average

    @average.setter
    def average(self, x):
        self.update(x)

    def __str__(self):
        return str(self.average)

    def __repr__(self):
        return str(self.average)

    def __lshift__(self, x):
        return self.update(x)

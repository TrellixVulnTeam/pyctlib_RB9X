import sys
import os
from sys import getsizeof

sys.path.append(os.path.abspath("."))
import zytlib
from zytlib.table import table
import pathlib
import numpy as np
from zytlib import vector, IndexMapping, scope, vhelp
from zytlib.vector import chain_function
from zytlib.filemanager import path, get_relative_path
from zytlib import touch
from zytlib.wrapper import generate_typehint_wrapper
import argparse
from time import sleep
from zytlib import totuple
from zytlib.touch import once
import matplotlib.pyplot as plt
from zytlib.visual.animation import TimeStamp
from zytlib import table
import time

vector.zeros(10).map(lambda x: 1./x)
vector.randn(3,4, truncate_std=1)
vector.from_range(10, lambda x: x)
vector.from_range((3, 4), lambda x, y: x + y)

vector().append(vector(np.zeros(10), np.zeros(10)))

with scope("all"):
    vec = vector(1, 2, 3)
    assert list(vec) == [1, 2, 3]
    vec = vector([1, 2, 3])
    assert list(vec) == [1, 2, 3]
    vec = vector((1, 2, 3))
    assert list(vec) == [1, 2, 3]
    vec = vector()
    for index in range(10):
        vec.append(index)
        assert vec.sum() == sum(_ for _ in range(index+1))
        assert vec.element_type == int
        assert vec.set() == set([_ for _ in range(index + 1)])
        assert vec.ishashable()
    vec.append("hello")
    assert vec.sum() is None
    assert vec.element_type == set([int, str])
    assert vec.set() == set([_ for _ in range(10)] + ["hello"])
    assert vec.ishashable()
    vec = vector.range(10).shuffle()
    vec.sort_()
    assert list(vec) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert vec.max() == 9
    assert vec.min() == 0
    assert list(vector([1, 2, 3, 4, 5, 6]).filter(lambda x: x > 3)) == [4, 5, 6]
    assert list(vector(0, 1, 2, 3).test(lambda x: 1 / x)) == [1, 2, 3]
    assert list(vector(0, 1, 2, 3).testnot(lambda x: 1 / x)) == [0]
    assert list(vector([0, 1, 2]).map(lambda x: x ** 2)) == [0, 1, 4]
    assert list(vector([[0, 1], [2, 3]], recursive=True).rmap(lambda x: x + 1).flatten()) == [1, 2, 3, 4]
    assert list(vector(0, 1, 2, 3, 1).replace(1, -1)) == [0, -1, 2, 3, -1]
    assert list(vector(0, 1, 2, 3, 4).replace(lambda x: x > 2, 2)) == [0, 1, 2, 2, 2]
    assert list(vector(0, 1, 2, 3, 4).replace(lambda x: x > 2, lambda x: x + 2)) == [0, 1, 2, 5, 6]
    assert list(vector([1, 2, 3]) * vector([4, 5, 6])) == [(1, 4), (2, 5), (3, 6)]
    assert list(vector([1, 2, 3]) ** vector([2, 3, 4])) == [(1, 2), (1, 3), (1, 4), (2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (3, 4)]
    assert list(vector([1, 2, 3, 2, 3, 1]).unique()) == [1, 2, 3]
    assert list(vector(0, 1, 2, 3, 4, 0, 1).findall_crash(lambda x: 1 / x)) == [0, 5]
    assert list(vector([1, 2, 3, 4, 2, 3]).findall(lambda x: x > 2)) == [2, 3, 5]
    assert list(vector.zip(vector(1, 2, 3), vector(1, 2, 3), vector(1, 2, 3))) == [(1, 1, 1), (2, 2, 2), (3, 3, 3)]
    assert list(vector([1, 2, 3, 4, 1]).sort_by_index(key=lambda x: -x)) == [1, 4, 3, 2, 1]
    x = vector.range(100).shuffle()
    assert x == vector.range(100).map_index_from(x)
    x = vector.range(100).sample(10, replace=False)
    assert x == vector.range(100).map_index_from(x)
    assert repr(vector.range(10).filter(lambda x: x < 5).unmap_index()) == "[0, 1, 2, 3, 4, Not Defined, Not Defined, Not Defined, Not Defined, Not Defined]"
    vector.range(5).map(lambda x, y: x / y, func_self=lambda x: x.sum())
    assert vector.range(100).reshape(2, -1).shape == (2, 50)
    x = vector.range(100)[:10]
    y = vector.range(100).map_index_from(x)
    assert x == y
    assert list(vector.range(100)[::-1]) == list(range(100)[::-1])
    x = vector.rand(10)
    assert all(x[::-2][::-1] == x[1::2])

with scope("IndexMapping"):
    t1 = IndexMapping(slice(0, 15, 2), 10, True)
    t2 = IndexMapping([4,3,2,1,0], 5, True)
    assert list(t1.map(t2).index_map) == [4, -1, 3, -1, 2, -1, 1, -1, 0, -1]
    t3 = IndexMapping(slice(0, 2, 1), range_size=5, reverse=True)
    assert list(t1.map(t3).index_map) == [0, -1, 1, -1, -1, -1, -1, -1, -1, -1]

with scope("register_result"):
    t = vector.randn(1000)
    r1 = t.map(lambda x: x+1, register_result="plus 1")
    r2 = t.map(lambda x: x+1, register_result="plus 1")
    assert all(r1 == r2)
    f1 = t.filter(lambda x: x > 0, register_result=">0")
    f2 = t.filter(lambda x: x > 0, register_result=">0")
    assert all(f1 == f2)
    assert list(t._vector__map_register.keys()) == ["plus 1"]
    assert list(t._vector__filter_register.keys()) == [">0"]

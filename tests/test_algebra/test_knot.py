# Copyright (c) 2018 Manfred Moitzi
# License: MIT License
from ezdxf.algebra.spline import knot_open_uniform, knot_uniform

open_uniform_order2 = [0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 4.0]
open_uniform_order3 = [0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 5.0, 5.0]
open_uniform_order4 = [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 6.0, 6.0, 6.0]


def test_open_uniform_knot_order_2():
    result = knot_open_uniform(5, 2)
    assert result == open_uniform_order2


def test_open_uniform_knot_order_3():
    result = knot_open_uniform(7, 3)
    assert result == open_uniform_order3


def test_open_uniform_knot_order_4():
    result = knot_open_uniform(9, 4)
    assert result == open_uniform_order4


uniform_order2 = [0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
uniform_order3 = [0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
uniform_order4 = [0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0]


def test_uniform_knot_order_2():
    result = knot_uniform(5, 2)
    assert result == uniform_order2


def test_uniform_knot_order_3():
    result = knot_uniform(7, 3)
    assert result == uniform_order3


def test_uniform_knot_order_4():
    result = knot_uniform(9, 4)
    assert result == uniform_order4

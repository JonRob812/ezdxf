# Created: 2012.01.03
# Copyright (c) 2012-2018 Manfred Moitzi
# License: MIT License
from .vector import Vector, distance
"""

B-Splines
=========

https://www.cl.cam.ac.uk/teaching/2000/AGraphHCI/SMEG/node4.html

n + 1 ... number of control points P_1, P_2, ..., P_{n+1} or P_0, P_1, ..., P_n
k ... order of the B-spline, 2 <= k <= n + 1
degree ... k - 1

B-splines are a more general type of curve than Bezier curves. In a B-spline each control point is associated with a 
basis function.

(87) P(t) = sum {i=1}^{n+1} N_{i,k}(t) P_i, t_min <= t < t_max

There are n + 1 control points,  P_1, P_2, ..., P_{n+1}. The N_{i,k} basis functions are of order k(degree k-1). 
k must be at least 2 (linear), and can be no more than n+1 (the number of control points). The important point here is 
that the order of the curve (linear, quadratic, cubic,...) is therefore not dependent on the number of control points 
(which it is for Bezier curves, where k must always equal n+1).

Equation (87) defines a piecewise continuous function. A knot vector,  (t_1, t_2, ..., t_{k+(n+1)}), must be specified. 
This determines the values of t at which the pieces of curve join, like knots joining bits of string. It is necessary 
that:

(88)  t_i <= t_{i+1}, for all i

The N_{i,k} depend only on the value of k and the values in the knot vector. N is defined recursively as:

(89) N_{i,1}(t)	= 1 for t_i <= t < t_{i+1}; 0 otherwise
     N_{i,k}(t)	= (t-t_i) / ({t_{i+k-1} - t_i}) * N_{i,k-1}(t) + (t_{i+k}-t) / (t_{i+k} - t_{i+1}) * N_{i+1,k-1}(t)

This is essentially a modified version of the idea of taking linear interpolations of linear interpolations of linear 
interpolations ... n


The Knot Vector
---------------

The above explanation shows that the knot vector is very important. The knot vector can, by its definition, be any 
sequence of numbers provided that each one is greater than or equal to the preceding one. Some types of knot vector are 
more useful than others. Knot vectors are generally placed into one of three categories: uniform, open uniform, and 
non-uniform.

Uniform Knot Vector
~~~~~~~~~~~~~~~~~~~

These are knot vectors for which 

(90) t_{i+1} - t_i = constant, for all i

e.g. [1, 2, 3, 4, 5, 6, 7, 8], [0, .25, .5, .75, 1.]

Open Uniform Knot Vector
~~~~~~~~~~~~~~~~~~~~~~~~

These are uniform knot vectors which have k equal knot values at each end
 
(91) t_i = t_1,  i <= k
     t_{i+1} - t_i = constant, k <= i < n+2
     t_i = t_{k+(n+1)}, i >= n + 2

e.g. [0, 0, 0, 0, 1, 2, 3, 4, 4, 4, 4] for k=4, 
     [1, 1, 1, 2, 3, 4, 5, 6, 6, 6] for k=3
     [.1, .1, .1, .1, .1, .3, .5, .7, .7, .7, .7, .7] for k=5

Non-uniform Knot Vector
~~~~~~~~~~~~~~~~~~~~~~~

This is the general case, the only constraint being the standard  t_i <= t_{i+1}, for all i (Equations 88). 

e.g. [1, 3, 7, 22, 23, 23, 49, 50, 50]
     [1, 1, 1, 2, 2, 3, 4, 5, 6, 6, 6, 7, 7, 7]
     [.2, .7, .7, .7, 1.2, 1.2, 2.9, 3.6]

The shapes of the N_{i,k} basis functions are determined entirely by the relative spacing between the knots.
 
    scaling: t_i' = alpha * t_i, for all i
    translating t_i'= t_i + delta t, for all i
    
The knot vector has no effect on the shapes of the N_{i,k}.

The above gives a description of the various types of knot vector but it doesn't really give you any insight into how 
the knot vector determines the shape of the curve. The following subsections look at the different types of knot vector 
in more detail. However, the best way to get to feel for these is to derive and draw the basis functions yourself.

Uniform Knot Vector
~~~~~~~~~~~~~~~~~~~

For simplicity, let t_i = i (this is allowable given that the scaling or translating the knot vector has no effect on 
the shapes of the N_{i,k}). The knot vector thus becomes  [1,2,3, ... ,k+(n+1)] and equation (89) simplifies to:

(92) N_{i,1}(t)	= 1 for t_i <= t < t_{i+1}; 0 otherwise
     N_{i,k}(t)	= (t-i)(k-1) * N_{i,k-1}(t) + (i+k-t)/ (k-1) * N_{i+1,k-1}(t)

Things you can change about a uniform B-spline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With a uniform B-spline, you obviously cannot change the basis functions (they are fixed because all the knots are 
equi-spaced). However you can alter the shape of the curve by modifying a number of things:

Moving control points:

Moving the control points obviously changes the shape of the curve.

Multiple control points:

Sticking two adjacent control points on top of one another causes the curve to pass closer to that point. Stick enough 
adjacent control points on top of one another and you can make the curve pass through that point.

Order:

Increasing the order k increases the continuity of the curve at the knots, increases the smoothness of the curve, and 
tends to move the curve farther from its defining polygon.

Joining the ends:

You can join the ends of the curve to make a closed loop. Say you have M points,  P_1, ... P_M. You want a closed 
B-spline defined by these points. For a given order, k, you will need M+(k-1) control points (repeating the first k-1 
points):  P_1, ... P_M, P_1, ..., P_{k-1}. Your knot vector will thus have M+2k-1 uniformly spaced knots.

Open Uniform Knot Vector
~~~~~~~~~~~~~~~~~~~~~~~~

The previous section intimated that uniform B-splines can be used to describe closed curves: all you have to do is join 
the ends as described above. If you do not want a closed curve, and you use a uniform knot vector, you find that you 
need to specify control points at each end of the curve which the curve doesn't go near.

If you wish your B-spline to start and end at your first and last control points then you need an open uniform knot 
vector. The only difference between this and the uniform knot vector being that the open uniform version has k equal 
knots at each end.

An order k open uniform B-spline with n+1=k points is the Bezier curve of order k.

Non-uniform Knot Vector
~~~~~~~~~~~~~~~~~~~~~~~

Any B-spline whose knot vector is neither uniform nor open uniform is non-uniform. Non-uniform knot vectors allow any 
spacing of the knots, including multiple knots (adjacent knots with the same value). We need to know how this 
non-uniform spacing affects the basis functions in order to understand where non-uniform knot vectors could be useful. 

It transpires that there are only three cases of any interest: 

    1. multiple knots (adjacent knots equal)
    2. adjacent knots more closely spaced than the next knot in the vector
    3. adjacent knots less closely spaced than the next knot in the vector 
    
Obviously, case (3) is simply case (2) turned the other way round.

Multiple knots:

A multiple knot reduces the degree of continuity at that knot value. Across a normal knot the continuity is Ck-2. Each 
extra knot with the same value reduces continuity at that value by one. This is the only way to reduce the continuity of 
the curve at the knot values. If there are k-1 (or more) equal knots then you get a discontinuity in the curve.

Close knots:

As two knots' values get closer together, relative to the spacing of the other knots, the curve moves closer to the 
related control point.

Distant knots:

As two knots' values get further apart, relative to the spacing of the other knots, the curve moves further away from 
the related control point.

Use of Non-uniform Knot Vectors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Standard procedure is to use uniform or open uniform B-splines unless there is a very good reason not to do so. 
Moving two knots closer together tends to move the curve only slightly and so there is usually little point in doing it. 
This leads to the conclusion that the main use of non-uniform B-splines is to allow for multiple knots, which adjust the 
continuity of the curve at the knot values.

However, non-uniform B-splines are the general form of the B-spline because they incorporate open uniform and uniform 
B-splines as special cases. Thus we will talk about non-uniform B-splines when we mean the general case, incorporating 
both uniform and open uniform.

What can you do to control the shape of a B-spline?

    - Move the control points.
    - Add or remove control points.
    - Use multiple control points.
    - Change the order, k.
    - Change the type of knot vector.
    - Change the relative spacing of the knots.
    - Use multiple knot values in the knot vector.

What should the defaults be?

If there are no pressing reasons for doing otherwise, your B-spline should be defined as follows:

    - k=4 (cubic)
    - no multiple control points
    - uniform (for a closed curve) or open uniform (for an open curve) knot vector.

"""


def one_based_array(values, decor=lambda x: x):
    newlist = [0.0]
    newlist.extend(decor(value) for value in values)
    return newlist


def knot_open_uniform(n, order):
    nplusc = n + order
    nplus2 = n + 2
    x = [0.0, 0.0]
    for i in range(2, nplusc+1):
        if (i > order) and (i < nplus2):
            x.append(x[i-1] + 1.0)
        else:
            x.append(x[i-1])
    return x


def knot_uniform(n, order):
    nplusc = n + order
    x = [0.0, 0.0]
    x.extend(float(i) for i in range(1, nplusc))
    return x


def knot_closed(control_points, order):  # closed ???
    # control_points is a 1 based array
    n = len(control_points) - 1
    spacing = list(distance(control_points[i-1], control_points[i]) for i in range(2, n+1))

    maxc = sum(spacing)
    x = [0.0] * (order + 1)
    for i in range(1, n - order + 2):
        csum = sum(spacing[:i])
        numerator = float(i) / float(n - order + 2) * spacing[i] + csum
        x.append(numerator / maxc * float(n - order + 2))
    x.extend([n - order + 2] * (order - 1))
    return x


class BSpline(object):
    """
    Calculate the points of a B-Spline curve, using an uniform open knot vector.

    Accepts 2d points as definition points, but output ist always 3d (z-axis is 0).

    """
    def __init__(self, control_points, order=4, knots=None):
        self._control_points = one_based_array(control_points, Vector)  # control points
        self._cp_count = len(control_points)  # control points count
        self.order = order
        self.nplusc = self._cp_count + self.order
        if knots is None:
            self.knots = self._knots()
        else:
            self.knots = knots

    @property
    def control_points(self):
        return self._control_points[1:]

    @property
    def count(self):
        return self._cp_count

    @property
    def max_t(self):
        return self.knots[self.nplusc]

    def _knots(self):
        return knot_open_uniform(self._cp_count, self.order)

    def _step_size(self, segments):
        return self.max_t / float(segments)

    def approximate(self, segments=20):
        step = self._step_size(segments)
        for point_index in range(segments+1):
            yield self.point(point_index * step)

    def point(self, t):
        """ Get point at SplineCurve(t) as tuple (x, y, z)

        Args:
            t: parameter in range [0, max_t]

        """
        max_t = self.max_t
        if (max_t - t) < 5e-6:
            t = max_t

        nbasis = self.basis(t)
        control_points = self._control_points
        npts1 = self._cp_count + 1

        def axis_value(axis):
            return sum(nbasis[i] * control_points[i][axis] for i in range(1, npts1))

        return tuple(axis_value(axis) for axis in (0, 1, 2))

    def create_nbasis(self, t):
        knots = self.knots
        nbasis = [0.0]  # [0] is a dummy value, 1-based array
        # calculate the first order basis functions n[i][1]
        nbasis.extend(1.0 if knots[i] <= t < knots[i+1] else 0.0 for i in range(1, self.nplusc))
        return nbasis

    def basis(self, t):
        knots = self.knots
        nbasis = self.create_nbasis(t)
        # calculate the higher order basis functions
        for k in range(2, self.order+1):
            for i in range(1, self.nplusc-k+1):
                d = ((t - knots[i]) * nbasis[i]) / (knots[i+k-1] - knots[i]) if nbasis[i] != 0.0 else 0.0
                e = ((knots[i+k] - t) * nbasis[i+1]) / (knots[i+k] - knots[i+1]) if nbasis[i+1] != 0.0 else 0.0
                nbasis[i] = d + e
        if t == knots[self.nplusc]:  # pick up last point
            nbasis[self._cp_count] = 1.0
        return nbasis


class BSplineU(BSpline):
    """
    Calculate the points of a B-Spline curve, uniform (periodic) knot vector.

    """
    def _knots(self):
        return knot_uniform(self._cp_count, self.order)

    def _step_size(self, segments):
        return float(self._cp_count - self.order + 1) / segments

    @property
    def max_t(self):
        return float(self._cp_count)

    def approximate(self, segments=20):
        step = self._step_size(segments)
        base = float(self.order - 1)
        for point_index in range(segments + 1):
            yield self.point(base + point_index * step)


class DBSplineMixin(object):
    # Mixin for DBSpline and DBSplineU
    def point(self, t):
        """
        Get point, 1st and 2nd derivative at B-Spline(t) as tuple (p, d1, d3),
        where p, d1 nad d2 is a tuple (x, y, z).

        Args:
            t: parameter in range [0, max_t]

        """
        max_t = self.max_t
        if (max_t - t) < 5e-6:
            t = max_t

        nbasis, d1nbasis, d2nbasis = self.dbasis(t)
        point = [0.0, 0.0, 0.0]
        d1 = [0.0, 0.0, 0.0]
        d2 = [0.0, 0.0, 0.0]
        for axis in (0, 1, 2):
            for i in range(1, self._cp_count + 1):
                control_point = self._control_points[i][axis]
                point[axis] += nbasis[i] * control_point
                d1[axis] += d1nbasis[i] * control_point
                d2[axis] += d2nbasis[i] * control_point
        return tuple(point), tuple(d1), tuple(d2)

    def dbasis(self, t):
        knots = self.knots
        nbasis = self.create_nbasis2(t)
        d1nbasis = [0.0] * (self.nplusc + 1)  # [0] is a dummy value, 1-based array
        d2nbasis = d1nbasis[:]

        for k in range(2, self.order + 1):
            for i in range(1, self.nplusc - k + 1):
                # calculate basis functions
                b1 = ((t - knots[i]) * nbasis[i]) / (knots[i + k - 1] - knots[i]) if nbasis[i] != 0.0 else 0.0
                b2 = ((knots[i + k] - t) * nbasis[i + 1]) / (knots[i + k] - knots[i + 1]) if nbasis[i + 1] != 0.0 else 0.0

                # calculate first derivative
                f1 = nbasis[i] / (knots[i + k - 1] - knots[i]) if nbasis[i] != 0.0 else 0.0
                f2 = -nbasis[i + 1] / (knots[i + k] - knots[i + 1]) if nbasis[i + 1] != 0.0 else 0.0
                f3 = ((t - knots[i]) * d1nbasis[i]) / (knots[i + k - 1] - knots[i]) if d1nbasis[i] != 0.0 else 0.0
                f4 = ((knots[i + k] - t) * d1nbasis[i + 1]) / (knots[i + k] - knots[i + 1]) if d1nbasis[i + 1] != 0.0 else 0.0

                # calculate second derivative
                s1 = (2 * d1nbasis[i]) / (knots[i + k - 1] - knots[i]) if d1nbasis[i] != 0.0 else 0.0
                s2 = (-2 * d1nbasis[i + 1]) / (knots[i + k] - knots[i + 1]) if d1nbasis[i + 1] != 0.0 else 0.0
                s3 = ((t - knots[i]) * d2nbasis[i]) / (knots[i + k - 1] - knots[i]) if d2nbasis[i] != 0.0 else 0.0
                s4 = ((knots[i + k] - t) * d2nbasis[i + 1]) / (knots[i + k] - knots[i + 1]) if d2nbasis[i + 1] != 0.0 else 0.0

                nbasis[i] = b1 + b2
                d1nbasis[i] = f1 + f2 + f3 + f4
                d2nbasis[i] = s1 + s2 + s3 + s4

        return nbasis, d1nbasis, d2nbasis


class DBSpline(DBSplineMixin, BSpline):
    """
    Calculate the Points and Derivative of a B-Spline curve.

    """
    def create_nbasis2(self, t):
        nbasis = self.create_nbasis(t)
        if t == self.knots[self.nplusc]:
            nbasis[self._cp_count] = 1.0
        return nbasis


class DBSplineU(DBSplineMixin, BSplineU):
    """
    Calculate the Points and Derivative of a B-SplineU curve.

    """
    def create_nbasis2(self, t):
        npts = self._cp_count
        nbasis = self.create_nbasis(t)
        if t == self.knots[npts + 1]:
            nbasis[npts] = 1.0
            nbasis[npts + 1] = 0.0
        return nbasis


"""

Rational B-splines
==================

https://www.cl.cam.ac.uk/teaching/2000/AGraphHCI/SMEG/node5.html:

Rational B-splines have all of the properties of non-rational B-splines plus the following two useful features:
They produce the correct results under projective transformations (while non-rational B-splines only produce the correct
results under affine transformations).

They can be used to represent lines, conics, non-rational B-splines; and, when generalised to patches, can represents
planes, quadrics, and tori.

The antonym of rational is non-rational. Non-rational B-splines are a special case of rational B-splines, just as
uniform B-splines are a special case of non-uniform B-splines. Thus, non-uniform rational B-splines encompass almost
every other possible 3D shape definition. Non-uniform rational B-spline is a bit of a mouthful and so it is generally
abbreviated to NURBS.

We have already learnt all about the the B-spline bit of NURBS and about the non-uniform bit. So now all we need to
know is the meaning of the rational bit and we will fully(?) understand NURBS.

Rational B-splines are defined simply by applying the B-spline equation (Equation 87) to homogeneous coordinates,
rather than normal 3D coordinates.

"""


def weighting(nbasis, weights, npts):
    s = sum(nbasis[i] * weights[i] for i in range(1, npts + 1))
    if s == 0.0:
        r = [0.0] * (npts + 1)
    else:
        r = one_based_array(nbasis[i] * weights[i] / s for i in range(1, npts + 1))
    return r


class RBSpline(BSpline):
    """
    Calculate the points of a rational B-Spline curve, using an uniform open knot vector.

    """
    def __init__(self, control_points, weights, order=3):
        if len(control_points) != len(weights):
            raise ValueError("Item count of 'control_points and 'weights' is different.")
        super(RBSpline, self).__init__(control_points, order)
        self.weights = one_based_array(weights, float)

    def basis(self, t):
        nbasis = super(RBSpline, self).basis(t)
        return weighting(nbasis, self.weights, self._cp_count)


class RBSplineU(BSplineU):
    """
    Calculate the points of a rational B-Spline curve, using an uniform open knot vector.

    """
    def __init__(self, control_points, weights, order=3):
        super(RBSplineU, self).__init__(control_points, order)
        self.weights = one_based_array(weights, float)

    def basis(self, t):
        nbasis = super(RBSplineU, self).basis(t)
        return weighting(nbasis, self.weights, self._cp_count)

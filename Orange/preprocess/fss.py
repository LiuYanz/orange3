import Orange
import numpy as np

from itertools import takewhile
from operator import itemgetter

from Orange.preprocess.preprocess import Preprocess

__all__ = ["SelectBestFeatures", "RemoveNaNColumns"]


class SelectBestFeatures:
    """
    A feature selector that builds a new data set consisting of either the top
    `k` features or all those that exceed a given `threshold`. Features are
    scored using the provided feature scoring `method`. By default it is
    assumed that feature importance diminishes with decreasing scores.

    If both `k` and `threshold` are set, only features satisfying both
    conditions will be selected.

    .. attribute:: method

        Univariate feature scoring method.

    .. attribute:: k

        The number of top features to select.

    .. attribute:: threshold

        A threshold that a feature should meet according to the provided method.

    .. attribute:: decreasing

        The order of feature importance when sorted from the most to the least
        important feature.

    """
    def __init__(self, method=None, k=None, threshold=None, decreasing=True):
        self.method = method
        self.k = k
        self.threshold = threshold
        self.decreasing = decreasing

    def __call__(self, data):
        if not isinstance(data.domain.class_var, self.method.class_type):
            raise ValueError(("Scoring method {} requires a class variable " +
                              "of type {}.").format(
                type(self.method), self.method.class_type))
        features = [f for f in data.domain.attributes
                    if isinstance(f, self.method.feature_type)]
        other = [f for f in data.domain.attributes
                 if not isinstance(f, self.method.feature_type)]
        scores = [self.method(f, data) for f in features]
        best = sorted(zip(scores, features), key=itemgetter(0),
                      reverse=self.decreasing)
        if self.k:
            best = best[:self.k]
        if self.threshold:
            pred = ((lambda x: x[0] >= self.threshold) if self.decreasing else
                    (lambda x: x[0] <= self.threshold))
            best = takewhile(pred, best)

        domain = Orange.data.Domain([f for s, f in best] + other,
                                    data.domain.class_vars, data.domain.metas)
        return data.from_table(domain, data)


class RemoveNaNColumns(Preprocess):
    """
    Removes data columns that contain only unknown values. Returns the
    resulting data set. Does not check optional class attribute(s).

    data : data table
        an input data table
    """
    def __call__(self, data):
        nan_col = np.all(np.isnan(data.X), axis=0)
        att = [a for a, nan in zip(data.domain.attributes, nan_col) if not nan]
        domain = Orange.data.Domain(att, data.domain.class_vars,
                                    data.domain.metas)
        return Orange.data.Table(domain, data)

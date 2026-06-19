"""Tests for the dependency-free agreement metrics."""

import math

from llm_judge import metrics


def test_agreement_rate():
    assert metrics.agreement_rate([1, 2, 3], [1, 2, 3]) == 1.0
    assert metrics.agreement_rate([1, 2, 3], [1, 2, 9]) == 2 / 3


def test_cohen_kappa_perfect_and_chance():
    # Perfect agreement => kappa 1.
    assert math.isclose(metrics.cohen_kappa([1, 2, 1, 2], [1, 2, 1, 2]), 1.0)
    # Total disagreement on a balanced 2-class set => negative kappa.
    assert metrics.cohen_kappa([1, 1, 2, 2], [2, 2, 1, 1]) < 0


def test_weighted_kappa_penalizes_distance():
    pred = [1, 2, 3, 4, 5]
    near = [1, 2, 3, 4, 4]   # one off-by-one
    far = [1, 2, 3, 4, 1]    # one off-by-four
    k_near = metrics.cohen_kappa(pred, near, weights="quadratic")
    k_far = metrics.cohen_kappa(pred, far, weights="quadratic")
    assert k_near > k_far


def test_spearman_monotonic():
    a = [1, 2, 3, 4, 5]
    assert math.isclose(metrics.spearman_rho(a, [2, 4, 6, 8, 10]), 1.0)
    assert math.isclose(metrics.spearman_rho(a, [5, 4, 3, 2, 1]), -1.0)


def test_kendall_tau_bounds():
    a = [1, 2, 3, 4]
    assert math.isclose(metrics.kendall_tau(a, [1, 2, 3, 4]), 1.0)
    assert math.isclose(metrics.kendall_tau(a, [4, 3, 2, 1]), -1.0)


def test_precision_recall_f1():
    pred = [True, True, False, False]
    truth = [True, False, False, True]
    m = metrics.precision_recall_f1(pred, truth)
    assert math.isclose(m["precision"], 0.5)
    assert math.isclose(m["recall"], 0.5)
    assert math.isclose(m["f1"], 0.5)


def test_disagreement_breakdown_surfaces_skew():
    # Judge consistently scores one notch high.
    pred = [2, 3, 4, 5]
    truth = [1, 2, 3, 4]
    out = metrics.disagreement_breakdown(pred, truth)
    assert out["agreement_rate"] == 0.0
    assert out["n"] == 4
    # Every mismatch is the same +1 skew.
    assert set(out["mismatches"]) == {"2->1", "3->2", "4->3", "5->4"}

"""Agreement metrics for validating a judge against human (or reference) labels.

Automated evaluation is only valuable if it correlates with human judgment, and
the useful question is rarely raw agreement — it's whether disagreement is
*systematic*. These metrics let you track that over time.

Implemented in pure Python (no scipy/sklearn) so the package stays dependency-light.
Pick the metric by label structure:

  - binary / categorical pass-fail .... accuracy, precision, recall, f1, cohen_kappa
  - ordinal rating (1-5) .............. spearman_rho, kendall_tau, cohen_kappa(weighted)
  - pairwise preference ............... agreement_rate
"""

from __future__ import annotations

from collections import Counter
from math import sqrt
from typing import Sequence

Number = float


def _check(a: Sequence, b: Sequence) -> None:
    if len(a) != len(b):
        raise ValueError(f"length mismatch: {len(a)} vs {len(b)}")
    if not a:
        raise ValueError("empty input")


def agreement_rate(a: Sequence, b: Sequence) -> float:
    """Fraction of positions where the two label sequences match."""
    _check(a, b)
    return sum(1 for x, y in zip(a, b) if x == y) / len(a)


accuracy = agreement_rate


def cohen_kappa(
    a: Sequence, b: Sequence, *, weights: str | None = None
) -> float:
    """Cohen's kappa: agreement corrected for chance.

    ``weights`` may be ``None`` (nominal), ``"linear"``, or ``"quadratic"``
    (for ordinal labels, penalizing larger disagreements more).
    """
    _check(a, b)
    labels = sorted(set(a) | set(b), key=lambda v: (isinstance(v, str), v))
    idx = {label: i for i, label in enumerate(labels)}
    k = len(labels)
    n = len(a)

    observed = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b):
        observed[idx[x]][idx[y]] += 1

    row = [sum(observed[i]) for i in range(k)]
    col = [sum(observed[i][j] for i in range(k)) for j in range(k)]

    def w(i: int, j: int) -> float:
        if weights is None:
            return 0.0 if i == j else 1.0
        d = abs(i - j)
        if weights == "linear":
            return d / (k - 1)
        if weights == "quadratic":
            return (d / (k - 1)) ** 2
        raise ValueError("weights must be None, 'linear', or 'quadratic'")

    obs_disagree = sum(
        w(i, j) * observed[i][j] for i in range(k) for j in range(k)
    ) / n
    exp_disagree = sum(
        w(i, j) * row[i] * col[j] for i in range(k) for j in range(k)
    ) / (n * n)

    if exp_disagree == 0:
        return 1.0
    return 1.0 - obs_disagree / exp_disagree


def _rank(values: Sequence[Number]) -> list[float]:
    """Average-rank transform (ties share the mean of their ranks)."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1  # 1-based average rank
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman_rho(a: Sequence[Number], b: Sequence[Number]) -> float:
    """Spearman rank correlation (Pearson correlation of ranks)."""
    _check(a, b)
    ra, rb = _rank(a), _rank(b)
    ma = sum(ra) / len(ra)
    mb = sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra)
    vb = sum((y - mb) ** 2 for y in rb)
    if va == 0 or vb == 0:
        return 0.0
    return cov / sqrt(va * vb)


def kendall_tau(a: Sequence[Number], b: Sequence[Number]) -> float:
    """Kendall's tau-b rank correlation (handles ties)."""
    _check(a, b)
    n = len(a)
    concordant = discordant = 0
    ties_a = ties_b = 0
    for i in range(n):
        for j in range(i + 1, n):
            da = a[i] - a[j]
            db = b[i] - b[j]
            prod = da * db
            if prod > 0:
                concordant += 1
            elif prod < 0:
                discordant += 1
            else:
                if da == 0:
                    ties_a += 1
                if db == 0:
                    ties_b += 1
    n0 = n * (n - 1) / 2
    denom = sqrt((n0 - ties_a) * (n0 - ties_b))
    if denom == 0:
        return 0.0
    return (concordant - discordant) / denom


def precision_recall_f1(
    pred: Sequence, truth: Sequence, *, positive_label=True
) -> dict[str, float]:
    """Precision, recall, and F1 for a binary classification against ``truth``."""
    _check(pred, truth)
    tp = sum(1 for p, t in zip(pred, truth) if p == positive_label and t == positive_label)
    fp = sum(1 for p, t in zip(pred, truth) if p == positive_label and t != positive_label)
    fn = sum(1 for p, t in zip(pred, truth) if p != positive_label and t == positive_label)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )
    return {"precision": precision, "recall": recall, "f1": f1}


def disagreement_breakdown(pred: Sequence, truth: Sequence) -> dict:
    """Summarize *where* a judge disagrees — the signal that matters most.

    Returns the overall agreement rate plus a count of each (pred, truth)
    mismatch pair, so systematic skew (e.g. the judge always scoring one notch
    high) is visible rather than hidden in an averaged number.
    """
    _check(pred, truth)
    mismatches = Counter(
        (p, t) for p, t in zip(pred, truth) if p != t
    )
    return {
        "agreement_rate": agreement_rate(pred, truth),
        "n": len(pred),
        "mismatches": {f"{p}->{t}": c for (p, t), c in mismatches.most_common()},
    }

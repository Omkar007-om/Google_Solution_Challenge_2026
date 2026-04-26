"""SHAP explainability helpers for the SAR risk model.

The risk score is currently deterministic and rule-based. Kernel SHAP is used
when available because it can explain any black-box scoring function.
"""

from __future__ import annotations

from typing import Any, Callable


def explain_risk_score(
    feature_values: dict[str, Any],
    feature_metadata: dict[str, dict[str, Any]],
    score_fn: Callable[[dict[str, Any]], float],
    final_score: float,
) -> dict[str, Any]:
    """Explain a SAR risk score with native SHAP, with a safe fallback."""

    try:
        return _kernel_shap_explanation(feature_values, feature_metadata, score_fn, final_score)
    except Exception as exc:
        return _additive_fallback_explanation(
            feature_values,
            feature_metadata,
            score_fn,
            final_score,
            fallback_reason=str(exc),
        )


def _kernel_shap_explanation(
    feature_values: dict[str, Any],
    feature_metadata: dict[str, dict[str, Any]],
    score_fn: Callable[[dict[str, Any]], float],
    final_score: float,
) -> dict[str, Any]:
    import numpy as np
    import shap

    feature_names = list(feature_values.keys())
    observed = np.array([[_as_numeric(feature_values[name]) for name in feature_names]], dtype=float)
    background = np.zeros((1, len(feature_names)), dtype=float)

    def predict(rows):
        predictions = []
        for row in rows:
            row_features = {
                name: _from_numeric(row[index], feature_values[name])
                for index, name in enumerate(feature_names)
            }
            predictions.append(score_fn(row_features))
        return np.array(predictions, dtype=float)

    explainer = shap.KernelExplainer(predict, background)
    raw_values = explainer.shap_values(
        observed,
        nsamples=max(50, len(feature_names) * 8),
        silent=True,
    )
    values = raw_values[0] if isinstance(raw_values, list) else raw_values[0]
    expected = explainer.expected_value[0] if isinstance(explainer.expected_value, list) else explainer.expected_value

    contributions = [
        _contribution(
            feature=name,
            value=feature_values[name],
            shap_value=float(values[index]),
            metadata=feature_metadata.get(name, {}),
        )
        for index, name in enumerate(feature_names)
        if abs(float(values[index])) > 0.001
    ]

    return _format_explanation(
        method="kernel_shap",
        base_value=float(expected),
        raw_score_before_cap=score_fn(feature_values),
        final_score=final_score,
        contributions=contributions,
        note="Native SHAP KernelExplainer output for the SAR risk scoring function.",
    )


def _additive_fallback_explanation(
    feature_values: dict[str, Any],
    feature_metadata: dict[str, dict[str, Any]],
    score_fn: Callable[[dict[str, Any]], float],
    final_score: float,
    fallback_reason: str,
) -> dict[str, Any]:
    contributions = [
        _contribution(
            feature=name,
            value=value,
            shap_value=float(feature_metadata.get(name, {}).get("weight", 0)),
            metadata=feature_metadata.get(name, {}),
        )
        for name, value in feature_values.items()
        if _as_numeric(value) and feature_metadata.get(name, {}).get("weight", 0)
    ]

    return _format_explanation(
        method="additive_rule_fallback",
        base_value=0,
        raw_score_before_cap=score_fn(feature_values),
        final_score=final_score,
        contributions=contributions,
        note=(
            "Native SHAP could not run in this environment, so additive rule "
            f"contributions were used. Reason: {fallback_reason}"
        ),
    )


def _format_explanation(
    method: str,
    base_value: float,
    raw_score_before_cap: float,
    final_score: float,
    contributions: list[dict[str, Any]],
    note: str,
) -> dict[str, Any]:
    ordered = sorted(contributions, key=lambda item: abs(item["shap_value"]), reverse=True)
    denominator = sum(abs(item["shap_value"]) for item in ordered) or 1
    for item in ordered:
        item["impact_pct"] = round((abs(item["shap_value"]) / denominator) * 100, 2)

    return {
        "method": method,
        "base_value": round(base_value, 2),
        "raw_score_before_cap": round(raw_score_before_cap, 2),
        "final_score": round(final_score, 2),
        "score_cap": 100,
        "values": ordered,
        "top_drivers": ordered[:5],
        "note": note,
    }


def _contribution(
    feature: str,
    value: Any,
    shap_value: float,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "feature": feature,
        "display_name": metadata.get("display_name", feature.replace("_", " ").title()),
        "value": value,
        "shap_value": round(shap_value, 2),
        "direction": "increases_risk" if shap_value >= 0 else "decreases_risk",
        "reason": metadata.get("reason", "This feature contributed to the risk score."),
    }


def _as_numeric(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _from_numeric(value: float, original_value: Any) -> Any:
    if isinstance(original_value, bool):
        return bool(round(float(value)))
    if isinstance(original_value, int):
        return int(round(float(value)))
    return float(value)

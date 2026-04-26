"""Pipeline Step 3: enrich flags with risk score and SHAP evidence."""

from __future__ import annotations

from typing import Dict

from app.agents.base import BaseAgent
from app.utils.shap_explainer import explain_risk_score


class FeatureProcessingAgent(BaseAgent):
    """Compute aggregate features, risk score, and SHAP explainability."""

    name = "Risk Enrichment"

    async def process(self, data: Dict) -> Dict:
        transactions = data.get("transactions", [])
        flags = data.get("analysis", {}).get("flags", [])

        amounts = [txn["amount"] for txn in transactions]
        total_amount = sum(amounts)
        count = len(transactions)
        avg_amount = total_amount / count if count else 0.0
        max_amount = max(amounts) if amounts else 0.0
        min_amount = min(amounts) if amounts else 0.0
        high_value_txns = [txn for txn in transactions if txn["amount"] >= 1_000_000]
        counterparties = {txn["to_account"] for txn in transactions}
        locations = {txn["location"] for txn in transactions}

        features = {
            "total_transactions": count,
            "total_amount": round(total_amount, 2),
            "avg_amount": round(avg_amount, 2),
            "max_amount": round(max_amount, 2),
            "min_amount": round(min_amount, 2),
            "high_value_count": len(high_value_txns),
            "unique_counterparties": len(counterparties),
            "unique_locations": len(locations),
            "flagged_transactions": len({flag["transaction_id"] for flag in flags}),
        }

        typologies = set(data.get("analysis", {}).get("typologies", []))
        weights = {
            "large_anomaly": 25,
            "offshore_exposure": 20,
            "structuring_smurfing": 30,
            "round_tripping": 20,
            "missing_purpose": 5,
        }
        feature_values = {typology: typology in typologies for typology in weights}
        feature_values["high_cumulative_volume"] = total_amount >= 2_500_000
        feature_values["multiple_counterparties"] = len(counterparties) >= 5

        feature_metadata = _feature_metadata(weights)
        feature_metadata["high_cumulative_volume"] = {
            "weight": 15,
            "display_name": "High Cumulative Transaction Volume",
            "reason": "The total reviewed value crossed the high-volume threshold.",
        }
        feature_metadata["multiple_counterparties"] = {
            "weight": 10,
            "display_name": "Multiple Counterparties",
            "reason": "The account interacted with several counterparties in the reviewed period.",
        }

        raw_score = _score_features(feature_values, feature_metadata)
        score = min(raw_score, 100.0)
        shap_explanation = explain_risk_score(
            feature_values=feature_values,
            feature_metadata=feature_metadata,
            score_fn=lambda values: _score_features(values, feature_metadata),
            final_score=score,
        )
        factors = _risk_factors(feature_values, feature_metadata)

        if score >= 80:
            level = "CRITICAL"
        elif score >= 60:
            level = "HIGH"
        elif score >= 30:
            level = "MEDIUM"
        else:
            level = "LOW"

        data["features"] = features
        data["risk"] = {
            "score": int(score),
            "level": level,
            "factors": factors or ["No material risk indicators detected"],
            "shap_explanation": shap_explanation,
        }
        return data


def _feature_metadata(weights: dict[str, int]) -> dict[str, dict]:
    descriptions = {
        "large_anomaly": "Very high value activity increased the risk score.",
        "offshore_exposure": "Offshore or high-risk location exposure increased the risk score.",
        "structuring_smurfing": "Repeated near-threshold transactions increased the risk score.",
        "round_tripping": "Funds moving back between the same parties increased the risk score.",
        "missing_purpose": "Missing payment purpose reduced transaction transparency.",
    }
    return {
        feature: {
            "weight": weight,
            "display_name": feature.replace("_", " ").title(),
            "reason": descriptions.get(feature, "This indicator increased the risk score."),
        }
        for feature, weight in weights.items()
    }


def _score_features(feature_values: dict, feature_metadata: dict[str, dict]) -> float:
    score = 0.0
    for feature, value in feature_values.items():
        if _is_active(value):
            score += float(feature_metadata.get(feature, {}).get("weight", 0))
    return min(score, 100.0)


def _risk_factors(feature_values: dict, feature_metadata: dict[str, dict]) -> list[str]:
    return [
        metadata.get("display_name", feature.replace("_", " ").title())
        for feature, metadata in feature_metadata.items()
        if _is_active(feature_values.get(feature))
    ]


def _is_active(value) -> bool:
    if isinstance(value, (int, float)):
        return bool(round(float(value)))
    return bool(value)

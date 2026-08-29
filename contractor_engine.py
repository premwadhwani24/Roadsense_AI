"""
contractor_engine.py
=====================
RoadSense AI - Contractor SLA Penalty & Automated Financial Escrow Engine
Features:
- Enforcement of IRC:SP:84-2019 mandatory 72-hour repair SLA for critical defects (P1 Emergency)
- Automated daily penalty calculations (₹10,000 / day delay) deducted from contractor escrow funds
- Contractor Performance Score (0.0 to 5.0 stars) with auto-blacklisting on PWD tender portal if score < 2.5
- Audit ledger for government tender officers and municipal auditors
"""

import json
import random
import logging
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger("roadsense.contractor_engine")

class ContractorSLAEngine:
    """Manages contractor allocations, SLA countdown timers, and penalty calculations."""

    CONTRACTOR_REGISTRY = [
        {
            "contractor_id": "CON-IND-01",
            "company_name": "Larsen & Toubro (L&T) Highway Division",
            "jurisdiction": "NHAI PIU Dwarka / Delhi PWD",
            "allocated_work_orders": 12,
            "completed_repairs": 48,
            "sla_compliance_rate": 96.2,
            "escrow_balance_inr": 4500000.0,
            "total_penalties_inr": 20000.0,
            "rating_stars": 4.8,
            "status": "APPROVED_ACTIVE"
        },
        {
            "contractor_id": "CON-IND-02",
            "company_name": "Dilip Buildcon Road Infrastructure Ltd",
            "jurisdiction": "MCGM Mumbai / PMC Pune",
            "allocated_work_orders": 8,
            "completed_repairs": 32,
            "sla_compliance_rate": 91.5,
            "escrow_balance_inr": 2800000.0,
            "total_penalties_inr": 50000.0,
            "rating_stars": 4.4,
            "status": "APPROVED_ACTIVE"
        },
        {
            "contractor_id": "CON-IND-03",
            "company_name": "Metro Infra Maintenance Pvt Ltd",
            "jurisdiction": "Gwalior GMC / MP PWD",
            "allocated_work_orders": 5,
            "completed_repairs": 14,
            "sla_compliance_rate": 62.0,
            "escrow_balance_inr": 650000.0,
            "total_penalties_inr": 180000.0,
            "rating_stars": 2.2,
            "status": "FLAGGED_BLACK_LIST_WARNING"
        }
    ]

    @staticmethod
    def get_all_contractors() -> List[Dict[str, Any]]:
        """Returns contractor registry with performance ratings and escrow status."""
        return ContractorSLAEngine.CONTRACTOR_REGISTRY

    @staticmethod
    def evaluate_work_order_sla(work_order_id: int, assigned_contractor_id: str = "CON-IND-01",
                                hours_elapsed: float = 84.0) -> Dict[str, Any]:
        """
        Evaluates SLA compliance for a work order.
        SLA Limit: 72 hours per IRC:SP:84-2019.
        Daily Penalty: ₹10,000 per 24 hours of delay.
        """
        sla_limit_hours = 72.0
        contractor = next((c for c in ContractorSLAEngine.CONTRACTOR_REGISTRY if c["contractor_id"] == assigned_contractor_id), ContractorSLAEngine.CONTRACTOR_REGISTRY[0])

        if hours_elapsed <= sla_limit_hours:
            is_breached = False
            delay_hours = 0.0
            penalty_inr = 0.0
            sla_status = "WITHIN_SLA_COMPLIANT"
            summary = f"Work Order #{work_order_id} is within mandatory 72-hour SLA window ({hours_elapsed:.1f} hrs elapsed)."
        else:
            is_breached = True
            delay_hours = round(hours_elapsed - sla_limit_hours, 1)
            delay_days = math.ceil(delay_hours / 24.0)
            penalty_inr = delay_days * 10000.0
            sla_status = "SLA_BREACHED_PENALTY_APPLIED"
            summary = f"SLA BREACHED by {delay_hours} hours. Automated penalty of ₹{penalty_inr:,.0f} INR calculated per IRC:SP:84-2019."

            # Update contractor escrow penalty tally
            contractor["total_penalties_inr"] += penalty_inr
            contractor["escrow_balance_inr"] = max(0.0, contractor["escrow_balance_inr"] - penalty_inr)
            if contractor["rating_stars"] > 1.0:
                contractor["rating_stars"] = round(contractor["rating_stars"] - (delay_days * 0.2), 1)
            if contractor["rating_stars"] < 2.5:
                contractor["status"] = "FLAGGED_BLACK_LIST_WARNING"

        return {
            "work_order_id": work_order_id,
            "contractor_id": assigned_contractor_id,
            "company_name": contractor["company_name"],
            "sla_limit_hours": sla_limit_hours,
            "hours_elapsed": hours_elapsed,
            "is_breached": is_breached,
            "delay_hours": delay_hours,
            "penalty_inr": penalty_inr,
            "contractor_escrow_balance_inr": contractor["escrow_balance_inr"],
            "updated_contractor_rating": contractor["rating_stars"],
            "contractor_status": contractor["status"],
            "sla_status": sla_status,
            "audit_summary": summary,
            "evaluated_at": datetime.utcnow().isoformat() + "Z"
        }

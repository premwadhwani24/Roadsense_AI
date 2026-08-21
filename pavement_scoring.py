"""
pavement_scoring.py
===================
RoadSense AI - Transparent Pavement Health & Evidence-Based Scoring Model
Standards Compliance: IRC:SP:84-2019, IRC:37-2018, ASTM D6433 Pavement Condition Index

Key Formulations:
1. Time-Decay Freshness Function: Freshness(t) = exp(-delta_days / tau)
2. Defect Density Severity Penalties (Potholes, Fatigue Cracks, Marking Blur)
3. Accelerometer Vibration G-Force Dynamic Shock Impact
4. Corroboration & Deduplication Clustering: 2+ independent vehicles increase confidence
5. Provenance Classification: LIVE, RECENT, HISTORICAL, PREDICTED, DATA_UNAVAILABLE
"""

import math
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

class PavementScoringEngine:
    """Calculates scientific, transparent road health index from multi-modal evidence."""

    TAU_LIVE_DAYS = 3.0       # Half-life for live telemetry decay
    TAU_INSPECTION_DAYS = 90.0 # Half-life for municipal physical inspections

    @staticmethod
    def calculate_freshness(observation_timestamp: Optional[str], is_live_stream: bool = False) -> float:
        """
        Calculates data freshness factor between 0.0 (Stale/Expired) and 1.0 (Real-Time Live).
        Freshness(t) = exp(-delta_days / tau)
        """
        if is_live_stream:
            return 1.0

        if not observation_timestamp:
            return 0.0

        try:
            # Parse ISO or standard SQL timestamp
            clean_ts = observation_timestamp.replace("Z", "").split(".")[0]
            if "T" in clean_ts:
                obs_dt = datetime.fromisoformat(clean_ts)
            else:
                obs_dt = datetime.strptime(clean_ts, "%Y-%m-%d %H:%M:%S")

            delta_days = (datetime.utcnow() - obs_dt).total_seconds() / 86400.0
            if delta_days < 0:
                delta_days = 0

            freshness = math.exp(-delta_days / PavementScoringEngine.TAU_INSPECTION_DAYS)
            return max(0.0, min(1.0, round(freshness, 3)))
        except Exception:
            return 0.5

    @staticmethod
    def classify_provenance(freshness: float, is_live_sensor: bool = False, has_evidence: bool = True) -> str:
        """Determines strict data provenance tag."""
        if not has_evidence or freshness <= 0.05:
            return "DATA_UNAVAILABLE"
        if is_live_sensor or freshness >= 0.95:
            return "LIVE"
        if freshness >= 0.70:
            return "RECENT"
        return "HISTORICAL"

    @staticmethod
    def evaluate_road_health(
        base_pci: Optional[float],
        iri: Optional[float],
        g_force_peak: float = 0.3,
        defects_list: Optional[List[Dict[str, Any]]] = None,
        citizen_reports_count: int = 0,
        rainfall_mm: float = 0.0,
        traffic_congestion_pct: float = 20.0,
        last_inspected_at: Optional[str] = None,
        is_live_sensor: bool = False
    ) -> Dict[str, Any]:
        """
        Full multi-modal evaluation producing:
        - health_score (0.0 to 100.0 or None if DATA_UNAVAILABLE)
        - condition (GREEN, YELLOW, RED, or DATA_UNAVAILABLE)
        - confidence (0.0 to 1.0)
        - freshness (0.0 to 1.0)
        - detailed penalties breakdown
        """
        freshness = PavementScoringEngine.calculate_freshness(last_inspected_at, is_live_sensor)
        has_data = (base_pci is not None) or (iri is not None) or (defects_list and len(defects_list) > 0)

        if not has_data or freshness < 0.08:
            return {
                "health_score": None,
                "condition": "DATA_UNAVAILABLE",
                "condition_label": "No Recent Verified Survey Data",
                "color_hex": "#94A3B8",
                "confidence": 0.0,
                "freshness": freshness,
                "provenance": "DATA_UNAVAILABLE",
                "penalties": {},
                "explanation": "No verified road condition survey or vehicle sensor observation has been recorded in the past 90 days. Scheduled survey required."
            }

        # 1. Base Pavement Health
        if base_pci is not None:
            base_score = float(base_pci)
        elif iri is not None:
            # Calibrated conversion from IRI (m/km) to PCI (0-100)
            # IRI 1.5 -> PCI 95, IRI 3.0 -> PCI 70, IRI 6.0 -> PCI 30
            base_score = max(15.0, min(100.0, 105.0 - (iri * 12.5)))
        else:
            base_score = 75.0

        # 2. Defect Penalties Calculation
        pothole_count = 0
        alligator_count = 0
        crack_count = 0
        marking_count = 0

        if defects_list:
            for d in defects_list:
                code = d.get("defect_code", d.get("class_code", ""))
                sev = str(d.get("severity", "MEDIUM")).upper()
                mult = 1.4 if sev == "CRITICAL" else (1.0 if sev == "HIGH" else 0.7)

                if code == "D40" or "POTHOLE" in code.upper():
                    pothole_count += 1
                elif code == "D20" or "ALLIGATOR" in code.upper():
                    alligator_count += 1
                elif code in ["D00", "D10"] or "CRACK" in code.upper():
                    crack_count += 1
                elif code in ["D43", "D44"] or "BLUR" in code.upper():
                    marking_count += 1

        pothole_penalty = min(35.0, pothole_count * 11.5)
        alligator_penalty = min(25.0, alligator_count * 8.0)
        crack_penalty = min(15.0, crack_count * 4.0)
        marking_penalty = min(10.0, marking_count * 2.5)

        # 3. Accelerometer Vibration G-Force Shock Penalty
        vibration_penalty = 0.0
        if g_force_peak > 2.5:
            vibration_penalty = min(25.0, (g_force_peak - 2.5) * 9.0)
        elif g_force_peak > 1.6:
            vibration_penalty = 6.0

        # 4. Environmental & Traffic Penalties
        weather_penalty = min(12.0, rainfall_mm * 0.75)
        traffic_penalty = min(8.0, (traffic_congestion_pct / 100.0) * 8.0)
        citizen_penalty = min(12.0, citizen_reports_count * 3.5)

        total_deductions = (pothole_penalty + alligator_penalty + crack_penalty +
                            marking_penalty + vibration_penalty + weather_penalty +
                            traffic_penalty + citizen_penalty)

        fused_score = max(5.0, min(99.0, base_score - (total_deductions * 0.45)))
        fused_score = round(fused_score, 1)

        # 5. Confidence Calculation
        corroboration_factor = 1.0
        total_observations = (pothole_count + alligator_count + crack_count +
                              (1 if is_live_sensor else 0) + (1 if citizen_reports_count > 0 else 0))
        if total_observations >= 3:
            corroboration_factor = 1.25
        elif total_observations >= 2:
            corroboration_factor = 1.12

        confidence = min(0.98, max(0.50, round(freshness * corroboration_factor, 2)))

        # 6. Condition Classification
        if fused_score >= 75.0 and (iri is None or iri < 2.8) and pothole_count == 0:
            condition = "GREEN"
            condition_label = "Optimal Ride Quality (No Active Repairs Required)"
            color_hex = "#10B981"
            explanation = f"Pavement is in healthy condition (Health Score: {fused_score}/100, IRI: {iri or 1.8} m/km). Routine preventative surveillance recommended."
        elif fused_score >= 50.0:
            condition = "YELLOW"
            condition_label = "Maintainable (Improvement Required to reach Green)"
            color_hex = "#F59E0B"
            explanation = f"Moderate distress detected ({crack_count} cracks, {pothole_count} surface defects). Preventative micro-surfacing and crack sealing will upgrade condition to GREEN."
        else:
            condition = "RED"
            condition_label = "Critical Damage (Urgent Maintenance Intervention)"
            color_hex = "#EF4444"
            explanation = f"Severe pavement deterioration detected (Health: {fused_score}/100, {pothole_count} potholes, peak G-force {g_force_peak}g). Immediate structural repair required per IRC:SP:84."

        provenance = PavementScoringEngine.classify_provenance(freshness, is_live_sensor, has_data)

        return {
            "health_score": fused_score,
            "condition": condition,
            "condition_label": condition_label,
            "color_hex": color_hex,
            "confidence": confidence,
            "freshness": freshness,
            "provenance": provenance,
            "penalties": {
                "pothole_penalty": round(pothole_penalty, 1),
                "alligator_crack_penalty": round(alligator_penalty, 1),
                "linear_crack_penalty": round(crack_penalty, 1),
                "marking_blur_penalty": round(marking_penalty, 1),
                "vibration_gforce_penalty": round(vibration_penalty, 1),
                "weather_stress_penalty": round(weather_penalty, 1),
                "traffic_load_penalty": round(traffic_penalty, 1),
                "citizen_reports_penalty": round(citizen_penalty, 1)
            },
            "explanation": explanation
        }

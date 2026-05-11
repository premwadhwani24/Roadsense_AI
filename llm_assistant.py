import random
from datetime import datetime

class LLMAssistant:
    """
    Mock integration for an LLM (Large Language Model) Decision Assistant.
    Provides natural language summaries of complex road data.
    """
    
    @staticmethod
    def generate_maintenance_recommendation(road_name: str, health_score: float, anomalies: list) -> str:
        """Generates a natural language advisory for city engineers."""
        
        if health_score > 80:
            return f"The {road_name} segment is currently in excellent condition with a health score of {health_score}. No immediate maintenance is recommended. Continue passive monitoring."
        elif health_score > 50:
            anomaly_text = f"We detected {len(anomalies)} minor anomalies." if anomalies else "No major anomalies isolated."
            return f"{road_name} is showing moderate signs of wear (Score: {health_score}). {anomaly_text} A routine inspection is recommended within the next 45 days to prevent further degradation."
        else:
            return f"URGENT: {road_name} is critically degraded (Score: {health_score}). Historical data indicates high risk of complete surface failure. Immediate resurfacing work is advised."

    @staticmethod
    def generate_budget_summary(city: str, total_budget: float, spent: float) -> str:
        remaining = total_budget - spent
        percentage = (spent / total_budget) * 100 if total_budget > 0 else 0
        
        if percentage > 80:
            return f"WARNING: {city} has utilized {percentage:.1f}% of its infrastructure budget. We recommend freezing low-priority repairs immediately."
        return f"{city} budget is healthy. {remaining:,.2f} remains available out of {total_budget:,.2f}. You have sufficient funds to action proactive AI maintenance tasks."

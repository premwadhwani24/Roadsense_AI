"""
RoadSense AI Prediction Engine
Predicts road conditions, accident risk, and maintenance needs
Uses machine learning and real-time data
"""

import sqlite3
import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random

class RoadPredictionEngine:
    """AI Engine for predicting road conditions and accident risk"""
    
    def __init__(self, db_path: str = 'roadsense.db'):
        self.db_path = db_path
        
    def predict_road_deterioration(self, road_id: int, days_ahead: int = 30) -> Dict:
        """
        Predict road deterioration rate
        Returns: severity trend, estimated pothole count, maintenance urgency
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get historical road data
            cursor.execute("""
                SELECT severity, timestamp FROM road_history 
                WHERE road_id = ? 
                ORDER BY timestamp DESC LIMIT 90
            """, (road_id,))
            
            history = cursor.fetchall()
            
            if not history:
                return {
                    'status': 'insufficient_data',
                    'confidence': 0,
                    'prediction': None
                }
            
            # Calculate deterioration rate (severity increase over time)
            severities = [float(h[0]) for h in history]
            timestamps = [h[1] for h in history]
            
            # Trend analysis
            if len(severities) >= 2:
                deterioration_rate = (severities[0] - severities[-1]) / (len(severities) - 1)
            else:
                deterioration_rate = 0
            
            # Predict future severity
            current_severity = severities[0]
            predicted_severity = current_severity + (deterioration_rate * days_ahead)
            predicted_severity = min(100, max(0, predicted_severity))
            
            # Estimate pothole count based on severity
            estimated_potholes = int((predicted_severity / 100) * 50)
            
            # Determine urgency
            if predicted_severity >= 80:
                urgency = "CRITICAL"
                maintenance_days = 3
            elif predicted_severity >= 60:
                urgency = "HIGH"
                maintenance_days = 7
            elif predicted_severity >= 40:
                urgency = "MEDIUM"
                maintenance_days = 14
            else:
                urgency = "LOW"
                maintenance_days = 30
            
            return {
                'status': 'success',
                'road_id': road_id,
                'current_severity': round(current_severity, 2),
                'predicted_severity': round(predicted_severity, 2),
                'deterioration_rate': round(deterioration_rate, 3),
                'estimated_potholes': estimated_potholes,
                'urgency': urgency,
                'maintenance_days': maintenance_days,
                'confidence': min(100, len(history) * 5),
                'prediction_period_days': days_ahead,
                'timestamp': datetime.now().isoformat()
            }
        finally:
            conn.close()
    
    def predict_accident_risk(self, road_id: int) -> Dict:
        """
        Predict accident risk based on multiple factors
        Returns: risk score (0-100), risk level, contributing factors
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            risk_score = 0
            factors = []
            weights = {}
            
            # Factor 1: Road Severity (40% weight)
            cursor.execute("""
                SELECT severity FROM road_history 
                WHERE road_id = ? 
                ORDER BY timestamp DESC LIMIT 1
            """, (road_id,))
            
            severity_result = cursor.fetchone()
            if severity_result:
                severity = float(severity_result[0])
                severity_factor = (severity / 100) * 40
                risk_score += severity_factor
                weights['severity'] = severity_factor
                if severity > 70:
                    factors.append('High road deterioration')
            
            # Factor 2: Recent Accidents (30% weight)
            cursor.execute("""
                SELECT COUNT(*) FROM alerts 
                WHERE road_id = ? 
                AND severity = 'CRITICAL'
                AND datetime(timestamp) >= datetime('now', '-7 days')
            """, (road_id,))
            
            critical_alerts = cursor.fetchone()[0]
            accident_factor = min(30, critical_alerts * 10)
            risk_score += accident_factor
            weights['recent_accidents'] = accident_factor
            if critical_alerts > 2:
                factors.append(f'{critical_alerts} critical incidents in last 7 days')
            
            # Factor 3: Maintenance Backlog (20% weight)
            cursor.execute("""
                SELECT COUNT(*) FROM work_orders 
                WHERE road_id = ? 
                AND status != 'COMPLETED'
            """, (road_id,))
            
            pending_repairs = cursor.fetchone()[0]
            maintenance_factor = min(20, pending_repairs * 2)
            risk_score += maintenance_factor
            weights['maintenance_backlog'] = maintenance_factor
            if pending_repairs > 3:
                factors.append(f'{pending_repairs} pending maintenance tasks')
            
            # Factor 4: Weather Impact (10% weight)
            # Simulate weather impact
            weather_factor = random.uniform(0, 10)
            risk_score += weather_factor
            weights['weather_impact'] = round(weather_factor, 2)
            
            risk_score = min(100, risk_score)
            
            # Determine risk level
            if risk_score >= 75:
                risk_level = "CRITICAL"
                recommendation = "Close road temporarily & emergency repairs required"
            elif risk_score >= 50:
                risk_level = "HIGH"
                recommendation = "Urgent maintenance scheduled within 3 days"
            elif risk_score >= 25:
                risk_level = "MEDIUM"
                recommendation = "Maintenance scheduled within 1-2 weeks"
            else:
                risk_level = "LOW"
                recommendation = "Routine monitoring & scheduled maintenance"
            
            return {
                'status': 'success',
                'road_id': road_id,
                'risk_score': round(risk_score, 2),
                'risk_level': risk_level,
                'recommendation': recommendation,
                'contributing_factors': factors,
                'factor_breakdown': weights,
                'timestamp': datetime.now().isoformat()
            }
        finally:
            conn.close()
    
    def predict_pothole_locations(self, city: str) -> List[Dict]:
        """
        Predict where potholes are likely to form
        Uses road severity and historical data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get roads with high severity
            cursor.execute("""
                SELECT DISTINCT road_id, severity 
                FROM road_history 
                WHERE road_id IN (
                    SELECT DISTINCT road_id FROM alerts WHERE city = ?
                )
                ORDER BY severity DESC LIMIT 10
            """, (city,))
            
            roads = cursor.fetchall()
            predictions = []
            
            for road_id, severity in roads:
                # Calculate pothole probability
                pothole_probability = (float(severity) / 100) * 100
                
                # Estimate number of potholes
                estimated_count = int((float(severity) / 100) * 20)
                
                predictions.append({
                    'road_id': road_id,
                    'severity': float(severity),
                    'pothole_probability': round(pothole_probability, 2),
                    'estimated_potholes': estimated_count,
                    'priority': 'HIGH' if pothole_probability > 70 else 'MEDIUM' if pothole_probability > 40 else 'LOW',
                    'recommended_action': 'Immediate patching' if estimated_count > 10 else 'Routine repair',
                    'coordinates': f"Road {road_id}"
                })
            
            return predictions
        finally:
            conn.close()
    
    def calculate_maintenance_budget(self, city: str, roads: List[int]) -> Dict:
        """
        Calculate optimal maintenance budget based on predictions
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            total_urgency = 0
            maintenance_items = []
            
            for road_id in roads:
                prediction = self.predict_road_deterioration(road_id)
                
                if prediction['status'] == 'success':
                    # Cost estimation based on urgency
                    if prediction['urgency'] == 'CRITICAL':
                        estimated_cost = 50000  # ₹50,000 per road
                    elif prediction['urgency'] == 'HIGH':
                        estimated_cost = 30000  # ₹30,000 per road
                    elif prediction['urgency'] == 'MEDIUM':
                        estimated_cost = 15000  # ₹15,000 per road
                    else:
                        estimated_cost = 5000   # ₹5,000 per road
                    
                    total_urgency += estimated_cost
                    
                    maintenance_items.append({
                        'road_id': road_id,
                        'urgency': prediction['urgency'],
                        'estimated_cost': estimated_cost,
                        'estimated_potholes': prediction['estimated_potholes']
                    })
            
            # Add 20% contingency
            total_budget = int(total_urgency * 1.2)
            
            return {
                'city': city,
                'total_roads': len(roads),
                'maintenance_items': maintenance_items,
                'total_estimated_cost': total_budget,
                'contingency_20percent': total_budget - total_urgency,
                'monthly_budget': int(total_budget / 12),
                'timestamp': datetime.now().isoformat()
            }
        finally:
            conn.close()
    
    def generate_ai_report(self, city: str) -> Dict:
        """
        Generate comprehensive AI-powered report
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all roads for city
            cursor.execute("""
                SELECT DISTINCT road_id FROM alerts WHERE city = ?
            """, (city,))
            
            roads = [r[0] for r in cursor.fetchall()]
            
            if not roads:
                return {'status': 'no_data', 'city': city}
            
            # Analyze each road
            all_risks = []
            all_predictions = []
            
            for road_id in roads:
                risk = self.predict_accident_risk(road_id)
                pred = self.predict_road_deterioration(road_id)
                
                all_risks.append(risk)
                all_predictions.append(pred)
            
            # Calculate statistics
            avg_risk = sum(r['risk_score'] for r in all_risks) / len(all_risks) if all_risks else 0
            critical_roads = len([r for r in all_risks if r['risk_level'] == 'CRITICAL'])
            avg_severity = sum(p['predicted_severity'] for p in all_predictions if p['status'] == 'success') / len([p for p in all_predictions if p['status'] == 'success']) if all_predictions else 0
            
            # Generate recommendations
            recommendations = []
            if avg_risk > 60:
                recommendations.append("Deploy emergency response teams")
            if critical_roads > 0:
                recommendations.append(f"Prioritize repair for {critical_roads} critical roads")
            if avg_severity > 70:
                recommendations.append("Allocate additional budget for accelerated repairs")
            
            return {
                'status': 'success',
                'city': city,
                'report_date': datetime.now().isoformat(),
                'total_roads_analyzed': len(roads),
                'critical_roads': critical_roads,
                'average_risk_score': round(avg_risk, 2),
                'average_severity': round(avg_severity, 2),
                'high_risk_roads': [r for r in all_risks if r['risk_level'] in ['CRITICAL', 'HIGH']],
                'budget_recommendation': self.calculate_maintenance_budget(city, roads),
                'recommendations': recommendations,
                'pothole_predictions': self.predict_pothole_locations(city)
            }
        finally:
            conn.close()

    def predict_disaster_impact(self, city: str) -> Dict:
        """
        Disaster Prediction Stub: Simulates forecasting flood, landslide, or heat impacts on road networks.
        In reality, this would ingest satellite and meteorological data.
        """
        disaster_types = ["Extreme Heat Expansion", "Flash Flooding", "Landslide Risk"]
        mock_vulnerable_roads = random.sample(range(1, 15), k=3)
        risk = random.choice(disaster_types)
        
        return {
            "city": city,
            "disaster_risk": risk,
            "probability": round(random.uniform(15.0, 85.0), 2),
            "vulnerable_road_ids": mock_vulnerable_roads,
            "preventative_action": "Reinforce sub-base and deploy temporary barricades to vulnerable locations."
        }

    def prescriptive_maintenance_recommendation(self, road_id: int, city: str, road_importance_score: float) -> Dict:
        """
        Evaluates road failure against the remaining budget. Picks between patch-work,
        resurfacing, or full reconstruction based on ROI and available budget.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get remaining budget
        cursor.execute("SELECT remaining FROM budget_tracking WHERE city = ? AND year = ?", (city, datetime.now().year))
        row = cursor.fetchone()
        remaining_budget = row['remaining'] if row else 100000.0  # Default mock 
        conn.close()
        
        pred = self.predict_road_deterioration(road_id)
        severity = pred.get('predicted_severity', 50)
        
        # Cost Matrix
        cost_patch = 5000
        cost_resurface = 25000
        cost_reconstruct = 80000
        
        action = "MONITOR"
        cost = 0
        roi = 0.0
        
        if severity > 85 and remaining_budget >= cost_reconstruct and road_importance_score > 8.0:
            action = "FULL_RECONSTRUCTION"
            cost = cost_reconstruct
            roi = 9.5
        elif severity > 60 and remaining_budget >= cost_resurface:
            action = "RESURFACE"
            cost = cost_resurface
            roi = 7.0
        elif severity > 30 and remaining_budget >= cost_patch:
            action = "PATCH_WORK"
            cost = cost_patch
            roi = 4.5
        elif severity > 30:
            action = "INSUFFICIENT_FUNDS_FOR_OPTIMAL_REPAIR"
            
        return {
            "road_id": road_id,
            "prescriptive_action_plan": action,
            "estimated_cost": cost,
            "budget_remaining_after_repair": remaining_budget - cost,
            "roi_score": roi,
            "description": f"AI prescribed {action} because severity is {severity:.1f} and budget allows it."
        }
        
    def geospatial_optimization(self, alerts: List[Dict]) -> Dict:
        """
        Uses DBSCAN clustering to group proximal alerts into Maintenance Zones, 
        saving fuel and labor deployments.
        """
        try:
            from sklearn.cluster import DBSCAN
            import numpy as np
            has_sklearn = True
        except ImportError:
            has_sklearn = False

        if not alerts:
            return {"zones": []}
            
        # Extract lat/lng; mock if missing
        coords = []
        for a in alerts:
            # Assuming alerts have lat/lng or we mock them based on id
            lat = a.get('latitude', random.uniform(28.5, 28.7))
            lng = a.get('longitude', random.uniform(77.1, 77.3))
            coords.append([lat, lng])
            
        if has_sklearn and len(coords) >= 2:
            db = DBSCAN(eps=0.05, min_samples=2).fit(np.array(coords))
            labels = db.labels_
        else:
            # Fallback simple grouping
            labels = [0] * len(coords)
            
        zones = {}
        for i, label in enumerate(labels):
            z_id = f"ZONE_{label}"
            if z_id not in zones:
                zones[z_id] = []
            zones[z_id].append(alerts[i])
            
        return {
            "algorithm": "DBSCAN" if has_sklearn else "Naive_Proximity",
            "total_incidents": len(alerts),
            "optimized_zones_created": len(zones),
            "zones": zones
        }

# Usage example
if __name__ == "__main__":
    engine = RoadPredictionEngine()
    
    # Example: Predict deterioration for road 1
    deterioration = engine.predict_road_deterioration(1, days_ahead=30)
    print("Road Deterioration Prediction:")
    print(json.dumps(deterioration, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Example: Predict accident risk
    accident_risk = engine.predict_accident_risk(1)
    print("Accident Risk Prediction:")
    print(json.dumps(accident_risk, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Example: Generate comprehensive report
    report = engine.generate_ai_report('Delhi')
    print("AI-Powered Report:")
    print(json.dumps(report, indent=2, default=str))

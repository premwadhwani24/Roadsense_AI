"""
RoadSense AI - Image Analysis Service
Analyzes road damage images from dataset and generates real-time status
Replaces hardcoded marks with actual CNN-based defect detection
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sqlite3
import glob
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

# Import vision service
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

try:
    from vision_service import RoadVisionService
except ImportError:
    RoadVisionService = None


class ImageAnalysisService:
    """
    Scans dataset directory for road damage images and classifies them.
    Maintains a cache of results and provides real-time road condition status.
    """

    def __init__(self, dataset_path="Dataset", db_path=None):
        from database import DB_PATH
        self.dataset_path = Path(dataset_path)
        self.db_path = db_path if db_path else DB_PATH
        self.vision_service = None
        self.analysis_cache = {}  # {road_segment_id: analysis_result}
        self.image_cache = {}  # {image_path: classification_result}
        
        self._init_vision_service()
        self._init_database()

    def _init_vision_service(self):
        """Initialize the CNN vision service for image classification"""
        try:
            if RoadVisionService is not None:
                self.vision_service = RoadVisionService()
                logger.info("RoadVisionService initialized successfully")
            else:
                logger.warning("RoadVisionService not available")
        except Exception as e:
            logger.error(f"Failed to initialize vision service: {e}")

    def _init_database(self):
        """Initialize database for storing analysis results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table for image analysis results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS image_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT UNIQUE NOT NULL,
                    folder_id TEXT NOT NULL,
                    label TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    severity TEXT NOT NULL,
                    probabilities TEXT,
                    defect_details TEXT,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create table for road segment analysis summary
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS road_analysis_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    road_id TEXT UNIQUE NOT NULL,
                    road_name TEXT,
                    overall_status TEXT NOT NULL,
                    overall_severity TEXT NOT NULL,
                    confidence_avg REAL,
                    defect_count INTEGER,
                    pothole_count INTEGER,
                    crack_count INTEGER,
                    normal_count INTEGER,
                    proof_images TEXT,
                    detailed_analysis TEXT,
                    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized for image analysis")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def extract_road_segment_from_folder(self, folder_name: str) -> Optional[str]:
        """
        Extract road segment ID from dataset folder name.
        Example: '1007599_RS_386_386RS289112_28920' -> can be mapped to road segment
        Returns: road segment identifier or None
        """
        try:
            # Format: {ID}_RS_{code}_{code}
            parts = folder_name.split('_')
            if len(parts) >= 2:
                # Use the identifier as road segment proxy
                return f"ROAD_{parts[0][:8]}"
            return None
        except Exception:
            return None

    def analyze_image(self, image_path: str) -> Optional[Dict]:
        """
        Analyze a single image using the CNN model.
        Returns classification result with confidence and defect details.
        """
        if self.vision_service is None:
            logger.warning(f"Vision service not available for {image_path}")
            return None

        try:
            if image_path in self.image_cache:
                return self.image_cache[image_path]

            result = self.vision_service.analyze_image(image_path)
            
            # Get detailed metrics if defect detected
            if result.get("label") != "Normal":
                img = Image.open(image_path).convert("RGB")
                metrics = self.vision_service.generate_bounding_boxes_and_metrics(
                    img, result["label"], result["confidence"]
                )
                result["metrics"] = metrics
            
            self.image_cache[image_path] = result
            return result
        except Exception as e:
            logger.error(f"Failed to analyze image {image_path}: {e}")
            return None

    def scan_dataset_and_analyze(self) -> Dict[str, List[Dict]]:
        """
        Scan the entire dataset directory and analyze all road images.
        Returns organized results by road segment and severity.
        """
        logger.info(f"Starting dataset scan: {self.dataset_path}")
        
        results = {
            "total_images": 0,
            "analyzed": 0,
            "defects_found": 0,
            "by_road": {},  # road_id -> analysis results
            "by_severity": {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": [], "NORMAL": []}
        }

        if not self.dataset_path.exists():
            logger.error(f"Dataset path does not exist: {self.dataset_path}")
            return results

        # Scan all folders in dataset
        folder_list = sorted([d for d in self.dataset_path.iterdir() if d.is_dir()])
        
        for folder_idx, folder in enumerate(folder_list):
            folder_name = folder.name
            road_id = self.extract_road_segment_from_folder(folder_name)
            
            if not road_id:
                continue

            # Find RAW image (original road image)
            raw_images = list(folder.glob("*_RAW.*"))
            
            for raw_image_path in raw_images:
                results["total_images"] += 1
                
                try:
                    # Analyze the raw image
                    analysis = self.analyze_image(str(raw_image_path))
                    
                    if analysis is None:
                        continue

                    results["analyzed"] += 1

                    # Store in database
                    self._store_image_analysis(
                        str(raw_image_path),
                        folder_name,
                        analysis
                    )

                    # Organize by road
                    if road_id not in results["by_road"]:
                        results["by_road"][road_id] = {
                            "folder_name": folder_name,
                            "images": [],
                            "defect_count": 0,
                            "max_severity": "NORMAL"
                        }

                    image_result = {
                        "path": str(raw_image_path),
                        "folder": folder_name,
                        "label": analysis["label"],
                        "confidence": analysis["confidence"],
                        "severity": analysis["severity"],
                        "status": analysis["status"]
                    }

                    results["by_road"][road_id]["images"].append(image_result)

                    # Track defects
                    if analysis["label"] != "Normal":
                        results["defects_found"] += 1
                        results["by_road"][road_id]["defect_count"] += 1
                        
                        severity = analysis["severity"]
                        results["by_severity"][severity].append(image_result)
                        
                        # Update max severity for road
                        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "NORMAL": 0}
                        if severity_order.get(severity, 0) > severity_order.get(
                            results["by_road"][road_id]["max_severity"], 0
                        ):
                            results["by_road"][road_id]["max_severity"] = severity

                except Exception as e:
                    logger.error(f"Error analyzing {raw_image_path}: {e}")

            if folder_idx % 50 == 0:
                logger.info(f"Progress: {folder_idx}/{len(folder_list)} folders processed")

        logger.info(
            f"Dataset scan complete: {results['analyzed']}/{results['total_images']} "
            f"images analyzed, {results['defects_found']} defects found"
        )
        return results

    def _store_image_analysis(self, image_path: str, folder_id: str, analysis: Dict):
        """Store image analysis result in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO image_analysis
                (image_path, folder_id, label, confidence, severity, probabilities, defect_details, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                image_path,
                folder_id,
                analysis.get("label"),
                analysis.get("confidence"),
                analysis.get("severity"),
                json.dumps(analysis.get("probabilities", {})),
                json.dumps(analysis.get("metrics", {})),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store analysis: {e}")

    def get_road_condition_status(self, road_id: str) -> Dict:
        """
        Get comprehensive road condition status based on analyzed images.
        Returns actual defect information with proof and severity.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get summary from road_analysis_summary
            cursor.execute(
                'SELECT * FROM road_analysis_summary WHERE road_id = ?',
                (road_id,)
            )
            summary_row = cursor.fetchone()
            
            if summary_row:
                summary = dict(summary_row)
                summary["proof_images"] = json.loads(summary.get("proof_images") or "[]")
                summary["detailed_analysis"] = json.loads(summary.get("detailed_analysis") or "{}")
                conn.close()
                return summary

            conn.close()
            return None
        except Exception as e:
            logger.error(f"Failed to get road status for {road_id}: {e}")
            return None

    def generate_road_summary(self, road_id: str, images_data: List[Dict]) -> Dict:
        """
        Generate comprehensive summary for a road based on all analyzed images.
        Maps confidence to zone (RED/YELLOW/GREEN) with proof.
        """
        if not images_data:
            return {
                "road_id": road_id,
                "zone": "GREEN",
                "overall_status": "CLEAR",
                "severity": "NORMAL",
                "confidence": 100.0,
                "defect_count": 0,
                "proof_images": [],
                "reasons": ["No defects detected in dataset"]
            }

        # Aggregate defect counts
        defects = {
            "POTHOLE": 0,
            "CRACK": 0,
            "NORMAL": 0
        }
        
        severity_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0,
            "NORMAL": 0
        }
        
        proof_images = []
        confidence_scores = []

        for img_data in images_data:
            label = img_data.get("label", "Normal")
            confidence = img_data.get("confidence", 0)
            severity = img_data.get("severity", "NORMAL")
            
            defects[label.upper()] = defects.get(label.upper(), 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            confidence_scores.append(confidence)
            
            # Collect critical/high severity images as proof
            if severity in ["CRITICAL", "HIGH"]:
                proof_images.append({
                    "path": img_data.get("path"),
                    "label": label,
                    "confidence": confidence,
                    "severity": severity
                })

        # Determine overall zone based on defect severity and count
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
        pothole_count = defects.get("POTHOLE", 0)
        crack_count = defects.get("CRACK", 0)
        total_defects = pothole_count + crack_count

        if pothole_count > 2 or severity_counts.get("CRITICAL", 0) > 0:
            zone = "RED"
            reason = f"CRITICAL: {pothole_count} potholes detected. Immediate repair required."
        elif pothole_count > 0 or crack_count > 2 or severity_counts.get("HIGH", 0) > 1:
            zone = "YELLOW"
            reason = f"WARNING: {pothole_count} potholes, {crack_count} cracks. Schedule preventive maintenance."
        elif crack_count > 0:
            zone = "YELLOW"
            reason = f"CAUTION: {crack_count} surface cracks detected."
        else:
            zone = "GREEN"
            reason = "Road condition is satisfactory."

        return {
            "road_id": road_id,
            "zone": zone,
            "overall_status": "DETECTED" if total_defects > 0 else "CLEAR",
            "severity": "CRITICAL" if pothole_count > 2 else "HIGH" if pothole_count > 0 else "MEDIUM" if crack_count > 1 else "LOW" if total_defects > 0 else "NORMAL",
            "confidence_avg": round(avg_confidence, 2),
            "defect_count": total_defects,
            "pothole_count": pothole_count,
            "crack_count": crack_count,
            "normal_count": defects.get("NORMAL", 0),
            "proof_images": proof_images[:5],  # Top 5 defect images
            "reasons": [reason],
            "defect_breakdown": defects,
            "severity_breakdown": severity_counts,
            "analyzed_at": datetime.now().isoformat()
        }

    def store_road_summary(self, summary: Dict):
        """Store road condition summary in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO road_analysis_summary
                (road_id, overall_status, overall_severity, confidence_avg, 
                 defect_count, pothole_count, crack_count, normal_count,
                 proof_images, detailed_analysis, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                summary["road_id"],
                summary["overall_status"],
                summary["severity"],
                summary.get("confidence_avg", 0),
                summary.get("defect_count", 0),
                summary.get("pothole_count", 0),
                summary.get("crack_count", 0),
                summary.get("normal_count", 0),
                json.dumps(summary.get("proof_images", [])),
                json.dumps(summary),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store road summary: {e}")

    def process_full_dataset(self):
        """
        Complete pipeline: scan dataset, analyze all images, 
        generate summaries, and store results.
        """
        logger.info("=" * 60)
        logger.info("STARTING FULL DATASET ANALYSIS")
        logger.info("=" * 60)
        
        # Step 1: Scan and analyze all images
        scan_results = self.scan_dataset_and_analyze()
        
        # Step 2: Generate summaries for each road
        summaries_by_road = {}
        for road_id, road_data in scan_results["by_road"].items():
            summary = self.generate_road_summary(road_id, road_data["images"])
            summaries_by_road[road_id] = summary
            self.store_road_summary(summary)
        
        # Step 3: Generate overall statistics
        overall_stats = {
            "total_roads_analyzed": len(summaries_by_road),
            "total_images_processed": scan_results["analyzed"],
            "total_defects_found": scan_results["defects_found"],
            "by_severity": scan_results["by_severity"],
            "roads_by_zone": {
                "RED": [r for r, s in summaries_by_road.items() if summaries_by_road[r]["zone"] == "RED"],
                "YELLOW": [r for r, s in summaries_by_road.items() if summaries_by_road[r]["zone"] == "YELLOW"],
                "GREEN": [r for r, s in summaries_by_road.items() if summaries_by_road[r]["zone"] == "GREEN"]
            }
        }
        
        logger.info("=" * 60)
        logger.info(f"Analysis Complete: {scan_results['analyzed']}/{scan_results['total_images']} images")
        logger.info(f"Defects Found: {scan_results['defects_found']}")
        logger.info(f"RED Roads: {len(overall_stats['roads_by_zone']['RED'])}")
        logger.info(f"YELLOW Roads: {len(overall_stats['roads_by_zone']['YELLOW'])}")
        logger.info(f"GREEN Roads: {len(overall_stats['roads_by_zone']['GREEN'])}")
        logger.info("=" * 60)
        
        return overall_stats, summaries_by_road


# Initialize and run on import
_service_instance = None

def get_image_analysis_service():
    """Get singleton instance of ImageAnalysisService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ImageAnalysisService()
    return _service_instance


if __name__ == "__main__":
    # Test: Run full analysis
    service = ImageAnalysisService()
    stats, summaries = service.process_full_dataset()
    
    # Print sample results
    print("\nSample Road Conditions:")
    for road_id, summary in list(summaries.items())[:10]:
        print(f"\n{road_id}: {summary['zone']} ({summary['overall_status']})")
        print(f"  Severity: {summary['severity']}")
        print(f"  Defects: {summary['defect_count']} (Potholes: {summary['pothole_count']}, Cracks: {summary['crack_count']})")
        print(f"  Confidence: {summary['confidence_avg']}%")

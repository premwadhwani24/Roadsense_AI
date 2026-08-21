package com.ai.smart.road.monitoring.system.application.test;

import java.io.File;

import com.ai.smart.road.monitoring.system.application.ai.AIResponseParser;
import com.ai.smart.road.monitoring.system.application.ai.PotholeDetectionPythonBridge;
import com.ai.smart.road.monitoring.system.application.ai.RoadSurfaceAnalyzer;

public class TestAIIntegration {
	
	public static void main(String[] args) {
		
		// Initialize Python Bridges
		PotholeDetectionPythonBridge bridge = new PotholeDetectionPythonBridge();
		RoadSurfaceAnalyzer analyzer = new RoadSurfaceAnalyzer();

		// 1️⃣ Send road image for pothole detection
		File testImage = new File("E:\\Project-Sakshi\\ai_smart_road_monitoring_system_application\\python_ai\\test_image_1.jpg");
		String potholeJson = bridge.analyzeImage(testImage);
		System.out.println("\n=== PYTHON POTHOLE RESPONSE ===");
		System.out.println(potholeJson);

		// 2️⃣ Parse the AI response
		String potholeStatus = AIResponseParser.getStatus(potholeJson);
		String potholeMsg = AIResponseParser.getMessage(potholeJson);
		double confidence = AIResponseParser.getConfidence(potholeJson);
		System.out.println("\nStatus: " + potholeStatus);
		System.out.println("Message: " + potholeMsg);
		System.out.println("Confidence: " + confidence);

		// 3️⃣ Send road surface data for analysis
		String surfaceJson = analyzer.analyzeSurface(1.5, 2.0, 0.1);
		System.out.println("\n=== PYTHON ROAD SURFACE RESPONSE ===");
		System.out.println(surfaceJson);

		// 4️⃣ Parse the road surface AI response
		String surfaceStatus = AIResponseParser.getStatus(surfaceJson);
		System.out.println("\nSurface Status: " + surfaceStatus);
	}
}

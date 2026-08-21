package com.ai.smart.road.monitoring.system.application.ai;

import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

/**
 * Handles AI analysis for road surface level and quality.
 */
@Component
public class RoadSurfaceAnalyzer {

	private static final Logger logger = LoggerFactory.getLogger(RoadSurfaceAnalyzer.class);
	private static final String PYTHON_API_URL = "http://127.0.0.1:5000/api/road/analyze";

	private final RestTemplate restTemplate;

	public RoadSurfaceAnalyzer() {
		this.restTemplate = new RestTemplate();
	}

	public String analyzeSurface(double length, double width, double height) {
		try {
			Map<String, Object> payload = new HashMap<>();
			payload.put("length", length);
			payload.put("width", width);
			payload.put("height", height);

			HttpHeaders headers = new HttpHeaders();
			headers.setContentType(MediaType.APPLICATION_JSON);

			HttpEntity<Map<String, Object>> request = new HttpEntity<>(payload, headers);
			logger.info("Sending road surface data to Python AI: {}", payload);

			ResponseEntity<String> response = restTemplate.postForEntity(PYTHON_API_URL, request, String.class);
			logger.info("Received road surface AI response: {}", response.getBody());

			return response.getBody();
		} catch (Exception e) {
			logger.error("Road surface analysis failed: {}", e.getMessage());
			return "{\"status\":\"ERROR\",\"message\":\"" + e.getMessage() + "\"}";
		}
	}
}

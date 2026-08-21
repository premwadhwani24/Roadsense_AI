package com.ai.smart.road.monitoring.system.application.ai;

import java.io.File;
import java.nio.file.Files;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

/**
 * Communicates with Python AI API for pothole detection.
 */
@Component
public class PotholeDetectionPythonBridge {

	private static final Logger logger = LoggerFactory.getLogger(PotholeDetectionPythonBridge.class);
	private static final String PYTHON_API_URL = "http://127.0.0.1:5000/api/pothole/detect";

	private final RestTemplate restTemplate;

	public PotholeDetectionPythonBridge() {
		this.restTemplate = new RestTemplate();
	}

	public String analyzeImage(File imageFile) {
		try {
			if (imageFile == null || !imageFile.exists()) {
				throw new IllegalArgumentException("Invalid image file path");
			}

			byte[] imageBytes = Files.readAllBytes(imageFile.toPath());
			HttpHeaders headers = new HttpHeaders();
			headers.setContentType(MediaType.MULTIPART_FORM_DATA);

			// Build multipart body
			MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
			body.add("file", new ByteArrayResource(imageBytes) {
				@Override
				public String getFilename() {
					return imageFile.getName();
				}
			});

			HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
			logger.info("Sending image {} to Python AI API...", imageFile.getName());

			ResponseEntity<String> response = restTemplate.postForEntity(PYTHON_API_URL, requestEntity, String.class);

			logger.info("Received AI response: {}", response.getBody());
			return response.getBody();

		} catch (Exception e) {
			logger.error("Error during pothole detection: {}", e.getMessage());
			return "{\"status\":\"ERROR\",\"message\":\"" + e.getMessage() + "\"}";
		}
	}
}

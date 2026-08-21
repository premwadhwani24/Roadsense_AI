package com.ai.smart.road.monitoring.system.application.ai;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Parses AI JSON responses safely and extracts core fields.
 */
public class AIResponseParser {
	private static final Logger logger = LoggerFactory.getLogger(AIResponseParser.class);
	private static final ObjectMapper mapper = new ObjectMapper();

	public static String getStatus(String jsonResponse) {
		try {
			JsonNode node = mapper.readTree(jsonResponse);
			return node.path("status").asText("UNKNOWN");
		} catch (Exception e) {
			logger.error("Error parsing status from AI response: {}", e.getMessage());
			return "ERROR";
		}
	}

	public static String getMessage(String jsonResponse) {
		try {
			JsonNode node = mapper.readTree(jsonResponse);
			return node.path("message").asText("No message");
		} catch (Exception e) {
			logger.error("Error parsing message from AI response: {}", e.getMessage());
			return "Parsing error";
		}
	}

	public static double getConfidence(String jsonResponse) {
		try {
			JsonNode node = mapper.readTree(jsonResponse);
			return node.path("confidence").asDouble(0.0);
		} catch (Exception e) {
			logger.error("Error parsing confidence: {}", e.getMessage());
			return 0.0;
		}
	}

	public static JsonNode getData(String jsonResponse) {
		try {
			JsonNode node = mapper.readTree(jsonResponse);
			return node.path("data");
		} catch (Exception e) {
			logger.error("Error parsing data field: {}", e.getMessage());
			return mapper.createObjectNode();
		}
	}
}

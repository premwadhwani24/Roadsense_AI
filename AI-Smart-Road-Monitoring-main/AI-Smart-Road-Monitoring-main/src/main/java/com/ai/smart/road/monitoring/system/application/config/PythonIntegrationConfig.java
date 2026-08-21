package com.ai.smart.road.monitoring.system.application.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class PythonIntegrationConfig {

	private final String flaskBaseUrl = "http://127.0.0.1:5000"; // Flask server

	@Bean
	public RestTemplate restTemplate() {
		return new RestTemplate();
	}

	public String getFlaskBaseUrl() {
		return flaskBaseUrl;
	}
}

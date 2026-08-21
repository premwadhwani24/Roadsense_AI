package com.ai.smart.road.monitoring.system.application.service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import com.ai.smart.road.monitoring.system.application.config.PythonIntegrationConfig;
import com.ai.smart.road.monitoring.system.application.model.Pothole;
import com.ai.smart.road.monitoring.system.application.repository.PotholeRepository;

@Service
public class PotholeDetectionService {

	@Autowired
	private RestTemplate restTemplate;

	@Autowired
	private PythonIntegrationConfig pythonIntegrationConfig;

	@Autowired
	private PotholeRepository potholeRepository;

	// 🔹 Detect pothole using Python AI model
	public Pothole detectPothole(String roadId, String gpsLocation) {
		Pothole pothole = new Pothole();
		pothole.setRoadId(Long.parseLong(roadId));
		pothole.setGpsLocation(gpsLocation);
		pothole.setLatitude(0.0); // Placeholder, replace with AI output
		pothole.setLongitude(0.0); // Placeholder, replace with AI output
		pothole.setDepth(0.2); // Placeholder
		pothole.setWidth(0.5); // Placeholder
		pothole.setLength(0.7); // Placeholder
		pothole.setSeverity("Moderate");
		pothole.setDetectedDate(LocalDateTime.now());
		pothole.setDetectedAt(LocalDateTime.now());
		pothole.setImagePath("/images/sample_pothole.jpg");
		return pothole;
	}

	// 🔹 Get all detected potholes
	public List<Pothole> getDetectedPotholes() {
		return potholeRepository.findAll();
	}

	// 🔹 Get pothole by ID
	public Optional<Pothole> findById(Long id) {
		return potholeRepository.findById(id);
	}

	// 🔹 Save pothole
	public Pothole save(Pothole pothole) {
		return potholeRepository.save(pothole);
	}

	// 🔹 Update pothole
	public Pothole update(Long id, Pothole potholeDetails) {
		return potholeRepository.findById(id).map(existing -> {
			existing.setLength(potholeDetails.getLength());
			existing.setWidth(potholeDetails.getWidth());
			existing.setDepth(potholeDetails.getDepth());
			existing.setGpsLocation(potholeDetails.getGpsLocation());
			existing.setGpsPin(potholeDetails.getGpsPin());
			existing.setSeverity(potholeDetails.getSeverity());
			existing.setDetectedDate(potholeDetails.getDetectedDate());
			existing.setDetectedAt(potholeDetails.getDetectedAt());
			existing.setImagePath(potholeDetails.getImagePath());
			return potholeRepository.save(existing);
		}).orElseThrow(() -> new RuntimeException("Pothole not found with id " + id));
	}

	// 🔹 Delete pothole
	public void delete(Long id) {
		potholeRepository.deleteById(id);
	}
}

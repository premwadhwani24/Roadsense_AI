package com.ai.smart.road.monitoring.system.application.service;

import java.util.List;
import java.util.Optional;

import com.ai.smart.road.monitoring.system.application.model.Pothole;

public interface PotholeService {
	List<Pothole> getAllPotholes();

	Optional<Pothole> getPotholeById(Long id);

	Pothole createPothole(Pothole pothole);

	Pothole updatePothole(Long id, Pothole potholeDetails);

	void deletePothole(Long id);

	// Dashboard analytics
	long countByStatus(String status);

	List<Object[]> countBySeverity();

	List<Object[]> dailyDetectionTrend();

	List<Object[]> potholeCountPerRoad();
}

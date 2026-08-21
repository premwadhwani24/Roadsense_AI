package com.ai.smart.road.monitoring.system.application.service;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.ai.smart.road.monitoring.system.application.model.Pothole;
import com.ai.smart.road.monitoring.system.application.repository.PotholeRepository;

@Service
public class DataSyncService {

	@Autowired
	private PotholeRepository potholeRepository;

	// 🔹 Sync pothole data to cloud
	public void syncToCloud() {
		List<Pothole> potholes = potholeRepository.findAll();
		for (Pothole p : potholes) {
			System.out.println("Syncing data -> RoadId: " + p.getRoadId() + " GPS: " + p.getGpsLocation() + " Lat: "
					+ p.getLatitude() + " Lon: " + p.getLongitude() + " DetectedAt: " + p.getDetectedAt()
					+ " ImagePath: " + p.getImagePath());
			// TODO: Implement AWS S3 / DynamoDB or other cloud sync
		}
	}
}

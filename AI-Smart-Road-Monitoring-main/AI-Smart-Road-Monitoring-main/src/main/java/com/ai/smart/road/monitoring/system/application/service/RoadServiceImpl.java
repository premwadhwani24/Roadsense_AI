package com.ai.smart.road.monitoring.system.application.service;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.ai.smart.road.monitoring.system.application.model.RoadData;
import com.ai.smart.road.monitoring.system.application.repository.RoadDataRepository;

@Service
public class RoadServiceImpl implements RoadService {

	@Autowired
	private RoadDataRepository roadRepository;

	@Override
	public List<RoadData> getAllRoads() {
		return roadRepository.findAll();
	}

	@Override
	public Optional<RoadData> getRoadById(Long id) {
		return roadRepository.findById(id);
	}

	@Override
	public RoadData createRoad(RoadData road) {
		return roadRepository.save(road);
	}

	@Override
	public RoadData updateRoad(Long id, RoadData roadDetails) {
		return roadRepository.findById(id).map(road -> {
			road.setRoadName(roadDetails.getRoadName());
			road.setLatitude(roadDetails.getLatitude());
			road.setLongitude(roadDetails.getLongitude());
			road.setSurfaceLevel(roadDetails.getSurfaceLevel());
			road.setSlope(roadDetails.getSlope());
			road.setStatus(roadDetails.getStatus());
			road.setSensorFile(roadDetails.getSensorFile());
			return roadRepository.save(road);
		}).orElseThrow(() -> new RuntimeException("Road data not found with id " + id));
	}

	@Override
	public void deleteRoad(Long id) {
		if (!roadRepository.existsById(id)) {
			throw new RuntimeException("Road data not found with id " + id);
		}
		roadRepository.deleteById(id);
	}
}

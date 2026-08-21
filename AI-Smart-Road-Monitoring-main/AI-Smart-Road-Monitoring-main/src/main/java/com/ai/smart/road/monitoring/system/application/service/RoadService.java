package com.ai.smart.road.monitoring.system.application.service;

import java.util.List;
import java.util.Optional;

import com.ai.smart.road.monitoring.system.application.model.RoadData;

public interface RoadService {

	List<RoadData> getAllRoads();

	Optional<RoadData> getRoadById(Long id);

	RoadData createRoad(RoadData road);

	RoadData updateRoad(Long id, RoadData road);

	void deleteRoad(Long id);
}

package com.ai.smart.road.monitoring.system.application.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.stereotype.Service;

import com.ai.smart.road.monitoring.system.application.dto.PotholeResponse;
import com.ai.smart.road.monitoring.system.application.dto.RoadDataDTO;
import com.ai.smart.road.monitoring.system.application.model.Pothole;
import com.ai.smart.road.monitoring.system.application.model.RoadData;

@Service
public class DashboardMapperService {

	public List<RoadDataDTO> toRoadDataDTOs(List<RoadData> roads) {
		return roads.stream()
				.map(r -> new RoadDataDTO(String.format("%.6f_%.6f", r.getLatitude(), r.getLongitude()),
						r.getSurfaceLevel(), r.getSlope(), r.getSurfaceLevel(), null, r.getLatitude(),
						r.getLongitude()))
				.collect(Collectors.toList());
	}

	public List<PotholeResponse> toPotholeResponses(List<Pothole> potholes) {
		return potholes
				.stream().map(p -> new PotholeResponse(p.getId(), p.getLength(), p.getWidth(), p.getDepth(),
						p.getGpsLocation(), p.getDetectedAt(), p.getLatitude(), p.getLongitude()))
				.collect(Collectors.toList());
	}
}

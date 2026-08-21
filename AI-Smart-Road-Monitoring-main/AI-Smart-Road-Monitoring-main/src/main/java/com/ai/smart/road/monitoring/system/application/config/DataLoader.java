package com.ai.smart.road.monitoring.system.application.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import com.ai.smart.road.monitoring.system.application.model.RoadData;
import com.ai.smart.road.monitoring.system.application.repository.RoadDataRepository;

@Component
public class DataLoader implements CommandLineRunner {

	@Autowired
	private RoadDataRepository roadRepo;

	@Override
	public void run(String... args) {
		if (roadRepo.count() == 0) {
			RoadData r = new RoadData();
			r.setRoadName("NH-44");
			r.setDistrict("Bhopal");
			r.setState("MP");
			r.setLatitude(23.2599);
			r.setLongitude(77.4126);
			roadRepo.save(r);
		}
	}
}

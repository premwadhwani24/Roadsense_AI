package com.ai.smart.road.monitoring.system.application.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.ai.smart.road.monitoring.system.application.model.RoadData;

@Repository
public interface RoadDataRepository extends JpaRepository<RoadData, Long> {
}

package com.ai.smart.road.monitoring.system.application.service;

import java.util.Map;

import com.ai.smart.road.monitoring.system.application.dto.StatsDTO;

public interface DashboardService {

	StatsDTO getStats();

	Map<String, Long> getSeverityDistribution();

	Map<String, Long> getDailyDetectionTrend();

	Map<String, Long> getRoadConditionOverview();
}

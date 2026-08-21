package com.ai.smart.road.monitoring.system.application.service;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.EnumMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.ai.smart.road.monitoring.system.application.dto.StatsDTO;
import com.ai.smart.road.monitoring.system.application.repository.PotholeRepository;
import com.ai.smart.road.monitoring.system.application.repository.RoadDataRepository;

@Service
public class DashboardServiceImpl implements DashboardService {

	@Autowired
	private PotholeRepository potholeRepository;

	@Autowired
	private RoadDataRepository roadRepository;

	/*
	 * ===================================================== ADMIN DASHBOARD – TOP
	 * STATS =====================================================
	 */

	@Override
	public StatsDTO getStats() {

		long totalRoads = roadRepository.count();
		long totalPotholes = potholeRepository.count();

		long open = potholeRepository.countByStatus("OPEN");
		long inProgress = potholeRepository.countByStatus("IN_PROGRESS");
		long closed = potholeRepository.countByStatus("REPAIRED");

		return new StatsDTO(totalRoads, totalPotholes, open, inProgress, closed);
	}

	/*
	 * ===================================================== CHART 1: POTHOLE
	 * SEVERITY DISTRIBUTION =====================================================
	 */

	@Override
	public Map<String, Long> getSeverityDistribution() {

		Map<String, Long> map = new HashMap<>();

		List<Object[]> rows = potholeRepository.countBySeverity();
		for (Object[] r : rows) {
			map.put(String.valueOf(r[0]), ((Number) r[1]).longValue());
		}

		return map;
	}

	/*
	 * ===================================================== CHART 2: DAILY
	 * DETECTION TREND (LAST 7 DAYS)
	 * =====================================================
	 */

	@Override
	public Map<String, Long> getDailyDetectionTrend() {

		Map<DayOfWeek, Long> temp = new EnumMap<>(DayOfWeek.class);

		// initialize last 7 days to 0
		for (int i = 6; i >= 0; i--) {
			DayOfWeek d = LocalDate.now().minusDays(i).getDayOfWeek();
			temp.put(d, 0L);
		}

		List<Object[]> rows = potholeRepository.dailyDetectionTrend();
		for (Object[] r : rows) {
			DayOfWeek day = DayOfWeek.valueOf(String.valueOf(r[0]).toUpperCase());
			temp.put(day, ((Number) r[1]).longValue());
		}

		// convert to ordered string map
		Map<String, Long> result = new HashMap<>();
		temp.forEach((k, v) -> result.put(k.name(), v));

		return result;
	}

	/*
	 * ===================================================== CHART 3: ROAD CONDITION
	 * OVERVIEW =====================================================
	 */

	@Override
	public Map<String, Long> getRoadConditionOverview() {

		long good = 0;
		long moderate = 0;
		long bad = 0;

		List<Object[]> rows = potholeRepository.potholeCountPerRoad();

		for (Object[] r : rows) {
			long count = ((Number) r[1]).longValue();

			if (count == 0)
				good++;
			else if (count <= 3)
				moderate++;
			else
				bad++;
		}

		Map<String, Long> map = new HashMap<>();
		map.put("GOOD", good);
		map.put("MODERATE", moderate);
		map.put("BAD", bad);

		return map;
	}
}

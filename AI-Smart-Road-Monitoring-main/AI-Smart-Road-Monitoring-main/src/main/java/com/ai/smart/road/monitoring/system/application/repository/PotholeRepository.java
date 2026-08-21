package com.ai.smart.road.monitoring.system.application.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import com.ai.smart.road.monitoring.system.application.model.Pothole;

@Repository
public interface PotholeRepository extends JpaRepository<Pothole, Long> {

	// Count by status
	long countByStatus(String status);

	// Severity distribution
	@Query("""
			    SELECT p.severity, COUNT(p)
			    FROM Pothole p
			    GROUP BY p.severity
			""")
	List<Object[]> countBySeverity();

	// Daily detection trend (last 7 days)
	@Query("""
			    SELECT FUNCTION('DAYNAME', p.detectedAt), COUNT(p)
			    FROM Pothole p
			    WHERE p.detectedAt >= CURRENT_DATE - 6
			    GROUP BY FUNCTION('DAYNAME', p.detectedAt)
			    ORDER BY MIN(p.detectedAt)
			""")
	List<Object[]> dailyDetectionTrend();

	// Potholes per road
	@Query("""
			    SELECT p.roadId, COUNT(p)
			    FROM Pothole p
			    GROUP BY p.roadId
			""")
	List<Object[]> potholeCountPerRoad();
}

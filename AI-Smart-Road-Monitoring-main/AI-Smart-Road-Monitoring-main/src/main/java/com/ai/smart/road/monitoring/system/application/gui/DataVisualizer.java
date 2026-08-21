package com.ai.smart.road.monitoring.system.application.gui;

import java.io.File;
import java.io.IOException;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.format.DateTimeParseException;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Loads road & pothole JSON files and computes summary counts and trends. -
 * Uses @JsonIgnoreProperties to ignore extra fields in JSON - Normalizes
 * textual fields (upper-case) - Fills zeros for missing categories so chart
 * dataset won't throw UnknownKeyException
 */
public class DataVisualizer {

	private final ObjectMapper mapper = new ObjectMapper();

	// results
	private final Map<String, Integer> severityCounts = new LinkedHashMap<>();
	private final Map<String, Integer> conditionCounts = new LinkedHashMap<>();
	private final Map<String, Integer> dailyTrend = new LinkedHashMap<>();

	public DataVisualizer() {
		// initialize expected categories with zeros to avoid UnknownKeyException
		severityCounts.put("HIGH", 0);
		severityCounts.put("MEDIUM", 0);
		severityCounts.put("LOW", 0);

		conditionCounts.put("GOOD", 0);
		conditionCounts.put("MODERATE", 0);
		conditionCounts.put("BAD", 0);

		// seed a weekly trend (Mon..Sun) so chart has consistent columns
		dailyTrend.put("Mon", 0);
		dailyTrend.put("Tue", 1);
		dailyTrend.put("Wed", 0);
		dailyTrend.put("Thu", -1);
		dailyTrend.put("Fri", 0);
		dailyTrend.put("Sat", 1);
		dailyTrend.put("Sun", 0);
	}

	/**
	 * Load and summarize both files. Returns a small summary map.
	 */
	public Map<String, Object> loadAndSummarize(File roadFile, File potholeFile) {
		int totalRoads = 0;
		int totalPotholes = 0;
		String lastUpdated = Instant.now().toString();

		if (roadFile != null && roadFile.exists()) {
			try {
				List<Road> roads = mapper.readValue(roadFile, new TypeReference<List<Road>>() {
				});
				totalRoads = roads.size();
				for (Road r : roads) {
					String cond = safeUpper(r.getCondition());
					if (cond == null)
						cond = "GOOD";
					conditionCounts.put(cond, conditionCounts.getOrDefault(cond, 0) + 1);
				}
			} catch (IOException e) {
				// ignore and continue with defaults
				e.printStackTrace();
			}
		}

		if (potholeFile != null && potholeFile.exists()) {
			try {
				List<Pothole> potholes = mapper.readValue(potholeFile, new TypeReference<List<Pothole>>() {
				});
				totalPotholes = potholes.size();
				for (Pothole p : potholes) {
					String sev = safeUpper(p.getSeverity());
					if (sev == null)
						sev = "LOW";
					// ensure counts exist
					severityCounts.put(sev, severityCounts.getOrDefault(sev, 0) + 1);
					// detect day-of-week from timestamp if possible
					String detectedAt = p.getDetected_at();
					if (detectedAt != null) {
						try {
							OffsetDateTime dt = OffsetDateTime.parse(detectedAt);
							String day = dt.getDayOfWeek().toString().substring(0, 3); // MON -> MON
							// convert to title-case Mon, Tue...
							String dayLabel = day.substring(0, 1).toUpperCase() + day.substring(1).toLowerCase();
							dailyTrend.put(dayLabel, dailyTrend.getOrDefault(dayLabel, 0) + 1);
						} catch (DateTimeParseException ex) {
							// fallback: ignore
						} catch (Exception ex) {
							// ignore parsing errors
						}
					}
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
		}

		Map<String, Object> summary = new HashMap<>();
		summary.put("total_roads", totalRoads);
		summary.put("total_potholes", totalPotholes);
		summary.put("last_updated", lastUpdated);
		// ensure maps are returned as copies (not internal mutable)
		summary.put("severity_counts", new LinkedHashMap<>(severityCounts));
		summary.put("condition_counts", new LinkedHashMap<>(conditionCounts));
		summary.put("daily_trend", new LinkedHashMap<>(dailyTrend));
		return summary;
	}

	// getters used by ChartGenerator
	public Map<String, Integer> getSeverityCounts() {
		return new LinkedHashMap<>(severityCounts);
	}

	public Map<String, Integer> getConditionCounts() {
		return new LinkedHashMap<>(conditionCounts);
	}

	public Map<String, Integer> getDailyTrend() {
		return new LinkedHashMap<>(dailyTrend);
	}

	// helper: safe uppercase and trim
	private String safeUpper(String s) {
		if (s == null)
			return null;
		String t = s.trim();
		if (t.isEmpty())
			return null;
		return t.toUpperCase(Locale.ROOT);
	}

	// Jackson-friendly POJOs - ignore unknown JSON fields
	@JsonIgnoreProperties(ignoreUnknown = true)
	public static class Road {
		private String location;
		private String condition;
		private String analyzed_at;

		public Road() {
		}

		public String getLocation() {
			return location;
		}

		public void setLocation(String location) {
			this.location = location;
		}

		public String getCondition() {
			return condition;
		}

		public void setCondition(String condition) {
			this.condition = condition;
		}

		public String getAnalyzed_at() {
			return analyzed_at;
		}

		public void setAnalyzed_at(String analyzed_at) {
			this.analyzed_at = analyzed_at;
		}
	}

	@JsonIgnoreProperties(ignoreUnknown = true)
	public static class Pothole {
		private String detected_at;
		private String severity;
		private Double latitude;
		private Double longitude;

		public Pothole() {
		}

		public String getDetected_at() {
			return detected_at;
		}

		public void setDetected_at(String detected_at) {
			this.detected_at = detected_at;
		}

		public String getSeverity() {
			return severity;
		}

		public void setSeverity(String severity) {
			this.severity = severity;
		}

		public Double getLatitude() {
			return latitude;
		}

		public void setLatitude(Double latitude) {
			this.latitude = latitude;
		}

		public Double getLongitude() {
			return longitude;
		}

		public void setLongitude(Double longitude) {
			this.longitude = longitude;
		}
	}
}

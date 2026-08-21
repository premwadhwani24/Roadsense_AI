package com.ai.smart.road.monitoring.system.application.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "roads")
public class RoadData {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id;

	@Column(name = "road_name", nullable = false)
	private String roadName;

	private String district;
	private String state;
	private String status;

	@Column(name = "sensor_file")
	private String sensorFile;

	@Column(precision = 10, scale = 6)
	private Double latitude;

	@Column(precision = 10, scale = 6)
	private Double longitude;

	private double slope;
	private double surfaceLevel;

	// =====================
	// Getters and Setters
	// =====================

	public Long getId() {
		return id;
	}

	// ✅ REQUIRED FOR TESTS
	public void setId(Long id) {
		this.id = id;
	}

	public String getRoadName() {
		return roadName;
	}

	public void setRoadName(String roadName) {
		this.roadName = roadName;
	}

	public String getDistrict() {
		return district;
	}

	public void setDistrict(String district) {
		this.district = district;
	}

	public String getState() {
		return state;
	}

	public void setState(String state) {
		this.state = state;
	}

	public String getStatus() {
		return status;
	}

	public void setStatus(String status) {
		this.status = status;
	}

	public String getSensorFile() {
		return sensorFile;
	}

	public void setSensorFile(String sensorFile) {
		this.sensorFile = sensorFile;
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

	public double getSlope() {
		return slope;
	}

	public void setSlope(double slope) {
		this.slope = slope;
	}

	public double getSurfaceLevel() {
		return surfaceLevel;
	}

	public void setSurfaceLevel(double surfaceLevel) {
		this.surfaceLevel = surfaceLevel;
	}
}

package com.ai.smart.road.monitoring.system.application.dto;

import java.time.LocalDateTime;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class PotholeResponse {

	private Long id;
	private double length;
	private double width;
	private double depth;
	private String gpsLocation;
	private LocalDateTime detectedAt;
	private double latitude;
	private double longitude;

	// No-arg constructor
	public PotholeResponse() {
	}

	// Constructor for DashboardService mapping
	public PotholeResponse(Long id, double length, double width, double depth, String gpsLocation,
			LocalDateTime detectedAt, double latitude, double longitude) {
		this.id = id;
		this.length = length;
		this.width = width;
		this.depth = depth;
		this.gpsLocation = gpsLocation;
		this.detectedAt = detectedAt;
		this.latitude = latitude;
		this.longitude = longitude;
	}

	// Getters and setters
	public Long getId() {
		return id;
	}

	public void setId(Long id) {
		this.id = id;
	}

	public double getLength() {
		return length;
	}

	public void setLength(double length) {
		this.length = length;
	}

	public double getWidth() {
		return width;
	}

	public void setWidth(double width) {
		this.width = width;
	}

	public double getDepth() {
		return depth;
	}

	public void setDepth(double depth) {
		this.depth = depth;
	}

	public String getGpsLocation() {
		return gpsLocation;
	}

	public void setGpsLocation(String gpsLocation) {
		this.gpsLocation = gpsLocation;
	}

	public LocalDateTime getDetectedAt() {
		return detectedAt;
	}

	public void setDetectedAt(LocalDateTime detectedAt) {
		this.detectedAt = detectedAt;
	}

	public double getLatitude() {
		return latitude;
	}

	public void setLatitude(double latitude) {
		this.latitude = latitude;
	}

	public double getLongitude() {
		return longitude;
	}

	public void setLongitude(double longitude) {
		this.longitude = longitude;
	}
}

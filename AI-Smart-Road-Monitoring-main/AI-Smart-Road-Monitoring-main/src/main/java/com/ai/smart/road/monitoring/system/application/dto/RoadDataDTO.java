package com.ai.smart.road.monitoring.system.application.dto;

import java.time.LocalDateTime;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public class RoadDataDTO {

	private String id; // composite of latitude_longitude
	private double length;
	private double width;
	private double height;
	private LocalDateTime recordedAt;
	private double latitude;
	private double longitude;

	// No-arg constructor
	public RoadDataDTO() {
	}

	// Constructor used in DashboardService
	public RoadDataDTO(String id, double length, double width, double height, LocalDateTime recordedAt, double latitude,
			double longitude) {
		this.id = id;
		this.length = length;
		this.width = width;
		this.height = height;
		this.recordedAt = recordedAt;
		this.latitude = latitude;
		this.longitude = longitude;
	}

	// Getters and setters
	public String getId() {
		return id;
	}

	public void setId(String id) {
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

	public double getHeight() {
		return height;
	}

	public void setHeight(double height) {
		this.height = height;
	}

	public LocalDateTime getRecordedAt() {
		return recordedAt;
	}

	public void setRecordedAt(LocalDateTime recordedAt) {
		this.recordedAt = recordedAt;
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

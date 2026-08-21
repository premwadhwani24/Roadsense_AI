package com.ai.smart.road.monitoring.system.application.dto;

public class PotholeRequest {

	private double length;
	private double width;
	private double depth;
	private String gpsLocation;
	private Long roadDataId; // reference to RoadData entity

	public PotholeRequest() {
	}

	public PotholeRequest(double length, double width, double depth, String gpsLocation, Long roadDataId) {
		this.length = length;
		this.width = width;
		this.depth = depth;
		this.gpsLocation = gpsLocation;
		this.roadDataId = roadDataId;
	}

	// Getters and Setters
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

	public Long getRoadDataId() {
		return roadDataId;
	}

	public void setRoadDataId(Long roadDataId) {
		this.roadDataId = roadDataId;
	}
}

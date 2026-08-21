package com.ai.smart.road.monitoring.system.application.dto;

public class StatsDTO {

	private long totalRoads;
	private long totalPotholes;
	private long openPotholes;
	private long inProgressPotholes;
	private long closedPotholes;

	public StatsDTO(long totalRoads, long totalPotholes, long openPotholes, long inProgressPotholes,
			long closedPotholes) {

		this.totalRoads = totalRoads;
		this.totalPotholes = totalPotholes;
		this.openPotholes = openPotholes;
		this.inProgressPotholes = inProgressPotholes;
		this.closedPotholes = closedPotholes;
	}

	public long getTotalRoads() {
		return totalRoads;
	}

	public long getTotalPotholes() {
		return totalPotholes;
	}

	public long getOpenPotholes() {
		return openPotholes;
	}

	public long getInProgressPotholes() {
		return inProgressPotholes;
	}

	public long getClosedPotholes() {
		return closedPotholes;
	}
}

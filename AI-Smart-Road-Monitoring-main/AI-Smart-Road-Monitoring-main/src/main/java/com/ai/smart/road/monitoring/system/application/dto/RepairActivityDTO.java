package com.ai.smart.road.monitoring.system.application.dto;

import java.time.LocalDate;

public class RepairActivityDTO {

	private Long potholeId;
	private String status;
	private LocalDate repairDate;
	private String technician;

	public RepairActivityDTO() {
	}

	public RepairActivityDTO(Long potholeId, String status, LocalDate repairDate, String technician) {
		this.potholeId = potholeId;
		this.status = status;
		this.repairDate = repairDate;
		this.technician = technician;
	}

	public Long getPotholeId() {
		return potholeId;
	}

	public void setPotholeId(Long potholeId) {
		this.potholeId = potholeId;
	}

	public String getStatus() {
		return status;
	}

	public void setStatus(String status) {
		this.status = status;
	}

	public LocalDate getRepairDate() {
		return repairDate;
	}

	public void setRepairDate(LocalDate repairDate) {
		this.repairDate = repairDate;
	}

	public String getTechnician() {
		return technician;
	}

	public void setTechnician(String technician) {
		this.technician = technician;
	}
}

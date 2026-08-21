package com.ai.smart.road.monitoring.system.application.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "roles")
public class Role {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Long id; // ✅ FIXED (Long, not Integer)

	@Column(name = "name", nullable = false, unique = true)
	private String name; // ✅ FIXED (String, not Integer)

	@Column(name = "description")
	private String description; // ✅ FIXED (String, not Integer)

	/*
	 * ====================== GETTERS & SETTERS ======================
	 */

	public Long getId() {
		return id;
	}

	public void setId(Long id) {
		this.id = id;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public String getDescription() {
		return description;
	}

	public void setDescription(String description) {
		this.description = description;
	}
}

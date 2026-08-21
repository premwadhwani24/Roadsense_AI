package com.ai.smart.road.monitoring.system.application.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseBody;

import com.ai.smart.road.monitoring.system.application.model.Pothole;
import com.ai.smart.road.monitoring.system.application.service.PotholeService;

@Controller
public class PotholeController {

	@Autowired
	private PotholeService potholeService;

	// ==============================
	// Thymeleaf Pages
	// ==============================

	// List all potholes page
	@GetMapping("/pothole/list")
	public String listPotholesPage(Model model) {
		model.addAttribute("potholes", potholeService.getAllPotholes());
		return "pothole-list"; // Thymeleaf template
	}

	// Show report pothole form
	@GetMapping("/pothole/report")
	public String showReportForm(Model model) {
		model.addAttribute("pothole", new Pothole());
		return "report-pothole"; // Thymeleaf template
	}

	// Handle report pothole form submission
	@PostMapping("/pothole/report")
	public String submitPothole(@ModelAttribute Pothole pothole) {
		potholeService.createPothole(pothole);
		return "redirect:/pothole/list"; // Redirect to list after reporting
	}

	// ==============================
	// REST API Endpoints
	// ==============================

	// Get all potholes (API)
	@GetMapping("/api/potholes")
	@ResponseBody
	public List<Pothole> getAllPotholes() {
		return potholeService.getAllPotholes();
	}

	// Get pothole by ID (API)
	@GetMapping("/api/potholes/{id}")
	@ResponseBody
	public ResponseEntity<Pothole> getPotholeById(@PathVariable Long id) {
		return potholeService.getPotholeById(id).map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
	}

	// Create pothole (API)
	@PostMapping("/api/potholes")
	@ResponseBody
	public Pothole createPothole(@RequestBody Pothole pothole) {
		return potholeService.createPothole(pothole);
	}

	// Update pothole (API)
	@PutMapping("/api/potholes/{id}")
	@ResponseBody
	public Pothole updatePothole(@PathVariable Long id, @RequestBody Pothole pothole) {
		return potholeService.updatePothole(id, pothole);
	}

	// Delete pothole (API)
	@DeleteMapping("/api/potholes/{id}")
	@ResponseBody
	public ResponseEntity<Void> deletePothole(@PathVariable Long id) {
		potholeService.deletePothole(id);
		return ResponseEntity.noContent().build();
	}
}

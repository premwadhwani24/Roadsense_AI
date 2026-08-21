package com.ai.smart.road.monitoring.system.application.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

import com.ai.smart.road.monitoring.system.application.service.PotholeService;

@Controller
@RequestMapping("/admin")
public class AdminDashboardController {

	@Autowired
	private PotholeService potholeService;

	@GetMapping("/dashboard")
	public String dashboard(Model model) {
		model.addAttribute("openCount", potholeService.countByStatus("Open"));
		model.addAttribute("fixedCount", potholeService.countByStatus("Fixed"));
		model.addAttribute("severityDistribution", potholeService.countBySeverity());
		model.addAttribute("dailyTrend", potholeService.dailyDetectionTrend());
		model.addAttribute("potholesPerRoad", potholeService.potholeCountPerRoad());
		return "admin-dashboard";
	}
}

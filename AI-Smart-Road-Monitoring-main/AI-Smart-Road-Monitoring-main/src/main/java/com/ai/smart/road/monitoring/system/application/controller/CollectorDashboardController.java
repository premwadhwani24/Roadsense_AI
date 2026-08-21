package com.ai.smart.road.monitoring.system.application.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/collector")
public class CollectorDashboardController {

	@GetMapping("/dashboard")
	public String collectorDashboard() {
		return "collector-dashboard";
	}
}

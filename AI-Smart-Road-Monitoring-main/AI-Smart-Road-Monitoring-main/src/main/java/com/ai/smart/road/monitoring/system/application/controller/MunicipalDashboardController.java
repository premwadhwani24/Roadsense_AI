package com.ai.smart.road.monitoring.system.application.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/municipal")
public class MunicipalDashboardController {

	@GetMapping("/dashboard")
	public String municipalDashboard() {
		return "municipal-dashboard";
	}
}

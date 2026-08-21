package com.ai.smart.road.monitoring.system.application.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/pwd")
public class PwdDashboardController {

	@GetMapping("/dashboard")
	public String pwdDashboard() {
		return "pwd-dashboard";
	}
}

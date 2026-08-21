package com.ai.smart.road.monitoring.system.application.controller;

import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class DashboardRedirectController {

	@GetMapping("/redirect-dashboard")
	public String redirectDashboard(Authentication auth) {

		if (auth.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"))) {
			return "redirect:/admin/dashboard";
		}
		if (auth.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_COLLECTOR"))) {
			return "redirect:/collector/dashboard";
		}
		if (auth.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_MUNICIPAL"))) {
			return "redirect:/municipal/dashboard";
		}
		if (auth.getAuthorities().stream().anyMatch(a -> a.getAuthority().equals("ROLE_PWD"))) {
			return "redirect:/pwd/dashboard";
		}

		return "redirect:/user/dashboard";
	}
}

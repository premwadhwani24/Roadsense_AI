package com.ai.smart.road.monitoring.system.application.controller;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class RoleRedirectController {

	@GetMapping("/postLogin")
	public String redirectAfterLogin(Authentication authentication) {

		if (authentication == null) {
			return "redirect:/login?error";
		}

		String role = authentication.getAuthorities().stream().map(GrantedAuthority::getAuthority).findFirst()
				.orElse("").replace("ROLE_", "");

		System.out.println("🔐 Logged-in user role: " + role);

		switch (role) {
		case "ADMIN":
			return "redirect:/admin/dashboard";
		case "COLLECTOR":
			return "redirect:/collector/dashboard";
		case "MUNICIPAL":
			return "redirect:/municipal/dashboard";
		case "PWD":
			return "redirect:/pwd/dashboard";
		case "USER":
			return "redirect:/user/dashboard";
		default:
			return "redirect:/login?error";
		}
	}
}

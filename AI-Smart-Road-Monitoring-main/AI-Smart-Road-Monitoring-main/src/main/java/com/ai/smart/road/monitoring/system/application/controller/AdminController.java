package com.ai.smart.road.monitoring.system.application.controller;

import java.io.File;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class AdminController {

	@GetMapping("/admin/open-gui")
	public String openDesktopGUI() {

		try {
			String projectRoot = System.getProperty("user.dir");

			String pythonExe = "python";
			String scriptPath = projectRoot + File.separator + "python_ai" + File.separator + "gui_desktop.py";

			ProcessBuilder pb = new ProcessBuilder(pythonExe, scriptPath);
			pb.start();

		} catch (Exception e) {
			e.printStackTrace(); // IMPORTANT FOR DEBUG
		}

		return "redirect:/admin/dashboard";
	}
}

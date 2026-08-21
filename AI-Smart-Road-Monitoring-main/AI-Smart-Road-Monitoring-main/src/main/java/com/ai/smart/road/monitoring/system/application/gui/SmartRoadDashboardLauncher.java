package com.ai.smart.road.monitoring.system.application.gui;

import javax.swing.SwingUtilities;

/**
 * Launcher for the Swing SmartRoadDashboard.
 */
public class SmartRoadDashboardLauncher {
	public static void main(String[] args) {
		// Launch UI on the Event Dispatch Thread
		SwingUtilities.invokeLater(() -> {
			SmartRoadDashboard dashboard = new SmartRoadDashboard();
			dashboard.setVisible(true);
		});
	}
}

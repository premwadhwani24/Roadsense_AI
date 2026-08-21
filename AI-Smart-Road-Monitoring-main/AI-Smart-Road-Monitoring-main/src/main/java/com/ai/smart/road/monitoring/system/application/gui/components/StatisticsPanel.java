package com.ai.smart.road.monitoring.system.application.gui.components;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Font;
import java.awt.Graphics;

import javax.swing.JPanel;

public class StatisticsPanel extends JPanel {
	
	private static final long serialVersionUID = 1L;

	private int totalPotholes;
	private int repairedPotholes;

	public StatisticsPanel(int totalPotholes, int repairedPotholes) {
		this.totalPotholes = totalPotholes;
		this.repairedPotholes = repairedPotholes;
		setPreferredSize(new Dimension(300, 200));
		setBackground(Color.WHITE);
	}

	public void updateStats(int totalPotholes, int repairedPotholes) {
		this.totalPotholes = totalPotholes;
		this.repairedPotholes = repairedPotholes;
		repaint();
	}

	@Override
	protected void paintComponent(Graphics g) {
		super.paintComponent(g);

		g.setColor(Color.BLACK);
		g.setFont(new Font("Arial", Font.BOLD, 16));

		g.drawString("Road Statistics:", 20, 30);
		g.drawString("Total Potholes: " + totalPotholes, 20, 70);
		g.drawString("Repaired Potholes: " + repairedPotholes, 20, 110);

		// Simple bar chart
		int barWidth = 100;
		int totalBarHeight = 100;
		int repairedHeight = (int) ((double) repairedPotholes / (totalPotholes == 0 ? 1 : totalPotholes)
				* totalBarHeight);

		g.setColor(Color.GRAY);
		g.fillRect(20, 130, barWidth, totalBarHeight); // total
		g.setColor(Color.GREEN);
		g.fillRect(20, 130 + (totalBarHeight - repairedHeight), barWidth, repairedHeight); // repaired
	}
}

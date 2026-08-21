package com.ai.smart.road.monitoring.system.application.gui.components;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics;
import java.util.List;

import javax.swing.JPanel;

import com.ai.smart.road.monitoring.system.application.dto.PotholeResponse;

public class PotholeMapPanel extends JPanel {

	private static final long serialVersionUID = 1L;

	private List<PotholeResponse> potholes;

	// Panel boundaries for coordinate scaling
	private double minLat = 0, maxLat = 1;
	private double minLon = 0, maxLon = 1;

	public PotholeMapPanel(List<PotholeResponse> potholes) {
		this.potholes = potholes;
		setPreferredSize(new Dimension(600, 400));
		setBackground(Color.WHITE);
		calculateBounds();
	}

	public void setPotholes(List<PotholeResponse> potholes) {
		this.potholes = potholes;
		calculateBounds();
		repaint();
	}

	// Calculate min/max latitude and longitude for scaling
	private void calculateBounds() {
		if (potholes == null || potholes.isEmpty())
			return;
		minLat = potholes.stream().mapToDouble(PotholeResponse::getLatitude).min().orElse(0);
		maxLat = potholes.stream().mapToDouble(PotholeResponse::getLatitude).max().orElse(1);
		minLon = potholes.stream().mapToDouble(PotholeResponse::getLongitude).min().orElse(0);
		maxLon = potholes.stream().mapToDouble(PotholeResponse::getLongitude).max().orElse(1);

		// Avoid division by zero
		if (minLat == maxLat)
			maxLat = minLat + 0.01;
		if (minLon == maxLon)
			maxLon = minLon + 0.01;
	}

	@Override
	protected void paintComponent(Graphics g) {
		super.paintComponent(g);
		if (potholes == null || potholes.isEmpty()) {
			g.drawString("No potholes detected", 20, 20);
			return;
		}

		g.setColor(Color.RED);
		int width = getWidth();
		int height = getHeight();

		for (PotholeResponse p : potholes) {
			int x = (int) ((p.getLongitude() - minLon) / (maxLon - minLon) * width);
			int y = (int) ((maxLat - p.getLatitude()) / (maxLat - minLat) * height); // invert Y for map
			int size = 10; // display size
			g.fillOval(x, y, size, size);
		}
	}
}

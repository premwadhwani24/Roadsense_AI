package com.ai.smart.road.monitoring.system.application.gui.components;

import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics;
import java.util.List;

import javax.swing.JPanel;

import com.ai.smart.road.monitoring.system.application.dto.RoadDataDTO;

public class RoadMapPanel extends JPanel {

	private static final long serialVersionUID = 1L;

	private List<RoadDataDTO> roads;

	private double minLat = 0, maxLat = 1;
	private double minLon = 0, maxLon = 1;

	public RoadMapPanel(List<RoadDataDTO> roads) {
		this.roads = roads;
		setPreferredSize(new Dimension(600, 400));
		setBackground(Color.WHITE);
		calculateBounds();
	}

	public void setRoads(List<RoadDataDTO> roads) {
		this.roads = roads;
		calculateBounds();
		repaint();
	}

	private void calculateBounds() {
		if (roads == null || roads.isEmpty())
			return;
		minLat = roads.stream().mapToDouble(RoadDataDTO::getLatitude).min().orElse(0);
		maxLat = roads.stream().mapToDouble(RoadDataDTO::getLatitude).max().orElse(1);
		minLon = roads.stream().mapToDouble(RoadDataDTO::getLongitude).min().orElse(0);
		maxLon = roads.stream().mapToDouble(RoadDataDTO::getLongitude).max().orElse(1);

		if (minLat == maxLat)
			maxLat = minLat + 0.01;
		if (minLon == maxLon)
			maxLon = minLon + 0.01;
	}

	@Override
	protected void paintComponent(Graphics g) {
		super.paintComponent(g);
		if (roads == null || roads.isEmpty()) {
			g.drawString("No road data available", 20, 20);
			return;
		}

		g.setColor(Color.BLUE);
		int width = getWidth();
		int height = getHeight();

		for (RoadDataDTO r : roads) {
			int x = (int) ((r.getLongitude() - minLon) / (maxLon - minLon) * width);
			int y = (int) ((maxLat - r.getLatitude()) / (maxLat - minLat) * height);
			int size = 8; // display size
			g.fillRect(x, y, size, size);
		}
	}
}

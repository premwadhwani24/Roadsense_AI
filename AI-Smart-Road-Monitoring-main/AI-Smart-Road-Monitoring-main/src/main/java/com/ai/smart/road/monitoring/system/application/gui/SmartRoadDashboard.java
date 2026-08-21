package com.ai.smart.road.monitoring.system.application.gui;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Font;
import java.awt.GridLayout;
import java.io.File;
import java.time.Instant;
import java.util.Map;

import javax.swing.BorderFactory;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.SwingConstants;

/**
 * Main Swing frame for the Smart Road Dashboard. - serialVersionUID to satisfy
 * serialization warnings. - Keeps same look and feel as before (layout and
 * colors preserved).
 */
public class SmartRoadDashboard extends JFrame {
	private static final long serialVersionUID = 20251203123456L;

	private final DataVisualizer visualizer;
	private final ChartGenerator chartGenerator;

	// UI components (preserve look & feel you had)
	private JPanel chartsContainer;
	private JLabel totalRoadsLabel;
	private JLabel totalPotholesLabel;
	private JLabel lastUpdatedLabel;

	public SmartRoadDashboard() {
		super("AI Smart Road Monitoring Dashboard");
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setSize(1200, 720);
		setLocationRelativeTo(null);

		visualizer = new DataVisualizer();
		chartGenerator = new ChartGenerator();

		initUI();
		loadAndRender();
	}

	private void initUI() {
		// Top title (preserve styling)
		JLabel title = new JLabel("AI Smart Road Monitoring Dashboard");
		title.setFont(new Font("Dialog", Font.BOLD, 20));
		title.setOpaque(true);
		title.setBackground(new Color(25, 38, 51));
		title.setForeground(Color.WHITE);
		title.setBorder(BorderFactory.createEmptyBorder(8, 12, 8, 12));
		add(title, BorderLayout.NORTH);

		// Charts container (3 charts horizontally)
		chartsContainer = new JPanel();
		chartsContainer.setLayout(new GridLayout(1, 3, 12, 0));
		chartsContainer.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));
		add(chartsContainer, BorderLayout.CENTER);

		// Footer stats preserve look
		JPanel footer = new JPanel(new GridLayout(1, 3));
		footer.setBackground(new Color(32, 31, 39));
		footer.setBorder(BorderFactory.createEmptyBorder(12, 12, 12, 12));

		totalRoadsLabel = new JLabel("0", SwingConstants.CENTER);
		totalRoadsLabel.setForeground(new Color(3, 195, 165));
		totalRoadsLabel.setFont(new Font("Dialog", Font.BOLD, 18));
		JPanel p1 = new JPanel(new BorderLayout());
		p1.setOpaque(false);
		p1.add(new JLabel("Total Roads", SwingConstants.CENTER), BorderLayout.NORTH);
		p1.add(totalRoadsLabel, BorderLayout.CENTER);

		totalPotholesLabel = new JLabel("0", SwingConstants.CENTER);
		totalPotholesLabel.setForeground(new Color(3, 195, 165));
		totalPotholesLabel.setFont(new Font("Dialog", Font.BOLD, 18));
		JPanel p2 = new JPanel(new BorderLayout());
		p2.setOpaque(false);
		p2.add(new JLabel("Potholes Detected", SwingConstants.CENTER), BorderLayout.NORTH);
		p2.add(totalPotholesLabel, BorderLayout.CENTER);

		lastUpdatedLabel = new JLabel(Instant.now().toString(), SwingConstants.CENTER);
		lastUpdatedLabel.setForeground(new Color(3, 195, 165));
		lastUpdatedLabel.setFont(new Font("Dialog", Font.BOLD, 16));
		JPanel p3 = new JPanel(new BorderLayout());
		p3.setOpaque(false);
		p3.add(new JLabel("Last Updated", SwingConstants.CENTER), BorderLayout.NORTH);
		p3.add(lastUpdatedLabel, BorderLayout.CENTER);

		footer.add(p1);
		footer.add(p2);
		footer.add(p3);

		add(footer, BorderLayout.SOUTH);
	}

	/**
	 * Load data via DataVisualizer and render charts using ChartGenerator.
	 */
	public void loadAndRender() {
		// default file locations relative to project root
		File roadFile = new File("data/sample/road_data.json");
		File potholeFile = new File("data/sample/potholes_data.json");

		Map<String, Object> summary = visualizer.loadAndSummarize(roadFile, potholeFile);

		// update stats safely
		Object roadsObj = summary.getOrDefault("total_roads", 0);
		Object potholesObj = summary.getOrDefault("total_potholes", 0);
		Object lastUpdatedObj = summary.getOrDefault("last_updated", Instant.now().toString());

		totalRoadsLabel.setText(String.valueOf(roadsObj));
		totalPotholesLabel.setText(String.valueOf(potholesObj));
		lastUpdatedLabel.setText(String.valueOf(lastUpdatedObj));

		chartsContainer.removeAll();

		// create charts (ChartGenerator returns JPanels)
		JPanel severityChart = chartGenerator.createPotholeSeverityChartPanel(visualizer.getSeverityCounts());
		JPanel conditionChart = chartGenerator.createRoadConditionChartPanel(visualizer.getConditionCounts());
		JPanel trendChart = chartGenerator.createDetectionTrendChartPanel(visualizer.getDailyTrend());

		chartsContainer.add(severityChart);
		chartsContainer.add(conditionChart);
		chartsContainer.add(trendChart);

		chartsContainer.revalidate();
		chartsContainer.repaint();
	}
}

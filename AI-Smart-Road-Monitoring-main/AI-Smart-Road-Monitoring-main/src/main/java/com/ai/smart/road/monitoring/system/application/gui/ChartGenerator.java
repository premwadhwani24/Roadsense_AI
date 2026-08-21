package com.ai.smart.road.monitoring.system.application.gui;

import java.awt.Color;
import java.awt.Dimension;
import java.util.Map;

import javax.swing.JPanel;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.axis.NumberAxis;
import org.jfree.chart.plot.CategoryPlot;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.chart.renderer.category.BarRenderer;
import org.jfree.chart.renderer.category.LineAndShapeRenderer;
import org.jfree.data.category.DefaultCategoryDataset;

/**
 * Creates JFreeChart panels for severity distribution, condition overview, and
 * daily trend. - Ensures DefaultCategoryDataset is populated with default
 * categories to avoid UnknownKeyException. - Uses null-safe retrieval patterns.
 */
public class ChartGenerator {

	public JPanel createPotholeSeverityChartPanel(Map<String, Integer> severityCounts) {
		// DefaultCategoryDataset is not generic. Fill with expected categories to avoid
		// missing keys.
		DefaultCategoryDataset dataset = new DefaultCategoryDataset();
		String series = "Potholes";

		// ensure keys exist and use uppercase keys HIGH/MEDIUM/LOW
		int high = severityCounts.getOrDefault("HIGH", 0);
		int med = severityCounts.getOrDefault("MEDIUM", 0);
		int low = severityCounts.getOrDefault("LOW", 0);

		dataset.addValue(high, series, "High");
		dataset.addValue(med, series, "Medium");
		dataset.addValue(low, series, "Low");

		JFreeChart chart = ChartFactory.createBarChart("Pothole Severity Distribution", "Severity", "Count", dataset,
				PlotOrientation.VERTICAL, true, false, false);

		// styling similar to previous app (keep look)
		CategoryPlot plot = chart.getCategoryPlot();
		BarRenderer renderer = (BarRenderer) plot.getRenderer();
		renderer.setDrawBarOutline(false);
		plot.setBackgroundPaint(Color.LIGHT_GRAY);

		ChartPanel panel = new ChartPanel(chart);
		panel.setPreferredSize(new Dimension(360, 420));
		return panel;
	}

	public JPanel createRoadConditionChartPanel(Map<String, Integer> conditionCounts) {
		DefaultCategoryDataset dataset = new DefaultCategoryDataset();
		String series = "Roads";

		// normalize and ensure GOOD, MODERATE, BAD exist
		int good = conditionCounts.getOrDefault("GOOD", 0);
		int moderate = conditionCounts.getOrDefault("MODERATE", 0);
		int bad = conditionCounts.getOrDefault("BAD", 0);

		dataset.addValue(good, series, "Good");
		dataset.addValue(moderate, series, "Moderate");
		dataset.addValue(bad, series, "Bad");

		JFreeChart chart = ChartFactory.createBarChart("Road Condition Overview", "Condition", "Count", dataset,
				PlotOrientation.VERTICAL, true, false, false);

		CategoryPlot plot = chart.getCategoryPlot();
		plot.setBackgroundPaint(Color.LIGHT_GRAY);
		ChartPanel panel = new ChartPanel(chart);
		panel.setPreferredSize(new Dimension(360, 420));
		return panel;
	}

	public JPanel createDetectionTrendChartPanel(Map<String, Integer> dailyTrend) {
		// line chart for days Mon..Sun
		DefaultCategoryDataset dataset = new DefaultCategoryDataset();
		String series = "Potholes";

		// ensure we add Mon..Sun in this order
		String[] days = { "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun" };
		for (String d : days) {
			int v = dailyTrend.getOrDefault(d, 0);
			dataset.addValue(v, series, d);
		}

		JFreeChart chart = ChartFactory.createLineChart("Daily Detection Trend", "Day", "Potholes", dataset,
				PlotOrientation.VERTICAL, true, false, false);

		CategoryPlot plot = chart.getCategoryPlot();
		plot.setBackgroundPaint(Color.LIGHT_GRAY);

		NumberAxis rangeAxis = (NumberAxis) plot.getRangeAxis();
		rangeAxis.setAutoRangeIncludesZero(true);

		// renderer to show lines + shapes consistently
		LineAndShapeRenderer renderer = new LineAndShapeRenderer();
		renderer.setDefaultShapesVisible(true);
		plot.setRenderer(renderer);

		ChartPanel panel = new ChartPanel(chart);
		panel.setPreferredSize(new Dimension(360, 420));
		return panel;
	}
}

package com.ai.smart.road.monitoring.system.application.util;

public class GpsUtil {

	private static final double EARTH_RADIUS_KM = 6371.0;

	/**
	 * Calculate the distance between two GPS points in meters using the Haversine
	 * formula
	 * 
	 * @param lat1 Latitude of point 1
	 * @param lon1 Longitude of point 1
	 * @param lat2 Latitude of point 2
	 * @param lon2 Longitude of point 2
	 * @return distance in meters
	 */
	public static double distance(double lat1, double lon1, double lat2, double lon2) {
		double dLat = Math.toRadians(lat2 - lat1);
		double dLon = Math.toRadians(lon2 - lon1);

		double a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(Math.toRadians(lat1))
				* Math.cos(Math.toRadians(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);

		double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

		return EARTH_RADIUS_KM * c * 1000; // convert km to meters
	}

	/**
	 * Format GPS coordinates as a string "lat,lon"
	 * 
	 * @param latitude
	 * @param longitude
	 * @return formatted string
	 */
	public static String format(double latitude, double longitude) {
		return String.format("%.6f,%.6f", latitude, longitude);
	}

	/**
	 * Check if a given GPS coordinate is valid
	 * 
	 * @param latitude
	 * @param longitude
	 * @return true if valid
	 */
	public static boolean isValid(double latitude, double longitude) {
		return latitude >= -90 && latitude <= 90 && longitude >= -180 && longitude <= 180;
	}
}

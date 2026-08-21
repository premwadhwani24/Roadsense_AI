package com.ai.smart.road.monitoring.system.application.util;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class DateUtil {

	private static final String DEFAULT_PATTERN = "yyyy-MM-dd HH:mm:ss";

	public static String format(LocalDateTime dateTime) {
		return format(dateTime, DEFAULT_PATTERN);
	}

	public static String format(LocalDateTime dateTime, String pattern) {
		if (dateTime == null)
			return "";
		DateTimeFormatter formatter = DateTimeFormatter.ofPattern(pattern);
		return dateTime.format(formatter);
	}

	public static LocalDateTime parse(String dateTimeStr) {
		return parse(dateTimeStr, DEFAULT_PATTERN);
	}

	public static LocalDateTime parse(String dateTimeStr, String pattern) {
		if (dateTimeStr == null || dateTimeStr.isEmpty())
			return null;
		DateTimeFormatter formatter = DateTimeFormatter.ofPattern(pattern);
		return LocalDateTime.parse(dateTimeStr, formatter);
	}
}

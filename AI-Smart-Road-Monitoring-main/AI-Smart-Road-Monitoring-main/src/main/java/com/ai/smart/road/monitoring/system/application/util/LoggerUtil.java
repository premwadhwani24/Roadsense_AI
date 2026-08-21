package com.ai.smart.road.monitoring.system.application.util;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LoggerUtil {

	public static Logger getLogger(Class<?> clazz) {
		return LoggerFactory.getLogger(clazz);
	}

	public static void info(Class<?> clazz, String message) {
		getLogger(clazz).info(message);
	}

	public static void error(Class<?> clazz, String message, Throwable t) {
		getLogger(clazz).error(message, t);
	}

	public static void warn(Class<?> clazz, String message) {
		getLogger(clazz).warn(message);
	}

	public static void debug(Class<?> clazz, String message) {
		getLogger(clazz).debug(message);
	}
}

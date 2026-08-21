package com.ai.smart.road.monitoring.system.application.test;

import java.io.IOException;
import java.util.List;

import com.fasterxml.jackson.databind.ObjectMapper;

public class TestUtils {

	public static <T> List<T> readJsonList(String resourcePath, Class<T> clazz) throws IOException {
		ObjectMapper mapper = new ObjectMapper();
		return mapper.readValue(TestUtils.class.getClassLoader().getResourceAsStream(resourcePath),
				mapper.getTypeFactory().constructCollectionType(List.class, clazz));
	}
}

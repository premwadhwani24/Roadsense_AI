package com.ai.smart.road.monitoring.system.application.test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.Collections;
import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import com.ai.smart.road.monitoring.system.application.model.RoadData;
import com.ai.smart.road.monitoring.system.application.repository.RoadDataRepository;
import com.ai.smart.road.monitoring.system.application.service.RoadServiceImpl;

class RoadServiceTest {

	@Mock
	private RoadDataRepository roadRepository;

	@InjectMocks
	private RoadServiceImpl roadService;

	private RoadData road;

	@BeforeEach
	void setUp() {
		MockitoAnnotations.openMocks(this);
		road = new RoadData();
		road.setId(1L);
		road.setRoadName("Main Street");
		road.setLatitude(23.456);
		road.setLongitude(77.123);
		road.setSurfaceLevel(0.95);
		road.setSlope(0.05);
		road.setStatus("Good");
		road.setSensorFile("sensor_data.csv");
	}

	@Test
	void testCreateRoad() {
		when(roadRepository.save(any(RoadData.class))).thenReturn(road);
		RoadData saved = roadService.createRoad(road);
		assertNotNull(saved);
		assertEquals("Main Street", saved.getRoadName());
	}

	@Test
	void testGetAllRoads() {
		when(roadRepository.findAll()).thenReturn(Collections.singletonList(road));
		List<RoadData> roads = roadService.getAllRoads();
		assertEquals(1, roads.size());
		assertEquals("Main Street", roads.get(0).getRoadName());
	}

	@Test
	void testGetRoadById() {
		when(roadRepository.findById(1L)).thenReturn(Optional.of(road));
		Optional<RoadData> found = roadService.getRoadById(1L);
		assertTrue(found.isPresent());
		assertEquals("Main Street", found.get().getRoadName());
	}

	@Test
	void testUpdateRoad() {
		when(roadRepository.findById(1L)).thenReturn(Optional.of(road));
		when(roadRepository.save(any(RoadData.class))).thenReturn(road);

		road.setStatus("Under Maintenance");
		RoadData updated = roadService.updateRoad(1L, road);
		assertEquals("Under Maintenance", updated.getStatus());
	}

	@Test
	void testDeleteRoad() {
		when(roadRepository.existsById(1L)).thenReturn(true);
		doNothing().when(roadRepository).deleteById(1L);
		assertDoesNotThrow(() -> roadService.deleteRoad(1L));
		verify(roadRepository, times(1)).deleteById(1L);
	}

	@Test
	void testDeleteRoad_NotFound() {
		when(roadRepository.existsById(99L)).thenReturn(false);
		RuntimeException ex = assertThrows(RuntimeException.class, () -> roadService.deleteRoad(99L));
		assertTrue(ex.getMessage().contains("not found"));
	}
}

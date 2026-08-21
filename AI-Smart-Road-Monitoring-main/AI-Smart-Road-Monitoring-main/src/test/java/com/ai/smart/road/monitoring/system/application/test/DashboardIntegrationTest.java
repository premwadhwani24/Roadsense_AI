package com.ai.smart.road.monitoring.system.application.test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

import java.time.LocalDateTime;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

import com.ai.smart.road.monitoring.system.application.dto.PotholeResponse;
import com.ai.smart.road.monitoring.system.application.dto.RoadDataDTO;
import com.ai.smart.road.monitoring.system.application.model.Pothole;
import com.ai.smart.road.monitoring.system.application.model.RoadData;
import com.ai.smart.road.monitoring.system.application.service.DashboardMapperService;
import com.ai.smart.road.monitoring.system.application.service.PotholeService;
import com.ai.smart.road.monitoring.system.application.service.RoadService;

@SpringBootTest
class DashboardIntegrationTest {

	@MockBean
	private DashboardMapperService dashboardMapperService;

	@MockBean
	private RoadService roadService;

	@MockBean
	private PotholeService potholeService;

	@Test
	void testDashboardDataMapping() {

		RoadData road = new RoadData();
		road.setLatitude(12.34);
		road.setLongitude(56.78);
		road.setSurfaceLevel(10);
		road.setSlope(2);

		Pothole pothole = new Pothole();
		pothole.setId(1L);
		pothole.setLength(1.5);
		pothole.setWidth(0.8);
		pothole.setDepth(0.3);
		pothole.setGpsLocation("12.34,56.78");
		pothole.setDetectedAt(LocalDateTime.now());
		pothole.setLatitude(12.34);
		pothole.setLongitude(56.78);

		when(roadService.getAllRoads()).thenReturn(List.of(road));
		when(potholeService.getAllPotholes()).thenReturn(List.of(pothole));

		RoadDataDTO roadDTO = new RoadDataDTO("12.340000_56.780000", 10, 2, 10, null, 12.34, 56.78);

		PotholeResponse potholeDTO = new PotholeResponse(1L, 1.5, 0.8, 0.3, "12.34,56.78", pothole.getDetectedAt(),
				12.34, 56.78);

		when(dashboardMapperService.toRoadDataDTOs(List.of(road))).thenReturn(List.of(roadDTO));

		when(dashboardMapperService.toPotholeResponses(List.of(pothole))).thenReturn(List.of(potholeDTO));

		List<RoadDataDTO> roads = dashboardMapperService.toRoadDataDTOs(List.of(road));

		List<PotholeResponse> potholes = dashboardMapperService.toPotholeResponses(List.of(pothole));

		assertThat(roads).hasSize(1);
		assertThat(roads.get(0).getId()).isEqualTo("12.340000_56.780000");

		assertThat(potholes).hasSize(1);
		assertThat(potholes.get(0).getGpsLocation()).isEqualTo("12.34,56.78");
	}
}

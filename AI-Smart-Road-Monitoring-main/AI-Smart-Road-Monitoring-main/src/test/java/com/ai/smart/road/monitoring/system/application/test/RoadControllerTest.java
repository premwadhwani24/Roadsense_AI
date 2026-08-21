package com.ai.smart.road.monitoring.system.application.test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

import com.ai.smart.road.monitoring.system.application.dto.RoadDataDTO;
import com.ai.smart.road.monitoring.system.application.model.RoadData;
import com.ai.smart.road.monitoring.system.application.service.DashboardMapperService;
import com.ai.smart.road.monitoring.system.application.service.RoadService;

@SpringBootTest
class RoadControllerTest {

	@MockBean
	private RoadService roadService;

	@MockBean
	private DashboardMapperService dashboardMapperService;

	@Test
	void testGetAllRoadData() {

		RoadData road = new RoadData();
		road.setLatitude(12.34);
		road.setLongitude(56.78);
		road.setSurfaceLevel(10);
		road.setSlope(2);

		when(roadService.getAllRoads()).thenReturn(List.of(road));

		RoadDataDTO dto = new RoadDataDTO("12.340000_56.780000", 10, 2, 10, null, 12.34, 56.78);

		when(dashboardMapperService.toRoadDataDTOs(List.of(road))).thenReturn(List.of(dto));

		List<RoadDataDTO> dtos = dashboardMapperService.toRoadDataDTOs(List.of(road));

		assertThat(dtos).hasSize(1);
		assertThat(dtos.get(0).getId()).isEqualTo("12.340000_56.780000");
		assertThat(dtos.get(0).getLength()).isEqualTo(10);
		assertThat(dtos.get(0).getWidth()).isEqualTo(2);
	}
}

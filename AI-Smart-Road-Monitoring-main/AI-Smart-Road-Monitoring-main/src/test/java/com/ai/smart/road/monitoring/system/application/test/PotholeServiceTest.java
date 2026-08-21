package com.ai.smart.road.monitoring.system.application.test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

import java.time.LocalDateTime;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

import com.ai.smart.road.monitoring.system.application.dto.PotholeResponse;
import com.ai.smart.road.monitoring.system.application.model.Pothole;
import com.ai.smart.road.monitoring.system.application.service.DashboardMapperService;
import com.ai.smart.road.monitoring.system.application.service.PotholeService;

@SpringBootTest
class PotholeServiceTest {

	@MockBean
	private PotholeService potholeService;

	@MockBean
	private DashboardMapperService dashboardMapperService;

	@Test
	void testGetPotholeResponses() {

		Pothole p1 = new Pothole();
		p1.setId(101L);
		p1.setLength(2.0);
		p1.setWidth(1.0);
		p1.setDepth(0.5);
		p1.setGpsLocation("12.34,56.78");
		p1.setDetectedAt(LocalDateTime.now());
		p1.setLatitude(12.34);
		p1.setLongitude(56.78);

		when(potholeService.getAllPotholes()).thenReturn(List.of(p1));

		PotholeResponse dto = new PotholeResponse(101L, 2.0, 1.0, 0.5, "12.34,56.78", p1.getDetectedAt(), 12.34, 56.78);

		when(dashboardMapperService.toPotholeResponses(List.of(p1))).thenReturn(List.of(dto));

		List<PotholeResponse> responses = dashboardMapperService.toPotholeResponses(List.of(p1));

		assertThat(responses).hasSize(1);
		assertThat(responses.get(0).getDepth()).isEqualTo(0.5);
		assertThat(responses.get(0).getLatitude()).isEqualTo(12.34);
	}
}

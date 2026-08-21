package com.ai.smart.road.monitoring.system.application.service;

import java.util.List;
import java.util.Optional;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.ai.smart.road.monitoring.system.application.model.Pothole;
import com.ai.smart.road.monitoring.system.application.repository.PotholeRepository;

@Service
public class PotholeServiceImpl implements PotholeService {

	@Autowired
	private PotholeRepository potholeRepository;

	@Override
	public List<Pothole> getAllPotholes() {
		return potholeRepository.findAll();
	}

	@Override
	public Optional<Pothole> getPotholeById(Long id) {
		return potholeRepository.findById(id);
	}

	@Override
	public Pothole createPothole(Pothole pothole) {
		return potholeRepository.save(pothole);
	}

	@Override
	public Pothole updatePothole(Long id, Pothole potholeDetails) {
		return potholeRepository.findById(id).map(p -> {
			p.setRoadId(potholeDetails.getRoadId());
			p.setGpsLocation(potholeDetails.getGpsLocation());
			p.setGpsPin(potholeDetails.getGpsPin());
			p.setLatitude(potholeDetails.getLatitude());
			p.setLongitude(potholeDetails.getLongitude());
			p.setLength(potholeDetails.getLength());
			p.setWidth(potholeDetails.getWidth());
			p.setDepth(potholeDetails.getDepth());
			p.setSeverity(potholeDetails.getSeverity());
			p.setStatus(potholeDetails.getStatus());
			p.setDetectedDate(potholeDetails.getDetectedDate());
			p.setDetectedAt(potholeDetails.getDetectedAt());
			p.setImagePath(potholeDetails.getImagePath());
			return potholeRepository.save(p);
		}).orElseThrow(() -> new RuntimeException("Pothole not found with id " + id));
	}

	@Override
	public void deletePothole(Long id) {
		if (!potholeRepository.existsById(id)) {
			throw new RuntimeException("Pothole not found with id " + id);
		}
		potholeRepository.deleteById(id);
	}

	// Analytics
	@Override
	public long countByStatus(String status) {
		return potholeRepository.countByStatus(status);
	}

	@Override
	public List<Object[]> countBySeverity() {
		return potholeRepository.countBySeverity();
	}

	@Override
	public List<Object[]> dailyDetectionTrend() {
		return potholeRepository.dailyDetectionTrend();
	}

	@Override
	public List<Object[]> potholeCountPerRoad() {
		return potholeRepository.potholeCountPerRoad();
	}
}

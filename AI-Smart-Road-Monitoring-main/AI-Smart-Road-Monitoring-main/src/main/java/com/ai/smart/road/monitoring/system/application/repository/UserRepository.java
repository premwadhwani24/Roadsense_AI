package com.ai.smart.road.monitoring.system.application.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.ai.smart.road.monitoring.system.application.model.User;

public interface UserRepository extends JpaRepository<User, Long> {

	User findByUsername(String username);

}

package com.ai.smart.road.monitoring.system.application.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

import com.ai.smart.road.monitoring.system.application.model.Role;
import com.ai.smart.road.monitoring.system.application.model.User;
import com.ai.smart.road.monitoring.system.application.repository.RoleRepository;
import com.ai.smart.road.monitoring.system.application.repository.UserRepository;

@Configuration
public class UserInitConfig implements CommandLineRunner {

	@Autowired
	private RoleRepository roleRepo;

	@Autowired
	private UserRepository userRepo;

	private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

	@Override
	public void run(String... args) {

		createRoleIfMissing("ADMIN");
		createRoleIfMissing("COLLECTOR");
		createRoleIfMissing("MUNICIPAL");
		createRoleIfMissing("PWD");
		createRoleIfMissing("USER");

		createUserIfMissing("admin", "admin123", "ADMIN");
		createUserIfMissing("collector", "collector123", "COLLECTOR");
		createUserIfMissing("municipal", "municipal123", "MUNICIPAL");
		createUserIfMissing("pwd", "pwd123", "PWD");
		createUserIfMissing("user", "user123", "USER");
	}

	private void createRoleIfMissing(String roleName) {
		if (roleRepo.findByName(roleName) != null)
			return;

		Role role = new Role();
		role.setName(roleName);
		role.setDescription(roleName + " role");
		roleRepo.save(role);
	}

	private void createUserIfMissing(String username, String password, String roleName) {
		if (userRepo.findByUsername(username) != null)
			return;

		Role role = roleRepo.findByName(roleName);
		if (role == null)
			throw new IllegalStateException("Role missing: " + roleName);

		User user = new User();
		user.setUsername(username);
		user.setPassword(encoder.encode(password));
		user.setEmail(username + "@system.com");
		user.setRole(role);
		user.setActive(true);

		userRepo.save(user);
	}
}

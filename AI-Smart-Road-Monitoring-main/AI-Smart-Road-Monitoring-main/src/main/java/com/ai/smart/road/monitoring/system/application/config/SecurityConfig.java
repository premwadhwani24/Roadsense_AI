package com.ai.smart.road.monitoring.system.application.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

import com.ai.smart.road.monitoring.system.application.service.UserDetailsServiceImpl;

import lombok.RequiredArgsConstructor;

@Configuration
@RequiredArgsConstructor
public class SecurityConfig {

	private final UserDetailsServiceImpl userDetailsService;

	@Bean
	public BCryptPasswordEncoder passwordEncoder() {
		return new BCryptPasswordEncoder();
	}

	@Bean
	public DaoAuthenticationProvider authenticationProvider() {
		DaoAuthenticationProvider auth = new DaoAuthenticationProvider();
		auth.setUserDetailsService(userDetailsService);
		auth.setPasswordEncoder(passwordEncoder());
		return auth;
	}

	@Bean
	public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {

	    http.csrf(csrf -> csrf.disable());

	    http.authorizeHttpRequests(auth -> auth
	        .requestMatchers("/login", "/css/**", "/js/**").permitAll()

	        .requestMatchers("/admin/**").hasRole("ADMIN")
	        .requestMatchers("/collector/**").hasRole("COLLECTOR")
	        .requestMatchers("/municipal/**").hasRole("MUNICIPAL")
	        .requestMatchers("/pwd/**").hasRole("PWD")
	        .requestMatchers("/user/**").hasRole("USER")

	        .anyRequest().authenticated()
	    );

	    http.formLogin(form -> form
	        .loginPage("/login")
	        .loginProcessingUrl("/do-login")
	        .defaultSuccessUrl("/redirect-dashboard", true)
	        .failureUrl("/login?error=true")
	        .permitAll()
	    );

	    http.logout(logout -> logout
	        .logoutUrl("/logout")
	        .logoutSuccessUrl("/login?logout=true")
	        .permitAll()
	    );

	    return http.build();
	}

}

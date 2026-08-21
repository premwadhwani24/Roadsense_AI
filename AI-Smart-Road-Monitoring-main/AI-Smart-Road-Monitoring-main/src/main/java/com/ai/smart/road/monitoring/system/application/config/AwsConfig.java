package com.ai.smart.road.monitoring.system.application.config;

import java.net.URI;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.EnvironmentVariableCredentialsProvider;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;

@Configuration
public class AwsConfig {

	@Value("${aws.accessKeyId:}")
	private String accessKey;

	@Value("${aws.secretAccessKey:}")
	private String secretKey;

	@Value("${aws.region:us-east-1}")
	private String region;

	@Value("${aws.s3.endpoint:}")
	private String s3Endpoint;

	@Bean
	public S3Client s3Client() {
		try {
			var builder = S3Client.builder().region(Region.of(region));

			// Use credentials based on what’s available
			if (accessKey != null && !accessKey.isBlank() && secretKey != null && !secretKey.isBlank()) {
				builder.credentialsProvider(
						StaticCredentialsProvider.create(AwsBasicCredentials.create(accessKey, secretKey)));
			} else {
				// fallback to environment or default AWS credentials
				builder.credentialsProvider(EnvironmentVariableCredentialsProvider.create());
			}

			// Optional custom endpoint (e.g., LocalStack)
			if (s3Endpoint != null && !s3Endpoint.isBlank()) {
				builder.endpointOverride(URI.create(s3Endpoint));
			}

			return builder.build();
		} catch (Exception e) {
			// Log and continue app startup without throwing
			System.err.println("⚠️ AWS S3 Client not initialized: " + e.getMessage());
			return null; // Application will still start for local testing
		}
	}
}

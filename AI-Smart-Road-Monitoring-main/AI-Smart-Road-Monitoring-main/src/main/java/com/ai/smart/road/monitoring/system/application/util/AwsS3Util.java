package com.ai.smart.road.monitoring.system.application.util;



import java.io.File;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.CannedAccessControlList;
import com.amazonaws.services.s3.model.PutObjectRequest;

@Component
public class AwsS3Util {

    private final AmazonS3 s3Client;

    public AwsS3Util(@Value("${aws.accessKey:}") String accessKey,
                     @Value("${aws.secretKey:}") String secretKey,
                     @Value("${aws.region:ap-south-1}") String region) {
        if (accessKey.isEmpty() || secretKey.isEmpty()) {
            // Create a dummy client for local testing
            this.s3Client = null;
        } else {
            this.s3Client = AmazonS3ClientBuilder.standard()
                    .withRegion(region)
                    .withCredentials(new AWSStaticCredentialsProvider(new BasicAWSCredentials(accessKey, secretKey)))
                    .build();
        }
    }

    public void uploadFile(String bucketName, String keyName, File file) {
        if (s3Client != null) {
            s3Client.putObject(
                new PutObjectRequest(bucketName, keyName, file)
                    .withCannedAcl(CannedAccessControlList.PublicRead)
            );
        }
    }
}

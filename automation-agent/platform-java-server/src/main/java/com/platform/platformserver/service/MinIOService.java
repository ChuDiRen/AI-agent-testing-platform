package com.platform.platformserver.service;

import io.minio.*;
import io.minio.http.Method;
import io.minio.messages.Bucket;
import io.minio.messages.Item;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

@Service
public class MinIOService {
    
    @Autowired
    private MinioClient minioClient;
    
    @Value("${minio.bucket-name}")
    private String bucketName;
    
    public void createBucket(String bucketName) throws Exception {
        boolean exists = minioClient.bucketExists(BucketExistsArgs.builder().bucket(bucketName).build());
        if (!exists) {
            minioClient.makeBucket(MakeBucketArgs.builder().bucket(bucketName).build());
        }
    }
    
    public List<String> listBuckets() throws Exception {
        List<Bucket> buckets = minioClient.listBuckets();
        List<String> bucketNames = new ArrayList<>();
        for (Bucket bucket : buckets) {
            bucketNames.add(bucket.name());
        }
        return bucketNames;
    }
    
    public String uploadFile(String objectName, MultipartFile file) throws Exception {
        try (InputStream inputStream = file.getInputStream()) {
            minioClient.putObject(
                PutObjectArgs.builder()
                    .bucket(bucketName)
                    .object(objectName)
                    .stream(inputStream, file.getSize(), -1)
                    .contentType(file.getContentType())
                    .build()
            );
        }
        return objectName;
    }
    
    public InputStream downloadFile(String objectName) throws Exception {
        return minioClient.getObject(
            GetObjectArgs.builder()
                .bucket(bucketName)
                .object(objectName)
                .build()
        );
    }
    
    public void deleteFile(String objectName) throws Exception {
        minioClient.removeObject(
            RemoveObjectArgs.builder()
                .bucket(bucketName)
                .object(objectName)
                .build()
        );
    }
    
    public List<String> listFiles() throws Exception {
        Iterable<Result<Item>> results = minioClient.listObjects(
            ListObjectsArgs.builder()
                .bucket(bucketName)
                .build()
        );
        
        List<String> fileNames = new ArrayList<>();
        for (Result<Item> result : results) {
            Item item = result.get();
            fileNames.add(item.objectName());
        }
        return fileNames;
    }
    
    public String getFileUrl(String objectName) throws Exception {
        return minioClient.getPresignedObjectUrl(
            GetPresignedObjectUrlArgs.builder()
                .method(Method.GET)
                .bucket(bucketName)
                .object(objectName)
                .expiry(60 * 60) // 1小时有效期
                .build()
        );
    }
}
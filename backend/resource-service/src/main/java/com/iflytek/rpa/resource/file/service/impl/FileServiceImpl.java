package com.iflytek.rpa.resource.file.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.resource.common.exp.ServiceException;
import com.iflytek.rpa.resource.common.response.AppResponse;
import com.iflytek.rpa.resource.common.response.ErrorCodeEnum;
import com.iflytek.rpa.resource.file.config.S3Config;
import com.iflytek.rpa.resource.file.dao.FileMapper;
import com.iflytek.rpa.resource.file.entity.File;
import com.iflytek.rpa.resource.file.service.FileService;
import com.iflytek.rpa.resource.file.utils.IdWorker;
import jakarta.servlet.http.HttpServletResponse;
import org.apache.commons.lang3.StringUtils;
import org.apache.tomcat.util.http.fileupload.IOUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.core.ResponseInputStream;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.*;

import java.io.IOException;
import java.net.URLDecoder;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Date;

import static software.amazon.awssdk.core.sync.RequestBody.fromBytes;

/**
 * 文件表 服务实现类
 *
 * @author system
 * @since 2024-01-01
 */
@Service
public class FileServiceImpl extends ServiceImpl<FileMapper, File> implements FileService {

    @Autowired
    private S3Config s3Config;

    @Autowired
    private HttpServletResponse response;

    @Autowired
    private IdWorker idWorker;

    @Override
    public AppResponse<Boolean> downloadFile(String fileId) throws IOException {
        // 1. 查询数据库获取文件信息

        File file = baseMapper.getFile(fileId);
        if (file == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode());
        }

        // 校验文件路径
        String filePath = file.getPath();
        if (StringUtils.isBlank(filePath)) {
            throw new ServiceException(ErrorCodeEnum.E_SQL.getCode());
        }

        // 2. 从S3下载文件
        downloadFileFromS3(file.getPath());

        return AppResponse.success(true);
    }


    /**
     * 从S3下载文件
     *
     * @param filePath 文件路径
     * @return 文件内容字节数组
     */
    private void downloadFileFromS3(String filePath) throws IOException {

        S3Client s3Client = null;
        ResponseInputStream<GetObjectResponse> s3Object = null;

        try {
            // 构建S3客户端
            s3Client = buildS3Client();

            // 构建完整的S3对象键
            String objectKey = filePath;

            // 从S3下载文件
            GetObjectRequest getObjectRequest = GetObjectRequest.builder()
                    .bucket(s3Config.getBucket())
                    .key(objectKey)
                    .build();

            s3Object = s3Client.getObject(getObjectRequest);

            String fileName = filePath.substring(filePath.lastIndexOf("/") + 1);

            response.reset();
            response.setCharacterEncoding("UTF-8");
            response.setContentType("application/octet-stream");
            response.addHeader("Content-Disposition", "attachment;filename=" + URLEncoder.encode(fileName, StandardCharsets.UTF_8));
            IOUtils.copy(s3Object, response.getOutputStream());

        } catch (NoSuchKeyException e) {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE_INFO_LOSE.getCode(), "文件在S3中不存在");
        } catch (S3Exception e) {
            throw new ServiceException(ErrorCodeEnum.E_API_EXCEPTION.getCode(), "S3服务异常: " + e.getMessage());
        } catch (IOException e) {
            throw new ServiceException(ErrorCodeEnum.E_COMMON.getCode(), "文件读取异常: " + e.getMessage());
        } catch (Exception e) {
            throw new ServiceException(ErrorCodeEnum.E_EXCEPTION.getCode(), "S3下载异常: " + e.getMessage());
        } finally {
            if (s3Client != null) s3Client.close();
            if (s3Object != null) s3Object.close();
        }
    }


    @Override
    public AppResponse<String> uploadFile(MultipartFile file) throws IOException {

        // 1. 获取原始文件名并URL解码
        String originalFileName = file.getOriginalFilename();

        // URL解码
        String decodedFileName = URLDecoder.decode(originalFileName, StandardCharsets.UTF_8);

        // 2. 生成文件ID和随机文件名
        String fileId = String.valueOf(idWorker.nextId());
        String fileExtension = getFileExtension(decodedFileName);
        String replaceName = fileId + fileExtension;

        // 3. 构建目标路径
        String date = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        String targetPath = "rpa/" + date + "/" + replaceName;

        // 4. 上传文件到S3
        uploadFileToS3(file.getBytes(), targetPath);

        // 5. 保存文件信息到数据库
        saveFileInfo(fileId, targetPath, decodedFileName);

        return AppResponse.success(fileId);

    }

    /**
     * 获取文件扩展名
     *
     * @param fileName 文件名
     * @return 扩展名
     */
    private String getFileExtension(String fileName) {
        if (StringUtils.isBlank(fileName)) {
            return "";
        }
        int lastDotIndex = fileName.lastIndexOf(".");
        if (lastDotIndex == -1) {
            return "";
        }
        return fileName.substring(lastDotIndex);
    }

    /**
     * 上传文件到S3
     *
     * @param fileContent 文件内容
     * @param targetPath  目标路径
     */
    private void uploadFileToS3(byte[] fileContent, String targetPath) {
        S3Client s3Client = null;
        try {
            s3Client = buildS3Client();
            
            PutObjectRequest putObjectRequest = PutObjectRequest.builder()
                    .bucket(s3Config.getBucket())
                    .key(targetPath)
                    .build();
            
            s3Client.putObject(putObjectRequest, fromBytes(fileContent));

        } catch (S3Exception e) {
            throw new ServiceException(ErrorCodeEnum.E_API_EXCEPTION.getCode(), "S3上传异常: " + e.getMessage());
        } catch (Exception e) {
            throw new ServiceException(ErrorCodeEnum.E_EXCEPTION.getCode(), "文件上传异常: " + e.getMessage());
        } finally {
            if (s3Client != null) {
                s3Client.close();
            }
        }
    }

    /**
     * 保存文件信息到数据库
     *
     * @param fileId     文件ID
     * @param targetPath 目标路径
     * @param fileName   文件名
     */
    private void saveFileInfo(String fileId, String targetPath, String fileName) {
        File file = new File();
        file.setFileId(fileId);
        file.setPath(targetPath);
        file.setFileName(fileName);
        file.setCreateTime(new Date());
        file.setUpdateTime(new Date());

        baseMapper.insert(file);
    }

    /**
     * 构建S3客户端
     */
    private S3Client buildS3Client() {
        AwsBasicCredentials awsCredentials = AwsBasicCredentials.create(
                s3Config.getAccessKey(),
                s3Config.getSecretKey()
        );

        return S3Client.builder()
                .region(Region.US_EAST_1) // 根据实际情况调整区域
                .credentialsProvider(StaticCredentialsProvider.create(awsCredentials))
                .endpointOverride(java.net.URI.create(s3Config.getUrl()))
                .build();
    }
}

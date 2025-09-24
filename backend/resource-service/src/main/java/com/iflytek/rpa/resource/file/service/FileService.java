package com.iflytek.rpa.resource.file.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.iflytek.rpa.resource.common.response.AppResponse;
import com.iflytek.rpa.resource.file.entity.File;
import java.io.IOException;
import org.springframework.web.multipart.MultipartFile;

/**
 * 文件表 服务类
 *
 * @author system
 * @since 2024-01-01
 */
public interface FileService extends IService<File> {

    /**
     * 根据文件ID下载文件
     *
     * @param fileId 文件ID
     * @return 文件流响应
     */
    AppResponse<Boolean> downloadFile(String fileId) throws IOException;

    /**
     * 上传文件
     *
     * @param file 文件对象
     * @return 文件ID
     */
    AppResponse<String> uploadFile(MultipartFile file) throws IOException;
}

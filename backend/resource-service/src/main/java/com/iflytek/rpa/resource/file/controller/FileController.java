package com.iflytek.rpa.resource.file.controller;

import com.iflytek.rpa.resource.common.exp.ServiceException;
import com.iflytek.rpa.resource.common.response.AppResponse;
import com.iflytek.rpa.resource.common.response.ErrorCodeEnum;
import com.iflytek.rpa.resource.file.entity.enums.FileType;
import com.iflytek.rpa.resource.file.entity.vo.ShareFileUploadVo;
import com.iflytek.rpa.resource.file.service.FileService;
import java.io.IOException;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/file")
public class FileController {

    // 文件大小校验 (50MB = 50 * 1024 * 1024 bytes)
    private final long maxFileSize = 50 * 1024 * 1024;
    // 文件大小校验 (100MB = 50 * 1024 * 1024 bytes)
    private final long maxShareSize = 100 * 1024 * 1024;

    @Autowired
    private FileService fileService;

    /**
     * 根据文件ID下载文件
     *
     * @param fileId 文件ID
     * @return 文件流响应
     */
    @GetMapping("/download")
    public AppResponse<Boolean> downloadFile(@RequestParam("fileId") String fileId) throws IOException {
        // 参数校验
        if (StringUtils.isEmpty(fileId)) throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode());

        // 调用Service层处理业务逻辑
        return fileService.downloadFile(fileId);
    }

    /**
     * 上传文件
     *
     * @param file 文件对象
     * @return 上传结果
     */
    @PostMapping("/upload")
    public AppResponse<String> uploadFile(@RequestParam("file") MultipartFile file) throws IOException {
        // 参数校验
        checkParam(file, maxFileSize);

        // 调用Service层处理业务逻辑
        return fileService.uploadFile(file);
    }

    /**
     * 上传视频文件
     *
     * @param file 视频文件对象
     * @return 上传结果
     */
    @PostMapping("/upload-video")
    public AppResponse<String> uploadVideoFile(@RequestParam("file") MultipartFile file) throws IOException {
        // 参数校验
        checkParam(file, maxFileSize);

        // 校验视频格式
        checkVideo(file);

        // 调用Service层处理业务逻辑
        return fileService.uploadFile(file);
    }

    /**
     * 上传共享文件
     *
     * @param file 视频文件对象
     * @return 上传结果
     */
    @PostMapping("/share-file-upload")
    public AppResponse<ShareFileUploadVo> shareFileUpload(@RequestParam("file") MultipartFile file) throws IOException {
        // 参数校验
        checkParam(file, maxShareSize);

        AppResponse<String> response = fileService.uploadFile(file);
        if (!response.ok()) throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "上传共享文件失败");

        String fileId = response.getData();
        String filename = file.getOriginalFilename();
        Integer type = FileType.getFileType(filename).getValue();

        ShareFileUploadVo resVo = new ShareFileUploadVo(fileId, type, filename);
        return AppResponse.success(resVo);
    }

    private void checkVideo(MultipartFile file) {
        // 校验视频文件格式
        String originalFilename = file.getOriginalFilename();
        String fileExtension = originalFilename
                .substring(originalFilename.lastIndexOf(".") + 1)
                .toLowerCase();
        String[] allowedVideoFormats = {"mp4", "webm", "ogg", "avi", "mov", "mpeg"};

        boolean isValidFormat = false;
        for (String format : allowedVideoFormats) {
            if (format.equals(fileExtension)) {
                isValidFormat = true;
                break;
            }
        }

        if (!isValidFormat) {
            throw new ServiceException(
                    ErrorCodeEnum.E_PARAM_CHECK.getCode(), "视频文件格式不支持，仅支持：mp4, webm, ogg, avi, mov, mpeg");
        }
    }

    private void checkParam(MultipartFile file, long maxSize) {
        if (file == null || file.isEmpty()) throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode(), "文件不能为空");

        if (file.getSize() > maxSize) throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "文件大小不能超过50MB");

        if (StringUtils.isBlank(file.getOriginalFilename()))
            throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode(), "文件名不能为空");
    }
}

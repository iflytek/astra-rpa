package com.iflytek.rpa.robot.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.robot.entity.dto.SharedFileBatchDeleteDto;
import com.iflytek.rpa.robot.entity.dto.SharedFileDto;
import com.iflytek.rpa.robot.entity.dto.SharedFilePageDto;
import com.iflytek.rpa.robot.entity.dto.UpdateSharedFileDto;
import com.iflytek.rpa.robot.entity.vo.SharedFilePageVo;
import com.iflytek.rpa.robot.entity.vo.TagVo;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;
import javax.servlet.http.HttpServletRequest;

/**
 * 共享文件服务接口
 *
 * @author yfchen40
 * @since 2025-07-21
 */
public interface SharedFileService {
    AppResponse<IPage<SharedFilePageVo>> getSharedFilePageList(SharedFilePageDto queryDto);

    AppResponse<String> deleteSharedFile(HttpServletRequest request, SharedFileBatchDeleteDto batchDeleteDto)
            throws NoLoginException;

    AppResponse<?> addSharedFileInfo(HttpServletRequest request, SharedFileDto dto) throws NoLoginException;

    AppResponse<?> updateSharedFileInfo(HttpServletRequest request, UpdateSharedFileDto dto) throws NoLoginException;

    AppResponse<List<TagVo>> getTags(HttpServletRequest request) throws NoLoginException;

    AppResponse<String> addTags(HttpServletRequest request, String tagName) throws NoLoginException;

    AppResponse<String> updateTags(HttpServletRequest request, Long tagId, String tagName) throws NoLoginException;

    AppResponse<String> deleteTags(HttpServletRequest request, Long tagId) throws NoLoginException;
}

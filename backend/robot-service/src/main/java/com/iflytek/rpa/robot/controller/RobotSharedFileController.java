package com.iflytek.rpa.robot.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.robot.entity.dto.SharedFileBatchDeleteDto;
import com.iflytek.rpa.robot.entity.dto.SharedFileDto;
import com.iflytek.rpa.robot.entity.dto.SharedFilePageDto;
import com.iflytek.rpa.robot.entity.dto.UpdateSharedFileDto;
import com.iflytek.rpa.robot.entity.vo.SharedFilePageVo;
import com.iflytek.rpa.robot.entity.vo.TagVo;
import com.iflytek.rpa.robot.service.SharedFileService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;
import javax.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 共享文件管理
 *
 * @author yfchen40
 * @since 2025-07-21
 */
@RestController
@RequestMapping("/robot-shared-file")
public class RobotSharedFileController {
    @Autowired
    private SharedFileService sharedFileService;

    /**
     * 获取共享文件分页列表
     *
     * @param queryDto 查询条件
     * @return 分页结果
     * @throws NoLoginException 如果用户未登录
     */
    @PostMapping("/page")
    public AppResponse<IPage<SharedFilePageVo>> getSharedFilePageList(@RequestBody SharedFilePageDto queryDto)
            throws NoLoginException {
        return sharedFileService.getSharedFilePageList(queryDto);
    }

    /**
     * 删除共享文件
     *
     * @param batchDeleteDto 批量删除dto
     * @return 删除结果
     * @throws NoLoginException 如果用户未登录
     */
    @PostMapping("/delete")
    public AppResponse<String> deleteSharedFile(
            HttpServletRequest request, @RequestBody SharedFileBatchDeleteDto batchDeleteDto) throws NoLoginException {
        return sharedFileService.deleteSharedFile(request, batchDeleteDto);
    }

    /**
     * 共享文件新增文件相关信息
     *
     * @param request
     * @param dto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/addSharedFileInfo")
    public AppResponse<?> addSharedFileInfo(HttpServletRequest request, @RequestBody SharedFileDto dto)
            throws NoLoginException {
        return sharedFileService.addSharedFileInfo(request, dto);
    }

    /**
     * 共享文件-修改文件相关信息
     *
     * @param request
     * @param dto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/updateSharedFileInfo")
    public AppResponse<?> updateSharedFileInfo(HttpServletRequest request, @RequestBody UpdateSharedFileDto dto)
            throws NoLoginException {
        return sharedFileService.updateSharedFileInfo(request, dto);
    }

    /**
     * 获取文件标签接口
     *
     * @return 标签列表
     * @throws NoLoginException 如果用户未登录
     */
    @PostMapping("/tags/page")
    public AppResponse<List<TagVo>> getTags(HttpServletRequest request) throws NoLoginException {
        return sharedFileService.getTags(request);
    }

    /**
     * 新增文件标签接口
     *
     * @param tagName 标签名称
     * @return 添加结果
     * @throws NoLoginException 如果用户未登录
     */
    @PostMapping("/tags/add")
    public AppResponse<String> addTags(HttpServletRequest request, @RequestParam String tagName)
            throws NoLoginException {
        return sharedFileService.addTags(request, tagName);
    }

    /**
     * 修改文件标签接口
     *
     * @param tagId   标签ID
     * @param tagName 标签名称
     * @return 更新结果
     * @throws NoLoginException 如果用户未登录
     */
    @PostMapping("/tags/update")
    public AppResponse<String> updateTags(
            HttpServletRequest request, @RequestParam Long tagId, @RequestParam String tagName)
            throws NoLoginException {
        return sharedFileService.updateTags(request, tagId, tagName);
    }

    /**
     * 删除标签接口
     *
     * @param tagId 文件ID
     * @return 删除结果
     * @throws NoLoginException 如果用户未登录
     */
    @PostMapping("/tags/delete")
    public AppResponse<String> deleteTags(HttpServletRequest request, @RequestParam Long tagId)
            throws NoLoginException {
        return sharedFileService.deleteTags(request, tagId);
    }
}

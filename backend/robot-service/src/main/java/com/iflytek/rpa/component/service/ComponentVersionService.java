package com.iflytek.rpa.component.service;

import com.iflytek.rpa.component.entity.dto.CreateVersionDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;

/**
 * 组件版本表(ComponentVersion)表服务接口
 *
 * @author makejava
 * @since 2024-12-19
 */
public interface ComponentVersionService {

    /**
     * 创建组件版本
     */
    AppResponse<Boolean> createComponentVersion(CreateVersionDto createVersionDto) throws NoLoginException;

    /**
     * 获取组件下一个版本号（最新版本号+1，如果没有版本则返回1）
     */
    AppResponse<Integer> getNextVersionNumber(String componentId) throws NoLoginException;
}

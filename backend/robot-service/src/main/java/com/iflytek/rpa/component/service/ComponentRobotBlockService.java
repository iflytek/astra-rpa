package com.iflytek.rpa.component.service;

import com.iflytek.rpa.component.entity.dto.AddRobotBlockDto;
import com.iflytek.rpa.component.entity.dto.GetRobotBlockDto;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;

/**
 * 机器人对组件屏蔽表(ComponentRobotBlock)表服务接口
 *
 * @author makejava
 * @since 2024-12-19
 */
public interface ComponentRobotBlockService {

    /**
     * 添加机器人对组件的屏蔽记录
     *
     * @param addRobotBlockDto 添加屏蔽记录请求参数
     * @return 操作结果
     * @throws Exception 异常信息
     */
    AppResponse<Boolean> addRobotBlock(AddRobotBlockDto addRobotBlockDto) throws Exception;

    /**
     * 删除机器人对组件的屏蔽记录
     *
     * @param addRobotBlockDto 删除屏蔽记录请求参数
     * @return 操作结果
     * @throws Exception 异常信息
     */
    AppResponse<Boolean> deleteRobotBlock(AddRobotBlockDto addRobotBlockDto) throws Exception;

    /**
     * 获取机器人屏蔽的组件ID列表
     *
     * @param queryDto
     * @return 屏蔽的组件ID列表
     * @throws Exception 异常信息
     */
    AppResponse<List<String>> getBlockedComponentIds(GetRobotBlockDto queryDto) throws Exception;
}

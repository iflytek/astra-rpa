package com.iflytek.rpa.component.service;

import com.iflytek.rpa.component.entity.dto.AddCompUseDto;
import com.iflytek.rpa.component.entity.dto.DelComponentUseDto;
import com.iflytek.rpa.component.entity.dto.GetComponentUseDto;
import com.iflytek.rpa.component.entity.dto.UpdateComponentUseDto;
import com.iflytek.rpa.component.entity.vo.ComponentUseVo;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;

/**
 * 机器人对组件引用表(ComponentRobotUse)表服务接口
 *
 * @author makejava
 * @since 2024-12-19
 */
public interface ComponentRobotUseService {

    AppResponse<List<ComponentUseVo>> getComponentUse(GetComponentUseDto getComponentUseDto) throws NoLoginException;

    /**
     * 添加组件引用
     *
     * @param addCompUseDto 添加组件引用DTO
     * @return 操作结果
     * @throws NoLoginException
     */
    AppResponse<String> addComponentUse(AddCompUseDto addCompUseDto) throws NoLoginException;

    /**
     * 删除组件引用
     *
     * @param delComponentUseDto 删除组件引用DTO
     * @return 操作结果
     * @throws NoLoginException
     */
    AppResponse<String> deleteComponentUse(DelComponentUseDto delComponentUseDto) throws NoLoginException;

    /**
     * 更新组件引用版本
     *
     * @param updateComponentUseDto 更新组件引用DTO
     * @return 操作结果
     * @throws NoLoginException
     */
    AppResponse<String> updateComponentUse(UpdateComponentUseDto updateComponentUseDto) throws NoLoginException;

    /**
     * 根据组件ID和版本查询流程ID
     *
     * @param componentId
     * @param componentVersion
     * @return 流程ID
     * @throws NoLoginException
     */
    AppResponse<String> getProcessId(String componentId, Integer componentVersion) throws NoLoginException;
}

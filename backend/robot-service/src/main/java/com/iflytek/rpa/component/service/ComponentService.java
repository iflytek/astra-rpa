package com.iflytek.rpa.component.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.base.entity.CProcess;
import com.iflytek.rpa.component.entity.dto.CheckNameDto;
import com.iflytek.rpa.component.entity.dto.ComponentListDto;
import com.iflytek.rpa.component.entity.dto.EditPageCompInfoDto;
import com.iflytek.rpa.component.entity.dto.GetComponentUseDto;
import com.iflytek.rpa.component.entity.vo.*;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;

/**
 * 组件表(Component)表服务接口
 *
 * @author makejava
 * @since 2024-12-19
 */
public interface ComponentService {

    /**
     * 创建组件
     */
    AppResponse<CProcess> createComponent(String componentName) throws NoLoginException;

    /**
     * 删除组件
     */
    AppResponse<Boolean> deleteComponent(String componentId) throws NoLoginException;

    /**
     * 重命名组件
     */
    AppResponse<Boolean> renameComponent(String componentId, String newName) throws NoLoginException;

    /**
     * 检查组件名称是否重复
     */
    AppResponse<Boolean> checkNameDuplicate(CheckNameDto checkNameDto) throws NoLoginException;

    /**
     * 新建组件名称
     */
    AppResponse<String> createComponentName() throws NoLoginException;

    /**
     * 获取组件详情
     *
     * @param componentId 组件ID
     * @return 组件详情信息
     * @throws NoLoginException
     */
    AppResponse<ComponentInfoVo> getComponentInfo(String componentId) throws NoLoginException;

    AppResponse<Boolean> copyComponent(String componentId, String name) throws Exception;

    /**
     * 创建副本组件名称
     *
     * @param componentId 原组件ID
     * @return 新的组件名称
     * @throws Exception
     */
    AppResponse<String> copyCreateName(String componentId) throws Exception;

    /**
     * 分页查询组件列表
     *
     * @param componentListDto 查询条件
     * @return 分页组件列表
     * @throws Exception
     */
    AppResponse<IPage<ComponentVo>> getComponentPageList(ComponentListDto componentListDto) throws Exception;

    /**
     * 获取编辑页组件列表
     *
     * @param queryDto 查询条件
     * @return 编辑页组件列表
     * @throws Exception
     */
    AppResponse<List<EditingPageCompVo>> getEditingPageCompList(GetComponentUseDto queryDto) throws Exception;

    /**
     * 获取编辑页组件详情
     *
     * @param queryDto 查询条件
     * @return 编辑页组件详情
     * @throws Exception
     */
    AppResponse<EditingPageCompInfoVo> getEditingPageCompInfo(EditPageCompInfoDto queryDto) throws Exception;

    /**
     * 获取组件管理列表
     *
     * @param queryDto 查询条件
     * @return 组件管理列表
     * @throws Exception
     */
    AppResponse<List<CompManageVo>> getCompManageList(GetComponentUseDto queryDto) throws Exception;
}

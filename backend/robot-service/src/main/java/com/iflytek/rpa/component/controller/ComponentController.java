package com.iflytek.rpa.component.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.base.entity.CProcess;
import com.iflytek.rpa.component.entity.dto.CheckNameDto;
import com.iflytek.rpa.component.entity.dto.ComponentListDto;
import com.iflytek.rpa.component.entity.dto.EditPageCompInfoDto;
import com.iflytek.rpa.component.entity.dto.GetComponentUseDto;
import com.iflytek.rpa.component.entity.vo.*;
import com.iflytek.rpa.component.service.ComponentService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;
import javax.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 组件表(Component)表控制层
 *
 * @author makejava
 * @since 2024-12-19
 */
@RestController
@RequestMapping("/component")
public class ComponentController {

    @Autowired
    private ComponentService componentService;

    /**
     * 新建组件-获取默认组件名称
     *
     * @return
     * @throws Exception
     */
    @PostMapping("/create-name")
    public AppResponse<String> createComponentName() throws Exception {
        return componentService.createComponentName();
    }

    /**
     * 创建组件
     */
    @GetMapping("/create")
    public AppResponse<CProcess> createComponent(@RequestParam("componentName") String componentName) throws Exception {
        return componentService.createComponent(componentName);
    }

    /**
     * 删除组件
     * 只是隐藏在列表页的显示，把is_shown设置为0，不是真的逻辑删除
     */
    @GetMapping("/delete")
    public AppResponse<Boolean> deleteComponent(@RequestParam("componentId") String componentId) throws Exception {
        return componentService.deleteComponent(componentId);
    }

    /**
     * 重命名组件
     */
    @GetMapping("/rename")
    public AppResponse<Boolean> renameComponent(@RequestParam String componentId, @RequestParam String newName)
            throws Exception {
        return componentService.renameComponent(componentId, newName);
    }

    /**
     * 检查组件名称是否重复，
     * 改名字的时候传 componentId
     * 新建的时候不穿 componentId
     *
     * @param checkNameDto
     * @return
     * @throws Exception
     */
    @PostMapping("/check-name")
    public AppResponse<Boolean> checkNameDuplicate(@RequestBody @Valid CheckNameDto checkNameDto) throws Exception {
        return componentService.checkNameDuplicate(checkNameDto);
    }

    /**
     * 获取组件详情（列表页的详细版本）
     *
     * @param componentId 组件ID
     * @return 组件详情信息
     * @throws NoLoginException
     */
    @GetMapping("/info")
    public AppResponse<ComponentInfoVo> getComponentInfo(@RequestParam("componentId") String componentId)
            throws NoLoginException {
        return componentService.getComponentInfo(componentId);
    }

    /**
     * 创建副本
     *
     * @param componentId
     * @param name
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/copy")
    public AppResponse<Boolean> copyComponent(
            @RequestParam("componentId") String componentId, @RequestParam("name") String name) throws Exception {
        return componentService.copyComponent(componentId, name);
    }

    /**
     * 创建副本组件名称
     * 根据原组件名称生成新的副本名称，自动添加"-副本"后缀，如果重名则添加数字
     *
     * @param componentId 原组件ID
     * @return 新的组件名称
     * @throws Exception
     */
    @GetMapping("/copy/create-name")
    public AppResponse<String> copyCreateName(@RequestParam("componentId") String componentId) throws Exception {
        return componentService.copyCreateName(componentId);
    }

    /**
     * 分页查询组件列表
     *
     * @param componentListDto 查询条件
     * @return 分页组件列表
     * @throws Exception
     */
    @PostMapping("/page-list")
    public AppResponse<IPage<ComponentVo>> getComponentPageList(@RequestBody @Valid ComponentListDto componentListDto)
            throws Exception {
        return componentService.getComponentPageList(componentListDto);
    }

    /**
     * 机器人编辑页左侧组件列表
     *
     * @param queryDto
     * @return
     * @throws Exception
     */
    @PostMapping("/editing/list")
    public AppResponse<List<EditingPageCompVo>> getEditingPageCompList(@RequestBody GetComponentUseDto queryDto)
            throws Exception {
        return componentService.getEditingPageCompList(queryDto);
    }

    /**
     * 编辑页里面的组件详情
     *
     * @param queryDto
     * @return
     */
    @PostMapping("/editing/info")
    public AppResponse<EditingPageCompInfoVo> editingPageCompInfo(@RequestBody EditPageCompInfoDto queryDto)
            throws Exception {
        return componentService.getEditingPageCompInfo(queryDto);
    }

    /**
     * 组件管理列表
     *
     * @param queryDto
     * @return
     * @throws Exception
     */
    @PostMapping("/editing/manage-list")
    public AppResponse<List<CompManageVo>> CompManageList(@RequestBody GetComponentUseDto queryDto) throws Exception {
        return componentService.getCompManageList(queryDto);
    }
}

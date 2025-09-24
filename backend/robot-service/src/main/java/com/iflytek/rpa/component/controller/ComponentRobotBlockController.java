package com.iflytek.rpa.component.controller;

import com.iflytek.rpa.component.entity.dto.AddRobotBlockDto;
import com.iflytek.rpa.component.entity.dto.GetRobotBlockDto;
import com.iflytek.rpa.component.service.ComponentRobotBlockService;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;
import javax.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 机器人对组件屏蔽表(ComponentRobotBlock)表控制层
 *
 * @author makejava
 * @since 2024-12-19
 */
@RestController
@RequestMapping("/component-robot-block")
public class ComponentRobotBlockController {

    @Autowired
    private ComponentRobotBlockService componentRobotBlockService;

    /**
     * 添加机器人对组件的屏蔽记录 - 移除
     *
     * @param addRobotBlockDto 添加屏蔽记录请求参数
     * @return 操作结果
     * @throws Exception 异常信息
     */
    @PostMapping("/add")
    public AppResponse<Boolean> addRobotBlock(@RequestBody @Valid AddRobotBlockDto addRobotBlockDto) throws Exception {
        return componentRobotBlockService.addRobotBlock(addRobotBlockDto);
    }

    /**
     * 删除机器人对组件的屏蔽记录 - 安装
     *
     * @param addRobotBlockDto 删除屏蔽记录请求参数
     * @return 操作结果
     * @throws Exception 异常信息
     */
    @PostMapping("/delete")
    public AppResponse<Boolean> deleteRobotBlock(@RequestBody @Valid AddRobotBlockDto addRobotBlockDto)
            throws Exception {
        return componentRobotBlockService.deleteRobotBlock(addRobotBlockDto);
    }

    /**
     * 获取机器人屏蔽的组件ID列表
     *
     * @param queryDto
     * @return 屏蔽的组件ID列表
     * @throws Exception 异常信息
     */
    @PostMapping("/blocked-components")
    public AppResponse<List<String>> getBlockedComponentIds(@RequestBody @Valid GetRobotBlockDto queryDto)
            throws Exception {
        return componentRobotBlockService.getBlockedComponentIds(queryDto);
    }
}

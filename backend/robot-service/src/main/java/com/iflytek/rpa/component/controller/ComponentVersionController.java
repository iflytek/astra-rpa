package com.iflytek.rpa.component.controller;

import com.iflytek.rpa.component.entity.dto.CreateVersionDto;
import com.iflytek.rpa.component.service.ComponentVersionService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import javax.annotation.Resource;
import org.springframework.web.bind.annotation.*;

/**
 * 组件版本表(ComponentVersion)表控制层
 *
 * @author makejava
 * @since 2024-12-19
 */
@RestController
@RequestMapping("/component-version")
public class ComponentVersionController {

    @Resource
    private ComponentVersionService componentVersionService;

    /**
     * 发版
     *
     * @param createVersionDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("create")
    AppResponse<Boolean> createComponentVersion(@RequestBody CreateVersionDto createVersionDto)
            throws NoLoginException {

        return componentVersionService.createComponentVersion(createVersionDto);
    }

    /**
     * 获取组件下一个版本号
     *
     * @param componentId 组件ID
     * @return 下一个版本号
     * @throws NoLoginException
     */
    @GetMapping("next-version")
    AppResponse<Integer> getNextVersionNumber(@RequestParam("componentId") String componentId) throws NoLoginException {
        return componentVersionService.getNextVersionNumber(componentId);
    }
}

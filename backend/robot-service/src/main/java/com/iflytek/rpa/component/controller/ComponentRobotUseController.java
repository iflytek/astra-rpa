package com.iflytek.rpa.component.controller;

import com.iflytek.rpa.component.entity.dto.AddCompUseDto;
import com.iflytek.rpa.component.entity.dto.DelComponentUseDto;
import com.iflytek.rpa.component.entity.dto.GetComponentUseDto;
import com.iflytek.rpa.component.entity.dto.UpdateComponentUseDto;
import com.iflytek.rpa.component.entity.vo.ComponentUseVo;
import com.iflytek.rpa.component.service.ComponentRobotUseService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import java.util.List;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 机器人对组件引用表(ComponentRobotUse)表控制层
 *
 * @author makejava
 * @since 2024-12-19
 */
@RestController
@RequestMapping("/component-robot-use")
public class ComponentRobotUseController {

    @Autowired
    private ComponentRobotUseService componentRobotUseService;

    /**
     * 机器人引用的组件id 和 对应的version
     *
     * @param getComponentUseDto 查询组件使用情况DTO
     * @return 组件使用情况列表
     * @throws NoLoginException
     */
    @PostMapping("/component-use")
    public AppResponse<List<ComponentUseVo>> getComponentUse(@RequestBody GetComponentUseDto getComponentUseDto)
            throws NoLoginException {
        return componentRobotUseService.getComponentUse(getComponentUseDto);
    }

    /**
     * 添加组件引用
     *
     * @param addCompUseDto 添加组件引用DTO
     * @return 操作结果
     * @throws NoLoginException
     */
    @PostMapping("/add")
    public AppResponse<String> addComponentUse(@RequestBody AddCompUseDto addCompUseDto) throws NoLoginException {
        return componentRobotUseService.addComponentUse(addCompUseDto);
    }

    /**
     * 删除组件引用
     *
     * @param delComponentUseDto 删除组件引用DTO
     * @return 操作结果
     * @throws NoLoginException
     */
    @PostMapping("/delete")
    public AppResponse<String> deleteComponentUse(@RequestBody DelComponentUseDto delComponentUseDto)
            throws NoLoginException {
        return componentRobotUseService.deleteComponentUse(delComponentUseDto);
    }

    /**
     * 更新组件引用版本
     *
     * @param updateComponentUseDto 更新组件引用DTO
     * @return 操作结果
     * @throws NoLoginException
     */
    @PostMapping("/update")
    public AppResponse<String> updateComponentUse(@RequestBody UpdateComponentUseDto updateComponentUseDto)
            throws NoLoginException {
        return componentRobotUseService.updateComponentUse(updateComponentUseDto);
    }

    /**
     * 根据组件ID和版本查询流程ID
     *
     * @param componentId      组件ID
     * @param componentVersion 组件版本
     * @return 流程ID
     * @throws NoLoginException
     */
    @GetMapping("/process-id")
    public AppResponse<String> getProcessIdByComponentIdAndVersion(
            @RequestParam("componentId") String componentId, @RequestParam("componentVersion") Integer componentVersion)
            throws NoLoginException {

        if (StringUtils.isBlank(componentId)) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode(), "组件ID不能为空");
        }
        if (componentVersion == null) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode(), "组件版本不能为空");
        }

        return componentRobotUseService.getProcessId(componentId, componentVersion);
    }
}

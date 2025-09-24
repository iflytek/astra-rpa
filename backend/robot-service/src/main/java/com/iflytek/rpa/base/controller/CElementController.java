package com.iflytek.rpa.base.controller;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDIT_PAGE;

import com.iflytek.rpa.base.entity.CElement;
import com.iflytek.rpa.base.entity.dto.FrontElementCreateDto;
import com.iflytek.rpa.base.entity.dto.FrontElementDto;
import com.iflytek.rpa.base.entity.dto.ServerBaseDto;
import com.iflytek.rpa.base.service.CElementService;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import javax.annotation.Resource;
import org.springframework.beans.BeanUtils;
import org.springframework.web.bind.annotation.*;

/**
 * 元素或图像信息
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
@RestController
@RequestMapping("element")
public class CElementController {
    /**
     * 服务对象
     */
    @Resource
    private CElementService cElementService;

    //    /**
    //     * 获取元素名称列表
    //     * @param robotId
    //     * @param mode
    //     * @return
    //     * @throws Exception
    //     */
    //    @PostMapping("/all")
    //    public AppResponse<?> getElementNameList(@RequestParam("robotId") String robotId, @RequestParam(required =
    // false, name = "mode", defaultValue = EDIT_PAGE) String mode) throws Exception {
    //        BaseDto baseDto = new BaseDto();
    //        baseDto.setRobotId(robotId);
    //        baseDto.setMode(mode);
    //        return cElementService.getElementNameList(baseDto);
    //    }

    /**
     * 元素、图像-查询详情
     *
     * @param
     * @return
     * @throws Exception
     */
    @PostMapping("/detail")
    public AppResponse<?> getElementDetail(
            @RequestParam("robotId") String robotId,
            @RequestParam("elementId") String elementId,
            @RequestParam(required = false, name = "mode", defaultValue = EDIT_PAGE) String mode,
            @RequestParam(required = false, name = "robotVersion") Integer robotVersion)
            throws Exception {
        ServerBaseDto serverBaseDto = new ServerBaseDto();
        serverBaseDto.setRobotId(robotId);
        serverBaseDto.setElementId(elementId);
        serverBaseDto.setRobotVersion(robotVersion);
        serverBaseDto.setMode(mode);
        return cElementService.getElementDetail(serverBaseDto);
    }

    /**
     * 元素、图像-移动至其他分组
     *
     * @param
     * @return
     * @throws Exception
     */
    @PostMapping("/move")
    public AppResponse<?> moveElementOrImage(
            @RequestParam("robotId") String robotId,
            @RequestParam("elementId") String elementId,
            @RequestParam("groupId") String groupId)
            throws Exception {
        ServerBaseDto serverBaseDto = new ServerBaseDto();
        serverBaseDto.setRobotId(robotId);
        serverBaseDto.setRobotVersion(0);
        serverBaseDto.setElementId(elementId);
        serverBaseDto.setGroupId(groupId);
        return cElementService.moveElementOrImage(serverBaseDto);
    }

    /**
     * 元素、图像-删除
     *
     * @param
     * @return
     * @throws Exception
     */
    @PostMapping("/delete")
    public AppResponse<?> deleteElementOrImage(
            @RequestParam("robotId") String robotId, @RequestParam("elementId") String elementId) throws Exception {
        ServerBaseDto serverBaseDto = new ServerBaseDto();
        serverBaseDto.setRobotId(robotId);
        serverBaseDto.setRobotVersion(0);
        serverBaseDto.setElementId(elementId);
        return cElementService.deleteElementOrImage(serverBaseDto);
    }

    /**
     * 生成默认图像名称
     *
     * @param
     * @return
     * @throws Exception
     */
    @PostMapping("/image/create-name")
    public AppResponse<?> createImageName(@RequestParam("robotId") String robotId) throws Exception {
        ServerBaseDto serverBaseDto = new ServerBaseDto();
        serverBaseDto.setRobotId(robotId);
        serverBaseDto.setRobotVersion(0);
        return cElementService.createImageName(serverBaseDto);
    }

    /**
     * 元素、图像-创建
     *
     * @param
     * @return
     * @throws Exception
     */
    @PostMapping("/create")
    public AppResponse<?> createElement(@RequestBody FrontElementCreateDto frontElementCreateDto) throws Exception {
        if (null == frontElementCreateDto.getType()
                || null == frontElementCreateDto.getRobotId()
                || null == frontElementCreateDto.getGroupName()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        ServerBaseDto serverBaseDto = new ServerBaseDto();
        transFrontParamToServerParamForElement(frontElementCreateDto, serverBaseDto);
        return cElementService.createElement(serverBaseDto);
    }

    public void transFrontParamToServerParamForElement(
            FrontElementCreateDto frontElementCreateDto, ServerBaseDto serverBaseDto) {
        serverBaseDto.setElementType(frontElementCreateDto.getType());
        serverBaseDto.setRobotId(frontElementCreateDto.getRobotId());
        serverBaseDto.setRobotVersion(0);
        serverBaseDto.setGroupName(frontElementCreateDto.getGroupName());
        CElement cElement = new CElement();
        FrontElementDto frontElementDto = frontElementCreateDto.getElement();
        BeanUtils.copyProperties(frontElementDto, cElement);
        cElement.setElementId(frontElementDto.getId());
        cElement.setElementName(frontElementDto.getName());
        cElement.setCommonSubType(frontElementDto.getCommonSubType());
        cElement.setRobotId(serverBaseDto.getRobotId());
        cElement.setRobotVersion(0);
        serverBaseDto.setElement(cElement);
    }

    /**
     * 元素、图像-更新信息
     *
     * @param frontElementCreateDto
     * @return
     * @throws Exception
     */
    @PostMapping("/update")
    public AppResponse<?> updateElement(@RequestBody FrontElementCreateDto frontElementCreateDto) throws Exception {
        if (null == frontElementCreateDto.getRobotId() || null == frontElementCreateDto.getElement()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        ServerBaseDto serverBaseDto = new ServerBaseDto();
        transFrontParamToServerParamForElement(frontElementCreateDto, serverBaseDto);
        return cElementService.updateElement(serverBaseDto);
    }

    /**
     * 元素-创建副本
     *
     * @param
     * @return
     * @throws Exception
     */
    @PostMapping("/copy")
    public AppResponse<?> copyElement(
            @RequestParam("robotId") String robotId, @RequestParam("elementId") String elementId) throws Exception {
        // 在当前分组下创建副本
        ServerBaseDto serverBaseDto = new ServerBaseDto();
        serverBaseDto.setRobotId(robotId);
        serverBaseDto.setRobotVersion(0);
        serverBaseDto.setElementId(elementId);
        return cElementService.copyElement(serverBaseDto);
    }

    /**
     * 元素、图像-查询所有分组名称及组内元素信息
     *
     * @param robotId
     * @param elementType
     * @return
     * @throws Exception
     */
    @PostMapping("/all")
    public AppResponse<?> getAllGroupInfo(
            @RequestParam(name = "robotId") String robotId,
            @RequestParam("elementType") String elementType,
            @RequestParam(required = false, name = "mode", defaultValue = EDIT_PAGE) String mode)
            throws Exception {
        ServerBaseDto serverBaseDto = new ServerBaseDto();
        serverBaseDto.setRobotId(robotId);
        serverBaseDto.setElementType(elementType);
        serverBaseDto.setMode(mode);
        return cElementService.getAllGroupInfo(serverBaseDto);
    }
}

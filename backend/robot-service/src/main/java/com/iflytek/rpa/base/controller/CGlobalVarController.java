package com.iflytek.rpa.base.controller;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDIT_PAGE;

import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CGlobalDto;
import com.iflytek.rpa.base.service.CGlobalVarService;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.UserUtils;
import javax.annotation.Resource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

/**
 * 客户端-全局变量(CGlobalVar)表控制层
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
@RestController
@RequestMapping("/global")
public class CGlobalVarController {
    private static final Logger logger = LoggerFactory.getLogger(CGlobalVarController.class);
    /**
     * 服务对象
     */
    @Resource
    private CGlobalVarService cGlobalVarService;

    @PostMapping("/all")
    public AppResponse<?> getGlobalVarInfoList(
            @RequestParam("robotId") String robotId,
            @RequestParam(required = false, name = "mode", defaultValue = EDIT_PAGE) String mode,
            @RequestParam(required = false, name = "robotVersion") Integer robotVersion)
            throws Exception {
        BaseDto baseDto = new BaseDto();
        baseDto.setRobotId(robotId);
        baseDto.setMode(mode);
        baseDto.setRobotVersion(robotVersion);
        return cGlobalVarService.getGlobalVarInfoList(baseDto);
    }

    /**
     * 创建全局变量
     *
     * @param globalDto 全局变量信息
     * @return AppResponse
     */
    @PostMapping("/create")
    public AppResponse<?> createGlobalVar(@RequestBody CGlobalDto globalDto) throws Exception {
        if (globalDto.getRobotId() == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        return cGlobalVarService.createGlobalVar(globalDto);
    }

    /**
     * 保存全局变量
     *
     * @param globalDto 全局变量信息
     * @return AppResponse
     */
    @PostMapping("/save")
    public AppResponse<?> saveGlobalVar(@RequestBody CGlobalDto globalDto) throws Exception {
        if (globalDto.getRobotId() == null || globalDto.getGlobalId() == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        globalDto.setUpdaterId(String.valueOf(UserUtils.nowUserId()));

        return cGlobalVarService.saveGlobalVar(globalDto);
    }

    /**
     * 获取全局变量名称列表
     *
     * @param robotId 机器人ID
     * @return AppResponse
     */
    @PostMapping("/name-list")
    public AppResponse<?> getGlobalVarNameList(@RequestParam("robotId") String robotId) throws Exception {
        return cGlobalVarService.getGlobalVarNameList(robotId);
    }

    /**
     * 删除全局变量
     *
     * @param globalDto 全局变量信息
     * @return AppResponse
     */
    @PostMapping("/delete")
    public AppResponse<?> deleteGlobalVar(@RequestBody CGlobalDto globalDto) throws Exception {
        if (globalDto.getRobotId() == null || globalDto.getGlobalId() == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        return cGlobalVarService.deleteGlobalVar(globalDto);
    }
}

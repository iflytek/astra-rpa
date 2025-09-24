package com.iflytek.rpa.base.controller;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDIT_PAGE;

import com.iflytek.rpa.base.entity.CProcess;
import com.iflytek.rpa.base.entity.dto.*;
import com.iflytek.rpa.base.service.CProcessService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import java.util.Map;
import javax.annotation.Resource;
import javax.validation.Valid;
import org.apache.commons.lang3.StringUtils;
import org.springframework.web.bind.annotation.*;

/**
 * 流程数据
 *
 * @author mjren
 * @since 2024-10-09 17:11:04
 */
@RestController
@RequestMapping("/process")
public class CProcessController {
    /**
     * 服务对象
     */
    @Resource
    private CProcessService cProcessService;

    /**
     * 产生下一个流程名称
     *
     * @param processDto
     * @return
     */
    @PostMapping("/name")
    public AppResponse<String> getProcessNextName(@RequestBody NextProcessNameDto processDto) {
        // 参数校验
        if (StringUtils.isBlank(processDto.getRobotId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        return cProcessService.getProcessNextName(processDto.getRobotId());
    }

    @PostMapping("/create")
    public AppResponse<Map> createNewProcess(@RequestBody CreateProcessDto processDto) throws NoLoginException {
        if (StringUtils.isBlank(processDto.getRobotId()) || StringUtils.isBlank(processDto.getProcessName())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String name = processDto.getProcessName().trim();
        if (StringUtils.isBlank(name)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "流程名称不能为空格");
        }
        processDto.setProcessName(name);
        return cProcessService.createNewProcess(processDto);
    }

    @PostMapping("/rename")
    public AppResponse<Boolean> renameProcess(@RequestBody RenameProcessDto processDto) throws NoLoginException {
        if (StringUtils.isBlank(processDto.getProcessId()) || StringUtils.isBlank(processDto.getProcessName())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String name = processDto.getProcessName().trim();
        if (StringUtils.isBlank(name)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "流程名称不能为空格");
        }
        processDto.setProcessName(name);
        return cProcessService.renameProcess(processDto);
    }

    /**
     * 查询机器人的所有流程数据
     *
     * @param process
     * @return
     * @throws Exception
     */
    @PostMapping("/all-data")
    public AppResponse<?> getAllProcessData(@RequestBody CProcess process) throws Exception {
        process.setRobotVersion(0);
        return cProcessService.getAllProcessData(process);
    }

    /**
     * 更新流程数据
     *
     * @param process
     * @return
     * @throws Exception
     */
    @PostMapping("/save")
    public AppResponse<?> saveProcessContent(@RequestBody CProcessDto process) throws Exception {
        if (StringUtils.isBlank(process.getRobotId()) || StringUtils.isBlank(process.getProcessId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        process.setRobotVersion(0);
        return cProcessService.saveProcessContent(process);
    }

    /**
     * 查询流程数据
     *
     * @param baseDto
     * @return
     * @throws Exception
     */
    @PostMapping("/process-json")
    public AppResponse<?> getProcessDataByProcessId(@RequestBody @Valid BaseDto baseDto) throws Exception {
        if (StringUtils.isBlank(baseDto.getProcessId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        return cProcessService.getProcessDataByProcessId(baseDto);
    }

    /**
     * 查询流程名称列表
     *
     * @param robotId
     * @param mode
     * @return
     * @throws Exception
     */
    @PostMapping("/name-list")
    public AppResponse<?> getProcessNameList(
            @RequestParam("robotId") String robotId,
            @RequestParam(required = false, name = "mode", defaultValue = EDIT_PAGE) String mode,
            @RequestParam(required = false, name = "robotVersion") Integer robotVersion)
            throws Exception {
        BaseDto baseDto = new BaseDto();
        baseDto.setRobotId(robotId);
        baseDto.setMode(mode);
        baseDto.setRobotVersion(robotVersion);
        return cProcessService.getProcessNameList(baseDto);
    }

    /**
     * 复制子流程
     *
     * @return
     * @throws Exception
     */
    @PostMapping("/copy")
    public AppResponse<?> copySubProcess(
            @RequestParam("robotId") String robotId,
            @RequestParam("processId") String processId,
            @RequestParam("type") String type)
            throws Exception {

        return cProcessService.copySubProcess(robotId, processId, type);
    }

    /**
     * 删除指定流程
     *
     * @param processDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/delete")
    public AppResponse<Boolean> deleteProcess(@RequestBody CProcessDto processDto) throws NoLoginException {
        if (StringUtils.isBlank(processDto.getProcessId())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        return cProcessService.deleteProcess(processDto);
    }
}

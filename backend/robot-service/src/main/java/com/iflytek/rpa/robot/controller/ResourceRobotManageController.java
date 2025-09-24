package com.iflytek.rpa.robot.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.robot.entity.dto.*;
import com.iflytek.rpa.robot.entity.vo.*;
import com.iflytek.rpa.robot.service.ResourceRobotManageService;
import com.iflytek.rpa.robot.service.RobotExecuteService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.DateUtils;
import java.io.IOException;
import java.util.Date;
import java.util.List;
import java.util.Objects;
import javax.annotation.Resource;
import javax.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.util.CollectionUtils;
import org.springframework.web.bind.annotation.*;

/**
 * 资源管理 - 机器人管理
 *
 * @author jqfang3
 * @since 2025-07-01
 */
@RestController
@RequestMapping("/robot-manage")
public class ResourceRobotManageController {
    @Resource
    private ResourceRobotManageService resourceRobotManageService;

    @Autowired
    private RobotExecuteService robotExecuteService;

    /**
     * 机器人管理 - 列表
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/robot-page-list")
    public AppResponse<IPage<RobotPageListVo>> getRobotPageList(@RequestBody RobotPageListDto queryDto)
            throws NoLoginException, IOException {
        paramCheck(queryDto);
        return resourceRobotManageService.getRobotPageList(queryDto);
    }

    private void paramCheck(RobotPageListDto queryDto) {
        createTimeCheck(queryDto);
        latestReleaseTimeCheck(queryDto);
    }

    private void createTimeCheck(RobotPageListDto queryDto) {
        Date createTimeStart = queryDto.getCreateTimeStart();
        Date createTimeEnd = queryDto.getCreateTimeEnd();
        if (createTimeStart == null && createTimeEnd != null)
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "创建时间区间参数异常");
        if (createTimeStart != null && createTimeEnd == null)
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "创建时间区间参数异常");
        if (createTimeStart != null && createTimeStart.after(createTimeEnd)) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode());
        }
        if (createTimeEnd != null) {
            queryDto.setCreateTimeEnd(DateUtils.getEndOfDay(createTimeEnd));
        }
    }

    private void latestReleaseTimeCheck(RobotPageListDto queryDto) {
        Date startTime = queryDto.getLatestReleaseTimeStart();
        Date endTime = queryDto.getLatestReleaseTimeEnd();
        if (startTime != null && endTime == null)
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "更新时间区间参数异常");
        if (startTime == null && endTime != null)
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "更新时间区间参数异常");
        if (startTime != null && startTime.after(endTime))
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode());
        if (endTime != null) {
            queryDto.setLatestReleaseTimeEnd(DateUtils.getEndOfDay(endTime));
        }
    }

    /**
     * 机器人管理 - 删除前检查
     *
     * @param dto
     * @return
     * @throws Exception
     */
    @PostMapping("/delete-robot-check")
    public AppResponse<DelResourceRobotVo> deleteRobotCheck(@RequestBody RobotDeleteCheckDto dto) throws Exception {
        return resourceRobotManageService.deleteRobotCheck(dto);
    }

    /**
     * 机器人管理 - 删除机器人
     *
     * @param dto
     * @return
     * @throws Exception
     */
    @PostMapping("/delete-robot")
    public AppResponse<String> deleteRobot(@RequestBody RobotDeleteDto dto) throws Exception {
        return resourceRobotManageService.deleteRobot(dto);
    }

    /**
     * 卓越中心-资源管理-机器人转移
     */
    @PostMapping("/transfer")
    public AppResponse<?> transferRobot(@RequestBody @Valid TransferRobotDto transferRobotDto) throws Exception {
        if (CollectionUtils.isEmpty(transferRobotDto.getRobotIdList())) {
            return AppResponse.success("转移成功");
        }
        List<String> robotIdList = transferRobotDto.getRobotIdList();
        robotIdList.removeIf(Objects::isNull);
        if (CollectionUtils.isEmpty(robotIdList)) {
            return AppResponse.success("转移成功");
        }
        return robotExecuteService.transferRobot(transferRobotDto);
    }

    /**
     * 获取机器人基本信息
     *
     * @param robotId 机器人ID
     */
    @PostMapping("/robot-baseinfo")
    public AppResponse<MyRobotDetailVo> getRobotBaseInfo(@RequestParam("robotId") String robotId) throws Exception {
        return resourceRobotManageService.getRobotBaseInfo(robotId);
    }

    /**
     * 获取机器人版本列表
     *
     * @param robotId 机器人ID
     */
    @PostMapping("/robot-versions")
    public AppResponse<ResourceVersionListVo> getRobotVersions(@RequestParam("robotId") String robotId)
            throws Exception {
        return resourceRobotManageService.getRobotVersions(robotId);
    }

    /**
     * 获取执行记录列表
     *
     * @param queryDto 查询条件
     * @throws Exception 异常
     */
    @PostMapping("/record-baseinfo")
    public AppResponse<IPage<RecordBaseInfoVo>> getRecordBaseInfo(@RequestBody ExecuteRecordPageDto queryDto)
            throws Exception {
        return resourceRobotManageService.getRecordBaseInfo(queryDto);
    }

    /**
     * 获取执行记录日志
     *
     * @param robotId   机器人ID
     * @param executeId 执行ID
     */
    @PostMapping("/record-log")
    public AppResponse<RecordLogVo> getRecordLog(
            @RequestParam("robotId") String robotId, @RequestParam("executeId") String executeId) throws Exception {
        return resourceRobotManageService.getRecordLog(robotId, executeId);
    }
}

package com.iflytek.rpa.robot.controller;

import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.EnableVersionDto;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import com.iflytek.rpa.robot.entity.dto.VersionListDto;
import com.iflytek.rpa.robot.service.RobotVersionService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import javax.annotation.Resource;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.*;

/**
 * 云端机器人版本表(RobotVersion)表控制层
 *
 * @author makejava
 * @since 2024-09-29 15:27:41
 */
@RestController
@RequestMapping("/robot-version")
public class RobotVersionController {

    /**
     * 服务对象
     */
    @Resource
    private RobotVersionService robotVersionService;

    /**
     * 机器人发版-重名校验
     *
     * @param robotVersionDto
     * @return
     * @throws Exception
     */
    @PostMapping("/same-name")
    public AppResponse<?> checkSameName(@RequestBody RobotVersionDto robotVersionDto) throws Exception {
        return robotVersionService.checkSameName(robotVersionDto);
    }

    /**
     * 机器人发版
     *
     * @param robotVersionDto
     * @return
     * @throws Exception
     */
    @PostMapping("/publish")
    public AppResponse<?> publishRobot(@Valid @RequestBody RobotVersionDto robotVersionDto) throws Exception {

        return robotVersionService.publishRobot(robotVersionDto);
    }

    /**
     * 机器人发版-上次发版信息回显
     *
     * @param robotVersion
     * @return
     */
    @PostMapping("/latest-info")
    public AppResponse<?> getRobotVersionInfo(@RequestBody RobotVersion robotVersion) throws NoLoginException {
        return robotVersionService.getLastRobotVersionInfo(robotVersion);
    }

    /**
     * 执行器里查询指定机器人所有版本
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/list4Execute")
    public AppResponse<?> list4Execute(VersionListDto queryDto) throws NoLoginException {
        return robotVersionService.versionList(queryDto);
    }

    /**
     * 启用指定版本
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/enable-version")
    public AppResponse<?> enableVersion(@RequestBody EnableVersionDto queryDto) throws Exception {
        return robotVersionService.enableVersion(queryDto);
    }

    /**
     * 恢复指定版本
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/recover-version")
    public AppResponse<?> recoverVersion(@RequestBody EnableVersionDto queryDto) throws Exception {
        return robotVersionService.recoverVersion(queryDto);
    }

    /**
     * 设计器版本管理列表
     *
     * @param robotId
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/list4Design")
    public AppResponse<?> list4Design(@RequestParam String robotId) throws NoLoginException {
        return robotVersionService.list4Design(robotId);
    }
}

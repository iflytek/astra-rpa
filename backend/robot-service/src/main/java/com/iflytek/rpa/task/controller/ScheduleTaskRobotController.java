package com.iflytek.rpa.task.controller;

import com.iflytek.rpa.task.service.ScheduleTaskRobotService;
import javax.annotation.Resource;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 计划任务机器人列表(ScheduleTaskRobot)表控制层
 *
 * @author mjren
 * @since 2024-10-15 14:59:09
 */
@RestController
@RequestMapping("scheduleTaskRobot")
public class ScheduleTaskRobotController {
    /**
     * 服务对象
     */
    @Resource
    private ScheduleTaskRobotService scheduleTaskRobotService;
}

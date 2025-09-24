package com.iflytek.rpa.task.service;

import com.iflytek.rpa.task.entity.ScheduleTaskRobot;

/**
 * 计划任务机器人列表(ScheduleTaskRobot)表服务接口
 *
 * @author mjren
 * @since 2024-10-15 14:59:09
 */
public interface ScheduleTaskRobotService {

    /**
     * 通过ID查询单条数据
     *
     * @param id 主键
     * @return 实例对象
     */
    ScheduleTaskRobot queryById(Long id);
}

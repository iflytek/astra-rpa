package com.iflytek.rpa.task.service.impl;

import com.iflytek.rpa.task.dao.ScheduleTaskRobotDao;
import com.iflytek.rpa.task.entity.ScheduleTaskRobot;
import com.iflytek.rpa.task.service.ScheduleTaskRobotService;
import javax.annotation.Resource;
import org.springframework.stereotype.Service;

/**
 * 计划任务机器人列表(ScheduleTaskRobot)表服务实现类
 *
 * @author mjren
 * @since 2024-10-15 14:59:09
 */
@Service("scheduleTaskRobotService")
public class ScheduleTaskRobotServiceImpl implements ScheduleTaskRobotService {
    @Resource
    private ScheduleTaskRobotDao scheduleTaskRobotDao;

    /**
     * 通过ID查询单条数据
     *
     * @param id 主键
     * @return 实例对象
     */
    @Override
    public ScheduleTaskRobot queryById(Long id) {
        return this.scheduleTaskRobotDao.queryById(id);
    }
}

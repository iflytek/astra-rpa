package com.iflytek.rpa.task.dao;

import com.iflytek.rpa.task.entity.ScheduleTask;
import org.apache.ibatis.annotations.Mapper;

/**
 * (ScheduleTaskPullLog)表数据库访问层
 *
 * @author mjren
 * @since 2024-11-18 14:13:21
 */
@Mapper
public interface ScheduleTaskPullLogDao {

    Integer insetLog(ScheduleTask task);
}

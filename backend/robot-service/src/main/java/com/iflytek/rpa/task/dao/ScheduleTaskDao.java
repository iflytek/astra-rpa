package com.iflytek.rpa.task.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.task.entity.ScheduleTask;
import com.iflytek.rpa.task.entity.dto.TaskDto;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface ScheduleTaskDao extends BaseMapper<ScheduleTask> {

    IPage<ScheduleTask> getTaskList(IPage<ScheduleTask> pageConfig, @Param("entity") TaskDto taskDto);

    Integer createScheduleTask(ScheduleTask scheduleTask);

    Integer updateScheduleTask(ScheduleTask scheduleTask);

    Integer queryCountByTaskId(@Param("taskId") String taskId);

    ScheduleTask getTaskInfoByTaskId(
            @Param("taskId") String taskId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    ScheduleTask getTaskListOrderByNextTime(@Param("userId") String userId, @Param("tenantId") String tenantId);

    Integer updateTask(ScheduleTask task);

    Integer countByTaskName(ScheduleTask task);

    Integer countTaskTotal(@Param("userId") String userId, @Param("tenantId") String tenantId);

    List<ScheduleTask> getTaskListByPage(@Param("userId") String userId, @Param("tenantId") String tenantId);

    String getTaskNameByTaskExecuteId(String taskExecuteId);
}

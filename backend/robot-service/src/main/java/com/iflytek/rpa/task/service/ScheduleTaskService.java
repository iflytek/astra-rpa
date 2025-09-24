package com.iflytek.rpa.task.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.task.entity.ScheduleTask;
import com.iflytek.rpa.task.entity.dto.ScheduleTaskDto;
import com.iflytek.rpa.task.entity.dto.TaskDto;

/**
 * <p>
 * 调度任务 服务类
 * </p>
 *
 * @author keler
 * @since 2021-10-08
 */
public interface ScheduleTaskService extends IService<ScheduleTask> {

    AppResponse<?> getTaskList(TaskDto taskDto) throws NoLoginException;

    AppResponse<?> saveTask(ScheduleTaskDto task) throws NoLoginException;

    AppResponse<?> getTaskInfoByTaskId(String taskId) throws NoLoginException;

    AppResponse<?> getNextTimeInfoAndUpdate() throws NoLoginException;

    AppResponse<?> enableTask(ScheduleTask task);

    AppResponse<?> deleteTask(ScheduleTask task);

    AppResponse<?> checkSameName(ScheduleTask task);

    AppResponse<?> checkCorn(ScheduleTask task);
}

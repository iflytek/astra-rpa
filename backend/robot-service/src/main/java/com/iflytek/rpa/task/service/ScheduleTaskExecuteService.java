package com.iflytek.rpa.task.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.task.entity.dto.ScheduleTaskRecordDeleteDto;
import com.iflytek.rpa.task.entity.dto.ScheduleTaskRecordDto;
import com.iflytek.rpa.task.entity.dto.TaskExecuteDto;
import com.iflytek.rpa.task.entity.vo.TaskRecordListVo;

/**
 * 计划任务执行记录(ScheduleTaskExecute)表服务接口
 *
 * @author mjren
 * @since 2024-10-15 14:59:09
 */
public interface ScheduleTaskExecuteService {

    AppResponse<?> setTaskExecuteStatus(TaskExecuteDto executeDto) throws NoLoginException;

    AppResponse<?> getTaskExecuteRecordList(TaskExecuteDto executeDto) throws NoLoginException;

    AppResponse<IPage<TaskRecordListVo>> getRecordList(ScheduleTaskRecordDto recordDto) throws NoLoginException;

    AppResponse<?> batchDelete(ScheduleTaskRecordDeleteDto taskExecuteIdList) throws NoLoginException;
}

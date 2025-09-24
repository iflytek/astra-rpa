package com.iflytek.rpa.triggerTask.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.triggerTask.entity.dto.InsertTaskDto;
import com.iflytek.rpa.triggerTask.entity.dto.TaskPageDto;
import com.iflytek.rpa.triggerTask.entity.dto.UpdateTaskDto;
import com.iflytek.rpa.triggerTask.entity.vo.Executor;
import com.iflytek.rpa.triggerTask.entity.vo.TaskPage4TriggerVo;
import com.iflytek.rpa.triggerTask.entity.vo.TaskPageVo;
import com.iflytek.rpa.triggerTask.entity.vo.TriggerTaskVo;
import java.util.List;

public interface TriggerTaskService {

    AppResponse<Boolean> isTaskNameCopy(String name) throws NoLoginException;

    AppResponse<List<Executor>> getRobotExeList(String name) throws NoLoginException, JsonProcessingException;

    List<String> getUsingTasksByMail(String mailId);

    AppResponse<Boolean> insertTriggerTask(InsertTaskDto queryDto) throws NoLoginException;

    AppResponse<TriggerTaskVo> getTriggerTask(String taskId) throws NoLoginException, JsonProcessingException;

    AppResponse<Boolean> deleteTriggerTask(String taskId) throws NoLoginException;

    AppResponse<Boolean> updateTriggerTask(UpdateTaskDto queryDto) throws NoLoginException;

    AppResponse<Boolean> enableTriggerTask(String taskId, Integer enable) throws NoLoginException;

    AppResponse<IPage<TaskPageVo>> triggerTaskPage(TaskPageDto queryDto) throws NoLoginException;

    AppResponse<IPage<TaskPage4TriggerVo>> triggerTaskPage4Trigger(TaskPageDto queryDto) throws NoLoginException;
}

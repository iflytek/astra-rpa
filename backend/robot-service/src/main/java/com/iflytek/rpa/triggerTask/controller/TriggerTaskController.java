package com.iflytek.rpa.triggerTask.controller;

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
import com.iflytek.rpa.triggerTask.service.TriggerTaskService;
import java.util.List;
import javax.annotation.Resource;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/triggerTask")
public class TriggerTaskController {

    @Resource
    private TriggerTaskService triggerTaskService;

    /**
     * 重命名校验
     *
     * @param name
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/isNameCopy")
    AppResponse<Boolean> isTaskNameCopy(@RequestParam String name) throws NoLoginException {
        return triggerTaskService.isTaskNameCopy(name);
    }

    /**
     * 选择机器人-机器人列表，支持模糊查询
     *
     * @param name
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/robotExe/list")
    AppResponse<List<Executor>> getRobotExeList(@RequestParam String name)
            throws NoLoginException, JsonProcessingException {
        return triggerTaskService.getRobotExeList(name);
    }

    /**
     * 新建计划任务
     * 同时插入计划任务相关param参数 到schedule_task_robot
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/insert")
    AppResponse<Boolean> insertTriggerTask(@Valid @RequestBody InsertTaskDto queryDto) throws NoLoginException {
        return triggerTaskService.insertTriggerTask(queryDto);
    }

    /**
     * 计划任务-编辑-任务信息回显
     *
     * @param taskId
     * @return
     */
    @GetMapping("/get")
    AppResponse<TriggerTaskVo> getTriggerTask(@RequestParam String taskId)
            throws NoLoginException, JsonProcessingException {
        return triggerTaskService.getTriggerTask(taskId);
    }

    /**
     * 删除单个计划任务接口
     *
     * @param taskId
     * @return
     */
    @GetMapping("/delete")
    AppResponse<Boolean> deleteTriggerTask(@RequestParam String taskId) throws NoLoginException {
        return triggerTaskService.deleteTriggerTask(taskId);
    }

    /**
     * 更新计划任务及配置参数
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/update")
    AppResponse<Boolean> updateTriggerTask(@Valid @RequestBody UpdateTaskDto queryDto) throws NoLoginException {
        return triggerTaskService.updateTriggerTask(queryDto);
    }

    /**
     * 启用，禁用计划任务接口
     *
     * @param taskId
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/enable")
    AppResponse<Boolean> enableTriggerTask(String taskId, Integer enable) throws NoLoginException {
        return triggerTaskService.enableTriggerTask(taskId, enable);
    }

    /**
     * 计划任务列表分页查询接口 - 前端请求
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/page/list")
    AppResponse<IPage<TaskPageVo>> triggerTaskPage(@Valid @RequestBody TaskPageDto queryDto) throws NoLoginException {
        return triggerTaskService.triggerTaskPage(queryDto);
    }

    /**
     * 计划任务列表分页查询接口 - 本地触发器请求(pageSize 设置为100条即可)
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/page/list4Trigger")
    AppResponse<IPage<TaskPage4TriggerVo>> triggerTaskPage4Trigger(@Valid @RequestBody TaskPageDto queryDto)
            throws NoLoginException {
        return triggerTaskService.triggerTaskPage4Trigger(queryDto);
    }
}

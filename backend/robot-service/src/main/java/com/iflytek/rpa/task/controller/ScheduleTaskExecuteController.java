package com.iflytek.rpa.task.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.task.entity.dto.ScheduleTaskRecordDeleteDto;
import com.iflytek.rpa.task.entity.dto.ScheduleTaskRecordDto;
import com.iflytek.rpa.task.entity.dto.TaskExecuteDto;
import com.iflytek.rpa.task.entity.vo.TaskRecordListVo;
import com.iflytek.rpa.task.service.ScheduleTaskExecuteService;
import javax.annotation.Resource;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 计划任务执行记录
 *
 * @author mjren
 * @since 2024-10-15 14:59:09
 */
@RestController
@RequestMapping("/task-execute")
public class ScheduleTaskExecuteController {
    /**
     * 服务对象
     */
    @Resource
    private ScheduleTaskExecuteService scheduleTaskExecuteService;

    /**
     * 计划任务-执行状态上报
     *
     * @param executeDto
     * @return String
     * @throws NoLoginException
     */
    @PostMapping("/status")
    public AppResponse<?> setTaskExecuteResult(@RequestBody TaskExecuteDto executeDto) throws NoLoginException {
        return scheduleTaskExecuteService.setTaskExecuteStatus(executeDto);
    }

    /**
     * 计划任务-执行记录列表
     *
     * @param executeDto
     * @return
     * @throws NoLoginException
     */
    /*    @PostMapping("/list")
    public AppResponse<?> getTaskExecuteRecordList(@Valid @RequestBody TaskExecuteDto executeDto) throws NoLoginException {
        return scheduleTaskExecuteService.getTaskExecuteRecordList(executeDto);
    }*/

    /**
     * 计划任务执行记录
     *
     * @param recordDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/list")
    public AppResponse<IPage<TaskRecordListVo>> getRecordList(@RequestBody ScheduleTaskRecordDto recordDto)
            throws NoLoginException {
        return scheduleTaskExecuteService.getRecordList(recordDto);
    }

    /**
     * 批量删除计划任务执行记录
     *
     * @param dto 包含要删除的任务执行ID列表
     * @return 删除结果
     * @throws NoLoginException
     */
    @PostMapping("/batch-delete")
    public AppResponse<?> batchDelete(@RequestBody ScheduleTaskRecordDeleteDto dto) throws NoLoginException {
        return scheduleTaskExecuteService.batchDelete(dto);
    }
}

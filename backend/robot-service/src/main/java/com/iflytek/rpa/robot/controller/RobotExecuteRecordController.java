package com.iflytek.rpa.robot.controller;

import com.iflytek.rpa.robot.entity.dto.ExecuteRecordDto;
import com.iflytek.rpa.robot.entity.dto.RobotExecuteRecordsBatchDeleteDto;
import com.iflytek.rpa.robot.service.RobotExecuteRecordService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 云端机器人执行记录表(RobotExecute)表控制层
 *
 * @author makejava
 * @since 2024-09-29 15:27:41
 */
@RestController
@RequestMapping("/robot-record")
public class RobotExecuteRecordController {

    @Autowired
    private RobotExecuteRecordService robotExecuteRecordService;

    /**
     * 执行记录列表
     *
     * @param recordDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/list")
    public AppResponse<?> recordList(@RequestBody ExecuteRecordDto recordDto) throws NoLoginException {
        return robotExecuteRecordService.recordList(recordDto);
    }

    /**
     * 查询执行日志
     *
     * @param recordDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/log")
    public AppResponse<?> getExecuteLog(@RequestBody ExecuteRecordDto recordDto) throws NoLoginException {
        return robotExecuteRecordService.getExecuteLog(recordDto);
    }

    // todo:0920
    //    /**
    //     * 执行器-机器人详情-执行概况
    //     * @paramMarketResourceDto
    //     * @return
    //     * @throws Exception
    //     */
    //    @PostMapping("/detail/overview")
    //    public AppResponse<?> getOverViewData(@RequestBody RobotMonitorDto robotMonitorDto){
    //        return robotExecuteRecordService.robotOverview(robotMonitorDto);
    //    }

    /**
     * 上传机器人执行结果
     *
     * @param recordDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/save-result")
    public AppResponse<?> saveExecuteResult(@RequestBody ExecuteRecordDto recordDto) throws NoLoginException {
        String currentRobotId = recordDto.getRobotId();
        return robotExecuteRecordService.saveExecuteResult(recordDto, currentRobotId);
    }

    /**
     * 上传机器人执行日志
     * @param recordDto
     * @return
     * @throws NoLoginException
     */
    //    @PostMapping("/save-log")
    //    public AppResponse<?> saveExecuteLog(@RequestBody ExecuteRecordDto recordDto) throws NoLoginException {
    //        return robotExecuteRecordService.saveExecuteLog(recordDto);
    //    }

    /**
     * 批量删除机器人执行记录
     *
     * @param batchDeleteDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/delete-robot-execute-records")
    public AppResponse<String> deleteRobotExecuteRecords(@RequestBody RobotExecuteRecordsBatchDeleteDto batchDeleteDto)
            throws NoLoginException {
        return robotExecuteRecordService.deleteRobotExecuteRecords(batchDeleteDto);
    }
}

package com.iflytek.rpa.robot.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.iflytek.rpa.robot.entity.RobotExecuteRecord;
import com.iflytek.rpa.robot.entity.dto.ExecuteRecordDto;
import com.iflytek.rpa.robot.entity.dto.RobotExecuteRecordsBatchDeleteDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;

/**
 * 云端机器人执行记录表(RobotExecute)表服务接口
 *
 * @author makejava
 * @since 2024-09-29 15:27:41
 */
public interface RobotExecuteRecordService extends IService<RobotExecuteRecord> {

    AppResponse<?> recordList(ExecuteRecordDto recordDto) throws NoLoginException;

    AppResponse<?> getExecuteLog(ExecuteRecordDto recordDto) throws NoLoginException;

    AppResponse<?> saveExecuteResult(ExecuteRecordDto recordDto, String currentRobotId) throws NoLoginException;

    Integer countRobotTotalNumOfExecuted(List<String> startAndEndOfDay, String lastProcessedId);

    Integer countTerminalTotalNumOfExecuted(List<String> startAndEndOfDay, String lastProcessedId);

    List<RobotExecuteRecord> getExecutedRobotByPage(
            List<String> startAndEndOfDay, String lastProcessedId, Integer limit, Integer offset);

    AppResponse<String> deleteRobotExecuteRecords(RobotExecuteRecordsBatchDeleteDto batchDeleteDto)
            throws NoLoginException;
}

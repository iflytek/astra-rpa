package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.robot.entity.RobotExecuteRecord;
import com.iflytek.rpa.robot.entity.dto.ExecuteRecordDto;
import com.iflytek.rpa.robot.entity.dto.ExecuteRecordPageDto;
import com.iflytek.rpa.robot.entity.vo.RecordBaseInfoVo;
import com.iflytek.rpa.robot.entity.vo.RecordLogVo;
import com.iflytek.rpa.robot.entity.vo.RobotExecutionData;
import java.util.Date;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 云端机器人执行记录表(RobotExecute)表数据库访问层
 *
 * @author makejava
 * @since 2024-09-29 15:27:41
 */
@Mapper
public interface RobotExecuteRecordDao extends BaseMapper<RobotExecuteRecord> {

    IPage<RobotExecuteRecord> getExecuteRecordList(
            IPage<RobotExecuteRecord> pageConfig, @Param("entity") ExecuteRecordDto recordDto);

    List<RobotExecuteRecord> getRecordByExecuteIdList(@Param("executeIdList") List<String> executeIdList);

    RobotExecutionData robotOverviewWithoutVersion(
            @Param("tenantId") String tenantId, @Param("robotId") String robotId, @Param("countTime") Date countTime);

    String getExecuteLog(ExecuteRecordDto recordDto);

    RobotExecuteRecord getExecuteRecord(ExecuteRecordDto recordDto);

    @Select("select creator_id, start_time, execute_time, result, robot_version, execute_id "
            + "from robot_execute_record "
            + "where robot_id = #{queryDto.robotId} and tenant_id = #{tenantId} and deleted = 0")
    IPage<RecordBaseInfoVo> getRecordBaseInfoPage(
            IPage<RecordBaseInfoVo> pageConfig, ExecuteRecordPageDto queryDto, String tenantId);

    @Select("select execute_log " + "from robot_execute_record "
            + "where robot_id = #{robotId} and execute_id = #{executeId} and tenant_id = #{tenantId} and deleted = 0")
    RecordLogVo getRecordLog(String robotId, String executeId, String tenantId);

    Integer insertExecuteRecord(ExecuteRecordDto recordDto);

    Integer updateExecuteRecord(ExecuteRecordDto recordDto);

    @Update("update robot_execute_record " + "set deleted = 1 "
            + "where robot_id = #{robotId} and creator_id = #{userId} and tenant_id = #{tenantId} and deleted = 0")
    Integer deleteRecord(
            @Param("tenantId") String tenantId, @Param("robotId") String robotId, @Param("userId") String userId);

    /**
     * 批量删除机器人执行记录（基于taskExecuteId）
     *
     * @param taskExecuteIdList 任务执行ID列表
     * @param userId            用户ID
     * @param tenantId          租户ID
     * @return 删除的记录数
     */
    Integer batchDeleteByTaskExecuteIds(
            @Param("taskExecuteIdList") List<String> taskExecuteIdList,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    Integer countRobotTotalNumOfExecuted(
            @Param("startAndEndOfDay") List<String> startAndEndOfDay, @Param("lastProcessedId") String lastProcessedId);

    Integer countTerminalTotalNumOfExecuted(
            @Param("startAndEndOfDay") List<String> startAndEndOfDay, @Param("lastProcessedId") String lastProcessedId);

    List<RobotExecuteRecord> getExecutedRobotByPage(
            @Param("startAndEndOfDay") List<String> startAndEndOfDay,
            @Param("lastProcessedId") String lastProcessedId,
            @Param("limit") Integer limit,
            @Param("offset") Integer offset);

    int deleteRobotExecuteRecords(List<String> recordsIds, String userId, String tenantId);
}

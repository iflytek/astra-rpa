package com.iflytek.rpa.task.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.task.entity.ScheduleTaskExecute;
import com.iflytek.rpa.task.entity.dto.ScheduleTaskRecordDto;
import com.iflytek.rpa.task.entity.dto.TaskExecuteDto;
import com.iflytek.rpa.task.entity.vo.TaskRecordListVo;
import java.util.Date;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 计划任务执行记录(ScheduleTaskExecute)表数据库访问层
 *
 * @author mjren
 * @since 2024-10-15 14:59:09
 */
@Mapper
public interface ScheduleTaskExecuteDao extends BaseMapper<ScheduleTaskExecute> {

    void insertExecuteRecord(ScheduleTaskExecute scheduleTaskExecute);

    Integer countExecuteRecord(@Param("taskExecuteId") String executeId);

    Integer getMaxBatch(@Param("taskId") String taskId);

    Integer updateExecuteStatus(@Param("entity") TaskExecuteDto taskExecuteDto);

    IPage<TaskExecuteDto> getTaskExecuteRecordList(
            IPage<TaskExecuteDto> pageConfig, @Param("entity") TaskExecuteDto executeDto);

    /**
     * 分页查询计划任务执行记录列表
     *
     * @param pageConfig 分页配置
     * @param recordDto  查询参数
     * @return 分页结果
     */
    IPage<TaskRecordListVo> getTaskRecordList(
            IPage<TaskRecordListVo> pageConfig, @Param("dto") ScheduleTaskRecordDto recordDto);

    /**
     * 批量逻辑删除计划任务执行记录
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

    /**
     * 查询超时的执行记录
     * 获取状态为executing且开始时间早于指定时间点的记录
     *
     * @param timeoutTime 超时时间点
     * @return 超时的执行记录列表
     */
    List<ScheduleTaskExecute> getTimeoutExecutingRecords(@Param("timeoutTime") Date timeoutTime);

    /**
     * 根据ID列表更新执行记录为取消状态
     *
     * @param idList 记录ID列表
     * @return 更新的记录数
     */
    Integer updateExecutingRecordsToCancelByIds(@Param("idList") List<Long> idList);
}

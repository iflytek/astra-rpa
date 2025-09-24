package com.iflytek.rpa.triggerTask.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.triggerTask.entity.TriggerTask;
import com.iflytek.rpa.triggerTask.entity.dto.TaskPageDto;
import com.iflytek.rpa.triggerTask.entity.vo.TaskPage4TriggerVo;
import com.iflytek.rpa.triggerTask.entity.vo.TaskPageVo;
import java.util.List;
import java.util.Set;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface TriggerTaskDao extends BaseMapper<TriggerTask> {
    @Select("select name " + "from trigger_task "
            + "where deleted=0 and creator_id = #{userId} and tenant_id = #{tenantId} ")
    List<String> getAllTaskName(@Param("userId") String userId, @Param("tenantId") String tenantId);

    @Update("update trigger_task " + "set enable = #{enable} "
            + "where deleted=0 and creator_id = #{userId} and tenant_id = #{tenantId} and task_id = #{taskId}")
    Boolean enableTask(
            @Param("userId") String userId,
            @Param("tenantId") String tenantId,
            @Param("taskId") String taskId,
            @Param("enable") Integer enable);

    @Select("select * " + "from trigger_task "
            + "where deleted=0 and creator_id = #{userId} and tenant_id = #{tenantId} and task_id = #{taskId} "
            + "limit 1")
    TriggerTask getTaskById(
            @Param("userId") String userId, @Param("tenantId") String tenantId, @Param("taskId") String taskId);

    @Update("update trigger_task " + "set deleted = 1 "
            + "where creator_id = #{userId} and tenant_id = #{tenantId} and task_id = #{taskId}")
    Integer deleteTaskById(
            @Param("userId") String userId, @Param("tenantId") String tenantId, @Param("taskId") String taskId);

    IPage<TaskPageVo> getExecuteDataList(
            IPage<TaskPageVo> page,
            @Param("queryDto") TaskPageDto queryDto,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    IPage<TaskPage4TriggerVo> getExecuteDataList4Trigger(
            IPage<TaskPage4TriggerVo> page,
            @Param("queryDto") TaskPageDto queryDto,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    Integer deleteTasks(@Param("taskIdList") Set<String> taskIdList);
}

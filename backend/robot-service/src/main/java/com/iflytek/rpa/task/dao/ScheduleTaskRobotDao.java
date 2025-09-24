package com.iflytek.rpa.task.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.dto.TaskRobotCountDto;
import com.iflytek.rpa.task.entity.ScheduleTaskRobot;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

/**
 * 计划任务机器人列表(ScheduleTaskRobot)表数据库访问层
 *
 * @author mjren
 * @since 2024-10-15 14:59:09
 */
@Mapper
public interface ScheduleTaskRobotDao extends BaseMapper<ScheduleTaskRobot> {

    Integer deleteByTaskId(@Param("taskId") String taskId);

    Integer deleteByTaskIdLogically(@Param("taskId") String taskId);

    List<String> queryHisRobotIdListByTaskId(@Param("taskId") String taskId);

    List<ScheduleTaskRobot> queryAllByTaskId(@Param("taskIdList") List<String> taskIdList);

    List<ScheduleTaskRobot> queryAll(@Param("taskIdList") List<String> taskIdList);

    void insertRobotBatch(@Param("taskId") String taskId, @Param("entities") List<ScheduleTaskRobot> entities);

    List<String> queryRobotIdListByTaskId(@Param("taskId") String taskId);

    /**
     * 通过ID查询单条数据
     *
     * @param id 主键
     * @return 实例对象
     */
    ScheduleTaskRobot queryById(Long id);

    @Select("select * " + "from schedule_task_robot "
            + "where deleted = 0 and creator_id = #{userId} and tenant_id = #{tenantId} and robot_id = #{robotId}")
    List<ScheduleTaskRobot> getAllTaskRobot(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    List<ScheduleTaskRobot> getScheduleRobotByTaskIds(@Param("taskIdList") List<String> taskIdList);

    Integer taskRobotDelete(
            @Param("robotId") String robotId,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId,
            @Param("taskIdList") List<String> taskIdList);

    List<TaskRobotCountDto> taskRobotCount(@Param("taskIdList") List<String> taskIdList);

    List<ScheduleTaskRobot> queryByTaskId(
            @Param("taskId") String taskId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    List<ScheduleTaskRobot> getAllTaskRobotByList(
            @Param("list") List<RobotExecute> list, @Param("tenantId") String tenantId);
}

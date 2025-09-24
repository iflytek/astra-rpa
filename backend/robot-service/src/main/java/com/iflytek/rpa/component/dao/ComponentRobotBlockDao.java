package com.iflytek.rpa.component.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.component.entity.ComponentRobotBlock;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 机器人对组件屏蔽表(ComponentRobotBlock)表数据库访问层
 *
 * @author makejava
 * @since 2024-12-19
 */
@Mapper
public interface ComponentRobotBlockDao extends BaseMapper<ComponentRobotBlock> {

    /**
     * 根据机器人ID和组件ID查询屏蔽记录
     */
    ComponentRobotBlock getBlockByRobotAndComponent(
            @Param("robotId") String robotId,
            @Param("componentId") String componentId,
            @Param("tenantId") String tenantId);

    /**
     * 根据机器人ID查询所有屏蔽的组件
     */
    List<ComponentRobotBlock> getBlocksByRobotId(@Param("robotId") String robotId, @Param("tenantId") String tenantId);

    /**
     * 根据组件ID查询所有屏蔽该组件的机器人
     */
    List<ComponentRobotBlock> getBlocksByComponentId(
            @Param("componentId") String componentId, @Param("tenantId") String tenantId);

    /**
     * 检查机器人是否屏蔽了指定组件
     */
    @Select("select count(*) from component_robot_block "
            + "where robot_id = #{robotId} and component_id = #{componentId} and robot_version = #{robotVersion} "
            + "and deleted = 0 and creator_id = #{userId}")
    Long checkBlockExists(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion,
            @Param("componentId") String componentId,
            @Param("userId") String userId);

    /**
     * 逻辑删除屏蔽记录
     */
    @Update("update component_robot_block " + "set deleted = 1, updater_id = #{updaterId}, update_time = now() "
            + "where id = #{id} and tenant_id = #{tenantId}")
    Integer deleteBlock(@Param("id") Long id, @Param("updaterId") String updaterId, @Param("tenantId") String tenantId);

    /**
     * 根据机器人ID和组件ID逻辑删除屏蔽记录
     */
    @Update("update component_robot_block " + "set deleted = 1, updater_id = #{updaterId}, update_time = now() "
            + "where robot_id = #{robotId} and component_id = #{componentId} and robot_version = #{robotVersion} "
            + "and deleted = 0 and tenant_id = #{tenantId}")
    Integer deleteBlockByRobotAndComponent(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion,
            @Param("componentId") String componentId,
            @Param("updaterId") String updaterId,
            @Param("tenantId") String tenantId);

    /**
     * 根据机器人ID和版本号查询屏蔽的组件ID列表
     */
    @Select("select component_id from component_robot_block "
            + "where robot_id = #{robotId} and robot_version = #{robotVersion} "
            + "and deleted = 0 and tenant_id = #{tenantId}")
    List<String> getBlockedComponentIds(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion,
            @Param("tenantId") String tenantId);

    /**
     * 批量插入组件屏蔽记录
     */
    int insertBatch(@Param("entities") List<ComponentRobotBlock> entities);

    /**
     * 删除之前的编辑态记录
     */
    @Update("update component_robot_block " + "set deleted = 1 "
            + "where robot_id = #{robotId} and robot_version = 0 and creator_id = #{userId}")
    boolean deleteOldEditVersion(@Param("robotId") String robotId, @Param("userId") String userId);

    /**
     * 查询指定版本的组件屏蔽记录
     */
    @Select("select * from component_robot_block "
            + "where robot_id = #{robotId} and robot_version = #{version} and creator_id = #{userId} and deleted = 0")
    List<ComponentRobotBlock> getComponentRobotBlock(
            @Param("robotId") String robotId, @Param("version") Integer version, @Param("userId") String userId);

    /**
     * 查询指定版本的组件屏蔽记录（用于复制操作，使用tenantId）
     */
    @Select("select * from component_robot_block "
            + "where robot_id = #{robotId} and robot_version = #{version} and tenant_id = #{tenantId} and deleted = 0")
    List<ComponentRobotBlock> getComponentRobotBlockForCopy(
            @Param("robotId") String robotId, @Param("version") Integer version, @Param("tenantId") String tenantId);
}

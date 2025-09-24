package com.iflytek.rpa.component.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.component.entity.ComponentRobotUse;
import com.iflytek.rpa.component.entity.bo.ComponentRobotUseDeleteBo;
import com.iflytek.rpa.component.entity.bo.ComponentRobotUseUpdateBo;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 机器人对组件引用表(ComponentRobotUse)表数据库访问层
 *
 * @author makejava
 * @since 2024-12-19
 */
@Mapper
public interface ComponentRobotUseDao extends BaseMapper<ComponentRobotUse> {

    /**
     * 根据机器人ID查询组件引用列表
     */
    List<ComponentRobotUse> getByRobotId(@Param("robotId") String robotId, @Param("tenantId") String tenantId);

    /**
     * 根据组件ID查询机器人引用列表
     */
    List<ComponentRobotUse> getByComponentId(
            @Param("componentId") String componentId, @Param("tenantId") String tenantId);

    /**
     * 根据机器人ID和版本号查询组件引用
     */
    @Select("select * from component_robot_use " + "where deleted = 0 and robot_id = #{robotId} "
            + "and robot_version = #{robotVersion} and tenant_id = #{tenantId}")
    List<ComponentRobotUse> getByRobotIdAndVersion(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion,
            @Param("tenantId") String tenantId);

    /**
     * 根据机器人ID、版本号和组件ID查询组件引用
     */
    @Select("select * from component_robot_use where deleted = 0 and robot_id = #{robotId} "
            + "and robot_version = #{robotVersion} and component_id = #{componentId} and creator_id = #{userId}")
    ComponentRobotUse getByRobotIdVersionAndComponentId(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion,
            @Param("componentId") String componentId,
            @Param("userId") String userId);

    /**
     * 根据组件ID和版本号查询机器人引用
     */
    @Select("select * from component_robot_use where deleted = 0 and component_id = #{componentId} "
            + "and component_version = #{componentVersion} and tenant_id = #{tenantId}")
    List<ComponentRobotUse> getByComponentIdAndVersion(
            @Param("componentId") String componentId,
            @Param("componentVersion") Integer componentVersion,
            @Param("tenantId") String tenantId);

    /**
     * 根据机器人ID、版本号、组件ID和组件版本号查询组件引用
     */
    @Select("select * from component_robot_use where deleted = 0 and robot_id = #{robotId} "
            + "and robot_version = #{robotVersion} and component_id = #{componentId} "
            + "and component_version = #{componentVersion} and tenant_id = #{tenantId}")
    ComponentRobotUse getByRobotIdVersionAndComponentIdVersion(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion,
            @Param("componentId") String componentId,
            @Param("componentVersion") Integer componentVersion,
            @Param("tenantId") String tenantId);

    /**
     * 删除组件引用（逻辑删除）
     */
    int deleteComponentUse(ComponentRobotUseDeleteBo deleteBo);

    /**
     * 更新组件引用版本
     */
    int updateComponentUse(ComponentRobotUseUpdateBo updateBo);

    /**
     * 批量插入组件引用记录
     */
    int insertBatch(@Param("entities") List<ComponentRobotUse> entities);

    /**
     * 删除之前的编辑态记录
     */
    @Update("update component_robot_use " + "set deleted = 1 "
            + "where robot_id = #{robotId} and robot_version = 0 and creator_id = #{userId}")
    boolean deleteOldEditVersion(@Param("robotId") String robotId, @Param("userId") String userId);

    /**
     * 查询指定版本的组件引用记录
     */
    @Select("select * from component_robot_use "
            + "where robot_id = #{robotId} and robot_version = #{version} and creator_id = #{userId} and deleted = 0")
    List<ComponentRobotUse> getComponentRobotUse(
            @Param("robotId") String robotId, @Param("version") Integer version, @Param("userId") String userId);
}

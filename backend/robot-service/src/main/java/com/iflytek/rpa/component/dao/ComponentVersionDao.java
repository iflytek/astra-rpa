package com.iflytek.rpa.component.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.component.entity.ComponentVersion;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 组件版本表(ComponentVersion)表数据库访问层
 *
 * @author makejava
 * @since 2024-12-19
 */
@Mapper
public interface ComponentVersionDao extends BaseMapper<ComponentVersion> {

    /**
     * 根据组件ID查询版本列表
     */
    List<ComponentVersion> getVersionsByComponentId(
            @Param("componentId") String componentId, @Param("tenantId") String tenantId);

    /**
     * 根据组件ID和版本号查询版本信息
     */
    ComponentVersion getVersionByComponentIdAndVersion(
            @Param("componentId") String componentId,
            @Param("version") Integer version,
            @Param("tenantId") String tenantId);

    /**
     * 获取组件的最新版本号
     */
    @Select("select max(version) from component_version "
            + "where component_id = #{componentId} and deleted = 0 and tenant_id = #{tenantId}")
    Integer getLatestVersion(@Param("componentId") String componentId, @Param("tenantId") String tenantId);

    /**
     * 获取组件的最新版本信息
     */
    @Select("select * from component_version "
            + "where component_id = #{componentId} and deleted = 0 and tenant_id = #{tenantId} "
            + "order by version desc limit 1")
    ComponentVersion getLatestVersionInfo(@Param("componentId") String componentId, @Param("tenantId") String tenantId);

    /**
     * 更新版本启用状态
     */
    @Update("update component_version set online = #{online}, " + "updater_id = #{userId}, update_time = now() "
            + "where component_id = #{componentId} and deleted = 0 and tenant_id = #{tenantId}")
    Integer updateOnlineStatus(
            @Param("userId") String userId,
            @Param("componentId") String componentId,
            @Param("online") Integer online,
            @Param("tenantId") String tenantId);

    /**
     * 逻辑删除版本
     */
    @Update("update component_version " + "set deleted = 1, update_time = now(), updater_id = #{userId} "
            + "where component_id = #{componentId} and deleted = 0 and tenant_id = #{tenantId}")
    Integer deleteVersion(
            @Param("componentId") String componentId,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    /**
     * 根据组件ID查询启用的版本
     */
    @Select("select * from component_version "
            + "where component_id = #{componentId} and online = 1 and deleted = 0 and tenant_id = #{tenantId}")
    ComponentVersion getOnlineVersion(@Param("componentId") String componentId, @Param("tenantId") String tenantId);

    /**
     * 获取已发过版本的组件ID列表
     *
     * @param tenantId 租户ID
     * @return 组件ID列表
     */
    @Select("select distinct component_id from component_version " + "where deleted = 0 and tenant_id = #{tenantId}")
    List<String> getPublishedComponentIds(@Param("tenantId") String tenantId);

    /**
     * 批量获取组件的最新版本信息
     *
     * @param componentIds 组件ID列表
     * @param tenantId     租户ID
     * @return 组件最新版本信息列表
     */
    List<ComponentVersion> getLatestVersionInfoBatch(
            @Param("componentIds") List<String> componentIds, @Param("tenantId") String tenantId);
}

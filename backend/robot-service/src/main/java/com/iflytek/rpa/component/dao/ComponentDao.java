package com.iflytek.rpa.component.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.iflytek.rpa.component.entity.Component;
import com.iflytek.rpa.component.entity.vo.ComponentVo;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 组件表(Component)表数据库访问层
 *
 * @author makejava
 * @since 2024-12-19
 */
@Mapper
public interface ComponentDao extends BaseMapper<Component> {

    /**
     * 根据组件ID查询组件信息
     */
    Component getComponentById(
            @Param("componentId") String componentId,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    Component getShownComponentById(
            @Param("componentId") String componentId,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    /**
     * 根据名称查询组件数量
     */
    Long countByName(
            @Param("name") String name,
            @Param("tenantId") String tenantId,
            @Param("userId") String userId,
            @Param("excludeId") Long excludeId);

    /**
     * 根据应用ID查询组件
     */
    @Select("select * from component where deleted = 0 and market_id = #{marketId} "
            + "and tenant_id = #{tenantId} and app_id = #{appId} "
            + "order by app_version desc limit 1")
    Component getComponentByAppId(
            @Param("userId") Long userId,
            @Param("tenantId") Long tenantId,
            @Param("marketId") String marketId,
            @Param("appId") String appId);

    /**
     * 根据应用ID列表查询组件
     */
    List<Component> getComponentsByAppIdList(
            @Param("userId") Long userId,
            @Param("tenantId") Long tenantId,
            @Param("marketId") String marketId,
            @Param("appIdList") List<String> appIdList);

    /**
     * 逻辑删除组件
     */
    @Update("update component " + "set is_shown = 0, "
            + "update_time = now() "
            + "where component_id = #{componentId} "
            + "and tenant_id = #{tenantId}")
    Integer deleteComponent(
            @Param("componentId") String componentId,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    /**
     * 根据租户ID和用户ID查询组件列表
     */
    List<Component> getComponentsByTenantAndUser(@Param("tenantId") Long tenantId, @Param("userId") Long userId);

    List<String> getComponentNameList(
            @Param("tenantId") String tenantId,
            @Param("userId") String userId,
            @Param("componentNameBase") String componentNameBase);

    /**
     * 分页查询组件列表
     *
     * @param page       分页参数
     * @param name       组件名称（模糊查询）
     * @param dataSource 数据来源
     * @param sortType   排序类型
     * @param tenantId   租户ID
     * @param userId     用户ID
     * @return 分页组件列表
     */
    IPage<ComponentVo> getComponentPageList(
            Page<ComponentVo> page,
            @Param("name") String name,
            @Param("dataSource") String dataSource,
            @Param("sortType") String sortType,
            @Param("tenantId") String tenantId,
            @Param("userId") String userId);

    /**
     * 获取用户权限内可获取的组件列表（shown = 1）
     *
     * @param tenantId 租户ID
     * @param userId   用户ID
     * @return 组件列表
     */
    List<Component> getAvailableComponentsByUser(@Param("tenantId") String tenantId, @Param("userId") String userId);

    /**
     * 根据组件ID列表查询组件信息
     *
     * @param componentIds 组件ID列表
     * @param tenantId     租户ID
     * @return 组件列表
     */
    List<Component> getComponentsByIds(
            @Param("componentIds") List<String> componentIds, @Param("tenantId") String tenantId);

    Integer updateTransformStatus(
            @Param("userId") String userId,
            @Param("componentId") String componentId,
            @Param("name") String name,
            @Param("transformStatus") String transformStatus);
}

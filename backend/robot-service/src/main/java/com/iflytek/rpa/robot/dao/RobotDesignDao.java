package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.CProcess;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 云端机器人表(Robot)表数据库访问层
 *
 * @author makejava
 * @since 2024-09-29 15:27:36
 */
@Mapper
public interface RobotDesignDao extends BaseMapper<RobotDesign> {

    List<String> getRobotNameList(
            @Param("tenantId") String tenantId,
            @Param("userId") String userId,
            @Param("robotNameBase") String robotNameBase);

    RobotDesign getRobotDesignInfo(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    Integer countByName(RobotVersionDto robotVersionDto);

    Long countRobotByName(RobotDesign robot);

    Long countRobotVersionByName(RobotDesign robot);

    Integer createRobot(RobotDesign robot);

    Integer updateTransformStatus(
            @Param("userId") String userId,
            @Param("robotId") String robotId,
            @Param("name") String name,
            @Param("transformStatus") String transformStatus);

    Integer obtainRobotToDesign(RobotDesign robotDesign);

    Integer deleteDesign(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    List<RobotDesign> getDesignByAppIdList(
            @Param("userId") String userId,
            @Param("tenantId") String tenantId,
            @Param("marketId") String marketId,
            @Param("appIdList") List<String> appIdList);

    @Select("select * " + "from robot_design "
            + "where deleted = 0 and creator_id = #{userId} and market_id = #{marketId} and tenant_id = #{tenantId} and app_id = #{appId} "
            + "order by app_version desc "
            + "limit 1")
    RobotDesign getDesignByAppId(
            @Param("userId") String userId,
            @Param("tenantId") String tenantId,
            @Param("marketId") String marketId,
            @Param("appId") String appId);

    @Select({
        "<script>",
        "select creator_id",
        "from app_market_resource",
        "where app_id in",
        "<foreach collection='appIdList' item='appId' open='(' separator=',' close=')'>",
        "#{appId}",
        "</foreach>",
        "</script>"
    })
    List<Long> getCreatorIdsByAppIds(@Param("appIdList") List<String> appIdList);

    @Select({
        "<script>",
        "select *",
        "from c_process",
        "where robot_id in",
        "<foreach collection='robotIdList' item='robotId' open='(' separator=',' close=')'>",
        "#{robotId}",
        "</foreach>",
        "</script>"
    })
    List<CProcess> getCProcessList(@Param("robotIdList") List<String> robotIdList);

    @Select({
        "<script>",
        "select *",
        "from robot_version",
        "where robot_id in",
        "<foreach collection='robotIdList' item='robotId' open='(' separator=',' close=')'>",
        "#{robotId}",
        "</foreach>",
        "</script>"
    })
    List<RobotVersion> getRobotVersionList(@Param("robotIdList") List<String> robotIdList);

    @Update("update robot_design " + "set name = #{newName} ,transform_status = 'editing' "
            + "where deleted = 0 and robot_id = #{robotId} and creator_id = #{userId} and tenant_id = #{tenantId}")
    boolean updateRobotName(
            @Param("newName") String newName,
            @Param("robotId") String robotId,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    @Update("update robot_design " + "set name = #{newName} "
            + "where deleted = 0 and robot_id = #{robotId} and creator_id = #{userId} and tenant_id = #{tenantId}")
    boolean updateRobotNameWithoutSetEditing(
            @Param("newName") String newName,
            @Param("robotId") String robotId,
            @Param("userId") String userId,
            @Param("tenantId") String tenantId);

    @Select("select name " + "from robot_design "
            + "where deleted = 0 and robot_id = #{robotId} and creator_id = #{userId} and tenant_id = #{tenantId}")
    String getRobotName(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Select("select market_id " + "from robot "
            + "where deleted = 0 and robot_id = #{robotId} and creator_id = #{userId} and tenant_id = #{tenantId}")
    String getMarketId(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Select("select * " + "from c_process "
            + "where robot_id = #{robotId} and robot_version = 0 and deleted = 0 limit 1")
    CProcess getCProcess(@Param("robotId") String robotId);

    @Select(
            "select count(name) " + "from robot_design "
                    + "where deleted = 0 and creator_id = #{userId} and tenant_id = #{tenantId} and name = #{newName} and robot_id <> #{robotId}")
    Integer checkNameDup(
            @Param("userId") String userId,
            @Param("tenantId") String tenantId,
            @Param("newName") String newName,
            @Param("robotId") String robotId);

    @Select("select count(name) " + "from robot_design "
            + "where deleted = 0 and creator_id = #{userId} and tenant_id = #{tenantId} and name = #{newName}")
    Integer checkNameDupWithoutRobotId(
            @Param("userId") String userId, @Param("tenantId") String tenantId, @Param("newName") String newName);

    @Select("select * " + "from robot_design "
            + "where deleted = 0 and creator_id = #{userId} and tenant_id = #{tenantId} and robot_id = #{robotId}")
    RobotDesign getRobot(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Select("select * " + "from robot_design "
            + "where creator_id = #{userId} and tenant_id = #{tenantId} and robot_id = #{robotId}")
    RobotDesign getRobotRegardlessLogicDel(
            @Param("robotId") String robotId, @Param("userId") String userId, @Param("tenantId") String tenantId);

    @Select("select * " + "from robot_design " + "where tenant_id = #{tenantId} and robot_id = #{robotId}")
    RobotDesign getRobotInfoAll(@Param("robotId") String robotId, @Param("tenantId") String tenantId);

    @Select("select robot_id " + "from app_market_resource " + "where app_id = #{appId} and deleted = 0")
    String getRobotIdFromAppResource(@Param("appId") String appId);

    @Select("select robot_id " + "from app_market_resource " + "where app_id = #{appId}")
    String getRobotIdFromAppResourceRegardlessDel(@Param("appId") String appId);
}

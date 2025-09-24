package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.CGroup;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * 元素或图像的分组(CGroup)表数据库访问层
 *
 * @author mjren
 * @since 2024-12-04 10:28:54
 */
@Mapper
public interface CGroupDao extends BaseMapper<CGroup> {

    CGroup getGroupByGroupName(CGroup cGroup);

    Integer insertGroup(CGroup cGroup);

    Integer updateGroup(CGroup cGroup);

    Integer deleteGroup(CGroup cGroup);

    CGroup getGroupSameName(CGroup cGroup);

    CGroup getGroupById(CGroup cGroup);

    List<CGroup> getGroupByRobotId(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion,
            @Param("elementType") String elementType);

    Integer createGroupForCurrentVersion(RobotVersionDto robotVersionDto);

    Integer createGroupForObtainedVersion(
            @Param("obtainedRobotDesign") RobotDesign obtainedRobotDesign,
            @Param("authorRobotVersion") RobotVersion authorRobotVersion);

    Integer copyGroupBatch(
            @Param("oldRobotId") String oldRobotId,
            @Param("newRobotId") String newRobotId,
            @Param("userId") String userId);

    Integer shareGroupBatch(
            @Param("oldRobotId") String oldRobotId,
            @Param("sharedUserId") String sharedUserId,
            @Param("newRobotId") String newRobotId,
            @Param("receivedUserId") String receivedUserId);
}

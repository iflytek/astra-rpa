package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.CElement;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 客户端，元素信息(CElement)表数据库访问层
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
@Mapper
public interface CElementDao extends BaseMapper<CElement> {

    Integer insertElement(CElement cElement);

    CElement getElementSameName(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer version,
            @Param("elementId") String elementId,
            @Param("elementName") String elementName,
            @Param("elementType") String elementType);

    List<String> getElementNameList(CElement cElement);

    Integer updateElement(CElement cElement);

    Integer copyElement(@Param("entity") CElement cElement, @Param("newElementId") String newElementId);

    Integer deleteElementOrImage(CElement cElement);

    Integer createElementForCurrentVersion(RobotVersionDto robotVersionDto);

    Integer createElementForObtainedVersion(
            @Param("obtainedRobotDesign") RobotDesign obtainedRobotDesign,
            @Param("authorRobotVersion") RobotVersion authorRobotVersion);

    CElement getElementByElementId(CElement element);

    List<CElement> getElementInfo(
            @Param("robotId") String robotId, @Param("version") Integer version, @Param("userId") String userId);

    Integer deleteByGroupId(CElement cElement);

    List<CElement> getElementsByGroupIds(@Param("entity") CElement celement, @Param("groupIds") List<String> groupIds);

    // 删除之前的编辑态
    // 查询指定版本 ,  查询出来之后把 robot_version set 为 0，id set 为null
    //
    @Update("update c_element " + "set deleted = 1 "
            + "where robot_id = #{robotId} and robot_version = 0 and creator_id = #{userId}")
    boolean deleteOldEditVersion(@Param("robotId") String robotId, @Param("userId") String userId);

    @Select("select * " + "from c_element "
            + "where robot_id = #{robotId} and robot_version = #{version} and creator_id = #{userId} and deleted = 0")
    List<CElement> getElement(
            @Param("robotId") String robotId, @Param("version") Integer version, @Param("userId") String userId);

    Integer insertEleBatch(@Param("entities") List<CElement> entities);
}

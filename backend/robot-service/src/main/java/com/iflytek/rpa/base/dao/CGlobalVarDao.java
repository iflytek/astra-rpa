package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.CGlobalVar;
import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CGlobalDto;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 客户端-全局变量(CGlobalVar)表数据库访问层
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
@Mapper
public interface CGlobalVarDao extends BaseMapper<CGlobalVar> {

    Integer createGlobalVarForCurrentVersion(RobotVersionDto robotVersionDto);

    Integer createGlobalVarForObtainedVersion(
            @Param("obtainedRobotDesign") RobotDesign obtainedRobotDesign,
            @Param("authorRobotVersion") RobotVersion authorRobotVersion);

    List<CGlobalVar> getGlobalVarInfoList(BaseDto baseDto);

    @Update("update c_global_var " + "set deleted = 1 "
            + "where robot_id = #{robotId} and robot_version = 0 and creator_id = #{userId}")
    boolean deleteOldEditVersion(@Param("robotId") String robotId, @Param("userId") String userId);

    @Select("select * " + "from c_global_var "
            + "where robot_id = #{robotId} and robot_version = #{version} and creator_id = #{userId} and deleted = 0")
    List<CGlobalVar> getGlobalVar(
            @Param("robotId") String robotId, @Param("version") Integer version, @Param("userId") String userId);

    Integer insertGloBatch(@Param("entities") List<CGlobalVar> entities);

    Integer countVarByName(CGlobalDto globalDto);

    boolean createGlobalVar(CGlobalDto globalDto);

    CGlobalVar getGlobalVarOne(CGlobalDto globalDto);

    boolean saveGlobalVar(CGlobalDto globalDto);

    List<CGlobalVar> getGlobalVarNameList(@Param("userId") String userId, @Param("robotId") String robotId);

    boolean deleteGlobalVar(CGlobalDto globalDto);
}

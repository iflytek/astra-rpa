package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.CRequire;
import com.iflytek.rpa.base.entity.dto.CRequireDeleteDto;
import com.iflytek.rpa.base.entity.dto.CRequireDto;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * python依赖管理(CRequire)表数据库访问层
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
@Mapper
public interface CRequireDao extends BaseMapper<CRequire> {

    Integer createRequireForCurrentVersion(RobotVersionDto robotVersionDto);

    Integer createRequireForObtainedVersion(
            @Param("obtainedRobotDesign") RobotDesign obtainedRobotDesign,
            @Param("authorRobotVersion") RobotVersion authorRobotVersion);

    @Select("select * " + "from c_require "
            + "where robot_id = #{robotId} and robot_version = #{version} and deleted = 0")
    List<CRequire> getRequireList(@Param("robotId") String robotId, @Param("version") Integer version);

    @Update("update c_require " + "set deleted = 1 "
            + "where robot_id = #{robotId} and robot_version = 0 and creator_id = #{userId}")
    boolean deleteOldEditVersion(@Param("robotId") String robotId, @Param("userId") String userId);

    @Select("select * " + "from c_require "
            + "where robot_id = #{robotId} and robot_version = #{version} and creator_id = #{userId} and deleted = 0")
    List<CRequire> getRequire(
            @Param("robotId") String robotId, @Param("version") Integer version, @Param("userId") String userId);

    Integer insertReqBatch(@Param("entities") List<CRequire> entities);

    int countRequire(CRequireDto crequireDto);

    boolean addRequire(CRequireDto crequireDto);

    boolean deleteRequire(CRequireDeleteDto cRequireDeleteDto);

    boolean updateRequire(CRequireDto crequireDto);
}

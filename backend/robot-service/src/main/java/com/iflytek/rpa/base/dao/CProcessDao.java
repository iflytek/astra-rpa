package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.CProcess;
import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CProcessDto;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import java.util.List;
import java.util.Set;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

/**
 * 流程项id数据(CProcess)表数据库访问层
 *
 * @author mjren
 * @since 2024-10-09 17:11:13
 */
@Mapper
public interface CProcessDao extends BaseMapper<CProcess> {

    Integer countProcessByName(CProcess searchDto);

    Integer renameProcess(CProcess process);

    List<CProcess> getAllProcessDataByRobotId(@Param("robotId") String robotId, @Param("version") Integer version);

    //    Integer updateProcessForVersionZero(@Param("userId") String userId, @Param("entities") List<CProcess>
    // processUpdateInfoList);
    Integer createProcessForCurrentVersion(RobotVersionDto robotVersionDto);

    Integer createProcessForObtainedVersion(
            @Param("obtainedRobotDesign") RobotDesign robotDesign,
            @Param("authorRobotVersion") RobotVersion authorRobotVersion);

    Integer createProcess(CProcess cProcess);

    Set<String> getProcessIdList(@Param("userId") String userId, @Param("robotId") String robotId);

    Integer updateProcessContent(@Param("process") CProcessDto process);

    CProcess getProcessById(BaseDto baseDto);

    List<String> getProcessNameListByPrefix(BaseDto baseDto);

    List<CProcess> getProcessNameList(BaseDto baseDto);

    @Update("update c_process " + "set deleted = 1 "
            + "where robot_id = #{robotId} and robot_version = 0 and creator_id = #{userId}")
    boolean deleteOldEditVersion(@Param("robotId") String robotId, @Param("userId") String userId);

    @Select("select * " + "from c_process "
            + "where robot_id = #{robotId} and robot_version = #{version} and creator_id = #{userId} and deleted = 0")
    List<CProcess> getProcess(
            @Param("robotId") String robotId, @Param("version") Integer version, @Param("userId") String userId);

    Integer insertProcessBatch(@Param("entities") List<CProcess> entities);

    boolean deleteProcessByProcessId(CProcessDto processDto);

    /**
     * 根据组件ID和版本查询流程ID
     *
     * @param componentId      组件ID
     * @param componentVersion 组件版本
     * @return 流程ID
     */
    @Select("select process_id from c_process "
            + "where robot_id = #{componentId} and robot_version = #{componentVersion} and deleted = 0 "
            + "limit 1")
    String getProcessIdByComp(
            @Param("componentId") String componentId, @Param("componentVersion") Integer componentVersion);
}

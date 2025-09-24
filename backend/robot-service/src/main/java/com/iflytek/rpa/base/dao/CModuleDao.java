package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.CModule;
import com.iflytek.rpa.base.entity.CProcess;
import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface CModuleDao extends BaseMapper<CModule> {

    @Select("select * " + "from c_module "
            + "where deleted = 0 "
            + "and creator_id = #{userId} and robot_id = #{robotId} and robot_version = #{robotVersion} "
            + "order by create_time desc")
    List<CModule> getAllModuleList(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion,
            @Param("userId") String userId);

    @Select("select * " + "from c_process "
            + "where deleted = 0 "
            + "and creator_id = #{userId} and robot_id = #{robotId} and robot_version = #{robotVersion} "
            + "order by create_time desc")
    List<CProcess> getAllProcessList(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion,
            @Param("userId") String userId);

    @Select("select * " + "from c_module "
            + "where deleted = 0 "
            + "and creator_id = #{userId} and module_id = #{moduleId}"
            + "and robot_id = #{robotId}"
            + "and robot_version = 0")
    CModule getOneModule(
            @Param("moduleId") String moduleId, @Param("userId") String userId, @Param("robotId") String robotId);

    @Update("update c_module " + "set deleted = 1 "
            + "where deleted = 0 "
            + "and creator_id = #{userId} and module_id = #{moduleId}")
    boolean deleteOneModule(@Param("moduleId") String moduleId, @Param("userId") String userId);

    @Update("update c_module " + "set module_content = #{moduleContent} "
            + "where deleted = 0 "
            + "and creator_id = #{userId} and module_id = #{moduleId}"
            + "and robot_id = #{robotId} and robot_version = 0")
    boolean saveModuleContent(
            @Param("moduleId") String moduleId,
            @Param("userId") String userId,
            @Param("robotId") String robotId,
            @Param("moduleContent") String moduleContent);

    @Select("select module_name " + "from c_module "
            + "where deleted = 0 "
            + "and creator_id = #{userId} and robot_id = #{robotId} and robot_version = #{robotVersion} and module_id <> #{moduleId} "
            + "order by create_time desc")
    List<String> getAllModuleNameExpSelf(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion,
            @Param("userId") String userId,
            @Param("moduleId") String moduleId);

    @Select("select module_name " + "from c_module "
            + "where deleted = 0 "
            + "and creator_id = #{userId} and robot_id = #{robotId} and robot_version = #{robotVersion} "
            + "order by create_time desc")
    List<String> getAllModuleName(
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion,
            @Param("userId") String userId);

    @Update("update c_module " + "set module_name = #{moduleName} "
            + "where deleted = 0 "
            + "and creator_id = #{userId} and module_id = #{moduleId}")
    boolean updateModuleName(
            @Param("userId") String userId, @Param("moduleId") String moduleId, @Param("moduleName") String moduleName);

    @Select("select *\n" + "        from c_module\n"
            + "        where\n"
            + "        robot_id = #{robotId}\n"
            + "        and robot_version = #{robotVersion}\n"
            + "        and module_id = #{id}\n"
            + "        and deleted = 0")
    CModule getCodeModeById(BaseDto baseDto);

    @Select("select module_name " + "from c_module "
            + "where deleted = 0 "
            + "and module_name like concat(#{name}, '%') and robot_id = #{robotId} and robot_version = #{robotVersion} "
            + "order by create_time desc")
    List<String> getModuleNameListByPrefix(BaseDto baseDto);

    Integer createModuleForObtainedVersion(
            @Param("obtainedRobotDesign") RobotDesign obtainedRobotDesign,
            @Param("authorRobotVersion") RobotVersion authorRobotVersion);

    @Select("select * " + "from c_module "
            + "where deleted = 0 "
            + "and module_id = #{moduleId} "
            + "and robot_id = #{robotId} "
            + "and robot_version = #{robotVersion} ")
    CModule getModule(
            @Param("moduleId") String moduleId,
            @Param("robotId") String robotId,
            @Param("robotVersion") Integer robotVersion);

    @Select("select *" + "from c_module " + "where deleted = 0 " + "and module_id = #{moduleId}")
    CModule getModuleByModuleId(@Param("moduleId") String moduleId);

    void insertBatch(List<CModule> moduleList);

    Integer createModuleForCurrentVersion(RobotVersionDto robotVersionDto);

    @Update("update c_module " + "set deleted = 1 "
            + "where robot_id = #{robotId} and robot_version = 0 and creator_id = #{userId}")
    boolean deleteOldEditVersion(@Param("robotId") String robotId, @Param("userId") String userId);
}

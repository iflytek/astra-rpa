package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.CParam;
import com.iflytek.rpa.robot.entity.RobotExecute;
import java.util.List;
import org.apache.ibatis.annotations.*;

/**
 * @author tzzhang
 * @date 2025/3/13 16:51
 */
@Mapper
public interface CParamDao extends BaseMapper<CParam> {

    List<CParam> getAllParams(
            @Param("processId") String processId, @Param("robotId") String robotId, @Param("version") Integer version);

    List<CParam> getParams(@Param("robotId") String robotId, @Param("userId") String userId);

    void insertParamBatch(List<CParam> params);

    /**
     * 根据robotId在c_process查询主流程id
     *
     * @param robotId
     * @param robotVersion
     * @return
     */
    @Select(
            "select process_id from c_process where process_name = '主流程' and robot_id=#{robotId} and robot_version=#{robotVersion} and deleted = 0")
    String getMianProcessId(String robotId, Integer robotVersion);

    @Insert(
            "insert into c_param(id,var_direction,var_name,var_type,var_value,var_describe,process_id,creator_id,updater_id,create_time,update_time,deleted,robot_id,robot_version) "
                    + "values"
                    + "(#{id},#{varDirection},#{varName},#{varType},#{varValue},#{varDescribe},#{processId},#{creatorId},#{updaterId},#{createTime},#{updateTime},#{deleted},#{robotId},#{robotVersion})")
    void addParam(CParam cParam);

    // 删除修改deleted不需要真正删除
    @Update("update c_param set deleted=1 where id=#{id}")
    void deleteParam(String id);

    Long countParamByName(CParam param);

    void updateParam(CParam cParamDto);

    /**
     * 批量插入新版本配置参数
     *
     * @param cParamList
     */
    void createParamForCurrentVersion(@Param("entities") List<CParam> cParamList);

    /**
     * 查询自己创建机器人默认参数
     *
     * @param robotId
     * @param processId
     * @param robotVersion
     * @return
     */
    List<CParam> getSelfRobotParam(String robotId, String processId, Integer robotVersion);

    /**
     * 查询原始机器人的robot_id
     *
     * @param robotExecute
     * @return
     */
    String getMarketRobotId(RobotExecute robotExecute);

    /**
     * 查询部署的原始机器人的robot_id
     *
     * @param robotExecute
     * @return
     */
    String getDeployOriginalRobotId(RobotExecute robotExecute);

    /**
     * 查询在线机器人版本号
     *
     * @param robotId
     * @return
     */
    Integer getRobotVersion(String robotId);

    /**
     * 根据robotId删除对应参数
     *
     * @param robotId
     */
    @Update("update c_param set deleted = 1 where robot_id =#{robotId} and robot_version = 0")
    void deleteParamByRobotId(String robotId);

    CParam getParamInfoById(@Param("id") String id);
}

package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.robot.entity.SharedVarUser;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

/**
 * 共享变量用户关系DAO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Mapper
public interface SharedVarUserDao extends BaseMapper<SharedVarUser> {

    /**
     * 批量插入用户关系
     *
     * @param entities 用户关系列表
     * @return 影响行数
     */
    Integer insertBatch(@Param("entities") List<SharedVarUser> entities);

    /**
     * 逻辑删除用户关系
     *
     * @param sharedVarId 共享变量ID
     * @param userId      用户ID
     * @return 影响行数
     */
    @Update("UPDATE shared_var_user SET deleted = 1 WHERE shared_var_id = #{sharedVarId} AND deleted = 0")
    void deleteBySharedVarId(@Param("sharedVarId") Long sharedVarId, @Param("userId") String userId);

    List<String> getAvailableSharedVarIds(String userId);
}

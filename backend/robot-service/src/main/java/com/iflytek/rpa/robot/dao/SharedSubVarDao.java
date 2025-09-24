package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.robot.entity.SharedSubVar;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

/**
 * 共享变量子变量DAO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Mapper
public interface SharedSubVarDao extends BaseMapper<SharedSubVar> {

    /**
     * 批量插入子变量
     *
     * @param entities 子变量列表
     * @return 影响行数
     */
    Integer insertBatch(@Param("entities") List<SharedSubVar> entities);

    /**
     * 逻辑删除子变量
     *
     * @param sharedVarId 共享变量ID
     * @param userId      用户ID
     * @return 影响行数
     */
    @Update("UPDATE shared_sub_var SET deleted = 1 WHERE shared_var_id = #{sharedVarId} AND deleted = 0")
    void deleteBySharedVarId(@Param("sharedVarId") Long sharedVarId, @Param("userId") String userId);
}

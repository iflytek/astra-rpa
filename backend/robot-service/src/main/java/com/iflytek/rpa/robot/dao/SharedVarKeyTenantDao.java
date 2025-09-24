package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.robot.entity.SharedVarKeyTenant;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

/**
 * 共享变量租户密钥DAO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Mapper
public interface SharedVarKeyTenantDao extends BaseMapper<SharedVarKeyTenant> {

    /**
     * 逻辑删除所有数据
     */
    @Update("UPDATE shared_var_key_tenant SET deleted = 1 WHERE deleted = 0")
    void deleteAll();

    /**
     * 批量插入租户密钥
     */
    void insertBatch(@Param("entities") List<SharedVarKeyTenant> entities);

    /**
     * 根据租户ID查询密钥
     *
     * @param tenantId 租户ID
     * @return 密钥实体
     */
    SharedVarKeyTenant selectByTenantId(@Param("tenantId") String tenantId);
}

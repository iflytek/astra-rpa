package com.iflytek.rpa.robot.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.robot.entity.SharedVar;
import com.iflytek.rpa.robot.entity.SharedVarUser;
import com.iflytek.rpa.robot.entity.vo.SharedSubVarVo;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Update;

/**
 * 共享变量DAO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Mapper
public interface SharedVarDao extends BaseMapper<SharedVar> {

    /**
     * 根据共享变量ID获取子变量列表
     *
     * @param sharedVarIds 共享变量ID列表
     * @return 子变量列表
     */
    List<SharedSubVarVo> getSubVarListBySharedVarIds(@Param("sharedVarIds") List<Long> sharedVarIds);

    /**
     * 根据共享变量ID获取用户列表
     *
     * @param sharedVarIds 共享变量ID列表
     * @return 用户列表
     */
    List<SharedVarUser> getUserListBySharedVarIds(@Param("sharedVarIds") List<Long> sharedVarIds);

    /**
     * 逻辑删除共享变量
     *
     * @param id     共享变量ID
     * @param userId 用户ID
     * @return 影响行数
     */
    @Update(
            "UPDATE shared_var SET deleted = 1, updater_id = #{userId}, update_time = NOW() WHERE id = #{id} AND deleted = 0")
    int deleteSharedVar(@Param("id") Long id, @Param("userId") String userId);

    /**
     * 获取所有租户ID
     *
     * @return 租户ID列表
     */
    List<String> getAllTenantId(String databaseName);

    /**
     * 查询用户可用的共享变量（usage_type='all'和dept_id匹配的）
     *
     * @param tenantId     租户ID
     * @param deptId       部门ID
     * @param selectVarIds
     * @return 共享变量列表
     */
    List<SharedVar> getAvailableSharedVars(
            @Param("tenantId") String tenantId,
            @Param("deptId") String deptId,
            @Param("selectVarIds") List<String> selectVarIds);

    List<SharedVar> getAvailableByIds(@Param("ids") List<Long> ids);
}

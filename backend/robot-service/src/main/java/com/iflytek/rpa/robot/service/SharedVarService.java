package com.iflytek.rpa.robot.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.robot.entity.dto.*;
import com.iflytek.rpa.robot.entity.vo.ClientSharedVarVo;
import com.iflytek.rpa.robot.entity.vo.SharedVarKeyVo;
import com.iflytek.rpa.robot.entity.vo.SharedVarPageVo;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;

/**
 * 共享变量服务接口
 *
 * @author jqfang3
 * @since 2025-07-21
 */
public interface SharedVarService {

    /**
     * 变量管理列表分页查询
     *
     * @param queryDto 查询条件
     * @return 分页结果
     * @throws NoLoginException 未登录异常
     */
    AppResponse<IPage<SharedVarPageVo>> getSharedVarPageList(SharedVarPageDto queryDto) throws NoLoginException;

    /**
     * 变量管理新增变量
     *
     * @param saveDto 变量信息
     * @return 保存结果
     * @throws NoLoginException 未登录异常
     */
    AppResponse<String> saveSharedVar(SharedVarSaveDto saveDto) throws NoLoginException;

    /**
     * 删除共享变量
     *
     * @param deleteDto
     * @return
     * @throws NoLoginException
     */
    AppResponse<String> deleteSharedVar(SharedVarDeleteDto deleteDto) throws NoLoginException;

    /**
     * 编辑共享变量
     *
     * @param updateDto 更新参数
     * @return 更新结果
     * @throws NoLoginException 未登录异常
     */
    AppResponse<String> updateSharedVar(SharedVarUpdateDto updateDto) throws NoLoginException;

    /**
     * 获取共享变量租户密钥
     *
     * @return 密钥信息
     * @throws NoLoginException 未登录异常
     */
    AppResponse<SharedVarKeyVo> getSharedVarKey() throws NoLoginException;

    //    /**
    //     * 客户端-查询该用户可用的所有共享变量
    //     *
    //     * @return 共享变量列表
    //     * @throws NoLoginException 未登录异常
    //     */
    //    AppResponse<List<ClientSharedVarVo>> getClientSharedVars() throws NoLoginException;

    AppResponse<List<ClientSharedVarVo>> getBatchSharedVar(SharedVarBatchDto updateDto) throws NoLoginException;
}

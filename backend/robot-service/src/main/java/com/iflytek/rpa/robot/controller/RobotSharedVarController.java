package com.iflytek.rpa.robot.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.robot.entity.dto.*;
import com.iflytek.rpa.robot.entity.vo.ClientSharedVarVo;
import com.iflytek.rpa.robot.entity.vo.SharedVarKeyVo;
import com.iflytek.rpa.robot.entity.vo.SharedVarPageVo;
import com.iflytek.rpa.robot.service.SharedVarService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;
import javax.annotation.Resource;
import org.springframework.web.bind.annotation.*;

/**
 * 共享变量管理
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@RestController
@RequestMapping("/robot-shared-var")
public class RobotSharedVarController {

    @Resource
    private SharedVarService sharedVarService;

    /**
     * 卓越中心-变量管理-分页查询
     *
     * @param queryDto 查询条件
     * @return 分页结果
     * @throws NoLoginException 未登录异常
     */
    @PostMapping("/page-list")
    public AppResponse<IPage<SharedVarPageVo>> getSharedVarPageList(@RequestBody SharedVarPageDto queryDto)
            throws NoLoginException {
        return sharedVarService.getSharedVarPageList(queryDto);
    }

    /**
     * 卓越中心-变量管理-新增共享变量
     *
     * @param saveDto 共享变量信息
     * @return 保存结果
     * @throws NoLoginException 未登录异常
     */
    @PostMapping("/save-shared-var")
    public AppResponse<String> saveSharedVar(@RequestBody SharedVarSaveDto saveDto) throws NoLoginException {
        return sharedVarService.saveSharedVar(saveDto);
    }

    /**
     * 卓越中心-变量管理-删除共享变量
     *
     * @param deleteDto 删除参数
     * @return 删除结果
     * @throws NoLoginException 未登录异常
     */
    @PostMapping("/delete-shared-var")
    public AppResponse<String> deleteSharedVar(@RequestBody SharedVarDeleteDto deleteDto) throws NoLoginException {
        return sharedVarService.deleteSharedVar(deleteDto);
    }

    /**
     * 卓越中心-变量管理-编辑共享变量
     *
     * @param updateDto 更新参数
     * @return 更新结果
     * @throws NoLoginException 未登录异常
     */
    @PostMapping("/update-shared-var")
    public AppResponse<String> updateSharedVar(@RequestBody SharedVarUpdateDto updateDto) throws NoLoginException {
        return sharedVarService.updateSharedVar(updateDto);
    }

    /**
     * 获取共享变量租户密钥
     *
     * @return 密钥信息
     * @throws NoLoginException 未登录异常
     */
    @GetMapping("/shared-var-key")
    public AppResponse<SharedVarKeyVo> getSharedVarKey() throws NoLoginException {
        return sharedVarService.getSharedVarKey();
    }

    //    /**
    //     * 客户端-查询该用户可用的所有共享变量
    //     *
    //     * @return 共享变量列表
    //     * @throws NoLoginException 未登录异常
    //     */
    //    @GetMapping("/get-shared-var")
    //    public AppResponse<List<ClientSharedVarVo>> getClientSharedVars() throws NoLoginException {
    //        return sharedVarService.getClientSharedVars();
    //    }

    /**
     * 客户端-根据id批量查询共享变量
     *
     * @param dto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/get-batch-shared-var")
    public AppResponse<List<ClientSharedVarVo>> getBatchSharedVar(@RequestBody SharedVarBatchDto dto)
            throws NoLoginException {
        return sharedVarService.getBatchSharedVar(dto);
    }
}

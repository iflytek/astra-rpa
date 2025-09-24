package com.iflytek.rpa.base.controller;

import com.iflytek.rpa.base.entity.dto.*;
import com.iflytek.rpa.base.entity.vo.ModuleListVo;
import com.iflytek.rpa.base.entity.vo.OpenModuleVo;
import com.iflytek.rpa.base.entity.vo.ProcessModuleListVo;
import com.iflytek.rpa.base.service.CModuleService;
import com.iflytek.rpa.robot.entity.dto.SaveModuleDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.sql.SQLException;
import java.util.List;
import javax.annotation.Resource;
import javax.validation.Valid;
import org.springframework.beans.BeanUtils;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/module")
public class CModuleController {

    @Resource
    private CModuleService cModuleService;

    /**
     * 流程和代码模块列表
     *
     * @param queryDto
     * @throws NoLoginException
     */
    @PostMapping("/processModuleList")
    public AppResponse<List<ProcessModuleListVo>> processModuleList(@RequestBody ProcessModuleListDto queryDto)
            throws NoLoginException {
        return cModuleService.processModuleList(queryDto);
    }

    /**
     * 代码模块列表
     *
     * @param queryDto
     * @throws NoLoginException
     */
    @PostMapping("/moduleList")
    public AppResponse<List<ModuleListVo>> moduleList(@RequestBody ProcessModuleListDto queryDto)
            throws NoLoginException {
        return cModuleService.moduleList(queryDto);
    }

    /**
     * 新建代码模块
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("create")
    public AppResponse<OpenModuleVo> create(@RequestBody CreateModuleDto queryDto) throws NoLoginException {
        return cModuleService.create(queryDto);
    }

    /**
     * 新建代码模块名称
     *
     * @param robotId
     * @return
     * @throws NoLoginException
     */
    @RequestMapping("newModuleName")
    public AppResponse<String> newModuleName(@RequestParam String robotId) throws NoLoginException {
        return cModuleService.newModuleName(robotId);
    }

    /**
     * 重命名代码模块
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("rename")
    public AppResponse<Boolean> rename(@RequestBody RenameModuleDto queryDto) throws NoLoginException {
        return cModuleService.rename(queryDto);
    }

    /**
     * 删除模块接口
     *
     * @param moduleId
     * @return
     * @throws NoLoginException
     */
    @GetMapping("delete")
    public AppResponse<Boolean> delete(@RequestParam String moduleId) throws NoLoginException, SQLException {
        return cModuleService.delete(moduleId);
    }

    /**
     * 打开模块文件
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("open")
    public AppResponse<OpenModuleVo> open(@RequestBody @Valid OpenModuleDto queryDto) throws NoLoginException {
        BaseDto baseDto = new BaseDto();
        BeanUtils.copyProperties(queryDto, baseDto);
        return cModuleService.open(baseDto, queryDto.getModuleId());
    }

    /**
     * 保存指定代码模块
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("save")
    public AppResponse<Boolean> save(@RequestBody SaveModuleDto queryDto) throws NoLoginException, SQLException {
        return cModuleService.save(queryDto);
    }
}

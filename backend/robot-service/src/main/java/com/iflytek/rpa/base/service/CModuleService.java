package com.iflytek.rpa.base.service;

import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CreateModuleDto;
import com.iflytek.rpa.base.entity.dto.ProcessModuleListDto;
import com.iflytek.rpa.base.entity.dto.RenameModuleDto;
import com.iflytek.rpa.base.entity.vo.ModuleListVo;
import com.iflytek.rpa.base.entity.vo.OpenModuleVo;
import com.iflytek.rpa.base.entity.vo.ProcessModuleListVo;
import com.iflytek.rpa.robot.entity.dto.SaveModuleDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;

public interface CModuleService {

    AppResponse<List<ProcessModuleListVo>> processModuleList(ProcessModuleListDto queryDto) throws NoLoginException;

    AppResponse<List<ModuleListVo>> moduleList(ProcessModuleListDto queryDto) throws NoLoginException;

    AppResponse<OpenModuleVo> create(CreateModuleDto queryDto) throws NoLoginException;

    AppResponse<String> newModuleName(String robotId) throws NoLoginException;

    AppResponse<OpenModuleVo> open(BaseDto baseDto, String moduleId) throws NoLoginException;

    AppResponse<Boolean> delete(String moduleId) throws NoLoginException, SQLException;

    AppResponse<Boolean> save(SaveModuleDto queryDto) throws NoLoginException, SQLException;

    AppResponse<Boolean> rename(RenameModuleDto queryDto) throws NoLoginException;

    Map<String, String> copyCodeModule(String robotId, String processOrModuleId);
}

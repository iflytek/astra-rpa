package com.iflytek.rpa.base.service;

import com.iflytek.rpa.base.entity.CProcess;
import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CProcessDto;
import com.iflytek.rpa.base.entity.dto.CreateProcessDto;
import com.iflytek.rpa.base.entity.dto.RenameProcessDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.Map;

/**
 * 流程项id数据(CProcess)表服务接口
 *
 * @author mjren
 * @since 2024-10-09 17:11:14
 */
public interface CProcessService {

    AppResponse<String> getProcessNextName(String robotId);

    AppResponse<Map> createNewProcess(CreateProcessDto processDto) throws NoLoginException;

    AppResponse<Boolean> renameProcess(RenameProcessDto processDto) throws NoLoginException;

    AppResponse<?> getAllProcessData(CProcess process);

    AppResponse<?> saveProcessContent(CProcessDto process) throws NoLoginException;

    AppResponse<?> getProcessDataByProcessId(BaseDto baseDto) throws NoLoginException;

    AppResponse<?> getProcessNameList(BaseDto baseDto) throws NoLoginException;

    AppResponse<?> copySubProcess(String robotId, String processId, String type);

    AppResponse<Boolean> deleteProcess(CProcessDto processDto) throws NoLoginException;
}

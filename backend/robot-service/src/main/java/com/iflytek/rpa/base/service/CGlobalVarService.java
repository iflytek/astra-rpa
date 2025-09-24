package com.iflytek.rpa.base.service;

import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CGlobalDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;

/**
 * 客户端-全局变量(CGlobalVar)表服务接口
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
public interface CGlobalVarService {

    AppResponse<?> getGlobalVarInfoList(BaseDto baseDto) throws NoLoginException;

    AppResponse<?> createGlobalVar(CGlobalDto globalDto) throws NoLoginException;

    AppResponse<?> saveGlobalVar(CGlobalDto globalDto);

    AppResponse<?> getGlobalVarNameList(String robotId) throws NoLoginException;

    AppResponse<?> deleteGlobalVar(CGlobalDto globalDto) throws NoLoginException;
}

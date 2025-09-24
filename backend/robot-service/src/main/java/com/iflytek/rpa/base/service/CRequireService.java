package com.iflytek.rpa.base.service;

import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CRequireDeleteDto;
import com.iflytek.rpa.base.entity.dto.CRequireDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import javax.validation.Valid;

/**
 * python依赖管理(CRequire)表服务接口
 *
 * @author mjren
 * @since 2024-10-14 17:21:35
 */
public interface CRequireService {

    AppResponse<?> getRequireInfoList(BaseDto baseDto) throws NoLoginException;

    AppResponse<?> addRequire(CRequireDto crequireDto) throws NoLoginException;

    AppResponse<?> deleteProject(@Valid CRequireDeleteDto cRequireDeleteDto) throws NoLoginException;

    AppResponse<?> updateRequire(@Valid CRequireDto crequireDto) throws NoLoginException;
}

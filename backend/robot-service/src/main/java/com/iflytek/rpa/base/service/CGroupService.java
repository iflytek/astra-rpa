package com.iflytek.rpa.base.service;

import com.iflytek.rpa.base.entity.dto.ServerBaseDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;

/**
 * 元素或图像的分组(CGroup)表服务接口
 *
 * @author mjren
 * @since 2024-12-04 10:28:54
 */
public interface CGroupService {

    AppResponse<?> createGroup(ServerBaseDto serverBaseDto) throws NoLoginException;

    AppResponse<?> renameGroup(ServerBaseDto serverBaseDto) throws NoLoginException;

    AppResponse<?> deleteGroup(ServerBaseDto serverBaseDto) throws NoLoginException;
}

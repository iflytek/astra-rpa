package com.iflytek.rpa.base.service;

import com.iflytek.rpa.base.entity.dto.ServerBaseDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;

/**
 * 客户端，元素信息(CElement)表服务接口
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
public interface CElementService {

    //    AppResponse<?> getElementNameList(BaseDto baseDto) throws NoLoginException;

    AppResponse<?> getElementDetail(ServerBaseDto serverBaseDto) throws NoLoginException;

    AppResponse<?> moveElementOrImage(ServerBaseDto serverBaseDto) throws NoLoginException;

    AppResponse<?> deleteElementOrImage(ServerBaseDto serverBaseDto) throws NoLoginException;

    AppResponse<?> createImageName(ServerBaseDto serverBaseDto) throws NoLoginException;

    AppResponse<?> createElement(ServerBaseDto serverBaseDto) throws NoLoginException;

    AppResponse<?> updateElement(ServerBaseDto serverBaseDto) throws NoLoginException;

    AppResponse<?> copyElement(ServerBaseDto serverBaseDto) throws NoLoginException;

    AppResponse<?> getAllGroupInfo(ServerBaseDto serverBaseDto);
}

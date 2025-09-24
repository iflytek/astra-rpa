package com.iflytek.rpa.base.service;

import com.iflytek.rpa.base.entity.vo.AtomLikeVo;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;

public interface AtomLikeService {
    AppResponse<Boolean> createLikeAtom(String atomKey) throws NoLoginException;

    AppResponse<Boolean> cancelLikeAtom(Long likeId) throws NoLoginException;

    AppResponse<List<AtomLikeVo>> likeList() throws NoLoginException;
}

package com.iflytek.rpa.base.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.base.entity.AtomCommon;
import com.iflytek.rpa.base.entity.Atomic;
import com.iflytek.rpa.base.entity.dto.AtomKeyListDto;
import com.iflytek.rpa.base.entity.dto.AtomListDto;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.Map;
import javax.validation.Valid;

public interface CAtomMetaService {

    AppResponse<?> getAtomTree(String atomKey);

    AppResponse<?> getAtomListByParentKey(String parentKey);

    AppResponse<?> getLatestAtomByKey(String atomKey);

    AppResponse<?> getLatestAtomsByList(@Valid AtomKeyListDto dto);

    AppResponse<?> getAtomList(AtomListDto atomListVo);

    AppResponse<?> addAtomCommonInfo(AtomCommon atomCommon) throws JsonProcessingException;

    AppResponse<?> updateAtomCommonInfo(AtomCommon atomCommon) throws JsonProcessingException;

    AppResponse<?> saveAtomicsInfo(Map<String, Atomic> atomMap, String saveWay) throws JsonProcessingException;

    Map getLatestAllAtoms() throws JsonProcessingException;
}

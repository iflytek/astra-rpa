package com.iflytek.rpa.base.service.handler;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import com.iflytek.rpa.base.entity.dto.QueryParamDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.List;

public interface ParamModeHandler {

    boolean supports(String mode);

    AppResponse<List<ParamDto>> handle(QueryParamDto dto) throws JsonProcessingException, NoLoginException;
}

package com.iflytek.rpa.base.service.handler;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.base.entity.CParam;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;
import org.springframework.beans.BeanUtils;

/**
 * @author mjren
 * @date 2025-04-17 15:15
 * @copyright Copyright (c) 2025 mjren
 */
public class ParamConverter {
    private static final ObjectMapper mapper = new ObjectMapper();

    public static List<ParamDto> convert(List<CParam> params) {
        return Optional.ofNullable(params).orElse(Collections.emptyList()).stream()
                .map(ParamConverter::convert)
                .collect(Collectors.toList());
    }

    public static ParamDto convert(CParam param) {
        ParamDto dto = new ParamDto();
        BeanUtils.copyProperties(param, dto);
        return dto;
    }

    public static List<CParam> parseJsonParams(String json) throws JsonProcessingException {
        return mapper.readValue(json, new TypeReference<List<CParam>>() {});
    }
}

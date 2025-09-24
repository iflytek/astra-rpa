package com.iflytek.rpa.base.entity.dto;

import com.iflytek.rpa.base.entity.Atomic;
import java.util.Map;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-03-10 16:23
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class SaveAtomicsDto {

    private Map<String, Atomic> atomMap;

    private String saveWay;
}

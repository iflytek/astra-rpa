package com.iflytek.rpa.base.entity.dto;

import lombok.Data;

/**
 * @author mjren
 * @date 2025-04-29 17:12
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class CreateProcessDto {

    private String robotId;

    private String processName;

    private String processContent;
}

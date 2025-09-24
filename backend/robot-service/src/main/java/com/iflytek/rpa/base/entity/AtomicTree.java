package com.iflytek.rpa.base.entity;

import java.util.List;
import javax.validation.Valid;
import javax.validation.constraints.NotBlank;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-02-19 10:31
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class AtomicTree {
    @NotBlank(message = "key 不能为空")
    private String key;

    @NotBlank(message = "title 不能为空")
    private String title;

    @Valid
    private List<AtomicTree> atomics;

    private String icon;
}

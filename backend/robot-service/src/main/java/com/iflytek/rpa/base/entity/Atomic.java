package com.iflytek.rpa.base.entity;

import java.util.List;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-02-20 14:25
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class Atomic {

    private String key;
    private String title;
    private String version;
    private String src;
    private String comment;
    private List<Object> inputList;
    private List<Object> outputList;
    private String icon;
    private String helpManual;
    private Boolean noAdvanced;
}

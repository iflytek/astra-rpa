package com.iflytek.rpa.base.entity;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;
import javax.validation.Valid;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-02-19 10:50
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class CommonAdvancedParameter {
    @NotBlank(message = "CommonAdvancedParameter.types 不能为空")
    private String types;

    @Valid
    @NotNull(message = "CommonAdvancedParameter.formType 不能为空")
    private FormType formType;

    @NotBlank(message = "CommonAdvancedParameter.key 不能为空")
    private String key;

    @NotBlank(message = "CommonAdvancedParameter.title 不能为空")
    private String title;

    @NotBlank(message = "CommonAdvancedParameter.name 不能为空")
    private String name;

    private String need_parse;

    private List<Dynamic> dynamics;

    @JsonProperty("default") // 将 JSON 中的 "default" 映射到 defaultValue
    private Object defaultValue;

    @Valid
    private List<Option> options;

    @Data
    public static class FormType {
        @NotBlank(message = "FormType.type 不能为空")
        private String type;

        private Object params;
    }

    @Data
    public static class Option {
        @NotBlank(message = "Option.label 不能为空")
        private String label;

        private Object value;
    }

    @Data
    public static class Dynamic {
        private String key;
        private String expression;
    }

    /*    @Data
    public static class Conditional{
        private String operators;
        private OperandItem[] Operands;
    }*/

    @Data
    public static class OperandItem {
        private String left;
        private String right;
        private Object operator;
    }
}

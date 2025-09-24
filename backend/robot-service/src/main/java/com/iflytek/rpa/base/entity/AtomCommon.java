package com.iflytek.rpa.base.entity;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import javax.validation.Valid;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-02-19 10:26
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class AtomCommon {

    /**
     * 层级顺序关系
     */
    @Valid
    @NotNull(message = "atomicTree 不能为空")
    private List<AtomicTree> atomicTree;

    /**
     * 我的收藏等层级顺序关系
     */
    @Valid
    private List<AtomicTree> atomicTreeExtend;

    /**
     * 高级参数
     */
    @Valid
    @NotNull(message = "commonAdvancedParameter 不能为空")
    private List<CommonAdvancedParameter> commonAdvancedParameter;

    /**
     * 变量类型
     */
    @Valid
    @NotNull(message = "types 不能为空")
    private Map<String, TypeInfo> types;

    public static List<String> getPropertyNames() {
        List<String> propertyNames = new ArrayList<>();
        Field[] fields = AtomCommon.class.getDeclaredFields();

        for (Field field : fields) {
            propertyNames.add(field.getName());
        }

        return propertyNames;
    }

    @Data
    public static class TypeInfo {
        @NotBlank(message = "types.key 不能为空")
        private String key;

        private String src;

        @NotBlank(message = "types.desc 不能为空")
        private String desc;

        @NotBlank(message = "types.version 不能为空")
        private String version;

        private String channel;

        private String template;

        @Valid
        private List<FuncItem> funcList;
    }

    @Data
    public static class FuncItem {
        @NotBlank(message = "funcList.key 不能为空")
        private String key;

        @NotBlank(message = "funcList.funcDesc 不能为空")
        private String funcDesc;

        @NotBlank(message = "funcList.resType 不能为空")
        private String resType;

        @NotBlank(message = "funcList.resDesc 不能为空")
        private String resDesc;

        @NotBlank(message = "funcList.useSrc 不能为空")
        private String useSrc;
    }
}

package com.iflytek.rpa.base.entity.dto;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;
import lombok.Data;

@Data
public class AtomTreeDto {
    /**
     * 层级顺序关系
     */
    private String atomicTree;

    /**
     * 我的收藏等层级顺序关系
     */
    private String atomicTreeExtend;

    /**
     * 高级参数
     */
    private String commonAdvancedParameter;

    /**
     * 变量类型
     */
    private String types;

    public static List<String> getPropertyNames() {
        List<String> propertyNames = new ArrayList<>();
        Field[] fields = AtomTreeDto.class.getDeclaredFields();

        for (Field field : fields) {
            propertyNames.add(field.getName());
        }

        return propertyNames;
    }

    //    /**
    //     * 节点key
    //     */
    //    private String key;
    //
    //    /**
    //     * 原子能力内容
    //     */
    //    private String atomContent;
}

package com.iflytek.rpa.robot.entity.enums;

import lombok.Getter;

@Getter
public enum SharedVarTypeEnum {
    TEXT("text", "文本"),
    PASSWORD("password", "密码"),
    ARRAY("array", "数组"),
    GROUP("group", "变量组"),
    ;

    private final String code;
    private final String name;

    SharedVarTypeEnum(String code, String name) {
        this.code = code;
        this.name = name;
    }
}

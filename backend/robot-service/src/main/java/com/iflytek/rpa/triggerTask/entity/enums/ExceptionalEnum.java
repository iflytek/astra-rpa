package com.iflytek.rpa.triggerTask.entity.enums;

import lombok.Getter;

@Getter
public enum ExceptionalEnum {
    JUMP("jump", "跳过"),
    STOP("stop", "中止"),
    ;

    private String code;
    private String name;

    ExceptionalEnum(String code, String name) {
        this.code = code;
        this.name = name;
    }
}

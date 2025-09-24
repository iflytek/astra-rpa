package com.iflytek.rpa.robot.entity.enums;

import lombok.Getter;

/**
 * 文件向量化状态
 */
@Getter
public enum FileIndexStatus {
    START("初始化", 1),
    END("完成", 2),
    FAIL("失败", 3),
    ;

    private final String comment;
    private final Integer value;

    FileIndexStatus(String comment, Integer value) {
        this.comment = comment;
        this.value = value;
    }
}

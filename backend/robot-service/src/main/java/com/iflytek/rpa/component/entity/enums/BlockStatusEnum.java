package com.iflytek.rpa.component.entity.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * 屏蔽状态枚举
 *
 * @author makejava
 * @since 2024-12-19
 */
@Getter
@AllArgsConstructor
public enum BlockStatusEnum {

    /**
     * 未屏蔽
     */
    UNBLOCKED(0, "未屏蔽"),

    /**
     * 已屏蔽
     */
    BLOCKED(1, "已屏蔽");

    /**
     * 状态码
     */
    private final Integer code;

    /**
     * 状态描述
     */
    private final String description;

    /**
     * 根据状态码获取枚举
     */
    public static BlockStatusEnum getByCode(Integer code) {
        if (code == null) {
            return null;
        }
        for (BlockStatusEnum status : values()) {
            if (status.getCode().equals(code)) {
                return status;
            }
        }
        return null;
    }

    /**
     * 判断是否为有效状态码
     */
    public static boolean isValidCode(Integer code) {
        return getByCode(code) != null;
    }
}

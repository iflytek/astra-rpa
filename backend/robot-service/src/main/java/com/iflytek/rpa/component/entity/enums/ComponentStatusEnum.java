package com.iflytek.rpa.component.entity.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * 组件状态枚举
 *
 * @author makejava
 * @since 2024-12-19
 */
@Getter
@AllArgsConstructor
public enum ComponentStatusEnum {

    /**
     * 资源状态枚举
     */
    RESOURCE_STATUS_TO_OBTAIN("toObtain", "待获取"),
    RESOURCE_STATUS_OBTAINED("obtained", "已获取"),
    RESOURCE_STATUS_TO_UPDATE("toUpdate", "待更新"),

    /**
     * 数据来源枚举
     */
    DATA_SOURCE_CREATE("create", "自己创建"),
    DATA_SOURCE_MARKET("market", "市场获取"),

    /**
     * 转换状态枚举
     */
    TRANSFORM_STATUS_EDITING("editing", "编辑中"),
    TRANSFORM_STATUS_PUBLISHED("published", "已发版"),
    TRANSFORM_STATUS_SHARED("shared", "已上架"),
    TRANSFORM_STATUS_LOCKED("locked", "锁定");

    /**
     * 状态码
     */
    private final String code;

    /**
     * 状态名称
     */
    private final String name;

    /**
     * 根据状态码获取状态名称
     */
    public static String getNameByCode(String code) {
        for (ComponentStatusEnum statusEnum : values()) {
            if (statusEnum.getCode().equals(code)) {
                return statusEnum.getName();
            }
        }
        return "未知状态";
    }

    /**
     * 根据状态码获取枚举
     */
    public static ComponentStatusEnum getByCode(String code) {
        for (ComponentStatusEnum statusEnum : values()) {
            if (statusEnum.getCode().equals(code)) {
                return statusEnum;
            }
        }
        return null;
    }
}

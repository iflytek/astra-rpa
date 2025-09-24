package com.iflytek.rpa.component.constants;

/**
 * 组件常量
 *
 * @author makejava
 * @since 2024-12-19
 */
public class ComponentConstant {

    /**
     * 资源状态：待获取
     */
    public static final String RESOURCE_STATUS_TO_OBTAIN = "toObtain";

    /**
     * 资源状态：已获取
     */
    public static final String RESOURCE_STATUS_OBTAINED = "obtained";

    /**
     * 资源状态：待更新
     */
    public static final String RESOURCE_STATUS_TO_UPDATE = "toUpdate";

    /**
     * 数据来源：自己创建
     */
    public static final String DATA_SOURCE_CREATE = "create";

    /**
     * 数据来源：市场获取
     */
    public static final String DATA_SOURCE_MARKET = "market";

    /**
     * 转换状态：编辑中
     */
    public static final String TRANSFORM_STATUS_EDITING = "editing";

    /**
     * 转换状态：已发版
     */
    public static final String TRANSFORM_STATUS_PUBLISHED = "published";

    /**
     * 转换状态：已上架
     */
    public static final String TRANSFORM_STATUS_SHARED = "shared";

    /**
     * 转换状态：锁定
     */
    public static final String TRANSFORM_STATUS_LOCKED = "locked";

    /**
     * 是否显示：不显示
     */
    public static final Integer IS_SHOWN_NO = 0;

    /**
     * 是否显示：显示
     */
    public static final Integer IS_SHOWN_YES = 1;

    /**
     * 是否删除：未删除
     */
    public static final Integer DELETED_NO = 0;

    /**
     * 是否删除：已删除
     */
    public static final Integer DELETED_YES = 1;
}

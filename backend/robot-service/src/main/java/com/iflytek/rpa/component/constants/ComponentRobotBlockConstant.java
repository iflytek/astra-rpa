package com.iflytek.rpa.component.constants;

/**
 * 机器人对组件屏蔽相关常量
 *
 * @author makejava
 * @since 2024-12-19
 */
public class ComponentRobotBlockConstant {

    /**
     * 表名
     */
    public static final String TABLE_NAME = "component_robot_block";

    /**
     * 删除状态 - 未删除
     */
    public static final Integer DELETED_NO = 0;

    /**
     * 删除状态 - 已删除
     */
    public static final Integer DELETED_YES = 1;

    /**
     * 默认机器人版本号
     */
    public static final Integer DEFAULT_ROBOT_VERSION = 1;

    /**
     * 批量操作最大数量限制
     */
    public static final Integer MAX_BATCH_SIZE = 100;

    /**
     * 错误消息
     */
    public static class ErrorMessage {
        /**
         * 机器人ID不能为空
         */
        public static final String ROBOT_ID_EMPTY = "机器人ID不能为空";

        /**
         * 组件ID不能为空
         */
        public static final String COMPONENT_ID_EMPTY = "组件ID不能为空";

        /**
         * 机器人版本号不能为空
         */
        public static final String ROBOT_VERSION_EMPTY = "机器人版本号不能为空";

        /**
         * 批量操作数量超出限制
         */
        public static final String BATCH_SIZE_EXCEEDED = "批量操作数量不能超过" + MAX_BATCH_SIZE + "个";

        /**
         * 屏蔽记录已存在
         */
        public static final String BLOCK_ALREADY_EXISTS = "该组件已被该机器人屏蔽";

        /**
         * 屏蔽记录不存在
         */
        public static final String BLOCK_NOT_EXISTS = "未找到屏蔽记录";
    }

    /**
     * 成功消息
     */
    public static class SuccessMessage {
        /**
         * 添加屏蔽成功
         */
        public static final String ADD_SUCCESS = "添加屏蔽成功";

        /**
         * 移除屏蔽成功
         */
        public static final String REMOVE_SUCCESS = "移除屏蔽成功";

        /**
         * 批量添加屏蔽成功
         */
        public static final String BATCH_ADD_SUCCESS = "批量添加屏蔽成功";

        /**
         * 批量移除屏蔽成功
         */
        public static final String BATCH_REMOVE_SUCCESS = "批量移除屏蔽成功";
    }
}

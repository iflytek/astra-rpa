package com.iflytek.rpa.robot.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import lombok.Data;

/**
 * 共享变量与用户的映射表(SharedVarUser)实体类
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
public class SharedVarUser implements Serializable {
    private static final long serialVersionUID = 221373423657236319L;

    /**
     * 主键id
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 共享变量id
     */
    private Long sharedVarId;

    /**
     * 用户id
     */
    private String userId;

    /**
     * 用户姓名
     */
    private String userName;

    /**
     * 用户手机号
     */
    private String userPhone;

    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;
}

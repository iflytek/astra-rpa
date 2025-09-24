package com.iflytek.rpa.robot.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import lombok.Data;

/**
 * 共享变量-子变量(SharedSubVar)实体类
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
public class SharedSubVar implements Serializable {
    private static final long serialVersionUID = 222473423657236318L;

    /**
     * 子变量id
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 共享变量id
     */
    private Long sharedVarId;

    /**
     * 子变量名
     */
    private String varName;

    /**
     * 变量类型：text/password/array
     */
    private String varType;

    /**
     * 变量具体值，加密则为密文，否则为明文
     */
    private String varValue;

    /**
     * 是否加密:1-加密
     */
    private Integer encrypt;

    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;
}

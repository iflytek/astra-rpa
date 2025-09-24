package com.iflytek.rpa.robot.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import lombok.Data;

/**
 * 共享变量租户密钥表(SharedVarKeyTenant)实体类
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Data
public class SharedVarKeyTenant implements Serializable {
    private static final long serialVersionUID = 221473413657231318L;

    /**
     * 主键id
     */
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /**
     * 租户id
     */
    private String tenantId;

    /**
     * 共享变量租户密钥
     */
    private String key;

    /**
     * 是否删除 0：未删除，1：已删除
     */
    private Integer deleted;
}

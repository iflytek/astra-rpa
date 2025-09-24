package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import java.util.Date;
import lombok.Data;

/**
 * 收藏的原子表
 * 收藏到 "用户" 级别
 */
@Data
public class AtomLike {
    @TableId(value = "id", type = IdType.AUTO)
    Long id;

    Long likeId; // 收藏id
    String atomKey; // 原子能力的key，全局唯一
    String creatorId; // 用户id
    String updaterId;
    String tenantId; // 租户id

    @TableLogic(value = "0", delval = "1")
    Integer isDeleted;

    Date createTime;
    Date updateTime;
}

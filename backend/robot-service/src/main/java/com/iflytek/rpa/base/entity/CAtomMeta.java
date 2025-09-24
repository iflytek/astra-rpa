package com.iflytek.rpa.base.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.util.Date;
import lombok.Data;

/**
 * @author mjren
 * @date 2025-02-18 16:33
 * @copyright Copyright (c) 2025 mjren
 */
@Data
public class CAtomMeta {

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private String parentKey;

    private String atomKey;

    private String atomContent;

    private String version;

    private Integer sort;

    private Integer versionNum;

    private Integer deleted;

    private String creatorId;

    private Date createTime;

    private String updaterId;

    private Date updateTime;
}

package com.iflytek.rpa.base.entity.vo;

import java.util.List;
import lombok.Data;

@Data
public class GroupInfoVo {
    /**
     * 分组名称
     */
    private String name;

    /**
     * 分组id
     */
    private String id;

    /**
     * 该组内所有图片对象
     */
    private List<com.iflytek.rpa.base.entity.vo.ElementInfoVo> elements;
}

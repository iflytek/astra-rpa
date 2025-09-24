package com.iflytek.rpa.base.entity.vo;

import lombok.Data;

@Data
public class ElementInfoVo {

    /**
     * 元素id
     */
    private String id;

    /**
     * 元素名称
     */
    private String name;

    /**
     * 图片链接
     */
    private String imageUrl;

    /**
     * parentImageUrl
     */
    private String parentImageUrl;

    /**
     * cv图像, sigle普通拾取，batch数据抓取
     */
    private String commonSubType;
}

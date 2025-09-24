package com.iflytek.rpa.base.entity.vo;

import lombok.Data;

/**
 * 收藏的原子能力vo
 */
@Data
public class AtomLikeVo {
    Long likeId;
    String key;
    String atomContent;
    String title;
    String icon;
}

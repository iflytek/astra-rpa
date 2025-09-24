package com.iflytek.rpa.component.entity.dto;

import javax.validation.constraints.Min;
import lombok.Data;

/**
 * 组件列表查询DTO
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
public class ComponentListDto {

    String sortType = "desc"; // asc desc

    /**
     * 页码
     */
    @Min(value = 1, message = "页码必须大于0")
    private Integer pageNum = 1;

    /**
     * 每页大小
     */
    @Min(value = 1, message = "每页大小必须大于0")
    private Integer pageSize = 10;

    /**
     * 组件名称（模糊查询）
     */
    private String name;

    /**
     * 数据来源 create:创建的 ; market:市场
     */
    private String dataSource = "create";
}

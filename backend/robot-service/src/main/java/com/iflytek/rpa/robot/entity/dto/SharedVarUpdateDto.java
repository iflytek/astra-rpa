package com.iflytek.rpa.robot.entity.dto;

import javax.validation.constraints.NotNull;
import lombok.Data;

/**
 * 共享变量更新DTO
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Data
public class SharedVarUpdateDto extends SharedVarSaveDto {

    /**
     * 共享变量ID
     */
    @NotNull(message = "共享变量ID不能为空")
    private Long id;
}

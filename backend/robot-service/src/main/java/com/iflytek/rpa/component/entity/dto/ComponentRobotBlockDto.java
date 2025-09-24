package com.iflytek.rpa.component.entity.dto;

import java.util.List;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 机器人对组件屏蔽数据传输对象
 *
 * @author makejava
 * @since 2024-12-19
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class ComponentRobotBlockDto {

    /**
     * 机器人id
     */
    @NotBlank(message = "机器人ID不能为空")
    private String robotId;

    /**
     * 机器人版本号
     */
    @NotNull(message = "机器人版本号不能为空")
    private Integer robotVersion;

    /**
     * 组件id列表
     */
    @NotNull(message = "组件ID列表不能为空")
    private List<String> componentIds;
}

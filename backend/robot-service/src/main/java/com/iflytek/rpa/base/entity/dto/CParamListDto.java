package com.iflytek.rpa.base.entity.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.iflytek.rpa.base.entity.CParam;
import java.util.ArrayList;
import java.util.List;
import lombok.Data;

/**
 * @author tzzhang
 * @date 2025/3/25 17:07
 */
@Data
public class CParamListDto {
    @JsonProperty("paramList")
    private List<CParam> paramList = new ArrayList<>();

    //    /**
    //     * 运行位置，默认编辑页，EDIT_PAGE编辑页,PROJECT_LIST设计器列表页,EXECUTOR执行器机器人列表页,CRONTAB触发器（本地计划任务）
    //     */
    //    @NotBlank(message = "运行位置不能为空")
    //    @Pattern(regexp = "EDIT_PAGE|PROJECT_LIST|EXECUTOR|CRONTAB", message =
    // "参数值必须是EDIT_PAGE|PROJECT_LIST|EXECUTOR|CRONTAB")
    //    private String mode = EDIT_PAGE;

}

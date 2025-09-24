package com.iflytek.rpa.base.entity.dto;

import java.util.List;
import javax.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class CRequireDeleteDto {
    @NotBlank
    private String robotId;

    private List<Integer> idList;

    private String creatorId;
}

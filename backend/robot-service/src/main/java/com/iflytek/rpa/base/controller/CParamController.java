package com.iflytek.rpa.base.controller;

import com.baomidou.mybatisplus.core.toolkit.StringUtils;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.base.entity.dto.CParamDto;
import com.iflytek.rpa.base.entity.dto.CParamListDto;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import com.iflytek.rpa.base.entity.dto.QueryParamDto;
import com.iflytek.rpa.base.service.CParamService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import java.util.List;
import javax.annotation.Resource;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.*;

/**
 * 参数管理
 */
@RestController
@RequestMapping("/param")
public class CParamController {
    @Resource
    private CParamService cParamService;

    /**
     * 查询流程参数
     *
     * @param
     * @return
     */
    @PostMapping("/all")
    public AppResponse<List<ParamDto>> getAllParams(@RequestBody @Valid QueryParamDto queryParamDto)
            throws JsonProcessingException, NoLoginException {
        // 判断机器人robotId是否为null
        if (StringUtils.isBlank(queryParamDto.getRobotId())) {
            throw new ServiceException((ErrorCodeEnum.E_SQL.getCode()), "机器人id不能为空");
        }
        return cParamService.getAllParams(queryParamDto);
    }

    /**
     * 新增流程参数
     *
     * @param ParamDto
     * @return
     */
    @PostMapping("/add")
    public AppResponse<String> addParam(@RequestBody @Valid CParamDto ParamDto) throws NoLoginException {

        return cParamService.addParam(ParamDto);
    }

    /**
     * 删除流程参数
     *
     * @param id
     * @return
     */
    @PutMapping("/delete")
    public AppResponse<Boolean> deleteParam(@RequestParam(value = "id") String id) {
        // 判断id是否为空
        if (StringUtils.isBlank(id)) {
            throw new ServiceException((ErrorCodeEnum.E_SQL.getCode()), "参数id不能为空");
        }
        return cParamService.deleteParam(id);
    }

    /**
     * 修改流程参数
     *
     * @param paramDto
     * @return
     */
    @PutMapping("/update")
    public AppResponse<Boolean> updateParam(@Valid @RequestBody CParamDto paramDto) throws NoLoginException {
        return cParamService.updateParam(paramDto);
    }

    /**
     * 保存用户自定义参数
     *
     * @param paramListDto
     * @return
     * @throws NoLoginException
     * @throws JsonProcessingException
     */
    @PostMapping("/saveUserParam")
    public AppResponse<Boolean> saveUserParam(@RequestBody CParamListDto paramListDto)
            throws NoLoginException, JsonProcessingException {

        return cParamService.saveUserParam(paramListDto.getParamList());
    }
}

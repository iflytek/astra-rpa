package com.iflytek.rpa.base.controller;

import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CRequireDeleteDto;
import com.iflytek.rpa.base.entity.dto.CRequireDto;
import com.iflytek.rpa.base.service.CRequireService;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import javax.annotation.Resource;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * python依赖管理(CRequire)表控制层
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
@RestController
@RequestMapping("/require")
public class CRequireController {
    /**
     * 服务对象
     */
    @Resource
    private CRequireService cRequireService;

    @PostMapping("/list")
    public AppResponse<?> getRequireInfoList(@RequestBody @Valid BaseDto baseDto) throws Exception {
        return cRequireService.getRequireInfoList(baseDto);
    }

    /**
     * 新增python包管理
     *
     * @param crequireDto 依赖信息
     * @return 响应结果
     */
    @PostMapping("/add")
    public AppResponse<?> addProject(@RequestBody @Valid CRequireDto crequireDto) throws Exception {
        return cRequireService.addRequire(crequireDto);
    }

    /**
     * 删除python包管理
     *
     * @param cRequireDeleteDto 依赖信息
     * @return 响应结果
     */
    @PostMapping("/delete")
    public AppResponse<?> deleteProject(@RequestBody @Valid CRequireDeleteDto cRequireDeleteDto) throws Exception {
        return cRequireService.deleteProject(cRequireDeleteDto);
    }

    /**
     * 更新python包管理
     *
     * @param crequireDto 依赖信息
     * @return 响应结果
     */
    @PostMapping("/update")
    public AppResponse<?> updateRequire(@RequestBody @Valid CRequireDto crequireDto) throws Exception {
        return cRequireService.updateRequire(crequireDto);
    }
}

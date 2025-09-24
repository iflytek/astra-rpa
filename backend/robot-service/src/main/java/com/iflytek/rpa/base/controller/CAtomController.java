package com.iflytek.rpa.base.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.iflytek.rpa.base.entity.AtomCommon;
import com.iflytek.rpa.base.entity.dto.AtomKeyListDto;
import com.iflytek.rpa.base.entity.dto.AtomListDto;
import com.iflytek.rpa.base.entity.dto.SaveAtomicsDto;
import com.iflytek.rpa.base.service.CAtomMetaService;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.util.Map;
import javax.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 原子能力定义信息
 */
@RestController
@RequestMapping("/atom")
public class CAtomController {

    @Autowired
    private CAtomMetaService cAtomMetaService;

    /**
     * 获取原子能力树层级关系和公共信息
     */
    @PostMapping("/tree")
    public AppResponse<?> getAtomTree() {
        return cAtomMetaService.getAtomTree("atomCommon");
    }

    /**
     * 查询指定目录的原子能力定义
     */
    @PostMapping("/getListByParentKey")
    public AppResponse<?> getAtomListByParentKey(@RequestParam(name = "parentKey") String parentKey) {
        return cAtomMetaService.getAtomListByParentKey(parentKey);
    }

    /**
     * 根据key和version列表批量获取原子能力定义
     */
    @PostMapping("/getByVersionList")
    public AppResponse<?> getAtomList(@RequestBody AtomListDto atomListDto) throws Exception {
        return cAtomMetaService.getAtomList(atomListDto);
    }

    /**
     * 根据key查询单个原子能力最新的定义
     */
    @PostMapping("/getLatestAtomByKey")
    public AppResponse<?> getLatestAtomByKey(@RequestParam(name = "key") String atomKey) throws Exception {
        return cAtomMetaService.getLatestAtomByKey(atomKey);
    }

    /**
     * 根据 List[key] 批量查询原子能力最新定义
     */
    @PostMapping("/getLatestAtomsByList")
    public AppResponse<?> getLatestAtomsByList(@RequestBody AtomKeyListDto dto) throws Exception {
        return cAtomMetaService.getLatestAtomsByList(dto);
    }

    /**
     * 新增原子能力公共数据（types、commonAdvancedParameter、atomicTree、atomicTreeExtend）
     */
    @PostMapping("/add-common")
    public AppResponse<?> addAtomCommonInfo(@Valid @RequestBody AtomCommon atomCommon) throws JsonProcessingException {
        // todo 加密码，限流

        return cAtomMetaService.addAtomCommonInfo(atomCommon);
    }

    /**
     * 更新原子能力公共数据（types、commonAdvancedParameter、atomicTree、atomicTreeExtend）
     *
     * @param atomCommon
     * @return
     */
    @PostMapping("/update-common")
    public AppResponse<?> updateAtomCommonInfo(@Valid @RequestBody AtomCommon atomCommon)
            throws JsonProcessingException {
        // todo 加密码，限流
        return cAtomMetaService.updateAtomCommonInfo(atomCommon);
    }

    /**
     * 插入或更新原子能力定义信息（atomics），存入DB
     */
    @PostMapping("/save-atomics")
    public AppResponse<?> saveAtomicsInfo(@RequestBody SaveAtomicsDto saveAtomicsDto) throws Exception {

        return cAtomMetaService.saveAtomicsInfo(saveAtomicsDto.getAtomMap(), saveAtomicsDto.getSaveWay());
    }

    /**
     * 原子能力最新定义全量查询接口
     */
    @GetMapping("/getLatestAllAtoms")
    public Map getLatestAllAtoms() throws Exception {
        return cAtomMetaService.getLatestAllAtoms();
    }
}

package com.iflytek.rpa.base.dao;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.rpa.base.entity.CAtomMeta;
import com.iflytek.rpa.base.entity.dto.AtomListDto;
import java.util.List;
import java.util.Set;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface CAtomMetaDao extends BaseMapper<CAtomMeta> {

    //    List<CAtomMeta> getAtomTreeLast(@Param("atomKeyList") List<String> atomKeyList);

    List<String> getLatestAtomListByParentKey(@Param("parentKey") String parentKey);

    String getLatestAtomByKey(@Param("atomKey") String atomKey);

    List<CAtomMeta> selectAtomList(@Param("atomList") List<AtomListDto.Atom> atomList);

    CAtomMeta getAtomCommonBaseInfoByAtomKey(@Param("atomKey") String atomCommon);

    //    Integer insertAtomMeta(CAtomMeta atomMeta);

    List<CAtomMeta> getLatestAtomListByKeySet(@Param("atomKeySet") Set<String> atomKeySet);

    Integer UpdateBatchByKeyAndVersion(@Param("entities") List<CAtomMeta> updateBatchList);

    List<String> getLatestAllAtoms();

    List<CAtomMeta> getKeyAndParentKeyByKeySet(@Param("atomKeySet") Set<String> atomKeySet);

    Integer updateBatchParentKey(@Param("updateBatchList") List<CAtomMeta> updateBatchList);

    List<CAtomMeta> getLatestAtomsByList(List<String> atomKeyList);
}

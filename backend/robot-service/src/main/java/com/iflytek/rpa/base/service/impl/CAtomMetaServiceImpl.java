package com.iflytek.rpa.base.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.base.dao.AtomMetaDuplicateLogDao;
import com.iflytek.rpa.base.dao.CAtomMetaDao;
import com.iflytek.rpa.base.entity.*;
import com.iflytek.rpa.base.entity.dto.AtomKeyListDto;
import com.iflytek.rpa.base.entity.dto.AtomListDto;
import com.iflytek.rpa.base.service.CAtomMetaService;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.ListBatchUtil;
import java.lang.reflect.Field;
import java.util.*;
import java.util.stream.Collectors;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

/**
 * @author mjren
 * @date 2025-02-18 14:53
 * @copyright Copyright (c) 2025 mjren
 */
@Service("cAtomMetaService")
public class CAtomMetaServiceImpl extends ServiceImpl<CAtomMetaDao, CAtomMeta> implements CAtomMetaService {

    @Autowired
    private CAtomMetaDao cAtomMetaDao;

    @Autowired
    private AtomMetaDuplicateLogDao atomMetaDuplicateLogDao;

    @Override
    public AppResponse<?> getAtomTree(String atomKey) {

        // 查询最新信息

        //        List<String> atomKeySearch = new ArrayList<>();
        //        atomKeySearch.add("types");
        //        atomKeySearch.add("commonAdvancedParameter");
        //        atomKeySearch.add("atomicTree");
        //        atomKeySearch.add("atomicTreeExtend");
        String atomCommonInfo = cAtomMetaDao.getLatestAtomByKey(atomKey);
        // 根据atomkey分组
        //        Map<String, String> atomMap = atomList.stream().collect(Collectors.toMap(CAtomMeta::getAtomKey,
        // CAtomMeta::getAtomContent));
        //        AtomTreeDto atomTreeDto = new AtomTreeDto();
        //        atomTreeDto.setAtomicTree(atomMap.get("atomicTree"));
        //        atomTreeDto.setAtomicTreeExtend(atomMap.get("atomicTreeExtend"));
        //        atomTreeDto.setCommonAdvancedParameter(atomMap.get("commonAdvancedParameter"));
        //        atomTreeDto.setTypes(atomMap.get("types"));
        return AppResponse.success(atomCommonInfo);
    }

    @Override
    public AppResponse<?> getAtomListByParentKey(String parentKey) {
        if (StringUtils.isBlank(parentKey)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        List<String> atomContentList = cAtomMetaDao.getLatestAtomListByParentKey(parentKey);
        return AppResponse.success(atomContentList);
    }

    @Override
    public AppResponse<?> getLatestAtomByKey(String atomKey) {
        if (StringUtils.isBlank(atomKey)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        String atomContent = cAtomMetaDao.getLatestAtomByKey(atomKey);
        return AppResponse.success(atomContent);
    }

    @Override
    public AppResponse<?> getLatestAtomsByList(AtomKeyListDto dto) {
        List<String> atomKeyList = dto.getAtomKeyList();
        atomKeyList.removeIf(Objects::isNull);
        if (atomKeyList.isEmpty()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "atomKeyList不能为空");
        }
        return AppResponse.success(cAtomMetaDao.getLatestAtomsByList(atomKeyList));
    }

    @Override
    public AppResponse<?> getAtomList(AtomListDto atomListDto) {
        if (atomListDto == null || CollectionUtils.isEmpty(atomListDto.getAtomList())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        if (atomListDto.getAtomList().size() > 500) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE_NOT_SUPPORT, "一次最多查询500条");
        }

        List<CAtomMeta> atomMetaList = cAtomMetaDao.selectAtomList(atomListDto.getAtomList());
        // 根据atomkey+verison分组
        Map<String, String> atomMap = atomMetaList.stream()
                .collect(Collectors.toMap(
                        atom -> atom.getAtomKey() + "_" + atom.getVersion(),
                        CAtomMeta::getAtomContent,
                        (existing, replacement) -> existing // 处理键冲突的情况
                        ));
        List<AtomListDto.Atom> atomList = atomListDto.getAtomList();
        List<String> result = new ArrayList<>();
        for (AtomListDto.Atom atom : atomList) {
            if (null == atom) {
                continue;
            }
            result.add(atomMap.get(atom.getKey() + "_" + atom.getVersion()));
        }

        return AppResponse.success(result);
    }

    @Override
    public AppResponse<?> addAtomCommonInfo(AtomCommon atomCommon) throws JsonProcessingException {
        CAtomMeta atomCommonCount = cAtomMetaDao.getAtomCommonBaseInfoByAtomKey("atomCommon");
        if (atomCommonCount != null) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "数据已存在，请勿重复新增");
        } else {
            // 新增
            CAtomMeta atomMeta = new CAtomMeta();
            atomMeta.setParentKey("root");
            atomMeta.setAtomKey("atomCommon");
            ObjectMapper mapper = new ObjectMapper();
            // 忽略null值
            mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
            atomMeta.setAtomContent(mapper.writeValueAsString(atomCommon));
            atomMeta.setCreatorId("1");
            atomMeta.setUpdaterId("1");
            atomMeta.setVersion("1");
            atomMeta.setVersionNum(1000000);
            atomMeta.setDeleted(0);
            cAtomMetaDao.insert(atomMeta);
        }
        return AppResponse.success("更新或新增成功");
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> updateAtomCommonInfo(AtomCommon atomCommon) throws JsonProcessingException {
        // 覆盖更新，数据库中只有一条记录，永远是最新的
        CAtomMeta atomMeta = cAtomMetaDao.selectOne(new LambdaQueryWrapper<CAtomMeta>()
                .eq(CAtomMeta::getAtomKey, "atomCommon")
                .eq(CAtomMeta::getDeleted, 0));
        ObjectMapper mapper = new ObjectMapper();
        // 忽略null值
        mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
        atomMeta.setAtomContent(mapper.writeValueAsString(atomCommon));
        atomMeta.setUpdateTime(new Date());
        cAtomMetaDao.updateById(atomMeta);

        // 根据新的层级关系   更新所有数据 的 ParentKey
        // updateAtomParentKey(atomCommon);

        return AppResponse.success("更新或新增成功");
    }

    private void updateAtomParentKey(AtomCommon atomCommon) {
        List<AtomicTree> atomicTree = atomCommon.getAtomicTree();
        List<AtomicTree> atomicTreeExtend = atomCommon.getAtomicTreeExtend();
        atomicTree.addAll(atomicTreeExtend);
        Map<String, String> atomParentKeyMap = new HashMap<>();
        processTreeListToMapWithAllPath(atomicTree, "", atomParentKeyMap);

        Set<String> atomKeys = atomParentKeyMap.keySet();
        List<CAtomMeta> atomList = cAtomMetaDao.getKeyAndParentKeyByKeySet(atomKeys);

        // 遍历  c_atom_meta 与  atomParentKeyMap 中的 parentKey进行对比，如果不同，则放入更新队列中
        List<CAtomMeta> preUpdateList = new ArrayList<>();
        for (CAtomMeta cAtomMeta : atomList) {
            String atomKey = cAtomMeta.getAtomKey();
            String newParentKey = atomParentKeyMap.get(atomKey);
            // 如果parentKey不同，则更新
            if (!Objects.equals(cAtomMeta.getParentKey(), newParentKey)) {
                cAtomMeta.setParentKey(newParentKey);
                preUpdateList.add(cAtomMeta);
            }
        }

        // 批量更新
        if (!preUpdateList.isEmpty()) {
            ListBatchUtil.process(preUpdateList, 10, updateBatchList -> {
                cAtomMetaDao.updateBatchParentKey(updateBatchList);
            });
        }
    }

    private void processTreeListToMapWithAllPath(
            List<AtomicTree> atomicTreeList, String parentKey, Map<String, String> resultMap) {
        for (AtomicTree atomicTree : atomicTreeList) {
            // 当前原子能力的key
            String key = atomicTree.getKey();
            // 如果有子节点，则递归处理
            if (!CollectionUtils.isEmpty(atomicTree.getAtomics())) {
                List<AtomicTree> atomics = atomicTree.getAtomics();
                if (parentKey.isEmpty()) {
                    processTreeListToMapWithAllPath(atomics, key, resultMap);
                } else {
                    processTreeListToMapWithAllPath(atomics, parentKey + '/' + key, resultMap);
                }
            } else {
                resultMap.put(key, parentKey);
            }
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> saveAtomicsInfo(Map<String, Atomic> atomNewMap, String saveWay)
            throws JsonProcessingException {
        if (CollectionUtils.isEmpty(atomNewMap)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "json数据为空");
        }
        Set<String> atomKeySet = atomNewMap.keySet();
        if (CollectionUtils.isEmpty(atomNewMap)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "key数据为空");
        }
        List<CAtomMeta> insertOrUpdateAtomList = new ArrayList<>();
        // 根据key列表查询最新版atomContent
        // 这个 只会 查出  最新版本的 原子能力
        List<CAtomMeta> atomMetaOldList = cAtomMetaDao.getLatestAtomListByKeySet(atomKeySet);
        String atomCommonInfoStr = cAtomMetaDao.getLatestAtomByKey("atomCommon");
        if (StringUtils.isBlank(atomCommonInfoStr)) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "无公共数据信息");
        }
        // 反序列化：将 JSON 转换为对象
        ObjectMapper mapper = new ObjectMapper();

        // 原子能力 的层级关系
        AtomCommon atomCommon = mapper.readValue(atomCommonInfoStr, AtomCommon.class);
        if (atomCommon == null
                || CollectionUtils.isEmpty(atomCommon.getAtomicTree())
                || CollectionUtils.isEmpty(atomCommon.getAtomicTreeExtend())) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "无层级关系等信息");
        }
        List<AtomicTree> atomicTree = atomCommon.getAtomicTree();
        List<AtomicTree> atomicTreeExtend = atomCommon.getAtomicTreeExtend();
        atomicTree.addAll(atomicTreeExtend);
        Map<String, String> atomParentKeyMap = new HashMap<>();
        // 生成parentKey和key的Map映射
        processTreeListToMapWithAllPath(atomicTree, "", atomParentKeyMap);

        // 对于的原子能力有没有老数据  这里 只会 取出 最新版本的原子能力 进行比较
        if (!CollectionUtils.isEmpty(atomMetaOldList)) {
            // 根据atomkey分组
            Map<String, CAtomMeta> atomMetaOldMap = atomMetaOldList.stream()
                    .collect(Collectors.toMap(
                            CAtomMeta::getAtomKey, cAtomMeta -> cAtomMeta, (existing, replacement) -> existing));

            atomNewMap.forEach((atomKey, atomContentNew) -> {
                CAtomMeta atomMetaOld = atomMetaOldMap.get(atomKey);
                try {
                    // 比较 新 旧原子能力的差异（只跟最新的 原子能力 进行比较）
                    if (null == atomMetaOld || isAtomContentDifferent(atomContentNew, atomMetaOld)) {
                        insertOrUpdateAtomList.add(
                                createAtomMeta(atomParentKeyMap.getOrDefault(atomKey, ""), atomContentNew));
                    }
                } catch (JsonProcessingException e) {
                    log.error("json转换异常：{}", e);
                    throw new RuntimeException(e);
                }
            });
        } else {
            // 直接插入
            atomNewMap.forEach((atomKey, atomContentNew) -> {
                try {
                    insertOrUpdateAtomList.add(
                            createAtomMeta(atomParentKeyMap.getOrDefault(atomKey, ""), atomContentNew));
                } catch (JsonProcessingException e) {
                    log.error("json转换异常：{}", e);
                    throw new RuntimeException(e);
                }
            });
        }

        if (!CollectionUtils.isEmpty(insertOrUpdateAtomList)) {
            if ("insert".equals(saveWay)) {
                // 批量插入
                ListBatchUtil.process(insertOrUpdateAtomList, 50, this::saveBatch);

                // 根据本次查询的 key  和版本号 查询 数据库中是否有 复的数据，如果有重复的数据就记录本次的完整请求
                checkDuplicateData(insertOrUpdateAtomList, atomNewMap, saveWay);
            } else if ("update".equals(saveWay)) {
                ListBatchUtil.process(insertOrUpdateAtomList, 50, updateBatchList -> {
                    cAtomMetaDao.UpdateBatchByKeyAndVersion(updateBatchList);
                });
            }
        }

        return AppResponse.success("保存成功");
    }

    private void checkDuplicateData(
            List<CAtomMeta> insertOrUpdateAtomList, Map<String, Atomic> atomNewMap, String saveWay) {
        for (CAtomMeta cAtomMeta : insertOrUpdateAtomList) {
            String atomKey = cAtomMeta.getAtomKey();
            String version = cAtomMeta.getVersion();
            // 查询数据库中是否有重复的数据
            List<CAtomMeta> existingAtomMeta = cAtomMetaDao.selectList(new LambdaQueryWrapper<CAtomMeta>()
                    .eq(CAtomMeta::getAtomKey, atomKey)
                    .eq(CAtomMeta::getVersion, version)
                    .eq(CAtomMeta::getDeleted, 0));
            if (existingAtomMeta.size() > 1) {
                // 获取完整请求
                Map map = new HashMap();
                map.put("atomMap", atomNewMap);
                map.put("saveWay", saveWay);
                String bodyStr = map.toString();

                log.error(String.format("发现重复数据，atomKey: %s, version: %s, 请求体: %s", atomKey, version, bodyStr));
                AtomMetaDuplicateLog atomMetaDuplicateLog = new AtomMetaDuplicateLog();
                atomMetaDuplicateLog.setAtomKey(atomKey);
                atomMetaDuplicateLog.setVersion(version);
                atomMetaDuplicateLog.setRequestBody(bodyStr);
                atomMetaDuplicateLog.setCreatorId(1L);
                atomMetaDuplicateLog.setUpdaterId(1L);
                atomMetaDuplicateLog.setDeleted(0);
                atomMetaDuplicateLog.setCreateTime(new Date());
                atomMetaDuplicateLog.setUpdateTime(new Date());
                atomMetaDuplicateLogDao.insert(atomMetaDuplicateLog);
            }
        }
    }

    /**
     * 递归获取key，parentKey键值对
     *
     * @param atomicTreeList
     * @param parentKey
     * @param resultMap
     */
    private void processTreeListToMap(
            List<AtomicTree> atomicTreeList, String parentKey, Map<String, String> resultMap) {
        for (AtomicTree atomicTree : atomicTreeList) {
            String key = atomicTree.getKey();
            resultMap.put(key, parentKey);

            if (!CollectionUtils.isEmpty(atomicTree.getAtomics())) {
                List<AtomicTree> atomics = atomicTree.getAtomics();
                processTreeListToMap(atomics, key, resultMap);
            }
        }
    }

    private CAtomMeta createAtomMeta(String parentKey, Atomic atomContentNew) throws JsonProcessingException {
        CAtomMeta atomMeta = new CAtomMeta();
        atomMeta.setParentKey(parentKey);
        atomMeta.setAtomKey(atomContentNew.getKey());
        ObjectMapper mapper = new ObjectMapper();
        // 忽略null值
        mapper.setSerializationInclusion(JsonInclude.Include.NON_NULL);
        atomMeta.setAtomContent(mapper.writeValueAsString(atomContentNew));
        atomMeta.setCreatorId("1");
        atomMeta.setUpdaterId("1");
        atomMeta.setVersion(atomContentNew.getVersion());
        atomMeta.setVersionNum(getVersion(atomContentNew.getVersion()));
        atomMeta.setDeleted(0);
        return atomMeta;
    }

    private Integer getVersion(String version) {
        if (StringUtils.isBlank(version)) {
            throw new IllegalArgumentException("版本号缺失");
        }
        String[] versionSplit = version.split("\\.");
        int splitSize = versionSplit.length;
        // 确保版本号最多有3部分（major, minor, patch）
        if (splitSize > 3) {
            throw new IllegalArgumentException("版本号格式不正确");
        }
        // 初始化 major, minor, patch
        int major = 0;
        int minor = 0;
        int patch = 0;
        // 解析 major
        if (splitSize >= 1) {
            major = Integer.parseInt(versionSplit[0]);
        }
        // 解析 minor
        if (splitSize >= 2) {
            minor = Integer.parseInt(versionSplit[1]);
        }
        // 解析 patch
        if (splitSize >= 3) {
            patch = Integer.parseInt(versionSplit[2]);
        }
        // 计算转换后的版本号
        return major * 1_000_000 + minor * 1_000 + patch;
    }

    private Boolean isAtomContentDifferent(Atomic newAtom, CAtomMeta oldAtomMeta) throws JsonProcessingException {
        // 去掉version,比较是否有不同
        Atomic atomic = new Atomic();
        BeanUtils.copyProperties(newAtom, atomic);
        atomic.setVersion(null);
        String oldAtomContent = oldAtomMeta.getAtomContent();
        // 转换为对象
        ObjectMapper mapper = new ObjectMapper();
        Atomic oldAtom = mapper.readValue(oldAtomContent, Atomic.class);
        oldAtom.setVersion(null);
        // 比较是否有不同
        return !areObjectsEqual(atomic, oldAtom);
    }

    private boolean areObjectsEqual(Object obj1, Object obj2) {
        // 获取对象的所有字段
        Field[] fields = obj1.getClass().getDeclaredFields();
        // 比较字段数量
        if (fields.length != obj2.getClass().getDeclaredFields().length) {
            return false;
        }
        // 比较每个字段的名称和值
        for (Field field : fields) {
            field.setAccessible(true); // 允许访问私有字段
            try {
                Object value1 = field.get(obj1);
                Object value2 = field.get(obj2);

                // 比较字段值
                if (value1 == null) {
                    if (value2 != null) {
                        return false;
                    }
                } else if (!value1.equals(value2)) {
                    return false;
                }
            } catch (IllegalAccessException e) {
                e.printStackTrace();
                return false;
            }
        }
        return true;
    }

    @Override
    public Map getLatestAllAtoms() throws JsonProcessingException {
        List<String> atomContentList = cAtomMetaDao.getLatestAllAtoms();
        HashMap<String, Atomic> map = new HashMap<>();
        for (String atomConten : atomContentList) {
            ObjectMapper mapper = new ObjectMapper();
            Atomic atomic = mapper.readValue(atomConten, Atomic.class);
            String key = atomic.getKey();
            map.put(key, atomic);
        }
        return map;
    }
}

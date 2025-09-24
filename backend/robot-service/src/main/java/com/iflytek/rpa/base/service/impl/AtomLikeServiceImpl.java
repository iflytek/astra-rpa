package com.iflytek.rpa.base.service.impl;

import static com.iflytek.rpa.utils.DeBounceUtils.deBounce;

import com.alibaba.fastjson.JSON;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.base.dao.AtomLikeDao;
import com.iflytek.rpa.base.dao.CAtomMetaDao;
import com.iflytek.rpa.base.entity.AtomLike;
import com.iflytek.rpa.base.entity.Atomic;
import com.iflytek.rpa.base.entity.CAtomMeta;
import com.iflytek.rpa.base.entity.vo.AtomLikeVo;
import com.iflytek.rpa.base.service.AtomLikeService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

@Service("AtomLikeService")
public class AtomLikeServiceImpl extends ServiceImpl<AtomLikeDao, AtomLike> implements AtomLikeService {

    @Resource
    private CAtomMetaDao atomMetaDao;

    @Resource
    private AtomLikeDao atomLikeDao;

    @Resource
    private IdWorker idWorker;

    @Value("${deBounce.prefix}")
    private String doBouncePrefix;

    @Value("${deBounce.window}")
    private Long deBounceWindow;

    @Override
    public AppResponse<Boolean> createLikeAtom(String atomKey) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        if (StringUtils.isBlank(atomKey)) throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "参数为空");

        // 查询原子能力是否为空
        String latestAtomByKey = atomMetaDao.getLatestAtomByKey(atomKey);
        if (latestAtomByKey == null) throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "原子能力不存在，无法收藏");

        // redis防抖处理
        String createLikeKey = doBouncePrefix + userId + atomKey;
        deBounce(createLikeKey, deBounceWindow);

        // 插入的时候查询是否已经存在
        Integer count = atomLikeDao.getAtomLikeByUserIdAtomKey(userId, atomKey);
        if (count >= 1) throw new ServiceException(ErrorCodeEnum.E_SQL_REPEAT.getCode(), "收藏的原子能力已经存在，无需重复收藏");

        AtomLike atomLike = new AtomLike();
        atomLike.setLikeId(idWorker.nextId());
        atomLike.setCreatorId(userId);
        atomLike.setTenantId(tenantId);
        atomLike.setUpdaterId(userId);
        atomLike.setAtomKey(atomKey);

        atomLikeDao.insert(atomLike);

        return AppResponse.success(true);
    }

    @Override
    public AppResponse<Boolean> cancelLikeAtom(Long likeId) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        if (likeId == null) throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode());

        AtomLike atomLike = atomLikeDao.getAtomLikeById(userId, tenantId, likeId);
        if (atomLike == null) throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "数据为空，无法取消收藏");
        atomLike.setIsDeleted(1);

        int i = atomLikeDao.deleteById(atomLike.getId());
        if (i < 1) throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode());
        return AppResponse.success(true);
    }

    @Override
    public AppResponse<List<AtomLikeVo>> likeList() throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        List<AtomLike> atomLikeList = atomLikeDao.getAtomLikeList(userId, tenantId);
        if (CollectionUtils.isEmpty(atomLikeList)) return AppResponse.success(Collections.emptyList());

        List<AtomLikeVo> resVoList = getResVoList(atomLikeList);

        return AppResponse.success(resVoList);
    }

    private List<AtomLikeVo> getResVoList(List<AtomLike> atomLikeList) {
        List<AtomLikeVo> resVoList = new ArrayList<>();
        List<String> atomKeyList =
                atomLikeList.stream().map(AtomLike::getAtomKey).collect(Collectors.toList());

        Set<String> atomKeySet = atomKeyList.stream().collect(Collectors.toSet());
        List<CAtomMeta> atomMetaList = atomMetaDao.getLatestAtomListByKeySet(atomKeySet);

        for (AtomLike atomLike : atomLikeList) {
            AtomLikeVo atomLikeVo = new AtomLikeVo();
            String atomKeyTmp = atomLike.getAtomKey();
            List<CAtomMeta> atomMetaListTmp = atomMetaList.stream()
                    .filter(cAtomMeta -> cAtomMeta.getAtomKey().equals(atomKeyTmp))
                    .collect(Collectors.toList());

            // 说明数据有点问题，直接跳过
            if (CollectionUtils.isEmpty(atomMetaListTmp) || atomMetaListTmp.size() > 1) continue;

            CAtomMeta atomMetaTmp = atomMetaListTmp.get(0);
            String atomContentJson = atomMetaTmp.getAtomContent();
            Atomic atomic = JSON.parseObject(atomContentJson, Atomic.class);

            atomLikeVo.setAtomContent(atomContentJson);
            atomLikeVo.setLikeId(atomLike.getLikeId());
            atomLikeVo.setKey(atomKeyTmp);
            atomLikeVo.setIcon(atomic.getIcon());
            atomLikeVo.setTitle(atomic.getTitle());

            resVoList.add(atomLikeVo);
        }

        return resVoList;
    }
}

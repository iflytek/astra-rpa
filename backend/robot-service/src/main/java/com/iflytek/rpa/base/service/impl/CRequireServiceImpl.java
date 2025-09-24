package com.iflytek.rpa.base.service.impl;

import com.iflytek.rpa.base.annotation.RobotVersionAnnotation;
import com.iflytek.rpa.base.dao.CRequireDao;
import com.iflytek.rpa.base.entity.CRequire;
import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CRequireDeleteDto;
import com.iflytek.rpa.base.entity.dto.CRequireDto;
import com.iflytek.rpa.base.service.CRequireService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.utils.UserUtils;
import java.util.List;
import javax.annotation.Resource;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * python依赖管理(CRequire)表服务实现类
 *
 * @author mjren
 * @since 2024-10-14 17:21:35
 */
@Service("cRequireService")
public class CRequireServiceImpl implements CRequireService {
    @Resource
    private CRequireDao cRequireDao;

    @Override
    @RobotVersionAnnotation
    public AppResponse<?> getRequireInfoList(BaseDto baseDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        baseDto.setCreatorId(userId);
        List<CRequire> requireList = cRequireDao.getRequireList(baseDto.getRobotId(), baseDto.getRobotVersion());
        return AppResponse.success(requireList);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> addRequire(CRequireDto crequireDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        crequireDto.setCreatorId(userId);
        crequireDto.setUpdaterId(userId);
        crequireDto.setRobotVersion(0);
        int count = cRequireDao.countRequire(crequireDto);
        if (count > 0) {
            return AppResponse.error("该依赖已存在：" + crequireDto.getPackageName());
        }
        boolean result = cRequireDao.addRequire(crequireDto);
        return AppResponse.success(result);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> deleteProject(CRequireDeleteDto cRequireDeleteDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        cRequireDeleteDto.setCreatorId(userId);
        if (cRequireDeleteDto.getIdList() == null
                || cRequireDeleteDto.getIdList().isEmpty()) {
            return AppResponse.error("删除失败，id不能为空");
        }
        boolean result = cRequireDao.deleteRequire(cRequireDeleteDto);
        return AppResponse.success(result);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> updateRequire(CRequireDto crequireDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        crequireDto.setUpdaterId(userId);
        boolean result = cRequireDao.updateRequire(crequireDto);
        return AppResponse.success(result);
    }
}

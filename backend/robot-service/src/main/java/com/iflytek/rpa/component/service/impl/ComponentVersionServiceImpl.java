package com.iflytek.rpa.component.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.base.dao.*;
import com.iflytek.rpa.base.service.CParamService;
import com.iflytek.rpa.component.dao.ComponentDao;
import com.iflytek.rpa.component.dao.ComponentVersionDao;
import com.iflytek.rpa.component.entity.Component;
import com.iflytek.rpa.component.entity.ComponentVersion;
import com.iflytek.rpa.component.entity.dto.CreateVersionDto;
import com.iflytek.rpa.component.service.ComponentVersionService;
import com.iflytek.rpa.robot.constants.RobotConstant;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.Date;
import javax.annotation.Resource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 组件版本表(ComponentVersion)表服务实现类
 *
 * @author makejava
 * @since 2024-12-19
 */
@Service("componentVersionService")
public class ComponentVersionServiceImpl extends ServiceImpl<ComponentVersionDao, ComponentVersion>
        implements ComponentVersionService {

    @Resource
    private ComponentVersionDao componentVersionDao;

    @Resource
    private ComponentDao componentDao;

    @Autowired
    private CProcessDao processDao;

    @Autowired
    private CGroupDao groupDao;

    @Autowired
    private CElementDao elementDao;

    @Autowired
    private CGlobalVarDao globalVarDao;

    @Autowired
    private CRequireDao requireDao;

    @Autowired
    private CModuleDao moduleDao;

    @Autowired
    private CParamService paramService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<Boolean> createComponentVersion(CreateVersionDto createVersionDto) throws NoLoginException {
        // 获取当前用户信息
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        String componentId = createVersionDto.getComponentId();

        // 获取最新版本号
        Integer nextVersion = createVersionDto.getNextVersion();
        Integer latestVersion = componentVersionDao.getLatestVersion(componentId, tenantId);
        if (null != latestVersion && latestVersion >= nextVersion) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM.getCode(), "版本号错误");
        }

        // 设置对应的component
        updateComponent(componentId, createVersionDto.getName(), userId, tenantId);

        // 插入对应的base库表
        createDataForComponentNewVersion(userId, nextVersion, componentId);

        // 插入下一个component Version
        boolean result = insertNextComponentVer(createVersionDto, userId, tenantId);

        if (result) {
            return AppResponse.success(true);
        } else {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "组件版本创建失败");
        }
    }

    public void createDataForComponentNewVersion(String userId, Integer nextVersion, String componentId) {

        RobotVersionDto robotVersionDto = new RobotVersionDto();
        robotVersionDto.setVersion(nextVersion);
        robotVersionDto.setRobotId(componentId);
        robotVersionDto.setCreatorId(userId);

        // 创建新版本的流程等数据
        processDao.createProcessForCurrentVersion(robotVersionDto);
        // 元素组数据
        groupDao.createGroupForCurrentVersion(robotVersionDto);
        // 元素数据
        elementDao.createElementForCurrentVersion(robotVersionDto);
        // 全局变量数据
        globalVarDao.createGlobalVarForCurrentVersion(robotVersionDto);
        // python依赖数据
        requireDao.createRequireForCurrentVersion(robotVersionDto);
        // python模块 module数据
        moduleDao.createModuleForCurrentVersion(robotVersionDto);
        // 流程参数
        paramService.createParamForCurrentVersion(null, robotVersionDto, 0);
    }

    public void updateComponent(String componentId, String name, String userId, String tenantId) {
        Component component = componentDao.getComponentById(componentId, userId, tenantId);
        if (component == null) throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode());

        // 重命名校验
        Long count = componentDao.countByName(name, tenantId, userId, component.getId());
        if (count > 0) throw new ServiceException(ErrorCodeEnum.E_SQL_REPEAT.getCode(), "组件名称已存在");

        component.setTransformStatus(RobotConstant.PUBLISHED);
        component.setName(name);
        component.setUpdateTime(new Date());

        int i = componentDao.updateById(component);
        if (i < 1) throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode());
    }

    public boolean insertNextComponentVer(CreateVersionDto createVersionDto, String userId, String tenantId) {
        ComponentVersion componentVersion = new ComponentVersion();

        // 设置版本信息
        componentVersion.setComponentId(createVersionDto.getComponentId());
        componentVersion.setVersion(createVersionDto.getNextVersion());
        componentVersion.setUpdateLog(createVersionDto.getUpdateLog());
        componentVersion.setIcon(createVersionDto.getIcon());
        componentVersion.setIntroduction(createVersionDto.getIntroduction());
        componentVersion.setCreatorId(userId);
        componentVersion.setTenantId(tenantId);
        componentVersion.setCreateTime(new Date());
        componentVersion.setUpdateTime(new Date());
        componentVersion.setDeleted(0);

        // 保存版本
        return save(componentVersion);
    }

    @Override
    public AppResponse<Integer> getNextVersionNumber(String componentId) throws NoLoginException {
        String tenantId = TenantUtils.getTenantId();
        Integer latestVersion = componentVersionDao.getLatestVersion(componentId, tenantId);

        // 如果没有版本，返回1；否则返回最新版本号+1
        Integer nextVersion = (latestVersion == null) ? 1 : latestVersion + 1;
        return AppResponse.success(nextVersion);
    }
}

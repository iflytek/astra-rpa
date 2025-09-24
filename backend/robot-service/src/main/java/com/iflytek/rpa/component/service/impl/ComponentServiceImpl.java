package com.iflytek.rpa.component.service.impl;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.base.annotation.RobotVersionAnnotation;
import com.iflytek.rpa.base.dao.CProcessDao;
import com.iflytek.rpa.base.entity.CProcess;
import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.component.dao.ComponentDao;
import com.iflytek.rpa.component.dao.ComponentRobotBlockDao;
import com.iflytek.rpa.component.dao.ComponentRobotUseDao;
import com.iflytek.rpa.component.dao.ComponentVersionDao;
import com.iflytek.rpa.component.entity.Component;
import com.iflytek.rpa.component.entity.ComponentRobotUse;
import com.iflytek.rpa.component.entity.ComponentVersion;
import com.iflytek.rpa.component.entity.dto.CheckNameDto;
import com.iflytek.rpa.component.entity.dto.ComponentListDto;
import com.iflytek.rpa.component.entity.dto.EditPageCompInfoDto;
import com.iflytek.rpa.component.entity.dto.GetComponentUseDto;
import com.iflytek.rpa.component.entity.vo.*;
import com.iflytek.rpa.component.service.ComponentService;
import com.iflytek.rpa.robot.constants.RobotConstant;
import com.iflytek.rpa.robot.service.RobotDesignService;
import com.iflytek.rpa.robot.service.impl.RobotDesignServiceImpl;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.*;
import java.util.stream.Collectors;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

/**
 * 组件表(Component)表服务实现类
 *
 * @author makejava
 * @since 2024-12-19
 */
@Service("componentService")
public class ComponentServiceImpl extends ServiceImpl<ComponentDao, Component> implements ComponentService {

    @Autowired
    private ComponentDao componentDao;

    @Autowired
    private CProcessDao cProcessDao;

    @Autowired
    private ComponentVersionDao componentVersionDao;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    private RobotDesignService robotDesignService;

    @Autowired
    private ComponentServiceImpl self;

    @Autowired
    private ComponentRobotBlockDao componentRobotBlockDao;

    @Autowired
    private ComponentRobotUseDao componentRobotUseDao;

    @Autowired
    private RobotDesignServiceImpl robotDesignServiceImpl;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<CProcess> createComponent(String componentName) throws NoLoginException {
        // 获取当前用户信息
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 检查名称是否重复
        Long count = componentDao.countByName(componentName, tenantId, userId, null);
        if (count > 0) throw new ServiceException("组件名称已存在");

        // 设置组件信息
        String componentId = String.valueOf(idWorker.nextId());
        Component component = new Component();
        component.setName(componentName);
        component.setComponentId(componentId);
        component.setCreatorId(userId);
        component.setUpdaterId(userId);
        component.setTenantId(tenantId);
        component.setCreateTime(new Date());
        component.setUpdateTime(new Date());
        component.setDeleted(0);
        component.setIsShown(1);
        component.setTransformStatus("editing");
        component.setDataSource("create");
        int insert = baseMapper.insert(component);
        if (insert < 1) throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "组件创建失败");

        // 新建默认流程,机器人版本是0
        CProcess cProcess = new CProcess();
        cProcess.setRobotId(componentId);
        cProcess.setProcessId(idWorker.nextId() + "");
        cProcess.setProcessName("主流程");
        cProcess.setProcessContent("[]");
        cProcess.setCreatorId(userId);
        cProcess.setUpdaterId(userId);
        cProcess.setRobotVersion(0);
        cProcessDao.createProcess(cProcess);

        CProcess cProcess1 = new CProcess();
        cProcess1.setRobotId(componentId);
        cProcess1.setProcessId(cProcess.getProcessId());
        return AppResponse.success(cProcess1);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<Boolean> deleteComponent(String componentId) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 检查组件是否存在
        Component shownComponent = componentDao.getShownComponentById(componentId, userId, tenantId);
        if (shownComponent == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "组件不存在");
        }

        // 逻辑删除组件
        Integer result = componentDao.deleteComponent(componentId, userId, tenantId);
        if (result > 0) {
            return AppResponse.success(true);
        } else {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "删除组件失败");
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<Boolean> renameComponent(String componentId, String newName) throws NoLoginException {

        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 检查组件是否存在
        Component existingComponent = componentDao.getComponentById(componentId, userId, tenantId);
        if (existingComponent == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "组件不存在");
        }

        // 检查名称是否重复，排除自己
        Long count = componentDao.countByName(newName, tenantId, userId, existingComponent.getId());
        if (count > 0) throw new ServiceException(ErrorCodeEnum.E_SQL_REPEAT.getCode(), "组件名称已经存在");

        // 更新组件名称
        Component updateComponent = new Component();
        updateComponent.setId(existingComponent.getId());
        updateComponent.setName(newName);
        updateComponent.setUpdaterId(userId);
        updateComponent.setUpdateTime(new Date());

        boolean result = updateById(updateComponent);
        if (result) return AppResponse.success(true);
        else throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "重命名失败");
    }

    @Override
    public AppResponse<Boolean> checkNameDuplicate(CheckNameDto checkNameDto) throws NoLoginException {

        String tenantId = TenantUtils.getTenantId();
        String userId = UserUtils.nowUserId();
        String componentId = checkNameDto.getComponentId();
        String name = checkNameDto.getName();
        Long excludeId = null;

        if (StringUtils.isNotBlank(componentId)) {
            Component existingComponent = componentDao.getComponentById(componentId, userId, tenantId);
            if (existingComponent != null) {
                excludeId = existingComponent.getId();
            }
        }

        Long count = componentDao.countByName(name, tenantId, userId, excludeId);
        boolean isDuplicate = count > 0;

        return AppResponse.success(isDuplicate);
    }

    @Override
    public AppResponse<String> createComponentName() throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        String componentNameBase = "组件";
        List<String> componentNameList = componentDao.getComponentNameList(tenantId, userId, componentNameBase);
        int componetNameIndex = 1;
        List<Integer> componentNameIndexList = new ArrayList<>();
        for (String componentName : componentNameList) {
            String[] componentNameSplit = componentName.split(componentNameBase);
            if (componentNameSplit.length == 2 && componentNameSplit[1].matches("^[1-9]\\d*$")) {
                int componentNameNum = Integer.parseInt(componentNameSplit[1]);
                componentNameIndexList.add(componentNameNum);
            }
        }
        Collections.sort(componentNameIndexList);
        for (int i = 0; i < componentNameIndexList.size(); i++) {
            if (componentNameIndexList.get(i) != i + 1) {
                componetNameIndex = i + 1;
                break;
            } else {
                componetNameIndex += 1;
            }
        }
        return AppResponse.success(componentNameBase + componetNameIndex);
    }

    @Override
    public AppResponse<ComponentInfoVo> getComponentInfo(String componentId) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 获取组件基本信息
        Component component = componentDao.getComponentById(componentId, userId, tenantId);
        if (component == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "组件不存在");
        }

        // 获取组件版本列表
        List<ComponentVersion> componentVersionList =
                componentVersionDao.getVersionsByComponentId(componentId, tenantId);

        // 获取最新版本号
        Integer latestVersion = componentVersionDao.getLatestVersion(componentId, tenantId);

        // 获取创建者名称
        String creatorName = UserUtils.getRealNameById(component.getCreatorId());

        // 获取最新版本的简介和图标
        String introduction = "";
        String icon = "";
        if (latestVersion != null && !componentVersionList.isEmpty()) {
            ComponentVersion latestVersionInfo = componentVersionList.stream()
                    .filter(v -> v.getVersion().equals(latestVersion))
                    .findFirst()
                    .orElse(null);
            if (latestVersionInfo != null) {
                introduction = latestVersionInfo.getIntroduction();
                icon = latestVersionInfo.getIcon();
            }
        }

        // 构建版本信息列表
        List<VersionInfo> versionInfoList = new ArrayList<>();
        for (ComponentVersion version : componentVersionList) {
            VersionInfo versionInfo = new VersionInfo();
            versionInfo.setVersion(version.getVersion());
            versionInfo.setCreateTime(version.getCreateTime());
            versionInfo.setUpdateLog(version.getUpdateLog());
            versionInfoList.add(versionInfo);
        }

        // 构建返回对象
        ComponentInfoVo componentInfoVo = new ComponentInfoVo();
        componentInfoVo.setName(component.getName());
        componentInfoVo.setIcon(icon);
        componentInfoVo.setLatestVersion(latestVersion);
        componentInfoVo.setCreatorName(creatorName);
        componentInfoVo.setIntroduction(introduction);
        componentInfoVo.setVersionInfoList(versionInfoList);

        return AppResponse.success(componentInfoVo);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<Boolean> copyComponent(String componentId, String name) throws Exception {
        // 获取当前用户信息
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 获取原组件信息
        Component originalComponent = componentDao.getComponentById(componentId, userId, tenantId);
        if (originalComponent == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "原组件不存在");
        }

        // 检查新名称是否重复
        Long count = componentDao.countByName(name, tenantId, userId, null);
        if (count > 0) {
            throw new ServiceException("组件名称已存在");
        }

        // 创建新组件
        String newComponentId = String.valueOf(idWorker.nextId());
        Component newComponent = new Component();
        newComponent.setName(name);
        newComponent.setComponentId(newComponentId);
        newComponent.setCreatorId(userId);
        newComponent.setUpdaterId(userId);
        newComponent.setTenantId(tenantId);
        newComponent.setDataSource(RobotConstant.CREATE);
        newComponent.setTransformStatus(RobotConstant.EDITING);
        newComponent.setIsShown(1);
        newComponent.setCreateTime(new Date());
        newComponent.setUpdateTime(new Date());

        // 保存新组件
        boolean saveResult = save(newComponent);
        if (!saveResult) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "创建副本组件失败");
        }

        // TODO: 复制组件版本信息等其他相关数据
        copyEditBase4Comp(originalComponent.getComponentId(), newComponentId, userId);

        return AppResponse.success(true);
    }

    @Override
    public AppResponse<String> copyCreateName(String componentId) throws Exception {
        // 获取当前用户信息
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 获取原组件信息
        Component originalComponent = componentDao.getComponentById(componentId, userId, tenantId);
        if (originalComponent == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "原组件不存在");
        }

        // 生成新名称
        String newName = generateCopyComponentName(originalComponent.getName(), tenantId, userId);

        return AppResponse.success(newName);
    }

    /**
     * 拷贝组件相关的基础数据
     *
     * @param oldComponentId
     * @param newComponentId
     * @param userId
     * @throws Exception
     */
    public void copyEditBase4Comp(String oldComponentId, String newComponentId, String userId) throws Exception {
        // 分组
        robotDesignServiceImpl.groupCopy(oldComponentId, newComponentId, userId);
        // 元素
        robotDesignServiceImpl.elementCopy(oldComponentId, newComponentId, userId);
        // 全局变量
        robotDesignServiceImpl.globalValCopy(oldComponentId, newComponentId, userId);
        // 流程
        robotDesignServiceImpl.processCopy(oldComponentId, newComponentId, userId);
        // python依赖
        robotDesignServiceImpl.requireCopy(oldComponentId, newComponentId, userId);
        // 配置参数
        robotDesignServiceImpl.paramCopy(oldComponentId, newComponentId, userId);
        // python模块
        robotDesignServiceImpl.moduleCopy(oldComponentId, newComponentId, userId);
    }

    /**
     * 生成副本组件名称
     *
     * @param originalName 原组件名称
     * @param tenantId     租户ID
     * @return 新的组件名称
     */
    private String generateCopyComponentName(String originalName, String tenantId, String userId) {
        String baseName = originalName + "-副本";
        String newName = baseName;
        int suffix = 1;

        // 循环检查名称是否重复，如果重复则增加数字后缀
        while (isComponentNameExists(newName, tenantId, userId)) {
            newName = baseName + suffix;
            suffix++;
        }

        return newName;
    }

    /**
     * 检查组件名称是否存在
     *
     * @param name     组件名称
     * @param tenantId 租户ID
     * @return 是否存在
     */
    private boolean isComponentNameExists(String name, String tenantId, String userId) {
        Long count = componentDao.countByName(name, tenantId, userId, null);
        return count > 0;
    }

    @Override
    public AppResponse<IPage<ComponentVo>> getComponentPageList(ComponentListDto componentListDto) throws Exception {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 创建分页对象
        Page<ComponentVo> page = new Page<>(componentListDto.getPageNum(), componentListDto.getPageSize());

        // 调用 DAO 进行分页查询
        IPage<ComponentVo> result = componentDao.getComponentPageList(
                page,
                componentListDto.getName(),
                componentListDto.getDataSource(),
                componentListDto.getSortType(),
                tenantId,
                userId);

        return AppResponse.success(result);
    }

    @Override
    public AppResponse<List<EditingPageCompVo>> getEditingPageCompList(GetComponentUseDto queryDto) throws Exception {

        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        Integer robotVersion =
                getRobotVersion(queryDto.getRobotId(), queryDto.getMode(), queryDto.getVersion(), new BaseDto());
        queryDto.setVersion(robotVersion);

        // 1. 获取用户权限内可获取的组件（shown = 1）
        List<Component> availableComponents = componentDao.getAvailableComponentsByUser(tenantId, userId);
        if (CollectionUtils.isEmpty(availableComponents)) {
            return AppResponse.success(Collections.emptyList());
        }

        // 2. 通过componentVersion表，过滤得到已发过版本的componentList
        List<String> publishedComponentIds = componentVersionDao.getPublishedComponentIds(tenantId);
        if (CollectionUtils.isEmpty(publishedComponentIds)) {
            return AppResponse.success(Collections.emptyList());
        }

        // 过滤出已发过版本的组件
        List<Component> publishedComponents = availableComponents.stream()
                .filter(component -> publishedComponentIds.contains(component.getComponentId()))
                .collect(Collectors.toList());

        if (CollectionUtils.isEmpty(publishedComponents)) {
            return AppResponse.success(Collections.emptyList());
        }

        // 3. 根据robotId和version获取屏蔽的blockComponentIdList
        List<String> blockedComponentIds =
                getBlockedComponentIds(queryDto.getRobotId(), queryDto.getVersion(), tenantId);

        // 4. 根据robotId和version获取引用的useComponentIdList
        List<String> usedComponentIds = getUsedComponentIds(queryDto.getRobotId(), queryDto.getVersion(), tenantId);

        // 5. componentList - blockComponentIdList + useComponentIdList 得到最终的渲染列表
        List<String> finalComponentIds = getFinalComponentIds(
                publishedComponents.stream().map(Component::getComponentId).collect(Collectors.toList()),
                blockedComponentIds,
                usedComponentIds);

        // 6. 组装成 List<EditingPageCompVo> 返回
        List<EditingPageCompVo> result = buildEditingPageCompVoList(finalComponentIds, tenantId);

        // 7. 设置icon和isLatest字段 ---- 临时新增需求
        setIconAndIsLatest(result, queryDto.getRobotId(), queryDto.getVersion(), tenantId);

        return AppResponse.success(result);
    }

    /**
     * 获取屏蔽的组件ID列表
     */
    private List<String> getBlockedComponentIds(String robotId, Integer version, String tenantId) {
        if (StringUtils.isBlank(robotId) || version == null) {
            return Collections.emptyList();
        }
        return componentRobotBlockDao.getBlockedComponentIds(robotId, version, tenantId);
    }

    /**
     * 获取引用的组件ID列表
     */
    private List<String> getUsedComponentIds(String robotId, Integer version, String tenantId) {
        if (StringUtils.isBlank(robotId) || version == null) {
            return Collections.emptyList();
        }
        List<ComponentRobotUse> usedComponents =
                componentRobotUseDao.getByRobotIdAndVersion(robotId, version, tenantId);
        if (CollectionUtils.isEmpty(usedComponents)) {
            return Collections.emptyList();
        }
        return usedComponents.stream().map(ComponentRobotUse::getComponentId).collect(Collectors.toList());
    }

    /**
     * 计算最终的组件ID列表
     */
    private List<String> getFinalComponentIds(
            List<String> publishedComponentIds, List<String> blockedComponentIds, List<String> usedComponentIds) {
        // 移除屏蔽的组件
        List<String> result = publishedComponentIds.stream()
                .filter(id -> !blockedComponentIds.contains(id))
                .collect(Collectors.toList());

        // 添加引用的组件（去重）
        for (String usedId : usedComponentIds) {
            if (!result.contains(usedId)) {
                result.add(usedId);
            }
        }

        return result;
    }

    /**
     * 构建编辑页组件VO列表
     */
    private List<EditingPageCompVo> buildEditingPageCompVoList(List<String> componentIds, String tenantId) {
        if (CollectionUtils.isEmpty(componentIds)) {
            return Collections.emptyList();
        }

        List<Component> components = componentDao.getComponentsByIds(componentIds, tenantId);
        if (CollectionUtils.isEmpty(components)) {
            return Collections.emptyList();
        }

        return components.stream().map(this::convertToEditingPageCompVo).collect(Collectors.toList());
    }

    /**
     * 转换为编辑页组件VO
     */
    private EditingPageCompVo convertToEditingPageCompVo(Component component) {
        EditingPageCompVo vo = new EditingPageCompVo();
        vo.setComponentId(component.getComponentId());
        vo.setName(component.getName());
        return vo;
    }

    /**
     * 设置组件的icon和isLatest字段
     */
    private void setIconAndIsLatest(
            List<EditingPageCompVo> componentVoList, String robotId, Integer robotVersion, String tenantId) {
        if (CollectionUtils.isEmpty(componentVoList)) {
            return;
        }

        // 获取所有组件的ID列表
        List<String> componentIds =
                componentVoList.stream().map(EditingPageCompVo::getComponentId).collect(Collectors.toList());

        // 批量获取组件的最新版本信息（包含icon）
        List<ComponentVersion> latestVersionInfoList =
                componentVersionDao.getLatestVersionInfoBatch(componentIds, tenantId);
        if (CollectionUtils.isEmpty(latestVersionInfoList)) {
            return;
        }

        // 将版本信息转换为Map，方便查找
        Map<String, ComponentVersion> versionInfoMap = latestVersionInfoList.stream()
                .collect(Collectors.toMap(ComponentVersion::getComponentId, version -> version));

        // 获取机器人在指定版本下使用的组件版本信息
        List<ComponentRobotUse> usedComponents =
                componentRobotUseDao.getByRobotIdAndVersion(robotId, robotVersion, tenantId);
        Map<String, ComponentRobotUse> usedComponentMap = new HashMap<>();
        if (!CollectionUtils.isEmpty(usedComponents)) {
            usedComponentMap = usedComponents.stream()
                    .collect(Collectors.toMap(
                            ComponentRobotUse::getComponentId,
                            usedComponent -> usedComponent,
                            (existing, replacement) -> existing));
        }

        // 设置icon和isLatest字段
        for (EditingPageCompVo vo : componentVoList) {
            ComponentVersion latestVersionInfo = versionInfoMap.get(vo.getComponentId());

            // 设置icon字段
            vo.setIcon(latestVersionInfo.getIcon());

            // 设置isLatest字段
            ComponentRobotUse usedComponent = usedComponentMap.get(vo.getComponentId());
            if (usedComponent != null) {
                // 比较使用的版本和最新版本
                Integer usedVersion = usedComponent.getComponentVersion();
                Integer latestVersion = latestVersionInfo.getVersion();
                vo.setIsLatest(usedVersion.equals(latestVersion) ? 1 : 0);
            } else {
                // 没有使用记录，默认为最新版本
                vo.setIsLatest(1);
            }
        }
    }

    @Override
    public AppResponse<EditingPageCompInfoVo> getEditingPageCompInfo(EditPageCompInfoDto queryDto) throws Exception {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 获取机器人版本号
        Integer robotVersion =
                getRobotVersion(queryDto.getRobotId(), queryDto.getMode(), queryDto.getRobotVersion(), new BaseDto());

        // 查询组件引用记录
        ComponentRobotUse componentRobotUse = componentRobotUseDao.getByRobotIdVersionAndComponentId(
                queryDto.getRobotId(), robotVersion, queryDto.getComponentId(), userId);

        // 构建组件详情VO
        EditingPageCompInfoVo result =
                buildEditingPageCompInfoVo(queryDto.getComponentId(), componentRobotUse, tenantId);

        return AppResponse.success(result);
    }

    /**
     * 构建编辑页组件详情VO
     */
    private EditingPageCompInfoVo buildEditingPageCompInfoVo(
            String componentId, ComponentRobotUse componentRobotUse, String tenantId) throws NoLoginException {
        EditingPageCompInfoVo vo = new EditingPageCompInfoVo();
        vo.setComponentId(componentId);

        // 获取组件基本信息
        Component component = componentDao.getComponentById(componentId, UserUtils.nowUserId(), tenantId);
        if (component == null) throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "获取组件失败，数据异常");
        vo.setName(component.getName());

        // 获取组件最新版本信息（包含版本号和简介）
        ComponentVersion latestVersionInfo = componentVersionDao.getLatestVersionInfo(componentId, tenantId);
        if (latestVersionInfo == null) throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "组件未发过版本，数据异常");

        Integer latestVersion = latestVersionInfo.getVersion();
        vo.setLatestVersion(latestVersion);
        vo.setIntroduction(latestVersionInfo.getIntroduction());

        // 如果有引用记录，使用引用表中的版本号
        if (componentRobotUse != null) {
            Integer usedVersion = componentRobotUse.getComponentVersion();
            if (usedVersion != null) {
                vo.setVersion(usedVersion);
                // 判断是否为最新版本
                vo.setIsLatest(usedVersion.equals(latestVersion) ? 1 : 0);
            }
        } else {
            // 没有引用记录，直接使用最新版本
            vo.setVersion(latestVersion);
            vo.setIsLatest(1);
        }

        return vo;
    }

    /**
     * 获取机器人版本号
     */
    public Integer getRobotVersion(String robotId, String mode, Integer version, BaseDto baseDto) {
        baseDto.setMode(mode);
        baseDto.setRobotVersion(version);
        baseDto.setRobotId(robotId);

        // 解决代理不生效问题，不能用类调用自己的方法，只能用注入的方式
        self.getVersion(baseDto);

        return baseDto.getRobotVersion();
    }

    @RobotVersionAnnotation
    public void getVersion(BaseDto baseDto) {}

    @Override
    public AppResponse<List<CompManageVo>> getCompManageList(GetComponentUseDto queryDto) throws Exception {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 获取机器人版本号
        Integer robotVersion =
                getRobotVersion(queryDto.getRobotId(), queryDto.getMode(), queryDto.getVersion(), new BaseDto());

        // 1. 根据robotId和robotVersion查询所有的shown = 1的component，联componentVersion表
        List<CompManageVo> resVoList = getComponentInfoList(tenantId, userId);
        if (CollectionUtils.isEmpty(resVoList)) {
            return AppResponse.success(Collections.emptyList());
        }

        // 2. 根据robotId和robotVersion查componentRobotBlock表中所有的componentId，设置blocked字段
        setBlockedStatus(resVoList, queryDto.getRobotId(), robotVersion, tenantId);

        // 3. 根据robotId和robotVersion查componentRobotUse表中所有的componentId和componentVersion，设置isLatest和version
        setUsageInfo(resVoList, queryDto.getRobotId(), robotVersion, tenantId);

        return AppResponse.success(resVoList);
    }

    /**
     * 获取组件信息列表
     */
    private List<CompManageVo> getComponentInfoList(String tenantId, String userId) {
        // 获取用户权限内可获取的组件（shown = 1）
        List<Component> availableComponents = componentDao.getAvailableComponentsByUser(tenantId, userId);
        if (CollectionUtils.isEmpty(availableComponents)) {
            return Collections.emptyList();
        }

        // 通过componentVersion表，过滤得到已发过版本的componentList
        List<String> publishedComponentIds = componentVersionDao.getPublishedComponentIds(tenantId);
        if (CollectionUtils.isEmpty(publishedComponentIds)) {
            return Collections.emptyList();
        }

        // 过滤出已发过版本的组件
        List<Component> publishedComponents = availableComponents.stream()
                .filter(component -> publishedComponentIds.contains(component.getComponentId()))
                .collect(Collectors.toList());

        if (CollectionUtils.isEmpty(publishedComponents)) {
            return Collections.emptyList();
        }

        // 批量获取所有组件的最新版本信息，避免重复IO
        List<String> componentIds =
                publishedComponents.stream().map(Component::getComponentId).collect(Collectors.toList());
        List<ComponentVersion> latestVersionInfoList =
                componentVersionDao.getLatestVersionInfoBatch(componentIds, tenantId);

        if (CollectionUtils.isEmpty(latestVersionInfoList)) {
            return Collections.emptyList();
        }

        // 将版本信息转换为Map，方便查找
        Map<String, ComponentVersion> versionInfoMap = latestVersionInfoList.stream()
                .collect(Collectors.toMap(ComponentVersion::getComponentId, version -> version));

        // 组装CompManageVo列表
        List<CompManageVo> result = new ArrayList<>();
        for (Component component : publishedComponents) {
            ComponentVersion latestVersionInfo = versionInfoMap.get(component.getComponentId());
            if (latestVersionInfo == null) {
                continue; // 如果没有版本信息，跳过此组件
            }

            CompManageVo vo = new CompManageVo();
            vo.setComponentId(component.getComponentId());
            vo.setName(component.getName());
            vo.setIcon(latestVersionInfo.getIcon());
            vo.setIntroduction(latestVersionInfo.getIntroduction());
            vo.setVersion(latestVersionInfo.getVersion());
            vo.setBlocked(0); // 默认未屏蔽
            vo.setIsLatest(1); // 默认是最新版本
            result.add(vo);
        }

        return result;
    }

    /**
     * 设置屏蔽状态
     */
    private void setBlockedStatus(
            List<CompManageVo> componentInfoList, String robotId, Integer robotVersion, String tenantId) {
        List<String> blockedComponentIds =
                componentRobotBlockDao.getBlockedComponentIds(robotId, robotVersion, tenantId);
        if (CollectionUtils.isEmpty(blockedComponentIds)) {
            return;
        }

        for (CompManageVo vo : componentInfoList) {
            if (blockedComponentIds.contains(vo.getComponentId())) {
                vo.setBlocked(1);
            }
        }
    }

    /**
     * 设置使用信息
     */
    private void setUsageInfo(
            List<CompManageVo> componentInfoList, String robotId, Integer robotVersion, String tenantId) {
        List<ComponentRobotUse> usedComponents =
                componentRobotUseDao.getByRobotIdAndVersion(robotId, robotVersion, tenantId);
        if (CollectionUtils.isEmpty(usedComponents)) {
            return;
        }

        // 将使用信息转换为Map，避免嵌套循环，提高性能
        Map<String, ComponentRobotUse> usedComponentMap = usedComponents.stream()
                .collect(Collectors.toMap(
                        ComponentRobotUse::getComponentId,
                        usedComponent -> usedComponent,
                        // 如果有重复的componentId，保留第一个（理论上不应该有重复）
                        (existing, replacement) -> existing));

        // 处理被引用了的component
        for (CompManageVo vo : componentInfoList) {
            ComponentRobotUse usedComponent = usedComponentMap.get(vo.getComponentId());

            // 被引用了
            if (usedComponent != null) {
                Integer componentUseVersion = usedComponent.getComponentVersion();

                // 比较版本号，设置isLatest和version
                if (componentUseVersion.equals(vo.getVersion())) vo.setIsLatest(1);
                else {
                    vo.setIsLatest(0);
                    vo.setLatestVersion(vo.getVersion()); // 最新版本
                    vo.setVersion(componentUseVersion); // 使用版本
                }
            }
        }
    }
}

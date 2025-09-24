package com.iflytek.rpa.robot.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.*;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.base.dao.*;
import com.iflytek.rpa.base.entity.*;
import com.iflytek.rpa.base.service.CElementService;
import com.iflytek.rpa.base.service.CParamService;
import com.iflytek.rpa.component.dao.ComponentRobotBlockDao;
import com.iflytek.rpa.component.dao.ComponentRobotUseDao;
import com.iflytek.rpa.component.entity.ComponentRobotBlock;
import com.iflytek.rpa.component.entity.ComponentRobotUse;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.File;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.EnableVersionDto;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import com.iflytek.rpa.robot.entity.dto.VersionListDto;
import com.iflytek.rpa.robot.entity.vo.VersionDetailVo;
import com.iflytek.rpa.robot.entity.vo.VersionInfo;
import com.iflytek.rpa.robot.entity.vo.VersionListVo;
import com.iflytek.rpa.robot.service.RobotVersionService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.*;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

/**
 * 云端机器人版本表(RobotVersion)表服务实现类
 *
 * @author makejava
 * @since 2024-09-29 15:27:42
 */
@Service("robotVersionService")
public class RobotVersionServiceImpl extends ServiceImpl<RobotVersionDao, RobotVersion> implements RobotVersionService {
    @Resource
    private RobotVersionDao robotVersionDao;

    @Resource
    private RobotDesignDao robotDesignDao;

    @Autowired
    private RobotExecuteDao robotExecuteDao;

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
    private IdWorker idWorker;

    @Resource
    private CElementService cElementService;

    @Resource
    private CParamDao cParamDao;

    @Autowired
    private CParamService paramService;

    @Autowired
    private ComponentRobotUseDao componentRobotUseDao;

    @Autowired
    private ComponentRobotBlockDao componentRobotBlockDao;

    @Autowired
    private RobotVersionService robotVersionService;
    /*    @Autowired
    private CProcessDao cProcessDao;*/

    @Override
    @Transactional(rollbackFor = Exception.class, propagation = Propagation.REQUIRED)
    public AppResponse<?> publishRobot(RobotVersionDto robotVersionDto) throws Exception {
        // 点击发版的时候，前端调接口已经把所有数据保存到v0了
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        robotVersionDto.setCreatorId(userId);
        robotVersionDto.setUpdaterId(userId);
        robotVersionDto.setTenantId(tenantId);
        String name = robotVersionDto.getName();
        // 根据该字段，前端显示不同的成功提示
        String haveShared = CREATE;
        Integer enableLastVersion = robotVersionDto.getEnableLastVersion();
        // 检查版本号是否正确
        Integer nextVersion = robotVersionDto.getVersion();
        if (null == nextVersion || nextVersion <= 0) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "版本号错误");
        }
        Integer latestVersion = robotVersionDao.getLatestVersionNum(robotVersionDto);
        if (null != latestVersion && latestVersion >= nextVersion) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "版本号错误");
        }
        RobotExecute robotExecute = new RobotExecute();
        // 检查Robot的类型 写入 web  还是 other类型 version为 0 的 content
        BeanUtils.copyProperties(robotVersionDto, robotExecute);
        // packageWebType(robotExecute);
        robotExecute.setDataSource(CREATE);
        //        String deptIdPath = DeptUtils.getLevelCode();
        //        robotExecute.setDeptIdPath(deptIdPath);
        Integer updateCount = null;
        // 第一次发布
        if (1 == nextVersion) {
            // 将状态改为已发布
            updateCount = robotDesignDao.updateTransformStatus(userId, robotVersionDto.getRobotId(), name, PUBLISHED);
            // 插入执行器表
            robotExecuteDao.insertRobot(robotExecute);
            // 插入版本表，默认启用
            robotVersionDto.setOnline(1);
            robotVersionDao.addRobotVersion(robotVersionDto);
        } else {
            // 非第一次发布
            // 更新执行器表
            robotExecuteDao.updateRobot(robotExecute);
            // 更新app_market_resource应用市场中的名字
            // 如果没分享过或者退出市场了，状态是已发版; 分享过，已上架
            updateCount = robotDesignDao.updateTransformStatus(userId, robotVersionDto.getRobotId(), name, PUBLISHED);

            // 插入版本表，默认未启用
            robotVersionDto.setOnline(0);
            // 这里对paramDetail字段进行删除
            robotVersionDao.addRobotVersion(robotVersionDto);
        }
        if (null == updateCount || 0 == updateCount) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "机器人状态错误");
        }
        createDataForNewVersion(robotVersionDto);

        // 启用最新版本
        if (enableLastVersion != null && enableLastVersion == 1) {
            EnableVersionDto enableVersionDto = new EnableVersionDto();
            enableVersionDto.setRobotId(robotVersionDto.getRobotId());
            enableVersionDto.setVersion(robotVersionDto.getVersion());
            robotVersionService.enableVersion(enableVersionDto);
        }

        return AppResponse.success(haveShared);
    }

    public void createDataForNewVersion(RobotVersionDto robotVersionDto) {
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
        // 组件引用数据
        createCompRobotUse4NewVer(robotVersionDto);
        // 组件屏蔽数据
        createCompRobotBlock4NewVer(robotVersionDto);
    }

    @Transactional(rollbackFor = Exception.class, propagation = Propagation.REQUIRED)
    public void updateAppAndRobot(RobotExecute robotExecute, Integer nextVersion) throws NoLoginException {
        robotDesignDao.updateTransformStatus(
                robotExecute.getCreatorId(), robotExecute.getRobotId(), robotExecute.getName(), SHARED);
    }

    /**
     * 设计器不允许重名，执行器和市场允许重名
     *
     * @param robotVersionDto
     * @return
     * @throws NoLoginException
     */
    @Override
    public AppResponse<?> checkSameName(RobotVersionDto robotVersionDto) throws NoLoginException {
        String name = robotVersionDto.getName();
        String robotId = robotVersionDto.getRobotId();
        if (StringUtils.isBlank(name) || StringUtils.isBlank(robotId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM);
        }
        robotVersionDto.setCreatorId(UserUtils.nowUserId());
        robotVersionDto.setTenantId(TenantUtils.getTenantId());
        Integer countDesign = robotDesignDao.countByName(robotVersionDto);
        //        Integer countExecute = robotExecuteDao.countByName(robotVersionDto);
        if (countDesign > 0) {
            return AppResponse.success(true);
        }
        return AppResponse.success(false);
    }

    @Override
    public AppResponse<?> getLastRobotVersionInfo(RobotVersion robotVersionSearch) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        String robotId = robotVersionSearch.getRobotId();
        if (StringUtils.isBlank(robotId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "机器人id不能为空");
        }
        RobotVersionDto robotVersionDto = new RobotVersionDto();
        // 查设计器名字
        RobotDesign robotDesign = robotDesignDao.getRobotDesignInfo(robotId, userId, tenantId);
        if (null == robotDesign) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "机器人不存在");
        }
        RobotVersion robotVersion = robotVersionDao.getLastRobotVersionInfo(robotId, userId, tenantId);
        if (null != robotVersion) {
            // 得到版本
            Integer version = robotVersion.getVersion();
            if (version == null) {
                return AppResponse.error(ErrorCodeEnum.E_SQL, "无历史版本号");
            }
            Integer nextVersion = version + 1;
            robotVersion.setVersion(nextVersion);
            BeanUtils.copyProperties(robotVersion, robotVersionDto);
            String videoId = robotVersion.getVideoId();
            String appendixId = robotVersion.getAppendixId();
            // 获取名称
            List<String> fileIdList = new ArrayList<>();
            fileIdList.add(videoId);
            fileIdList.add(appendixId);
            List<File> fileInfoList = robotVersionDao.getFileNameInfo(fileIdList);
            Map<String, String> fileInfoMap =
                    fileInfoList.stream().collect(Collectors.toMap(File::getFileId, File::getFileName));
            robotVersionDto.setVideoName(fileInfoMap.get(videoId));
            robotVersionDto.setAppendixName(fileInfoMap.get(appendixId));
            robotVersionDto.setName(robotDesign.getName());
        } else {
            robotVersionDto.setName(robotDesign.getName());
            robotVersionDto.setVersion(1);
        }
        return AppResponse.success(robotVersionDto);
    }

    @Override
    public AppResponse<?> versionList(VersionListDto queryDto) throws NoLoginException {
        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            Long pageNo = queryDto.getPageNo();
            Long pageSize = queryDto.getPageSize();
            String robotId = queryDto.getRobotId();
            Integer sortType = queryDto.getSortType() == null ? 1 : queryDto.getSortType();

            String marketId = robotDesignDao.getMarketId(robotId, userId, tenantId);

            IPage<RobotVersion> page = new Page<>(pageNo, pageSize);
            LambdaQueryWrapper<RobotVersion> wrapper = new LambdaQueryWrapper<>();

            // userID tenantId 筛选
            wrapper.eq(RobotVersion::getCreatorId, userId);
            wrapper.eq(RobotVersion::getTenantId, tenantId);

            wrapper.eq(RobotVersion::getRobotId, robotId);

            // 更新时间排序
            if (sortType.equals(0)) wrapper.orderByAsc(RobotVersion::getVersion);
            else wrapper.orderByDesc(RobotVersion::getVersion);

            String sourceName = "";
            IPage<RobotVersion> rePage = this.page(page, wrapper);

            if (rePage.getRecords().size() == 0) {
                sourceName = StringUtils.isBlank(marketId) ? "本地" : "团队市场";

                IPage<VersionInfo> ansPage = new Page<>(pageNo, pageSize);

                VersionListVo resVo = new VersionListVo();
                resVo.setSourceName(sourceName);
                resVo.setAnsPage(ansPage);

                return AppResponse.success(resVo);
            }

            IPage<VersionInfo> ansPage = getVersionInfoPage(rePage, pageNo, pageSize);

            sourceName = StringUtils.isBlank(marketId) ? "本地" : "团队市场";

            // 结果组装
            VersionListVo resVo = new VersionListVo();
            resVo.setSourceName(sourceName);
            resVo.setAnsPage(ansPage);

            return AppResponse.success(resVo);
        }

        return response;
    }

    @Override
    @Transactional(rollbackFor = Exception.class, propagation = Propagation.REQUIRED)
    public AppResponse<?> enableVersion(EnableVersionDto queryDto) throws Exception {

        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            String robotId = queryDto.getRobotId();
            Integer version = queryDto.getVersion();

            if (StringUtils.isBlank(robotId) || version == null) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "请求参数缺失");
            }

            // 清空robotExecute表的参数配置,使用启用版本的默认配置参数
            robotExecuteDao.updateParamToNUll(robotId, userId, tenantId);
            // 将历史启用版本下线
            robotVersionDao.unEnableAllVersion(robotId, userId, tenantId);

            // 上线指定版本
            boolean b = robotVersionDao.enableVersion(robotId, version, userId, tenantId);
            if (b) return AppResponse.success("上线新版本成功");
            else throw new Exception();
        }
        return response;
    }

    @Override
    @Transactional(rollbackFor = Exception.class, propagation = Propagation.REQUIRED)
    public AppResponse<?> recoverVersion(EnableVersionDto queryDto) throws Exception {

        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            String robotId = queryDto.getRobotId();
            Integer version = queryDto.getVersion();

            if (StringUtils.isBlank(robotId) || version == null) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "请求参数缺失");
            }

            // 恢复指定版本，在 c_element, c_global_var, c_process, c_require , c_module操作
            recover(robotId, version, userId, tenantId);

            String massage = "";
            massage = "恢复版本" + version + "成功！";

            return AppResponse.success(massage);
        }
        return response;
    }

    public void recover(String robotId, Integer version, String userId, String tenantId) throws Exception {
        elementRecover(robotId, version, userId);
        globalVarRecover(robotId, version, userId);
        processRecover(robotId, version, userId);
        requireRecover(robotId, version, userId);
        moduleRecover(robotId, version, userId);
        // 恢复编辑参数
        paramRecover(robotId, version, userId);
        // 恢复组件引用数据
        recoverComponentUse(robotId, version, userId);
        // 恢复组件屏蔽数据
        recoverComponentBlock(robotId, version, userId);

        // 设计器状态更改为编辑中
        RobotDesign robotDesign = robotDesignDao.getRobot(robotId, userId, tenantId);
        robotDesign.setTransformStatus("editing");
        robotDesignDao.updateById(robotDesign);
    }

    // element 恢复
    public void elementRecover(String robotId, Integer version, String userId) throws Exception {
        elementDao.deleteOldEditVersion(robotId, userId);
        List<CElement> elementList = elementDao.getElement(robotId, version, userId);
        if (CollectionUtils.isEmpty(elementList)) return;

        for (CElement element : elementList) {

            element.setId(null);
            element.setRobotVersion(0);
            element.setCreateTime(new Date());
            element.setUpdateTime(new Date());
        }

        // 最后批量插入
        elementDao.insertEleBatch(elementList);
    }

    public void globalVarRecover(String robotId, Integer version, String userId) {
        globalVarDao.deleteOldEditVersion(robotId, userId);
        List<CGlobalVar> globalVarList = globalVarDao.getGlobalVar(robotId, version, userId);
        if (CollectionUtils.isEmpty(globalVarList)) return;

        for (CGlobalVar globalVar : globalVarList) {

            globalVar.setId(null);
            globalVar.setRobotVersion(0);
            globalVar.setCreateTime(new Date());
            globalVar.setUpdateTime(new Date());
        }

        globalVarDao.insertGloBatch(globalVarList);
    }

    public void processRecover(String robotId, Integer version, String userId) throws Exception {
        processDao.deleteOldEditVersion(robotId, userId);

        List<CProcess> processList = processDao.getProcess(robotId, version, userId);
        if (CollectionUtils.isEmpty(processList)) throw new Exception();

        for (CProcess process : processList) {

            process.setId(null);
            process.setRobotVersion(0);
            process.setCreateTime(new Date());
            process.setUpdateTime(new Date());
        }

        processDao.insertProcessBatch(processList);
    }

    public void moduleRecover(String robotId, Integer version, String userId) throws Exception {
        moduleDao.deleteOldEditVersion(robotId, userId);

        List<CModule> moduleList = moduleDao.getAllModuleList(robotId, version, userId);
        if (CollectionUtils.isEmpty(moduleList)) {
            return;
        }

        for (CModule module : moduleList) {

            module.setId(null);
            module.setRobotVersion(0);
            module.setCreateTime(new Date());
            module.setUpdateTime(new Date());
        }

        moduleDao.insertBatch(moduleList);
    }

    public void requireRecover(String robotId, Integer version, String userId) {
        requireDao.deleteOldEditVersion(robotId, userId);
        List<CRequire> requireList = requireDao.getRequire(robotId, version, userId);
        if (CollectionUtils.isEmpty(requireList)) return;

        for (CRequire require : requireList) {

            require.setId(null);
            require.setRobotVersion(0);
            require.setCreateTime(new Date());
            require.setUpdateTime(new Date());
        }

        requireDao.insertReqBatch(requireList);
    }

    // 参数恢复
    public void paramRecover(String robotId, Integer version, String userId) {
        // 删除0版本对应的参数
        cParamDao.deleteParamByRobotId(robotId);
        // 查询当前版本对应参数
        List<CParam> cParamList = cParamDao.getAllParams(null, robotId, version);
        for (CParam cParam : cParamList) {
            cParam.setUpdaterId(userId);
            cParam.setId(idWorker.nextId() + "");
        }
        // 批量插入版本参数
        cParamList.removeIf(Objects::isNull);
        if (!cParamList.isEmpty()) {
            cParamDao.createParamForCurrentVersion(cParamList);
        }
    }

    @Override
    public AppResponse<?> list4Design(String robotId) throws NoLoginException {

        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            if (StringUtils.isBlank(robotId)) return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "参数缺失");

            RobotDesign robotDesign = robotDesignDao.getRobot(robotId, userId, tenantId);
            List<RobotVersion> robotVersionList = robotVersionDao.getAllVersion(robotId, userId, tenantId);

            List<VersionDetailVo> ansVersionList = getAnsVersionList(robotVersionList, robotId, robotDesign);

            return AppResponse.success(ansVersionList);
        }
        return response;
    }

    private List<VersionDetailVo> getAnsVersionList(
            List<RobotVersion> robotVersionList, String robotId, RobotDesign robotDesign) {

        List<VersionDetailVo> ansVoList = new ArrayList<>();

        for (RobotVersion robotVersion : robotVersionList) {
            VersionDetailVo tempVo = new VersionDetailVo();

            String onlineStr = "";
            onlineStr = robotVersion.getOnline().equals(0) ? "disable" : "enable";

            tempVo.setUpdateLog(robotVersion.getUpdateLog());
            tempVo.setRobotId(robotId);
            tempVo.setVersionNum(robotVersion.getVersion());
            tempVo.setOnline(onlineStr);
            tempVo.setUpdateTime(robotVersion.getUpdateTime());

            ansVoList.add(tempVo);
        }

        // 加入编辑态的版本
        if (robotDesign.getTransformStatus().equals("editing")) {
            VersionDetailVo tempVo = new VersionDetailVo();

            tempVo.setVersionNum(0);
            tempVo.setRobotId(robotId);
            tempVo.setUpdateLog(null);
            tempVo.setOnline("disable");
            tempVo.setUpdateTime(robotDesign.getUpdateTime());

            ansVoList.add(0, tempVo);
        }

        return ansVoList;
    }

    private IPage<VersionInfo> getVersionInfoPage(IPage<RobotVersion> rePage, Long pageNo, Long pageSize) {

        List<RobotVersion> robotVersionList = rePage.getRecords();

        IPage<VersionInfo> ansPage = new Page<>(pageNo, pageSize);
        List<VersionInfo> ansRecords = new ArrayList<>();

        for (int i = 0; i < robotVersionList.size(); i++) {
            VersionInfo versionInfo = new VersionInfo();

            RobotVersion robotVersionTmp = robotVersionList.get(i);

            versionInfo.setVersionNum(robotVersionTmp.getVersion());
            versionInfo.setCreateTime(robotVersionTmp.getCreateTime());
            versionInfo.setOnline(robotVersionTmp.getOnline());

            ansRecords.add(versionInfo);
        }

        ansPage.setSize(rePage.getSize());
        ansPage.setTotal(rePage.getTotal());
        ansPage.setRecords(ansRecords);

        return ansPage;
    }

    /**
     * 为新版本创建组件引用数据
     *
     * @param robotVersionDto 机器人版本信息
     */
    private void createCompRobotUse4NewVer(RobotVersionDto robotVersionDto) {
        String robotId = robotVersionDto.getRobotId();
        String creatorId = robotVersionDto.getCreatorId();
        Integer newVersion = robotVersionDto.getVersion();
        String tenantId = robotVersionDto.getTenantId();

        // 根据robotId、robotVersion=0和creatorId查询所有的componentRobotUseList记录
        List<ComponentRobotUse> componentRobotUseList =
                componentRobotUseDao.getByRobotIdAndVersion(robotId, 0, tenantId);
        if (CollectionUtils.isEmpty(componentRobotUseList)) return;

        List<ComponentRobotUse> newComponentRobotUseList = new ArrayList<>();

        for (ComponentRobotUse componentRobotUse : componentRobotUseList) {
            // 2. 创建新的记录，设置robotVersion为新版本
            ComponentRobotUse newComponentRobotUse = new ComponentRobotUse();
            newComponentRobotUse.setRobotId(componentRobotUse.getRobotId());
            newComponentRobotUse.setRobotVersion(newVersion);
            newComponentRobotUse.setComponentId(componentRobotUse.getComponentId());
            newComponentRobotUse.setComponentVersion(componentRobotUse.getComponentVersion());
            newComponentRobotUse.setCreatorId(creatorId);
            newComponentRobotUse.setCreateTime(new Date());
            newComponentRobotUse.setUpdaterId(creatorId);
            newComponentRobotUse.setUpdateTime(new Date());
            newComponentRobotUse.setDeleted(0);
            newComponentRobotUse.setTenantId(tenantId);

            newComponentRobotUseList.add(newComponentRobotUse);
        }

        // 批量插入新记录
        componentRobotUseDao.insertBatch(newComponentRobotUseList);
    }

    /**
     * 为新版本创建组件屏蔽数据
     *
     * @param robotVersionDto 机器人版本信息
     */
    private void createCompRobotBlock4NewVer(RobotVersionDto robotVersionDto) {
        String robotId = robotVersionDto.getRobotId();
        String creatorId = robotVersionDto.getCreatorId();
        Integer newVersion = robotVersionDto.getVersion();
        String tenantId = robotVersionDto.getTenantId();

        // 1. 根据robotId、robotVersion=0和creatorId查询所有的componentRobotBlockList记录
        List<ComponentRobotBlock> componentRobotBlockList =
                componentRobotBlockDao.getBlocksByRobotId(robotId, tenantId);

        if (CollectionUtils.isEmpty(componentRobotBlockList)) return;

        List<ComponentRobotBlock> resList = new ArrayList<>();

        for (ComponentRobotBlock componentRobotBlock : componentRobotBlockList) {
            // 只处理版本为0的记录
            if (componentRobotBlock.getRobotVersion() != null && componentRobotBlock.getRobotVersion() == 0) {
                // 2. 创建新的记录，设置robotVersion为新版本
                ComponentRobotBlock newCompRobotBlock = new ComponentRobotBlock();
                newCompRobotBlock.setRobotId(componentRobotBlock.getRobotId());
                newCompRobotBlock.setRobotVersion(newVersion);
                newCompRobotBlock.setComponentId(componentRobotBlock.getComponentId());
                newCompRobotBlock.setCreatorId(creatorId);
                newCompRobotBlock.setCreateTime(new Date());
                newCompRobotBlock.setUpdaterId(creatorId);
                newCompRobotBlock.setUpdateTime(new Date());
                newCompRobotBlock.setDeleted(0);
                newCompRobotBlock.setTenantId(tenantId);

                resList.add(newCompRobotBlock);
            }
        }

        // 批量插入新记录
        componentRobotBlockDao.insertBatch(resList);
    }

    /**
     * 恢复组件引用数据
     *
     * @param robotId 机器人ID
     * @param version 版本号
     * @param userId  用户ID
     */
    public void recoverComponentUse(String robotId, Integer version, String userId) {
        // 删除之前的编辑态记录
        componentRobotUseDao.deleteOldEditVersion(robotId, userId);

        // 查询指定版本的组件引用记录
        List<ComponentRobotUse> componentRobotUseList =
                componentRobotUseDao.getComponentRobotUse(robotId, version, userId);
        if (CollectionUtils.isEmpty(componentRobotUseList)) return;

        // 处理每条记录：id置为null，version改为0，更新时间
        for (ComponentRobotUse componentRobotUse : componentRobotUseList) {
            componentRobotUse.setId(null);
            componentRobotUse.setRobotVersion(0);
            componentRobotUse.setCreateTime(new Date());
            componentRobotUse.setUpdateTime(new Date());
        }

        // 批量插入新记录
        componentRobotUseDao.insertBatch(componentRobotUseList);
    }

    /**
     * 恢复组件屏蔽数据
     *
     * @param robotId 机器人ID
     * @param version 版本号
     * @param userId  用户ID
     */
    public void recoverComponentBlock(String robotId, Integer version, String userId) {
        // 删除之前的编辑态记录
        componentRobotBlockDao.deleteOldEditVersion(robotId, userId);

        // 查询指定版本的组件屏蔽记录
        List<ComponentRobotBlock> componentRobotBlockList =
                componentRobotBlockDao.getComponentRobotBlock(robotId, version, userId);
        if (CollectionUtils.isEmpty(componentRobotBlockList)) return;

        // 处理每条记录：id置为null，version改为0，更新时间
        for (ComponentRobotBlock componentRobotBlock : componentRobotBlockList) {
            componentRobotBlock.setId(null);
            componentRobotBlock.setRobotVersion(0);
            componentRobotBlock.setCreateTime(new Date());
            componentRobotBlock.setUpdateTime(new Date());
        }

        // 批量插入新记录
        componentRobotBlockDao.insertBatch(componentRobotBlockList);
    }
}

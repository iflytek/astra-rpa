package com.iflytek.rpa.robot.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDITING;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.base.dao.*;
import com.iflytek.rpa.base.entity.*;
import com.iflytek.rpa.component.dao.ComponentRobotBlockDao;
import com.iflytek.rpa.component.dao.ComponentRobotUseDao;
import com.iflytek.rpa.component.entity.ComponentRobotBlock;
import com.iflytek.rpa.component.entity.ComponentRobotUse;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotExecuteRecordDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.DeleteDesignDto;
import com.iflytek.rpa.robot.entity.dto.DesignListDto;
import com.iflytek.rpa.robot.entity.dto.ShareDesignDto;
import com.iflytek.rpa.robot.entity.dto.TaskRobotCountDto;
import com.iflytek.rpa.robot.entity.vo.*;
import com.iflytek.rpa.robot.service.RobotDesignService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.task.dao.ScheduleTaskDao;
import com.iflytek.rpa.task.dao.ScheduleTaskRobotDao;
import com.iflytek.rpa.task.entity.ScheduleTaskRobot;
import com.iflytek.rpa.triggerTask.dao.TriggerTaskDao;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.jetbrains.annotations.NotNull;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

/**
 * 云端机器人表(Robot)表服务实现类
 *
 * @author makejava
 * @since 2024-09-29 15:27:41
 */
@Service("robotDesignService")
public class RobotDesignServiceImpl extends ServiceImpl<RobotDesignDao, RobotDesign> implements RobotDesignService {
    @Resource
    private RobotDesignDao robotDesignDao;

    @Resource
    private RobotExecuteDao robotExecuteDao;

    @Resource
    private RobotVersionDao robotVersionDao;

    @Autowired
    private CGroupDao groupDao;

    @Resource
    private CElementDao elementDao;

    @Resource
    private CGlobalVarDao globalVarDao;

    @Resource
    private CProcessDao processDao;

    @Resource
    private CRequireDao requireDao;

    @Resource
    private ScheduleTaskRobotDao scheduleTaskRobotDao;

    @Resource
    private ScheduleTaskDao scheduleTaskDao;

    @Autowired
    private IdWorker idWorker;

    @Autowired
    private CProcessDao cProcessDao;

    @Autowired
    private TriggerTaskDao triggerTaskDao;

    @Autowired
    private CParamDao cParamDao;

    @Autowired
    private CModuleDao cModuleDao;

    @Autowired
    private ComponentRobotUseDao componentRobotUseDao;

    @Autowired
    private ComponentRobotBlockDao componentRobotBlockDao;

    @Resource
    private RobotExecuteRecordDao robotExecuteRecordDao;

    private final String filePathPrefix = "/api/resource/file/download?fileId=";

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse createRobot(RobotDesign robot) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        robot.setCreatorId(userId);
        robot.setUpdaterId(userId);
        String tenantId = TenantUtils.getTenantId();
        robot.setTenantId(tenantId);
        String robotName = robot.getName();
        robotName = robotName.trim();
        if (StringUtils.isBlank(robotName)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "机器人名称不能为空");
        }
        robot.setName(robotName);
        Long countRobot = robotDesignDao.countRobotByName(robot);
        if (countRobot > 0) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "存在同名机器人，请重新命名");
        }
        String robotId = idWorker.nextId() + "";
        robot.setRobotId(robotId);
        robot.setDataSource("create");
        robot.setEditEnable(1);
        robot.setTransformStatus(EDITING);
        robotDesignDao.createRobot(robot);
        // 新建默认流程,机器人版本是0
        CProcess cProcess = new CProcess();
        cProcess.setRobotId(robotId);
        cProcess.setProcessId(idWorker.nextId() + "");
        cProcess.setProcessName("主流程");
        cProcess.setCreatorId(userId);
        cProcess.setUpdaterId(userId);
        cProcess.setRobotVersion(0);
        cProcessDao.createProcess(cProcess);
        CProcess cProcess1 = new CProcess();
        cProcess1.setRobotId(robotId);
        cProcess1.setProcessId(cProcess.getProcessId());
        return AppResponse.success(cProcess1);
    }

    @Override
    public AppResponse<?> createRobotName() throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        String robotNameBase = "机器人";
        List<String> getRobotNameList = robotDesignDao.getRobotNameList(tenantId, userId, robotNameBase);
        int robotNameIndex = 1;
        List<Integer> robotNameIndexList = new ArrayList<>();
        for (String robotName : getRobotNameList) {
            String[] robotNameSplit = robotName.split(robotNameBase);
            if (robotNameSplit.length == 2 && robotNameSplit[1].matches("^[1-9]\\d*$")) {
                int robotNameNum = Integer.parseInt(robotNameSplit[1]);
                robotNameIndexList.add(robotNameNum);
            }
        }
        Collections.sort(robotNameIndexList);
        for (int i = 0; i < robotNameIndexList.size(); i++) {
            if (robotNameIndexList.get(i) != i + 1) {
                robotNameIndex = i + 1;
                break;
            } else {
                robotNameIndex += 1;
            }
        }
        return AppResponse.success(robotNameBase + robotNameIndex);
    }

    @Override
    public AppResponse<?> designList(DesignListDto queryDto) throws NoLoginException {

        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            Long pageNo = queryDto.getPageNo();
            Long pageSize = queryDto.getPageSize();
            String name = queryDto.getName();
            String sortType = StringUtils.isBlank(queryDto.getSortType()) ? "desc" : queryDto.getSortType();
            String dataSource = queryDto.getDataSource() == null ? "create" : queryDto.getDataSource();

            IPage<RobotDesign> page = new Page<>(pageNo, pageSize);
            LambdaQueryWrapper<RobotDesign> wrapper = new LambdaQueryWrapper<>();

            // userID tenantId 筛选
            wrapper.eq(RobotDesign::getCreatorId, userId);
            wrapper.eq(RobotDesign::getTenantId, tenantId);
            wrapper.eq(RobotDesign::getDeleted, 0);

            // dataSource 筛选
            wrapper.eq(RobotDesign::getDataSource, dataSource);

            // 名字模糊匹配
            if (StringUtils.isNotBlank(name)) {
                wrapper.like(RobotDesign::getName, name);
            }

            // 更新时间排序
            if (sortType.equals("asc")) wrapper.orderByAsc(RobotDesign::getUpdateTime);
            else wrapper.orderByDesc(RobotDesign::getUpdateTime);

            IPage<RobotDesign> rePage = this.page(page, wrapper);

            if (CollectionUtils.isEmpty(rePage.getRecords())) return AppResponse.success(rePage);

            IPage<DesignListVo> ansPage = new Page<>(pageNo, pageSize);
            List<DesignListVo> ansRecords = new ArrayList<>();

            ArrayList<String> robotIdList = new ArrayList<>();

            for (RobotDesign record : rePage.getRecords()) {

                DesignListVo designListVo = new DesignListVo();
                designListVo.setRobotName(record.getName());
                designListVo.setUpdateTime(record.getUpdateTime());
                designListVo.setRobotId(record.getRobotId());
                designListVo.setPublishStatus(record.getTransformStatus());
                designListVo.setEditEnable(record.getTransformStatus().equals("locked") ? 0 : 1);

                ansRecords.add(designListVo);
            }

            setAnsRecords(rePage, ansRecords);

            ansPage.setSize(rePage.getSize());
            ansPage.setTotal(rePage.getTotal());
            ansPage.setRecords(ansRecords);

            return AppResponse.success(ansPage);
        }
        return response;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> rename(String newName, String robotId) throws NoLoginException {
        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            if (StringUtils.isBlank(newName) || StringUtils.isBlank(robotId))
                return AppResponse.error("更新失败，新名字或机器人Id为空");

            // 去掉首尾的空格
            newName = trimSpaces(newName);
            String robotName = robotDesignDao.getRobotName(robotId, userId, tenantId);

            if (StringUtils.isBlank(newName)) return AppResponse.error("新名字不能为空");

            Integer i = robotDesignDao.checkNameDup(userId, tenantId, newName, robotId);
            if (i >= 1) return AppResponse.error("存在重复名称，请修改名称");

            boolean b = false;
            // 如果不开放源码，就不改为editing
            RobotDesign robotDesign = robotDesignDao.getRobot(robotId, userId, tenantId);
            if (robotDesign.getTransformStatus().equals("locked") || newName.equals(robotName)) {
                b = robotDesignDao.updateRobotNameWithoutSetEditing(newName, robotId, userId, tenantId);
            } else {
                b = robotDesignDao.updateRobotName(newName, robotId, userId, tenantId);
            }

            if (b) return AppResponse.success("更新成功");
            else return AppResponse.error("更新失败");
        }
        return response;
    }

    @Override
    public AppResponse<?> designNameDup(String newName, String robotId) throws NoLoginException {

        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            if (StringUtils.isNotBlank(newName)) {

                //                String oriRobotName = robotDesignDao.getRobotName(robotId, userId, tenantId);
                //                if (newName.equals(oriRobotName)) return AppResponse.error("不能和原名相同");
                trimSpaces(newName); // 去除首尾空格
                if (StringUtils.isBlank(newName)) return AppResponse.error("新名字不能为空");

                Integer i = robotDesignDao.checkNameDup(userId, tenantId, newName, robotId);
                if (i >= 1) return AppResponse.error("存在重复名称，请修改名称");
                else return AppResponse.success("重命名校验通过");
            }

            return AppResponse.error("校验失败，新名字为空");
        }
        return response;
    }

    @Override
    public AppResponse<?> myRobotDetail(String robotId) throws NoLoginException {
        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            RobotDesign robot = robotDesignDao.getRobot(robotId, userId, tenantId);
            RobotVersion enableVersion = robotVersionDao.getEnableVersion(robotId, userId, tenantId);

            if (robot.getDataSource().equals("market")) return AppResponse.error("设计器来源错误，请检查数据");

            if (robot == null) return AppResponse.error("机器人不存在");

            MyRobotDetailVo resVo = getMyRobotDetailRes(robot, enableVersion);

            return AppResponse.success(resVo);
        }
        return response;
    }

    @Override
    public AppResponse<?> marketRobotDetail(String robotId) throws Exception {
        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            RobotDesign robot = robotDesignDao.getRobot(robotId, userId, tenantId);
            RobotVersion enableVersion = robotVersionDao.getEnableVersion(robotId, userId, tenantId);

            if (robot.getDataSource().equals("create")) return AppResponse.error("设计器来源错误，请检查数据");

            MarketRobotDetailVo resVo = getMarketRobotDetailRes(robot, enableVersion, userId, tenantId);

            return AppResponse.success(resVo);
        }

        return response;
    }

    @Transactional(rollbackFor = Exception.class)
    @Override
    public AppResponse<?> copyDesignRobot(String robotId, String robotName) throws Exception {

        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            RobotDesign robot = robotDesignDao.getRobot(robotId, userId, tenantId);
            if (robot == null) return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION);

            String newName = robot.getName() + "副本1";
            if (StringUtils.isNotBlank(robotName)) {
                // 重命名校验
                Integer i = robotDesignDao.checkNameDup(userId, tenantId, robotName, robotId);
                if (i >= 1) return AppResponse.error("存在重复名称，请修改名称");

                newName = robotName;
            }

            // 开始复制
            designRobotCopy(robot, userId, robotId, newName);

            return AppResponse.success("创建副本成功");
        }
        return response;
    }

    @Override
    public AppResponse<?> deleteRobotRes(String robotId) throws Exception {

        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            RobotExecute robotExecute = robotExecuteDao.getRobotExecute(robotId, userId, tenantId);
            // 获取所有引用该机器人的task
            List<ScheduleTaskRobot> taskRobotList = scheduleTaskRobotDao.getAllTaskRobot(robotId, userId, tenantId);

            // 获取响应结果
            DelDesignRobotVo resVo = getDeleteRobotVo(robotExecute, taskRobotList, robotId, userId, tenantId);

            return AppResponse.success(resVo);
        }
        return response;
    }

    @Transactional(rollbackFor = Exception.class)
    @Override
    public AppResponse<?> deleteRobot(DeleteDesignDto queryDto) throws Exception {
        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String userId = UserUtils.nowUserId();
            String tenantId = TenantUtils.getTenantId();

            Integer situation = queryDto.getSituation();
            String robotId = queryDto.getRobotId();
            String taskIds = queryDto.getTaskIds();

            // 删除相关的执行记录
            Integer n = robotExecuteRecordDao.deleteRecord(tenantId, robotId, userId);

            switch (situation) {
                case 1: // 只有设计器中存在
                    Integer i = robotDesignDao.deleteDesign(robotId, userId, tenantId);

                    if (i.equals(1)) return AppResponse.success("删除设计器成功");
                    else throw new Exception(); // 回滚

                case 2: // 设计器 执行器 和 执行器中都存在
                    Integer j = robotDesignDao.deleteDesign(robotId, userId, tenantId);
                    Integer p = robotExecuteDao.deleteExecute(robotId, userId, tenantId);

                    if (j.equals(1) && p.equals(1)) return AppResponse.success("删除设计器,相关执行器成功");
                    else throw new Exception(); // 回滚

                case 3: // 设计器、 执行期、 计划任务也引用
                    if (StringUtils.isBlank(taskIds)) return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK);

                    List<String> taskIdList = Arrays.stream(taskIds.split(",")).collect(Collectors.toList());
                    Integer x = robotDesignDao.deleteDesign(robotId, userId, tenantId);
                    Integer y = robotExecuteDao.deleteExecute(robotId, userId, tenantId);
                    Integer z = scheduleTaskRobotDao.taskRobotDelete(robotId, userId, tenantId, taskIdList);

                    // 删除taskRobot后处理
                    taskRobotDeleteAfter(taskIdList);

                    if (x.equals(1) && y.equals(1) && z.equals(taskIdList.size())) {
                        return AppResponse.success("删除设计器,相关执行器,相关计划任务引用成功");
                    } else throw new Exception();

                default:
                    return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK);
            }
        }
        return response;
    }

    // 后处理，查看以taskIdList为taskId的在taskRobot中还是否存在，如果不存在，则需要在schedule task表中也删除
    public void taskRobotDeleteAfter(List<String> taskIdList) throws Exception {
        List<TaskRobotCountDto> taskRobotCountDtoList = scheduleTaskRobotDao.taskRobotCount(taskIdList);
        // 求 taskRobotCountDtoList 与  taskIdList 的 差集，  taskIdNotInList中存放差集元素
        Set<String> taskIdNotInList = taskIdList.stream()
                .filter(taskId -> taskRobotCountDtoList.stream()
                        .noneMatch(taskRobotCountDto ->
                                taskRobotCountDto.getTaskId().equals(taskId)))
                .collect(Collectors.toSet());
        /*for (String taskId : taskIdList) {
            List<TaskRobotCountDto> collect = taskRobotCountDtoList
                    .stream()
                    .filter(taskRobotCountDto -> taskRobotCountDto.getTaskId().equals(taskId))
                    .collect(Collectors.toList());

            if (collect == null || collect.size() == 0){
                taskIdNotInList.add(taskId);
            }
        }*/
        // 删除不存在于taskRobot对应schedule task
        Integer i = 0;
        if (!taskIdNotInList.isEmpty()) {
            i = triggerTaskDao.deleteTasks(taskIdNotInList);
        }

        if (!i.equals(taskIdNotInList.size())) {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "删除数据与实际数据不对应");
        }
    }

    private DelDesignRobotVo getDeleteRobotVo(
            RobotExecute robotExecute,
            List<ScheduleTaskRobot> taskRobotList,
            String robotId,
            String userId,
            String tenantId)
            throws Exception {

        DelDesignRobotVo resVo = new DelDesignRobotVo();
        resVo.setRobotId(robotId);

        // 1：设计器
        if (robotExecute == null) resVo.setSituation(1);
        // 2：设计器 执行器
        else if (robotExecute != null && (CollectionUtils.isEmpty(taskRobotList))) resVo.setSituation(2);
        // 3：设计器 执行器 被计划任务引用
        else {
            resVo.setSituation(3);
            setDelDesignRobotVo(resVo, taskRobotList, robotId);
        }

        return resVo;
    }

    // 第三种情况
    public void setDelDesignRobotVo(DelDesignRobotVo resVo, List<ScheduleTaskRobot> taskRobotList, String robotId)
            throws Exception {

        List<TaskReferInfo> taskReferInfoList = new ArrayList<>();

        // 获取所有引用该执行器的taskId
        List<String> taskIdList =
                taskRobotList.stream().map(ScheduleTaskRobot::getTaskId).collect(Collectors.toList());

        // 查询数据
        List<ScheduleTaskRobot> taskRobots = scheduleTaskRobotDao.getScheduleRobotByTaskIds(taskIdList);
        if (CollectionUtils.isEmpty(taskRobots)) {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "机器人引用关系异常");
        }

        // 处理数据
        for (String taskId : taskIdList) {
            TaskReferInfo taskReferInfo = new TaskReferInfo();

            // 筛选出当前taskId的taskRobot
            List<ScheduleTaskRobot> taskRobotsTmp = taskRobots.stream()
                    .filter(taskRobot -> taskRobot.getTaskId().equals(taskId))
                    .collect(Collectors.toList());

            // 通过sort字段排序  正序
            taskRobotsTmp.sort((o1, o2) -> o1.getSort().compareTo(o2.getSort()));

            List<String> robotNames = new ArrayList<>();
            List<Integer> highIndex = new ArrayList<>();
            for (int i = 0; i < taskRobotsTmp.size(); i++) {
                ScheduleTaskRobot taskRobot = taskRobotsTmp.get(i);
                String robotNameTmp = taskRobot.getRobotName();
                String robotIdTmp = taskRobot.getRobotId();
                if (robotIdTmp.equals(robotId)) {
                    highIndex.add(i);
                }
                robotNames.add(robotNameTmp);
            }

            taskReferInfo.setTaskId(taskId);
            taskReferInfo.setTaskName(taskRobotsTmp.get(0).getTaskName());
            taskReferInfo.setRobotNames(robotNames);
            taskReferInfo.setHighIndex(highIndex);

            taskReferInfoList.add(taskReferInfo);
        }

        resVo.setTaskReferInfoList(taskReferInfoList);
    }

    public void designRobotCopy(RobotDesign robot, String userId, String robotId, String robotName) throws Exception {

        String newRobotId = String.valueOf(idWorker.nextId());

        robot.setId(null);
        robot.setRobotId(newRobotId);
        robot.setName(robotName);
        robot.setCreateTime(new Date());
        robot.setUpdateTime(new Date());
        robot.setTransformStatus("editing");
        robot.setDataSource("create");
        robotDesignDao.insert(robot);

        // 复制基础工程内容，复制的版本 0 的内容
        copyEditingBase(robotId, newRobotId, userId);
    }

    @Override
    public void copyEditingBase(String oldRobotId, String newRobotId, String userId) throws Exception {
        // 分组
        groupCopy(oldRobotId, newRobotId, userId);
        // 元素
        elementCopy(oldRobotId, newRobotId, userId);
        // 全局变量
        globalValCopy(oldRobotId, newRobotId, userId);
        // 流程
        processCopy(oldRobotId, newRobotId, userId);
        // python依赖
        requireCopy(oldRobotId, newRobotId, userId);
        // 配置参数
        paramCopy(oldRobotId, newRobotId, userId);
        // python模块
        moduleCopy(oldRobotId, newRobotId, userId);
        // 组件引用数据
        componentUseCopy(oldRobotId, newRobotId, userId);
        // 组件屏蔽数据
        componentBlockCopy(oldRobotId, newRobotId, userId);
    }

    public void moduleCopy(String oldRobotId, String newRobotId, String userId) {
        List<CModule> moduleList = cModuleDao.getAllModuleList(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(moduleList)) {
            return;
        }
        for (CModule cModule : moduleList) {
            cModule.setId(null);
            cModule.setModuleId(String.valueOf(idWorker.nextId()));
            cModule.setRobotId(newRobotId);
            cModule.setCreateTime(new Date());
            cModule.setUpdateTime(new Date());
        }
        cModuleDao.insertBatch(moduleList);
    }

    public void paramCopy(String oldRobotId, String newRobotId, String userId) {
        List<CParam> params = cParamDao.getParams(oldRobotId, userId);

        // 原机器人的流程id  和  副本机器人的流程id 的映射Map:（k,v） 为 （oldProcessId,newProcessId）
        List<CProcess> oldProcessList = processDao.getProcess(oldRobotId, 0, userId);
        List<CProcess> newProcessList = processDao.getProcess(newRobotId, 0, userId);
        Map<String, String> oldNewProcessIdMap = getOldNewProcessIdMap(newProcessList, oldProcessList);

        for (CParam cParam : params) {
            cParam.setId(idWorker.nextId() + "");
            cParam.setRobotId(newRobotId);
            // 保证子流程的processId和配置参数对应
            cParam.setProcessId(oldNewProcessIdMap.get(cParam.getProcessId()));
            cParam.setRobotVersion(0); // 新版本为0
            cParam.setCreateTime(new Date());
            cParam.setUpdateTime(new Date());
            cParam.setCreatorId(userId);
            cParam.setUpdaterId(userId);
            cParam.setDeleted(0);
        }
        if (!params.isEmpty()) {
            cParamDao.insertParamBatch(params);
        }
    }

    @NotNull
    private Map<String, String> getOldNewProcessIdMap(List<CProcess> newProcessList, List<CProcess> oldProcessList) {
        Map<String, String> newContentToId = new HashMap<>();
        for (CProcess newProcess : newProcessList) {
            if (newProcess.getProcessContent() != null) {
                newContentToId.put(newProcess.getProcessContent(), newProcess.getProcessId());
            }
        }
        Map<String, String> oldNewProcessIdMap = new HashMap<>();
        for (CProcess oldProcess : oldProcessList) {
            String oldContent = oldProcess.getProcessContent();
            if (oldContent != null && newContentToId.containsKey(oldContent)) {
                oldNewProcessIdMap.put(oldProcess.getProcessId(), newContentToId.get(oldContent));
            }
        }
        return oldNewProcessIdMap;
    }

    public void groupCopy(String oldRobotId, String newRobotId, String userId) {
        groupDao.copyGroupBatch(oldRobotId, newRobotId, userId);
    }

    public void elementCopy(String oldRobotId, String newRobotId, String userId) {

        List<CElement> elementList = elementDao.getElement(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(elementList)) return;

        for (CElement element : elementList) {
            //            String nextId = String.valueOf(idWorker.nextId());

            element.setId(null);
            //            element.setElementId(nextId);
            element.setRobotId(newRobotId);
            element.setCreateTime(new Date());
            element.setUpdateTime(new Date());
        }

        // 最后批量插入
        elementDao.insertEleBatch(elementList);
    }

    public void globalValCopy(String oldRobotId, String newRobotId, String userId) {

        List<CGlobalVar> globalVarList = globalVarDao.getGlobalVar(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(globalVarList)) return;

        for (CGlobalVar globalVar : globalVarList) {
            String nextId = String.valueOf(idWorker.nextId());

            globalVar.setId(null);
            globalVar.setGlobalId(nextId);
            globalVar.setRobotId(newRobotId);
            globalVar.setCreateTime(new Date());
            globalVar.setUpdateTime(new Date());
        }

        globalVarDao.insertGloBatch(globalVarList);
    }

    public void processCopy(String oldRobotId, String newRobotId, String userId) throws Exception {

        List<CProcess> processList = processDao.getProcess(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(processList)) throw new Exception();

        for (CProcess process : processList) {
            String nextId = String.valueOf(idWorker.nextId());

            process.setId(null);
            process.setProcessId(nextId);
            process.setRobotId(newRobotId);
            process.setCreateTime(new Date());
            process.setUpdateTime(new Date());
        }

        // 主流程中子流程的引用重新替换成新的子流程 processId
        subProcessWrite(processList);

        processDao.insertProcessBatch(processList);
    }

    // 主流程中子流程的引用重新替换成新的子流程 processId
    private void subProcessWrite(List<CProcess> processList) {
        // 说明不存在子流程
        if (processList.size() == 1) return;

        // 主流程的内容
        String processContent = processList.get(0).getProcessContent();

        // 子流程idList
        List<String> processIdList =
                processList.stream().skip(1).map(CProcess::getProcessId).collect(Collectors.toList());

        // 替换之后的主流程content
        String newProcessContent = replaceProcessIds(processContent, processIdList);

        // 替换回去
        processList.get(0).setProcessContent(newProcessContent);
    }

    private String replaceProcessIds(String processContent, List<String> processIdList) {
        if (processContent == null || processIdList == null) {
            throw new IllegalArgumentException("processContent and processIdList cannot be null.");
        }

        String patternString = Pattern.quote("\"key\":\"process\",\"value\":\"") + "(\\d+)";
        Pattern pattern = Pattern.compile(patternString);
        Matcher matcher = pattern.matcher(processContent);

        StringBuffer resultBuffer = new StringBuffer();
        int matchCount = 0;

        // 查找所有匹配项
        while (matcher.find()) {
            matchCount++;
            if (matchCount > processIdList.size()) {
                // 如果匹配到的位置数量超过了提供的ID数量，说明不匹配
                throw new IllegalArgumentException("Number of matched positions (" + matchCount
                        + ") exceeds the size of processIdList (" + processIdList.size() + ").");
            }
            // 获取当前匹配到的ID
            String replacementId = processIdList.get(matchCount - 1); // processIdList 是0-indexed

            // 构建替换文本：模板部分 + 替换的ID
            String replacementText = "\"key\":\"process\",\"value\":\"" + replacementId;
            matcher.appendReplacement(resultBuffer, replacementText);
        }

        // 检查匹配到的位置数量是否与processIdList的size相同
        if (matchCount != processIdList.size()) {
            throw new IllegalArgumentException("Number of matched positions (" + matchCount
                    + ") does not match the size of processIdList (" + processIdList.size() + ").");
        }

        // 将剩余的字符串追加到结果中
        matcher.appendTail(resultBuffer);

        return resultBuffer.toString();
    }

    public void requireCopy(String oldRobotId, String newRobotId, String userId) {
        List<CRequire> requireList = requireDao.getRequire(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(requireList)) return;

        for (CRequire require : requireList) {

            require.setId(null);
            require.setRobotId(newRobotId);
            require.setCreateTime(new Date());
            require.setUpdateTime(new Date());
        }

        requireDao.insertReqBatch(requireList);
    }

    private MarketRobotDetailVo getMarketRobotDetailRes(
            RobotDesign robot, RobotVersion enableVersion, String userId, String tenantId) throws Exception {

        String appId = robot.getAppId();
        Integer appVersion = robot.getAppVersion();

        MyRobotDetailVo myRobotDetailRes = getMyRobotDetailRes(robot, enableVersion);

        // 设置useDescription 和 file相关信息
        setAddInfo(myRobotDetailRes, robot);

        String robotId = robotDesignDao.getRobotIdFromAppResourceRegardlessDel(appId);

        List<RobotVersion> allVersion = robotVersionDao.getAllVersion(robotId, userId, tenantId);
        List<VersionInfo> versionInfoList = new ArrayList<>();

        for (int i = 0; i < allVersion.size(); i++) {
            RobotVersion robotVersion = allVersion.get(i);
            Integer online = 0;

            VersionInfo versionInfo = new VersionInfo();
            versionInfo.setVersionNum(robotVersion.getVersion());
            versionInfo.setCreateTime(robotVersion.getCreateTime());

            // 这是他获取时候的version
            online = appVersion.equals(robotVersion.getVersion()) ? 1 : 0;

            versionInfo.setOnline(online);

            versionInfoList.add(versionInfo);
        }

        MarketRobotDetailVo resVo = new MarketRobotDetailVo();
        resVo.setMyRobotDetailVo(myRobotDetailRes);
        resVo.setSourceName("团队市场");
        resVo.setVersionInfoList(versionInfoList);

        return resVo;
    }

    private void setAddInfo(MyRobotDetailVo myRobotDetailRes, RobotDesign robot) throws Exception {
        String appId = robot.getAppId();
        String sourceRobotId = robotDesignDao.getRobotIdFromAppResourceRegardlessDel(appId);

        RobotVersion latestRobotVersion = robotVersionDao.getLatestVersionRegardlessDel(sourceRobotId);
        if (latestRobotVersion == null) throw new Exception();

        String fileId = latestRobotVersion.getAppendixId();
        String videoId = latestRobotVersion.getVideoId();
        String fileName = robotExecuteDao.getFileName(fileId);
        String videoName = robotExecuteDao.getFileName(videoId);

        myRobotDetailRes.setUseDescription(latestRobotVersion.getUseDescription());
        myRobotDetailRes.setFileName(fileName);
        myRobotDetailRes.setFilePath(filePathPrefix + fileId);
        myRobotDetailRes.setVideoName(videoName);
        myRobotDetailRes.setVideoPath(StringUtils.isEmpty(videoId) ? null : (filePathPrefix + videoId));
    }

    private MyRobotDetailVo getMyRobotDetailRes(RobotDesign robot, RobotVersion enableVersion) {
        MyRobotDetailVo resVo = new MyRobotDetailVo();
        String introduction = "";
        Integer version = 0;
        String fileId = null;
        String videoId = null;
        String fileName = null;
        String videoName = null;
        String useDescription = null;

        if (enableVersion != null) {
            introduction = enableVersion.getIntroduction();
            version = enableVersion.getVersion();
            fileId = enableVersion.getAppendixId();
            videoId = enableVersion.getVideoId();
            fileName = robotExecuteDao.getFileName(fileId);
            videoName = robotExecuteDao.getFileName(videoId);
            useDescription = enableVersion.getUseDescription();
        }

        String creatorName = UserUtils.getRealNameById(robot.getCreatorId());

        resVo.setName(robot.getName());
        resVo.setVersion(version);
        resVo.setIntroduction(introduction);
        resVo.setUseDescription(useDescription);
        resVo.setCreatorName(creatorName);
        resVo.setCreateTime(robot.getCreateTime());
        resVo.setFileName(fileName);
        resVo.setFilePath(filePathPrefix + fileId);
        resVo.setVideoName(videoName);
        resVo.setVideoPath(StringUtils.isEmpty(videoId) ? null : (filePathPrefix + videoId));

        return resVo;
    }

    private void setAnsRecords(IPage<RobotDesign> rePage, List<DesignListVo> ansRecords) {

        List<RobotDesign> robotDesignList = rePage.getRecords();

        List<String> robotIdList =
                robotDesignList.stream().map(RobotDesign::getRobotId).collect(Collectors.toList());

        List<RobotVersion> robotVersionList = robotDesignDao.getRobotVersionList(robotIdList);

        for (DesignListVo ansRecord : ansRecords) {
            String robotId = ansRecord.getRobotId();

            // 过滤出当前robotId的robotVersion
            List<RobotVersion> robotVersionsTmp = robotVersionList.stream()
                    .filter(robotVersion -> robotVersion.getRobotId().equals(robotId))
                    .collect(Collectors.toList());

            if (robotVersionsTmp.size() == 0 || robotVersionsTmp == null) {
                // 说明没有发过版本， 团队市场获取的设计器没有版本，和产品确认过了
                ansRecord.setVersion(0);
            } else {

                List<RobotVersion> enableList = robotVersionsTmp.stream()
                        .filter(robotVersion1 -> robotVersion1.getOnline().equals(1))
                        .collect(Collectors.toList());

                if (CollectionUtils.isEmpty(enableList))
                    throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "数据异常，发过版本的机器人无启用版本");

                // 发过版本的，设置启用启用版本
                RobotVersion enableRobotVersion = enableList.get(0);

                // 发过版本的，设置最新版本
                Optional<RobotVersion> optionalRobotVersion =
                        robotVersionsTmp.stream().max(Comparator.comparing(RobotVersion::getVersion));

                ansRecord.setLatestVersion(optionalRobotVersion.get().getVersion());
                ansRecord.setVersion(enableRobotVersion.getVersion());
                ansRecord.setIconUrl(enableRobotVersion.getIcon());
            }
        }
    }

    public String trimSpaces(String input) {
        if (input == null) {
            return null;
        }
        return input.trim();
    }

    @Transactional(rollbackFor = Exception.class)
    @Override
    public AppResponse<?> shareRobot(ShareDesignDto queryDto) throws Exception {
        AppResponse<?> response = UserUtils.nowLoginUserResponse();
        if (response.ok()) {
            String robotId = queryDto.getRobotId();
            String sharedUserId = queryDto.getSharedUserId();
            String sharedTenantId = queryDto.getSharedTenantId();
            String receivedUserId = queryDto.getReceivedUserId();
            String receivedTenantId = queryDto.getReceivedTenantId();

            // 获取要分享的机器人
            RobotDesign robot = robotDesignDao.getRobot(robotId, sharedUserId, sharedTenantId);
            if (robot == null) return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION);
            String receivedRobotName = robot.getName() + "分享";
            // 检查接收用户 机器人是否重名
            Integer i = robotDesignDao.checkNameDupWithoutRobotId(receivedUserId, receivedTenantId, receivedRobotName);
            while (i > 1) {
                receivedRobotName += "分享";
                i = robotDesignDao.checkNameDupWithoutRobotId(receivedUserId, receivedTenantId, receivedRobotName);
            }

            String newRobotId =
                    designRobotShare(robot, sharedUserId, receivedUserId, receivedTenantId, receivedRobotName);
            return AppResponse.success(newRobotId);
        }
        return response;
    }

    /**
     * 设计器分享
     *
     * @param robot             分享的机器人
     * @param receivedUserId    接收机器人的用户id
     * @param receivedTenantId  接收机器人的用户的租户id
     * @param receivedRobotName 机器人名称
     */
    public String designRobotShare(
            RobotDesign robot,
            String sharedUserId,
            String receivedUserId,
            String receivedTenantId,
            String receivedRobotName)
            throws Exception {
        String oldRobotId = robot.getRobotId();
        // 修改 robotDesign 的 信息
        robot.setId(null);
        String newRobotId = String.valueOf(idWorker.nextId());
        robot.setRobotId(newRobotId);
        robot.setName(receivedRobotName);
        // 租户id
        robot.setTenantId(receivedTenantId);
        // 用户id
        robot.setCreatorId(receivedUserId);
        robot.setUpdaterId(receivedUserId);
        robot.setCreateTime(new Date());
        robot.setUpdateTime(new Date());
        robot.setTransformStatus("editing");
        robot.setDataSource("create");
        robotDesignDao.insert(robot);
        // 迁移其他相关的数据
        shareRobotBaseInfo(oldRobotId, newRobotId, sharedUserId, receivedUserId);

        return robot.getRobotId();
    }

    public void shareRobotBaseInfo(String oldRobotId, String newRobotId, String sharedUserId, String receivedUserId)
            throws Exception {
        // 分组
        groupShare(oldRobotId, sharedUserId, newRobotId, receivedUserId);
        // 元素
        elementShare(oldRobotId, sharedUserId, newRobotId, receivedUserId);
        // 全局变量
        globalValShare(oldRobotId, sharedUserId, newRobotId, receivedUserId);
        // 流程
        processShare(oldRobotId, sharedUserId, newRobotId, receivedUserId);
        // python依赖
        requireShare(oldRobotId, sharedUserId, newRobotId, receivedUserId);
        // 配置参数
        paramShare(oldRobotId, sharedUserId, newRobotId, receivedUserId);
    }

    private void groupShare(String oldRobotId, String sharedUserId, String newRobotId, String receivedUserId) {
        groupDao.shareGroupBatch(oldRobotId, sharedUserId, newRobotId, receivedUserId);
    }

    private void elementShare(String oldRobotId, String sharedUserId, String newRobotId, String receivedUserId) {
        List<CElement> elementList = elementDao.getElement(oldRobotId, 0, sharedUserId);
        if (CollectionUtils.isEmpty(elementList)) return;
        for (CElement element : elementList) {
            element.setId(null);
            element.setRobotId(newRobotId);
            element.setCreateTime(new Date());
            element.setUpdateTime(new Date());
            element.setCreatorId(receivedUserId);
            element.setUpdaterId(receivedUserId);
        }
        elementDao.insertEleBatch(elementList);
    }

    private void globalValShare(String oldRobotId, String sharedUserId, String newRobotId, String receivedUserId) {
        List<CGlobalVar> globalVarList = globalVarDao.getGlobalVar(oldRobotId, 0, sharedUserId);
        if (CollectionUtils.isEmpty(globalVarList)) return;
        for (CGlobalVar globalVar : globalVarList) {
            String nextId = String.valueOf(idWorker.nextId());
            globalVar.setId(null);
            globalVar.setGlobalId(nextId);
            globalVar.setRobotId(newRobotId);
            globalVar.setCreateTime(new Date());
            globalVar.setUpdateTime(new Date());
            globalVar.setCreatorId(receivedUserId);
            globalVar.setUpdaterId(receivedUserId);
        }
        globalVarDao.insertGloBatch(globalVarList);
    }

    private void processShare(String oldRobotId, String sharedUserId, String newRobotId, String receivedUserId)
            throws Exception {
        List<CProcess> processList = processDao.getProcess(oldRobotId, 0, sharedUserId);
        if (CollectionUtils.isEmpty(processList)) throw new Exception();
        for (CProcess process : processList) {
            String nextId = String.valueOf(idWorker.nextId());
            process.setId(null);
            process.setProcessId(nextId);
            process.setRobotId(newRobotId);
            process.setCreateTime(new Date());
            process.setUpdateTime(new Date());
            process.setCreatorId(receivedUserId);
            process.setUpdaterId(receivedUserId);
        }
        processDao.insertProcessBatch(processList);
    }

    private void requireShare(String oldRobotId, String sharedUserId, String newRobotId, String receivedUserId) {
        List<CRequire> requireList = requireDao.getRequire(oldRobotId, 0, sharedUserId);
        if (CollectionUtils.isEmpty(requireList)) return;
        for (CRequire require : requireList) {
            require.setId(null);
            require.setRobotId(newRobotId);
            require.setCreateTime(new Date());
            require.setUpdateTime(new Date());
            require.setCreatorId(receivedUserId);
            require.setUpdaterId(receivedUserId);
        }
        requireDao.insertReqBatch(requireList);
    }

    private void paramShare(String oldRobotId, String sharedUserId, String newRobotId, String receivedUserId) {
        List<CParam> params = cParamDao.getParams(oldRobotId, sharedUserId);
        // 原机器人的流程id  和  副本机器人的流程id 的映射Map:（k,v） 为 （oldProcessId,newProcessId）
        List<CProcess> oldProcessList = processDao.getProcess(oldRobotId, 0, sharedUserId);
        List<CProcess> newProcessList = processDao.getProcess(newRobotId, 0, receivedUserId);
        Map<String, String> oldNewProcessIdMap = getOldNewProcessIdMap(newProcessList, oldProcessList);
        for (CParam cParam : params) {
            cParam.setId(idWorker.nextId() + "");
            cParam.setRobotId(newRobotId);
            // 保证子流程的processId和配置参数对应
            cParam.setProcessId(oldNewProcessIdMap.get(cParam.getProcessId()));
            cParam.setRobotVersion(0); // 新版本为0
            cParam.setCreateTime(new Date());
            cParam.setUpdateTime(new Date());
            cParam.setCreatorId(receivedUserId);
            cParam.setUpdaterId(receivedUserId);
            cParam.setDeleted(0);
        }
        cParamDao.insertParamBatch(params);
    }

    /**
     * 复制组件引用数据
     *
     * @param oldRobotId 原机器人ID
     * @param newRobotId 新机器人ID
     * @param userId     用户ID
     */
    private void componentUseCopy(String oldRobotId, String newRobotId, String userId) {
        // 查询原机器人的组件引用记录（版本0）
        List<ComponentRobotUse> componentRobotUseList =
                componentRobotUseDao.getComponentRobotUse(oldRobotId, 0, userId);
        if (CollectionUtils.isEmpty(componentRobotUseList)) return;

        // 处理每条记录：id置为null，robotId改为新ID，更新时间
        for (ComponentRobotUse componentRobotUse : componentRobotUseList) {
            componentRobotUse.setId(null);
            componentRobotUse.setRobotId(newRobotId);
            componentRobotUse.setCreateTime(new Date());
            componentRobotUse.setUpdateTime(new Date());
        }

        // 批量插入新记录
        componentRobotUseDao.insertBatch(componentRobotUseList);
    }

    /**
     * 复制组件屏蔽数据
     *
     * @param oldRobotId 原机器人ID
     * @param newRobotId 新机器人ID
     * @param userId     用户ID
     */
    private void componentBlockCopy(String oldRobotId, String newRobotId, String userId) {
        String tenantId = TenantUtils.getTenantId();
        // 查询原机器人的组件屏蔽记录（版本0）
        List<ComponentRobotBlock> componentRobotBlockList =
                componentRobotBlockDao.getComponentRobotBlockForCopy(oldRobotId, 0, tenantId);
        if (CollectionUtils.isEmpty(componentRobotBlockList)) return;

        // 处理每条记录：id置为null，robotId改为新ID，更新时间
        for (ComponentRobotBlock componentRobotBlock : componentRobotBlockList) {
            componentRobotBlock.setId(null);
            componentRobotBlock.setRobotId(newRobotId);
            componentRobotBlock.setCreateTime(new Date());
            componentRobotBlock.setUpdateTime(new Date());
        }

        // 批量插入新记录
        componentRobotBlockDao.insertBatch(componentRobotBlockList);
    }
}

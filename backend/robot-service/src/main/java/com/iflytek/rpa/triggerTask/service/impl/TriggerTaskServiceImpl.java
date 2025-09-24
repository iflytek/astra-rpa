package com.iflytek.rpa.triggerTask.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.*;
import static com.iflytek.rpa.utils.DeBounceUtils.deBounce;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import com.iflytek.rpa.base.entity.dto.QueryParamDto;
import com.iflytek.rpa.base.service.CParamService;
import com.iflytek.rpa.robot.constants.RobotConstant;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.task.dao.ScheduleTaskRobotDao;
import com.iflytek.rpa.task.entity.ScheduleTaskRobot;
import com.iflytek.rpa.task.entity.dto.RobotInfo;
import com.iflytek.rpa.triggerTask.dao.TriggerTaskDao;
import com.iflytek.rpa.triggerTask.entity.TriggerTask;
import com.iflytek.rpa.triggerTask.entity.dto.InsertTaskDto;
import com.iflytek.rpa.triggerTask.entity.dto.TaskPageDto;
import com.iflytek.rpa.triggerTask.entity.dto.UpdateTaskDto;
import com.iflytek.rpa.triggerTask.entity.enums.ExceptionalEnum;
import com.iflytek.rpa.triggerTask.entity.enums.TaskTypeEnum;
import com.iflytek.rpa.triggerTask.entity.vo.*;
import com.iflytek.rpa.triggerTask.service.TriggerTaskService;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

@Service("triggerTaskService")
public class TriggerTaskServiceImpl extends ServiceImpl<TriggerTaskDao, TriggerTask> implements TriggerTaskService {

    @Resource
    private RobotExecuteDao robotExecuteDao;

    @Resource
    private RobotDesignDao robotDesignDao;

    @Resource
    private ScheduleTaskRobotDao scheduleTaskRobotDao;

    @Autowired
    private CParamService paramService;

    @Autowired
    private IdWorker idWorker;

    @Value("${deBounce.prefix}")
    private String doBouncePrefix; // 防抖前缀

    @Value("${deBounce.window}")
    private Long deBounceWindow; // 防抖窗口

    @Override
    public AppResponse<Boolean> isTaskNameCopy(String name) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        return AppResponse.success(checkNameCopy(name, userId, tenantId));
    }

    /**
     * 查询执行器所有机器人，包括机器人基本信息、是否置灰、配置参数
     * @param name
     * @return
     * @throws NoLoginException
     */
    @Override
    public AppResponse<List<Executor>> getRobotExeList(String name) throws NoLoginException, JsonProcessingException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        name = StringUtils.trim(name);
        List<RobotExecute> robotExecuteList = robotExecuteDao.getRobotExecuteByName(name, userId, tenantId);
        packageCreateRobotVersion(robotExecuteList);
        // 如果为 create 本地创建  是没有 version的
        if (CollectionUtils.isEmpty(robotExecuteList)) return AppResponse.success(Collections.EMPTY_LIST); // 如果为空，直接返回

        List<Executor> resVoList = getExecutorList(robotExecuteList);

        return AppResponse.success(resVoList);
    }

    private void packageCreateRobotVersion(List<RobotExecute> robotExecuteList) {
        for (RobotExecute robotExecute : robotExecuteList) {
            String dataSource = robotExecute.getDataSource();
            if (CREATE.equals(dataSource)) {
                robotExecute.setAppVersion(robotExecute.getRobotVersion());
            }
        }
    }

    @Override
    public List<String> getUsingTasksByMail(String mailId) {
        return baseMapper
                .selectList(
                        new LambdaQueryWrapper<TriggerTask>()
                                .eq(TriggerTask::getTaskType, TaskTypeEnum.MAIL_TASK.getCode())
                                .eq(TriggerTask::getDeleted, 0)
                                .like(TriggerTask::getTaskJson, mailId) // 此处迁移不一定能奏效，数据结构设计不同
                        )
                .stream()
                .map(TriggerTask::getName)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<Boolean> insertTriggerTask(InsertTaskDto queryDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        checkInsertParam(queryDto); // 参数校验

        // 防抖
        String deBounceRedisKey = doBouncePrefix + tenantId + "-" + userId + "-" + queryDto.getName();
        deBounce(deBounceRedisKey, deBounceWindow);

        if (checkNameCopy(queryDto.getName(), userId, tenantId))
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "命名重复");

        // 插入triggerTask
        String triggerTaskId = insertTask(queryDto, userId, tenantId);
        // 插入scheduleTaskRobot
        insertTaskRobot(queryDto, userId, tenantId, triggerTaskId);

        return AppResponse.success(true);
    }

    /**
     * 计划任务-编辑-任务信息回显，包括机器人基本信息、是否置灰、配置参数
     * @param taskId
     * @return
     * @throws NoLoginException
     */
    @Override
    public AppResponse<TriggerTaskVo> getTriggerTask(String taskId) throws NoLoginException, JsonProcessingException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        if (StringUtils.isBlank(taskId)) throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "参数缺失");
        TriggerTask triggerTask = baseMapper.getTaskById(userId, tenantId, taskId);
        if (triggerTask == null) throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode());

        TriggerTaskVo triggerTaskVo = getTriggerTaskVo(triggerTask, userId, tenantId);

        return AppResponse.success(triggerTaskVo);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<Boolean> deleteTriggerTask(String taskId) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        if (StringUtils.isBlank(taskId)) throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "参数缺失");
        TriggerTask triggerTask = baseMapper.getTaskById(userId, tenantId, taskId);
        if (triggerTask == null) throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "该计划任务不存在，无法删除");

        Integer i = baseMapper.deleteTaskById(userId, tenantId, taskId);
        Integer j = scheduleTaskRobotDao.deleteByTaskIdLogically(taskId);

        if (i == 0 || j == 0) throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode());

        return AppResponse.success(true);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<Boolean> updateTriggerTask(UpdateTaskDto queryDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        TriggerTask oldTriggerTask = baseMapper.getTaskById(userId, tenantId, queryDto.getTaskId());
        if (oldTriggerTask == null) throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "该计划任务不存在，无法编辑");

        // 重名校验， 排除自己
        if (checkNameCopy(queryDto.getName(), userId, tenantId, oldTriggerTask.getName()))
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "命名重复");

        List<RobotInfo> robotInfoList = queryDto.getRobotInfoList();
        if (CollectionUtils.isEmpty(robotInfoList)) throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode());

        TriggerTask newTriggerTask = new TriggerTask();
        BeanUtils.copyProperties(queryDto, newTriggerTask);
        newTriggerTask.setId(oldTriggerTask.getId());

        // 更新 triggerTask表
        int i = baseMapper.updateById(newTriggerTask);
        if (i == 0) throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "计划任务更新失败");
        // 更新scheduleTaskRobot表
        updateScheduleTaskRobot(queryDto, userId, tenantId);

        return AppResponse.success(true);
    }

    @Override
    public AppResponse<Boolean> enableTriggerTask(String taskId, Integer enable) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        TriggerTask oldTriggerTask = baseMapper.getTaskById(userId, tenantId, taskId);
        if (oldTriggerTask == null) throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "该计划任务不存在，无法编辑");

        Boolean b = baseMapper.enableTask(userId, tenantId, taskId, enable);
        if (b) return AppResponse.success(true);
        else throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode());
    }

    @Override
    public AppResponse<IPage<TaskPageVo>> triggerTaskPage(TaskPageDto queryDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        IPage<TaskPageVo> resPage = new Page<>();
        IPage<TaskPageVo> pageConfig = new Page<>(queryDto.getPageNo(), queryDto.getPageSize(), true);
        resPage = baseMapper.getExecuteDataList(pageConfig, queryDto, userId, tenantId);
        if (resPage.getTotal() == 0) return AppResponse.success(resPage); // 如果为空，直接返回

        // 设置机器人信息
        setRobotInfo(resPage);

        return AppResponse.success(resPage);
    }

    @Override
    public AppResponse<IPage<TaskPage4TriggerVo>> triggerTaskPage4Trigger(TaskPageDto queryDto)
            throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        IPage<TaskPage4TriggerVo> resPage = new Page<>();
        IPage<TaskPage4TriggerVo> pageConfig = new Page<>(queryDto.getPageNo(), queryDto.getPageSize(), true);
        resPage = baseMapper.getExecuteDataList4Trigger(pageConfig, queryDto, userId, tenantId);

        if (resPage.getTotal() == 0L) return AppResponse.success(resPage); // 如果为空，直接返回结果

        // 设置机器人数据 robotInfoList
        setRobotInfoVoList(resPage);

        return AppResponse.success(resPage);
    }

    private void setRobotInfoVoList(IPage<TaskPage4TriggerVo> resPage) {
        List<TaskPage4TriggerVo> records = resPage.getRecords();
        List<String> taskIdList = records.stream().map(TaskPageVo::getTaskId).collect(Collectors.toList());

        List<ScheduleTaskRobot> scheduleTaskRobotList = scheduleTaskRobotDao.queryAll(taskIdList);
        for (TaskPage4TriggerVo record : records) {
            String taskId = record.getTaskId();

            // 当前taskId 对应的 scheduleTaskRobots
            List<ScheduleTaskRobot> scheduleTaskRobots = scheduleTaskRobotList.stream()
                    .filter(scheduleTaskRobot -> scheduleTaskRobot.getTaskId().equals(taskId))
                    .collect(Collectors.toList());

            List<RobotInfoVo> robotInfoVoList = getRobotInfoVoList(scheduleTaskRobots);

            record.setRobotInfoList(robotInfoVoList);
        }
    }

    private List<RobotInfoVo> getRobotInfoVoList(List<ScheduleTaskRobot> scheduleTaskRobots) {
        List<RobotInfoVo> ansVoList = new ArrayList<>();

        for (ScheduleTaskRobot scheduleTaskRobot : scheduleTaskRobots) {
            RobotInfoVo robotInfoVo = new RobotInfoVo();
            BeanUtils.copyProperties(scheduleTaskRobot, robotInfoVo);
            ansVoList.add(robotInfoVo);
        }

        return ansVoList;
    }

    private void setRobotInfo(IPage<TaskPageVo> resPage) {
        List<TaskPageVo> records = resPage.getRecords();

        List<String> taskIdList = records.stream().map(TaskPageVo::getTaskId).collect(Collectors.toList());
        if (CollectionUtils.isEmpty(taskIdList)) {
            return;
        }
        List<ScheduleTaskRobot> scheduleTaskRobotList = scheduleTaskRobotDao.queryAllByTaskId(taskIdList);

        for (TaskPageVo record : records) {
            String taskId = record.getTaskId();
            List<ScheduleTaskRobot> taskRobotList = scheduleTaskRobotList.stream()
                    .filter(scheduleTaskRobot -> scheduleTaskRobot.getTaskId().equals(taskId))
                    .collect(Collectors.toList());
            List<String> robotNameList =
                    taskRobotList.stream().map(ScheduleTaskRobot::getRobotName).collect(Collectors.toList());
            String robotNames = String.join(",", robotNameList);
            record.setRobotNames(robotNames);
        }

        resPage.setRecords(records);
    }

    public void updateScheduleTaskRobot(UpdateTaskDto queryDto, String userId, String tenantId) {
        InsertTaskDto insertTaskDto = new InsertTaskDto();
        BeanUtils.copyProperties(queryDto, insertTaskDto);
        String taskId = queryDto.getTaskId();
        Integer i = scheduleTaskRobotDao.deleteByTaskIdLogically(taskId);
        if (i == 0) throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "计划任务更新失败：计划任务机器人引用更新失败");

        insertTaskRobot(insertTaskDto, userId, tenantId, taskId);
    }

    private void checkInsertParam(InsertTaskDto queryDto) {
        if (CollectionUtils.isEmpty(queryDto.getRobotInfoList()))
            throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode());

        // 任务类型 是否属于四种枚举
        boolean b = Arrays.stream(TaskTypeEnum.values())
                .anyMatch(taskType -> taskType.getCode().equals(queryDto.getTaskType()));
        if (!b) throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "任务类型错误");

        // 异常类型是否属于枚举类
        boolean f = Arrays.stream(ExceptionalEnum.values())
                .anyMatch(exceptionalType -> exceptionalType.getCode().equals(queryDto.getExceptional()));
        if (!f) throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "异常类型错误");
    }

    private TriggerTaskVo getTriggerTaskVo(TriggerTask triggerTask, String userId, String tenantId)
            throws NoLoginException, JsonProcessingException {
        TriggerTaskVo triggerTaskVo = new TriggerTaskVo();
        BeanUtils.copyProperties(triggerTask, triggerTaskVo);

        List<ScheduleTaskRobot> taskRobotList =
                scheduleTaskRobotDao.queryByTaskId(triggerTask.getTaskId(), userId, tenantId);
        // 机器人必须有数据，如果没有，说明数据有问题
        if (CollectionUtils.isEmpty(taskRobotList)) throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode());

        List<RobotInfoVo> robotInfoVoList = getRobotInfoVos(taskRobotList);
        triggerTaskVo.setRobotInfoVoList(robotInfoVoList);
        triggerTaskVo.setEnable(triggerTaskVo.getEnable());
        triggerTaskVo.setQueueEnable(triggerTaskVo.getQueueEnable());

        return triggerTaskVo;
    }

    private List<RobotInfoVo> getRobotInfoVos(List<ScheduleTaskRobot> taskRobotList)
            throws NoLoginException, JsonProcessingException {
        List<RobotInfoVo> robotInfoVoList = new ArrayList<>();
        for (ScheduleTaskRobot scheduleTaskRobot : taskRobotList) {
            RobotInfoVo robotInfoVo = new RobotInfoVo();
            robotInfoVo.setId(scheduleTaskRobot.getId());
            robotInfoVo.setRobotName(scheduleTaskRobot.getRobotName());
            robotInfoVo.setSort(scheduleTaskRobot.getSort());
            setParam(robotInfoVo, scheduleTaskRobot.getRobotId());
            robotInfoVo.setParamJson(scheduleTaskRobot.getParamJson());
            robotInfoVo.setRobotId(scheduleTaskRobot.getRobotId());

            robotInfoVoList.add(robotInfoVo);
        }
        return robotInfoVoList;
    }

    private void setParam(RobotInfoVo robotInfoVo, String robotId) throws JsonProcessingException, NoLoginException {
        QueryParamDto queryParamDto = new QueryParamDto();
        queryParamDto.setRobotId(robotId);
        AppResponse<List<ParamDto>> paramListResponse = paramService.getAllParams(queryParamDto);
        List<ParamDto> paramList = paramListResponse.getData();
        if (CollectionUtils.isEmpty(paramList)) {
            robotInfoVo.setHaveParam(false);
            robotInfoVo.setParamJson(null);
            return;
        }
        robotInfoVo.setHaveParam(true);
        ObjectMapper mapper = new ObjectMapper();
        String paramJson = mapper.writeValueAsString(paramList);
        robotInfoVo.setParamJson(paramJson);
    }

    public void insertTaskRobot(InsertTaskDto queryDto, String userId, String tenantId, String triggerTaskId) {
        List<RobotInfo> robotInfoList = queryDto.getRobotInfoList();
        List<ScheduleTaskRobot> scheduleTaskRobotList = new ArrayList<>();

        for (int i = 0; i < robotInfoList.size(); i++) {
            RobotInfo robotInfo = robotInfoList.get(i);

            ScheduleTaskRobot scheduleTaskRobot = new ScheduleTaskRobot();

            scheduleTaskRobot.setRobotId(robotInfo.getRobotId());
            scheduleTaskRobot.setSort(i + 1);
            scheduleTaskRobot.setTenantId(tenantId);
            scheduleTaskRobot.setCreatorId(userId);
            scheduleTaskRobot.setUpdaterId(userId);
            scheduleTaskRobot.setParamJson(robotInfo.getParamJson());

            scheduleTaskRobotList.add(scheduleTaskRobot);
        }

        scheduleTaskRobotDao.insertRobotBatch(triggerTaskId, scheduleTaskRobotList);
    }

    public String insertTask(InsertTaskDto queryDto, String userId, String tenantId) {
        TriggerTask triggerTask = new TriggerTask();

        String taskId = String.valueOf(idWorker.nextId());

        triggerTask.setTaskId(taskId);
        triggerTask.setName(queryDto.getName());
        triggerTask.setTaskJson(queryDto.getTaskJson());
        triggerTask.setTaskType(queryDto.getTaskType());
        triggerTask.setEnable(queryDto.getEnable());
        triggerTask.setExceptional(queryDto.getExceptional());
        triggerTask.setQueueEnable(queryDto.getQueueEnable());
        triggerTask.setTimeout(queryDto.getTimeout());
        triggerTask.setCreatorId(userId);
        triggerTask.setUpdaterId(userId);
        triggerTask.setTenantId(tenantId);

        baseMapper.insert(triggerTask);

        return taskId;
    }

    private List<Executor> getExecutorList(List<RobotExecute> robotExecuteList)
            throws NoLoginException, JsonProcessingException {
        List<Executor> result = new ArrayList<>();
        for (RobotExecute robotExecute : robotExecuteList) {
            Executor executor = new Executor();
            String robotId = robotExecute.getRobotId();
            executor.setRobotName(robotExecute.getName());
            executor.setRobotId(robotId);

            executor.setRobotVersion(robotExecute.getAppVersion());

            QueryParamDto queryParamDto = new QueryParamDto();
            // Mode 设置为 EXECUTOR 模式
            queryParamDto.setMode(RobotConstant.EXECUTOR);
            queryParamDto.setRobotId(robotId);
            AppResponse<List<ParamDto>> paramListResponse = paramService.getAllParams(queryParamDto);
            List<ParamDto> paramList = paramListResponse.getData();
            if (CollectionUtils.isEmpty(paramList)) {
                executor.setHaveParam(false);
                executor.setParamJson(null);
                result.add(executor);
                continue;
            }
            executor.setHaveParam(true);
            ObjectMapper mapper = new ObjectMapper();
            String paramJson = mapper.writeValueAsString(paramList);
            executor.setParamJson(paramJson);
            result.add(executor);
        }

        return result;
    }

    // 插入的时候，不用排除自己
    private boolean checkNameCopy(String name, String userId, String tenantId) {
        List<String> allTaskName = baseMapper.getAllTaskName(userId, tenantId);
        if (allTaskName.contains(name)) return true;
        return false;
    }

    // 更新的时候，需要排除自己再判断
    private boolean checkNameCopy(String name, String userId, String tenantId, String oldName) {
        if (name.equals(oldName)) return false; // 名字和自己相同

        // 在判断其他的
        List<String> allTaskName = baseMapper.getAllTaskName(userId, tenantId);
        if (allTaskName.contains(name)) return true;
        return false;
    }
}

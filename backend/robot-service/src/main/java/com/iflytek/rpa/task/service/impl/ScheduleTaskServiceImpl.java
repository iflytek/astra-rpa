package com.iflytek.rpa.task.service.impl;

import com.alibaba.fastjson.JSONObject;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.task.dao.ScheduleTaskDao;
import com.iflytek.rpa.task.dao.ScheduleTaskExecuteDao;
import com.iflytek.rpa.task.dao.ScheduleTaskPullLogDao;
import com.iflytek.rpa.task.dao.ScheduleTaskRobotDao;
import com.iflytek.rpa.task.entity.ScheduleTask;
import com.iflytek.rpa.task.entity.ScheduleTaskRobot;
import com.iflytek.rpa.task.entity.bo.ScheduleRule;
import com.iflytek.rpa.task.entity.bo.TimeTask;
import com.iflytek.rpa.task.entity.dto.NextTaskDto;
import com.iflytek.rpa.task.entity.dto.ScheduleTaskDto;
import com.iflytek.rpa.task.entity.dto.TaskDto;
import com.iflytek.rpa.task.entity.dto.TaskInfoDto;
import com.iflytek.rpa.task.entity.enums.CycleWeekEnum;
import com.iflytek.rpa.task.service.CronExpression;
import com.iflytek.rpa.task.service.ScheduleTaskService;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.*;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

/**
 * <p>
 * 调度任务 服务实现类
 * </p>
 *
 * @author keler
 * @since 2021-10-08
 */
@Slf4j
@Service("scheduleTaskService")
public class ScheduleTaskServiceImpl extends ServiceImpl<ScheduleTaskDao, ScheduleTask> implements ScheduleTaskService {

    @Autowired
    private ScheduleTaskDao scheduleTaskDao;

    @Autowired
    private ScheduleTaskRobotDao scheduleTaskRobotDao;

    @Autowired
    private ScheduleTaskExecuteDao scheduleTaskExecuteDao;

    @Autowired
    private ScheduleTaskPullLogDao scheduleTaskPullLogDao;

    @Autowired
    private RobotVersionDao robotVersionDao;

    @Autowired
    private IdWorker idWorker;

    private int taskMaxSize = 100;

    public Date generateNextValidTimeNew(ScheduleTask task, Date fromTime) throws Exception {
        if ("fixed".equals(task.getRunMode()) || "custom".equals(task.getRunMode())) {
            return new CronExpression(task.getScheduleConf()).getNextValidTimeAfter(fromTime);
        } else if ("cycle".equals(task.getRunMode())) {
            return generateValidTimeByStartTime(Integer.parseInt(task.getScheduleConf()), task.getStartAt());
        }
        return null;
    }

    public static Date generateValidTimeByStartTime(Integer time, Date fromTime) {
        Date date = new Date();
        if (date.before(fromTime)) {
            // 如果当前时间还没到第一次执行时间，直接返回第一次执行时间
            return new Date(fromTime.getTime());
        }
        // 计算当前时间与开始时间之间的秒数:
        int seconds = (int) Math.ceil(Double.valueOf((date.getTime() - fromTime.getTime()) / (1000)));
        // 计算当前时间前最后一次符合时间间隔的执行时间
        long newTime = (long) (Math.ceil((double) seconds / time) * time * 1000) + fromTime.getTime();
        return new Date(newTime);
    }

    public Date getCalSecond(Date date, int calSeconds) {
        Calendar c = Calendar.getInstance();
        c.setTime(date);
        c.add(Calendar.SECOND, calSeconds);
        return c.getTime();
    }

    private void timeTransToCron(ScheduleTask task) {
        // 设置类型，转换为cron表达式
        // 时间触发
        if ("cycle".equals(task.getRunMode())) {
            // 循环
            long seconds = 0L;
            // 循环
            if ("custom".equals(task.getCycleFrequency())) {
                // 自定义时长
                if ("minute".equals(task.getCycleUnit())) {
                    // 分钟
                    seconds = 60 * Long.parseLong(task.getCycleNum());
                } else if ("hour".equals(task.getCycleUnit())) {
                    // 小时
                    seconds = 3600 * Long.parseLong(task.getCycleNum());
                }
            } else {
                seconds = Long.parseLong(task.getCycleFrequency());
            }
            // todo 首次执行时间
            task.setScheduleConf(Long.toString(seconds));
        } else if ("fixed".equals(task.getRunMode())) {
            // 定时

            String cron = "";
            // 定时
            ScheduleRule rule = JSONObject.parseObject(task.getScheduleRule(), ScheduleRule.class);
            if ("month".equals(task.getScheduleType())) {
                // 每月固定时间点
                cron = rule.getSecond() + " " + rule.getMinute() + " " + rule.getHour() + " " + rule.getDate() + " * ?";
            } else if ("week".equals(task.getScheduleType())) {
                // 每周固定时间点
                cron = rule.getSecond() + " " + rule.getMinute() + " " + rule.getHour() + " ? * "
                        + CycleWeekEnum.getCodeByNum(rule.getDayOfWeek());
            } else if ("day".equals(task.getScheduleType())) {
                // 每日固定时间点
                cron = rule.getSecond() + " " + rule.getMinute() + " " + rule.getHour() + " * * ?";
            }
            task.setScheduleConf(cron);
        } else if ("custom".equals(task.getRunMode())) {
            // 自定义
            String cron = task.getCronExpression();
            task.setScheduleConf(cron);
        }
    }

    @Override
    public AppResponse<?> getTaskList(TaskDto taskDto) throws NoLoginException {
        IPage<ScheduleTask> pages = new Page<>();
        if (null == taskDto.getPageNo() || null == taskDto.getPageSize()) {
            return AppResponse.success(pages);
        }
        taskDto.setUserId(UserUtils.nowUserId());
        IPage<ScheduleTask> pageConfig = new Page<>(taskDto.getPageNo(), taskDto.getPageSize(), true);
        pages = scheduleTaskDao.getTaskList(pageConfig, taskDto);
        List<ScheduleTask> taskList = pages.getRecords();
        if (CollectionUtils.isEmpty(taskList)) {
            return AppResponse.success(pages);
        }
        // 获取机器人名称
        // 获取机器人id和版本
        //        Map<String, List<TaskRobotBo>> taskRobotMap = new HashMap<>();
        //        List<TaskRobotBo> allRobotList = new ArrayList<>();
        // 获取taskId列表
        List<String> taskIdList = taskList.stream().map(ScheduleTask::getTaskId).collect(Collectors.toList());
        // 查询所有计划任务机器人
        List<ScheduleTaskRobot> scheduleTaskRobotList = scheduleTaskRobotDao.queryAllByTaskId(taskIdList);
        // 机器人根据taskId分组
        Map<String, List<ScheduleTaskRobot>> scheduleTaskRobotMap =
                scheduleTaskRobotList.stream().collect(Collectors.groupingBy(ScheduleTaskRobot::getTaskId));
        if (CollectionUtils.isEmpty(scheduleTaskRobotMap)) {
            return AppResponse.success(pages);
        }

        //        for (ScheduleTask task: taskList) {
        //            if(null == task || null == task.getExecuteSequence()){
        //                continue;
        //            }
        //            List<TaskRobotBo> taskRobotList = JSONObject.parseArray(task.getExecuteSequence(),
        // TaskRobotBo.class);
        //            taskRobotMap.put(task.getTaskId(), taskRobotList);
        //            allRobotList.addAll(taskRobotList);
        //        }
        //        if(CollectionUtils.isEmpty(allRobotList)){
        //            return AppResponse.error(ErrorCodeEnum.E_SQL,"数据异常，计划任务无机器人信息");
        //        }
        // 根据id和版本查名字
        //        List<RobotVersion> robotVersionList = robotVersionDao.getRobotNameList(allRobotList);
        //        if(CollectionUtils.isEmpty(robotVersionList)){
        //            return AppResponse.success(pages);
        //        }
        //        //根据robotId分组
        //        Map<String, String> robotVersionMap =
        // robotVersionList.stream().collect(Collectors.toMap(RobotVersion::getRobotId,RobotVersion::getName));
        // 设置名字
        for (ScheduleTask task : taskList) {
            String taskId = task.getTaskId();
            List<ScheduleTaskRobot> taskRobotList = scheduleTaskRobotMap.get(taskId);
            StringBuilder robotNameStr = new StringBuilder();
            if (CollectionUtils.isEmpty(taskRobotList)) {
                continue;
            }
            for (ScheduleTaskRobot taskRobot : taskRobotList) {
                if (null == taskRobot) {
                    continue;
                }
                robotNameStr.append(taskRobot.getRobotName()).append(",");
            }
            robotNameStr.deleteCharAt(robotNameStr.length() - 1);
            task.setAllRobotName(robotNameStr.toString());
            // 设置下次执行时间
            // 如果是禁用，或截止时间小于当前，则不获取时间，
            if (!needNextTime(task)) {
                task.setNextTime(null);
            } else {
                try {
                    setNextTime(task);
                } catch (Exception e) {
                    task.setNextTime(null);
                    log.error("getTaskList获取下次执行时间错误：{}", e.getMessage());
                }
            }
        }

        return AppResponse.success(pages);
    }

    private void setNextTime(ScheduleTask task) throws Exception {
        Date date = new Date();
        //        task.setLastTime(task.getNextTime());
        //        task.setPullTime(new Date());
        timeTransToCron(task);
        //        try {
        task.setNextTime(generateNextValidTimeNew(task, getCalSecond(date, 5)));
        //        }catch (Exception e){
        //            log.error(e.getMessage());
        //        task.setNextTime(null);
        //        }
    }

    private boolean needNextTime(ScheduleTask task) {
        if (null == task || null == task.getEnable()) {
            return false;
        }
        if (0 == task.getEnable()) {
            return false;
        }
        if (null == task.getStartAt() || null == task.getEndAt()) {
            return false;
        }
        if (task.getEndAt().before(new Date())) {
            return false;
        }
        return true;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> saveTask(ScheduleTaskDto task) throws NoLoginException {
        ScheduleTask scheduleTask = new ScheduleTask();
        BeanUtils.copyProperties(task, scheduleTask);
        // 从timeTask获取信息
        TimeTask timeTask = task.getTimeTask();
        if (null != timeTask) {
            BeanUtils.copyProperties(timeTask, scheduleTask);
            if (null != timeTask.getScheduleRule()) {
                scheduleTask.setScheduleRule(JSONObject.toJSONString(timeTask.getScheduleRule()));
            }
        }
        scheduleTask.setTenantId(TenantUtils.getTenantId());
        String userId = UserUtils.nowUserId();
        scheduleTask.setCreatorId(userId);
        scheduleTask.setUpdaterId(userId);
        // 设置下次执行时间
        try {
            setNextTime(scheduleTask);
        } catch (Exception e) {
            log.error(e.getMessage());
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "不正确的时间配置");
        }
        List<String> taskRobotIdList = task.getExecuteSequence();
        if (CollectionUtils.isEmpty(taskRobotIdList)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "请选择机器人");
        }
        // 设置执行顺序
        List<ScheduleTaskRobot> taskRobotList = new ArrayList<>();
        for (int i = 0; i < taskRobotIdList.size(); i++) {
            if (null == taskRobotIdList.get(i)) {
                continue;
            }
            ScheduleTaskRobot scheduleTaskRobot = new ScheduleTaskRobot();
            scheduleTaskRobot.setRobotId(taskRobotIdList.get(i));
            scheduleTaskRobot.setSort(i + 1);
            scheduleTaskRobot.setTenantId(TenantUtils.getTenantId());
            scheduleTaskRobot.setCreatorId(userId);
            scheduleTaskRobot.setUpdaterId(userId);
            taskRobotList.add(scheduleTaskRobot);
        }
        if (StringUtils.isNotBlank(task.getTaskId())) {
            Integer count = scheduleTaskDao.queryCountByTaskId(task.getTaskId());
            if (count > 0) {
                scheduleTask.setTaskId(task.getTaskId());
                scheduleTaskDao.updateScheduleTask(scheduleTask);
                // 查询历史机器人
                List<String> hisTaskRobotIdList =
                        scheduleTaskRobotDao.queryHisRobotIdListByTaskId(scheduleTask.getTaskId());
                // 是更新操作，且数据修改了，则先删后增
                if (!hisTaskRobotIdList.equals(taskRobotIdList)) {
                    // 插入或更新计划任务包含的机器人和执行顺序
                    scheduleTaskRobotDao.deleteByTaskId(scheduleTask.getTaskId());
                    scheduleTaskRobotDao.insertRobotBatch(scheduleTask.getTaskId(), taskRobotList);
                }
            } else {
                return AppResponse.error(ErrorCodeEnum.E_SQL, "数据异常，任务不存在");
            }
        } else {
            scheduleTask.setTaskId(idWorker.nextId() + "");
            scheduleTask.setEnable(1);
            scheduleTaskDao.createScheduleTask(scheduleTask);
            // 首次创建计划任务，直接插入机器人列表
            scheduleTaskRobotDao.insertRobotBatch(scheduleTask.getTaskId(), taskRobotList);
        }
        return AppResponse.success(true);
    }

    @Override
    public AppResponse<?> getTaskInfoByTaskId(String taskId) throws NoLoginException {
        if (StringUtils.isBlank(taskId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "缺少计划任务id");
        }
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        TaskInfoDto taskInfoDto = new TaskInfoDto();
        ScheduleTask task = scheduleTaskDao.getTaskInfoByTaskId(taskId, userId, tenantId);
        if (null == task) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "数据异常，任务不存在");
        }
        // 查询包含机器人
        List<String> robotIdList = scheduleTaskRobotDao.queryRobotIdListByTaskId(taskId);
        task.setExecuteSequence(robotIdList);
        TimeTask timeTask = new TimeTask();
        BeanUtils.copyProperties(task, timeTask, "scheduleRule");
        if (null != task.getScheduleRule()) {
            timeTask.setScheduleRule(JSONObject.parseObject(task.getScheduleRule(), ScheduleRule.class));
        }
        BeanUtils.copyProperties(task, taskInfoDto);
        taskInfoDto.setTimeTask(timeTask);
        return AppResponse.success(taskInfoDto);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> getNextTimeInfoAndUpdate() throws NoLoginException {
        // todo 机器人、其他计划任务和本次计划任务冲突
        /**
         * 本次计划任务还没执行完，下次的执行时间就到了，那下次的直接记为失败
         */
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        // 查询启用状态的计划任务
        ScheduleTask task = getRecentlyTask(userId, tenantId);
        //        ScheduleTask task = scheduleTaskDao.getTaskListOrderByNextTime(userId, tenantId);
        if (null == task || null == task.getNextTime()) {
            return AppResponse.success(null);
        }
        task.setPullTime(new Date());
        task.setLastTime(task.getNextTime());
        NextTaskDto nextTaskDto = new NextTaskDto();
        // 本计划任务下次执行时间
        nextTaskDto.setNextTime(task.getNextTime());
        //        return AppResponse.error(ErrorCodeEnum.E_SQL,"数据异常");
        nextTaskDto.setTaskId(task.getTaskId());
        nextTaskDto.setTaskName(task.getName());
        nextTaskDto.setExceptionHandleWay(task.getExceptionHandleWay());
        // 查找机器人列表
        List<String> robotIdList = scheduleTaskRobotDao.queryRobotIdListByTaskId(task.getTaskId());
        if (CollectionUtils.isEmpty(robotIdList)) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "数据异常，计划任务无有效机器人");
        }
        nextTaskDto.setRobotIdList(robotIdList);
        // 更新下次执行时间
        scheduleTaskDao.updateScheduleTask(task);
        if (null != task.getLogEnable() && "T".equals(task.getLogEnable())) {
            scheduleTaskPullLogDao.insetLog(task);
        }

        return AppResponse.success(nextTaskDto);
    }

    public ScheduleTask getRecentlyTask(String userId, String tenantId) {
        int total = scheduleTaskDao.countTaskTotal(userId, tenantId);
        if (0 == total) {
            return null;
        }
        if (total > taskMaxSize) {
            throw new IllegalStateException("启用中计划任务数量超过" + taskMaxSize + "个" + ", 请将部分任务禁用");
        }
        //        PageBatch pageBatch = new PageBatch();
        // 批量操作，防止数据量过大，内存溢出或mybatis报错
        ScheduleTask recentlyTask = new ScheduleTask();
        //        pageBatch.process(total, batchSize, (start, end) -> {
        List<ScheduleTask> taskList = scheduleTaskDao.getTaskListByPage(userId, tenantId);
        for (ScheduleTask scheduleTask : taskList) {
            if (null == scheduleTask) {
                continue;
            }
            try {
                setNextTime(scheduleTask);
            } catch (Exception e) {
                throw new IllegalArgumentException("数据异常");
            }

            if (null == recentlyTask.getNextTime()) {
                BeanUtils.copyProperties(scheduleTask, recentlyTask);
            }
            if (recentlyTask.getNextTime().after(scheduleTask.getNextTime())) {
                BeanUtils.copyProperties(scheduleTask, recentlyTask);
            }
        }
        //            return new ArrayList<>();
        //        });

        return recentlyTask;
    }

    @Override
    public AppResponse<?> enableTask(ScheduleTask task) {
        if (null == task.getTaskId() || null == task.getEnable()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM);
        }
        if (1 == task.getEnable()) {
            try {
                // 每次启用更新一下下次执行时间
                setNextTime(task);
            } catch (Exception e) {
                return AppResponse.error(ErrorCodeEnum.E_SQL, "数据异常");
            }
        }
        scheduleTaskDao.updateTask(task);
        return AppResponse.success(true);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> deleteTask(ScheduleTask task) {
        if (null == task.getTaskId()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM);
        }
        task.setDeleted(1);
        scheduleTaskDao.updateTask(task);
        // 删除schedule——robot
        scheduleTaskRobotDao.deleteByTaskId(task.getTaskId());
        return AppResponse.success(true);
    }

    @Override
    public AppResponse<?> checkSameName(ScheduleTask task) {
        String taskName = task.getName();
        if (StringUtils.isBlank(taskName)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "任务名称不能为空");
        }
        Integer count = scheduleTaskDao.countByTaskName(task);
        return AppResponse.success(count > 0);
    }

    @Override
    public AppResponse<?> checkCorn(ScheduleTask task) {
        if (StringUtils.isBlank(task.getCronExpression())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "corn表达式不能为空");
        }
        try {
            new CronExpression(task.getCronExpression());
        } catch (Exception e) {
            return AppResponse.success(false);
        }
        return AppResponse.success(true);
    }
}

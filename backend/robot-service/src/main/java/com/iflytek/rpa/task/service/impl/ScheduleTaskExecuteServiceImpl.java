package com.iflytek.rpa.task.service.impl;

import static com.iflytek.rpa.task.constants.TaskConstant.TASK_RESULT_EXECUTE;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.robot.dao.RobotExecuteRecordDao;
import com.iflytek.rpa.robot.entity.RobotExecuteRecord;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.task.dao.ScheduleTaskExecuteDao;
import com.iflytek.rpa.task.entity.ScheduleTaskExecute;
import com.iflytek.rpa.task.entity.dto.ScheduleTaskRecordDeleteDto;
import com.iflytek.rpa.task.entity.dto.ScheduleTaskRecordDto;
import com.iflytek.rpa.task.entity.dto.TaskExecuteDto;
import com.iflytek.rpa.task.entity.vo.TaskRecordListVo;
import com.iflytek.rpa.task.service.ScheduleTaskExecuteService;
import com.iflytek.rpa.utils.DateUtils;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.*;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

/**
 * 计划任务执行记录(ScheduleTaskExecute)表服务实现类
 *
 * @author mjren
 * @since 2024-10-15 14:59:09
 */
@Slf4j
@Service("scheduleTaskExecuteService")
public class ScheduleTaskExecuteServiceImpl extends ServiceImpl<ScheduleTaskExecuteDao, ScheduleTaskExecute>
        implements ScheduleTaskExecuteService {
    @Resource
    private ScheduleTaskExecuteDao scheduleTaskExecuteDao;

    @Autowired
    private RobotExecuteRecordDao robotExecuteRecordDao;

    @Autowired
    private IdWorker idWorker;

    /**
     * 任务执行超时时间（小时），默认24小时
     */
    @Value("${schedule.task.timeout.hours:24}")
    private Integer taskTimeoutHours;

    @Override
    public AppResponse<?> setTaskExecuteStatus(TaskExecuteDto executeDto) throws NoLoginException {

        // 原有业务逻辑
        // 生成executeId
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        String taskExecuteId = executeDto.getTaskExecuteId();
        if (null == executeDto.getTaskId()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "任务ID不能为空");
        }
        if (null == taskExecuteId) {
            // 第一次执行
            taskExecuteId = idWorker.nextId() + "";
            ScheduleTaskExecute scheduleTaskExecute = new ScheduleTaskExecute();
            scheduleTaskExecute.setTaskId(executeDto.getTaskId());
            scheduleTaskExecute.setTaskExecuteId(taskExecuteId);
            scheduleTaskExecute.setResult(TASK_RESULT_EXECUTE);
            scheduleTaskExecute.setTenantId(tenantId);
            scheduleTaskExecute.setCreatorId(userId);
            scheduleTaskExecute.setUpdaterId(userId);
            scheduleTaskExecute.setStartTime(new Date());
            // 获取最大批次号
            Integer maxBatch = scheduleTaskExecuteDao.getMaxBatch(executeDto.getTaskId());
            if (null == maxBatch || 0 == maxBatch) {
                scheduleTaskExecute.setCount(1);
            } else {
                scheduleTaskExecute.setCount(maxBatch + 1);
            }
            // 插入
            scheduleTaskExecuteDao.insertExecuteRecord(scheduleTaskExecute);
            // 返回执行id
            return AppResponse.success(taskExecuteId);
        }
        Integer executeCount = scheduleTaskExecuteDao.countExecuteRecord(taskExecuteId);
        if (executeCount < 1) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "划任务执行记录数据异常");
        }
        // 不是第一次执行，更新执行状态
        if (null == executeDto.getResult()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "计划任务执行结果不能为空");
        }
        if (null == executeDto.getEndTime()) {
            executeDto.setEndTime(new Date());
        }
        scheduleTaskExecuteDao.updateExecuteStatus(executeDto);
        return AppResponse.success(taskExecuteId);
    }

    @Override
    public AppResponse<?> getTaskExecuteRecordList(TaskExecuteDto executeDto) throws NoLoginException {
        // 计划任务记录
        IPage<TaskExecuteDto> pages = new Page<>();
        if (null == executeDto.getPageNo() || null == executeDto.getPageSize()) {
            return AppResponse.success(pages);
        }
        executeDto.setCreatorId(UserUtils.nowUserId());
        executeDto.setTenantId(TenantUtils.getTenantId());
        IPage<TaskExecuteDto> pageConfig = new Page<>(executeDto.getPageNo(), executeDto.getPageSize(), true);
        pages = scheduleTaskExecuteDao.getTaskExecuteRecordList(pageConfig, executeDto);
        List<TaskExecuteDto> taskList = pages.getRecords();
        if (CollectionUtils.isEmpty(taskList)) {
            return AppResponse.success(pages);
        }
        // 设置序号,从1到n
        long offset = pageConfig.offset() + 1;
        for (int i = 0; i < taskList.size(); i++) {
            taskList.get(i).setId(offset + i);
        }
        // 获取执行id列表，查询执行记录
        List<String> executeIdList =
                taskList.stream().map(TaskExecuteDto::getTaskExecuteId).collect(Collectors.toList());
        executeIdList.removeIf(executeId -> null == executeId || executeId.isEmpty());
        if (CollectionUtils.isEmpty(executeIdList)) {
            return AppResponse.success(pages);
        }
        List<RobotExecuteRecord> executeRecordList = robotExecuteRecordDao.getRecordByExecuteIdList(executeIdList);
        // 根据执行id分组，按照开始时间正序排序
        Map<String, List<RobotExecuteRecord>> executeRecordMap = executeRecordList.stream()
                .collect(Collectors.groupingBy(RobotExecuteRecord::getTaskExecuteId, Collectors.toList()));
        for (TaskExecuteDto task : taskList) {
            List<RobotExecuteRecord> executeRecordListByExecuteId = executeRecordMap.get(task.getTaskExecuteId());
            if (CollectionUtils.isEmpty(executeRecordListByExecuteId)) {
                continue;
            }
            // 按照开始时间正序排序
            executeRecordListByExecuteId.sort(Comparator.comparing(RobotExecuteRecord::getStartTime));
            task.setRobotExecuteRecordList(executeRecordListByExecuteId);
        }

        return AppResponse.success(pages);
    }

    @Override
    public AppResponse<IPage<TaskRecordListVo>> getRecordList(ScheduleTaskRecordDto recordDto) throws NoLoginException {
        // 参数校验
        if (recordDto.getPageNo() == null || recordDto.getPageSize() == null) {
            return AppResponse.success(new Page<>());
        }

        // 获取用户和租户信息
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        recordDto.setUserId(userId);
        recordDto.setTenantId(tenantId);

        // 构造分页对象
        IPage<TaskRecordListVo> pageConfig = new Page<>(recordDto.getPageNo(), recordDto.getPageSize());

        // 调用DAO层查询
        IPage<TaskRecordListVo> pages = baseMapper.getTaskRecordList(pageConfig, recordDto);

        List<TaskRecordListVo> taskList = pages.getRecords();
        if (CollectionUtils.isEmpty(taskList)) {
            return AppResponse.success(pages);
        }

        // 获取执行ID列表，查询机器人执行记录
        List<String> taskExecuteIdList = taskList.stream()
                .map(TaskRecordListVo::getTaskExecuteId)
                .filter(executeId -> executeId != null && !executeId.isEmpty())
                .collect(Collectors.toList());

        if (!CollectionUtils.isEmpty(taskExecuteIdList)) {
            // 查询机器人执行记录
            List<RobotExecuteRecord> executeRecordList =
                    robotExecuteRecordDao.getRecordByExecuteIdList(taskExecuteIdList);

            // 将机器人执行记录分组并设置到对应的任务记录中
            if (!CollectionUtils.isEmpty(executeRecordList)) {
                // 按任务执行ID分组
                java.util.Map<String, List<RobotExecuteRecord>> recordMap =
                        executeRecordList.stream().collect(Collectors.groupingBy(RobotExecuteRecord::getTaskExecuteId));

                // 为每个任务记录设置对应的机器人执行记录
                taskList.forEach(task -> {
                    List<RobotExecuteRecord> robotRecords = recordMap.get(task.getTaskExecuteId());
                    if (robotRecords != null) {
                        task.setRobotExecuteRecordList(robotRecords);
                    }
                });
            }
        }

        return AppResponse.success(pages);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> batchDelete(ScheduleTaskRecordDeleteDto dto) throws NoLoginException {
        List<String> taskExecuteIdList = dto.getTaskExecuteIdList();
        taskExecuteIdList.removeIf(Objects::isNull);
        if (CollectionUtils.isEmpty(taskExecuteIdList)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_CHECK, "任务执行ID列表不能为空");
        }
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 1. 逻辑删除 schedule_task_execute 表中的记录
        Integer scheduleDeleted =
                scheduleTaskExecuteDao.batchDeleteByTaskExecuteIds(taskExecuteIdList, userId, tenantId);

        // 2. 删除 robot_execute_record 表中的记录
        Integer robotDeleted = robotExecuteRecordDao.batchDeleteByTaskExecuteIds(taskExecuteIdList, userId, tenantId);

        return AppResponse.success(String.format("成功删除 %d 条计划任务执行记录，%d 条机器人执行记录", scheduleDeleted, robotDeleted));
    }

    /**
     * 定时任务：每小时执行一次，处理超时的执行记录
     * 将状态为executing且开始时间已经过去指定小时数的记录更新为cancel状态
     */
    @Scheduled(fixedRate = 3_600_000)
    public void cleanUpTimeoutExecutingRecords() {
        try {
            log.info("开始执行定时任务：清理执行超时的执行记录 [超时时间: {} 小时]", taskTimeoutHours);
            // 1. 计算超时时间点
            Date currentTime = new Date();
            int timeoutMinutes = taskTimeoutHours * 60;
            Date timeoutTime = DateUtils.getCalMinute(currentTime, -timeoutMinutes);
            // 2. 查询超时的执行记录
            List<ScheduleTaskExecute> timeoutRecords = scheduleTaskExecuteDao.getTimeoutExecutingRecords(timeoutTime);
            timeoutRecords.removeIf(Objects::isNull);
            if (CollectionUtils.isEmpty(timeoutRecords)) {
                return;
            }
            // 3. 提取ID列表
            List<Long> idList =
                    timeoutRecords.stream().map(ScheduleTaskExecute::getId).collect(Collectors.toList());
            // 4. 根据ID列表批量更新
            Integer updatedCount = scheduleTaskExecuteDao.updateExecutingRecordsToCancelByIds(idList);
            log.info("定时任务执行完成，共更新了 {} 条超时的执行记录为取消状态", updatedCount);
        } catch (Exception e) {
            log.error("执行清理超时执行记录定时任务时发生异常", e);
        }
    }
}

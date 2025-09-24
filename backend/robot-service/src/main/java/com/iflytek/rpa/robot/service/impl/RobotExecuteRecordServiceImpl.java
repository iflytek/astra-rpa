package com.iflytek.rpa.robot.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.ROBOT_RESULT_EXECUTE;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.base.annotation.RobotVersionAnnotation;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotExecuteRecordDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotExecuteRecord;
import com.iflytek.rpa.robot.entity.dto.ExecuteRecordDto;
import com.iflytek.rpa.robot.entity.dto.RobotExecuteRecordsBatchDeleteDto;
import com.iflytek.rpa.robot.service.RobotExecuteRecordService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.task.dao.ScheduleTaskDao;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

/**
 * 云端机器人执行记录表(RobotExecute)表服务实现类
 *
 * @author makejava
 * @since 2024-09-29 15:27:41
 */
@Slf4j
@Service("robotExecuteRecordService")
public class RobotExecuteRecordServiceImpl extends ServiceImpl<RobotExecuteRecordDao, RobotExecuteRecord>
        implements RobotExecuteRecordService {

    @Autowired
    ScheduleTaskDao scheduleTaskDao;

    @Autowired
    private RobotExecuteRecordDao robotExecuteRecordDao;

    @Autowired
    private RobotExecuteDao robotExecuteDao;

    @Autowired
    private RobotVersionDao robotVersionDao;

    @Autowired
    private IdWorker idWorker;

    @Override
    public AppResponse<?> recordList(ExecuteRecordDto recordDto) throws NoLoginException {
        IPage<RobotExecuteRecord> pages = new Page<>();
        if (null == recordDto.getPageNo() || null == recordDto.getPageSize()) {
            return AppResponse.success(pages);
        }
        recordDto.setCreatorId(UserUtils.nowUserId());
        recordDto.setTenantId(TenantUtils.getTenantId());
        IPage<RobotExecuteRecord> pageConfig = new Page<>(recordDto.getPageNo(), recordDto.getPageSize(), true);
        pages = robotExecuteRecordDao.getExecuteRecordList(pageConfig, recordDto);
        List<RobotExecuteRecord> list = pages.getRecords();
        if (list.isEmpty()) {
            AppResponse.success(pages);
        }
        packageTaskInfo(list);
        return AppResponse.success(pages);
    }

    private void packageTaskInfo(List<RobotExecuteRecord> list) {
        for (RobotExecuteRecord robotExecuteRecord : list) {
            String taskExecuteId = robotExecuteRecord.getTaskExecuteId();
            if (!StringUtils.isEmpty(taskExecuteId)) {
                String taskName = scheduleTaskDao.getTaskNameByTaskExecuteId(taskExecuteId);
                if (taskName != null && !StringUtils.isEmpty(taskName)) {
                    robotExecuteRecord.setTaskName(taskName);
                } else {
                    robotExecuteRecord.setTaskName(null);
                }
            }
        }
    }

    @Override
    public AppResponse<?> getExecuteLog(ExecuteRecordDto recordDto) throws NoLoginException {
        String executeId = recordDto.getExecuteId();
        if (null == executeId) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "执行ID为空");
        }
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        recordDto.setCreatorId(userId);
        recordDto.setTenantId(tenantId);
        String executeLog = robotExecuteRecordDao.getExecuteLog(recordDto);
        return AppResponse.success(executeLog);
    }

    @Override
    @RobotVersionAnnotation(clazz = ExecuteRecordDto.class)
    public AppResponse<?> saveExecuteResult(ExecuteRecordDto recordDto, String currentRobotId) throws NoLoginException {

        // 原有业务逻辑
        String executeId = recordDto.getExecuteId();
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        recordDto.setCreatorId(userId);
        recordDto.setUpdaterId(userId);
        recordDto.setTenantId(tenantId);
        recordDto.setRobotId(currentRobotId);
        //        String deptIdPath = DeptUtils.getLevelCode();
        //        recordDto.setDeptIdPath(deptIdPath);
        // 根据executeId，是否是第一次，是第一次，设置开始时间
        if (null == executeId) {
            if (null == recordDto.getResult() || !ROBOT_RESULT_EXECUTE.equals(recordDto.getResult())) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "执行结果为空或数据错误");
            }
            executeId = idWorker.nextId() + "";
            recordDto.setExecuteId(executeId);
            recordDto.setStartTime(new Date());
            // 插入
            robotExecuteRecordDao.insertExecuteRecord(recordDto);
        } else {
            if (null == recordDto.getResult() || ROBOT_RESULT_EXECUTE.equals(recordDto.getResult())) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "执行结果错误");
            }
            RobotExecuteRecord executeRecord = robotExecuteRecordDao.getExecuteRecord(recordDto);
            if (null == executeRecord || null == executeRecord.getStartTime()) {
                return AppResponse.error(ErrorCodeEnum.E_SQL, "执行记录数据异常");
            }

            Date endTime = new Date();
            recordDto.setEndTime(endTime);
            // 计算执行耗时
            recordDto.setExecuteTime(endTime.toInstant().getEpochSecond()
                    - executeRecord.getStartTime().toInstant().getEpochSecond());
            robotExecuteRecordDao.updateExecuteRecord(recordDto);
        }
        return AppResponse.success(executeId);
    }

    @Override
    public Integer countRobotTotalNumOfExecuted(List<String> startAndEndOfDay, String lastProcessedId) {
        if (CollectionUtils.isEmpty(startAndEndOfDay) || StringUtils.isBlank(lastProcessedId)) {
            return 0;
        }
        return robotExecuteRecordDao.countRobotTotalNumOfExecuted(startAndEndOfDay, lastProcessedId);
    }

    @Override
    public Integer countTerminalTotalNumOfExecuted(List<String> startAndEndOfDay, String lastProcessedId) {
        if (CollectionUtils.isEmpty(startAndEndOfDay) || StringUtils.isBlank(lastProcessedId)) {
            return 0;
        }
        return robotExecuteRecordDao.countTerminalTotalNumOfExecuted(startAndEndOfDay, lastProcessedId);
    }

    @Override
    public List<RobotExecuteRecord> getExecutedRobotByPage(
            List<String> startAndEndOfDay, String lastProcessedId, Integer limit, Integer offset) {
        if (CollectionUtils.isEmpty(startAndEndOfDay) || StringUtils.isBlank(lastProcessedId)) {
            return new ArrayList<>();
        }
        return robotExecuteRecordDao.getExecutedRobotByPage(startAndEndOfDay, lastProcessedId, limit, offset);
    }

    // todo:dept
    //    @Override
    //    public List<HisBase> auditByDeptIdPath(String endOfDay, List<UapOrg> deptInfoList){
    //        if(CollectionUtils.isEmpty(deptInfoList) || StringUtils.isBlank(endOfDay)){
    //            return new ArrayList<>();
    //        }
    //        return robotExecuteRecordDao.auditByDeptIdPath(endOfDay,deptInfoList);
    //    }

    @Override
    public AppResponse<String> deleteRobotExecuteRecords(RobotExecuteRecordsBatchDeleteDto batchDeleteDto)
            throws NoLoginException {
        // 批量删除机器人执行记录
        String tenantId = TenantUtils.getTenantId();
        String userId = UserUtils.nowUserId();
        List<String> recordsIds = batchDeleteDto.getRecordIds();

        // 2. 批量删除
        int deleted = baseMapper.deleteRobotExecuteRecords(recordsIds, userId, tenantId);
        if (deleted != recordsIds.size()) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "批量删除共享文件失败");
        }
        return AppResponse.success("删除成功");
    }
}

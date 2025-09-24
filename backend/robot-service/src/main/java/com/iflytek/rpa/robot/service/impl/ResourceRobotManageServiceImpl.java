package com.iflytek.rpa.robot.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.iflytek.rpa.robot.dao.*;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.robot.entity.dto.ExecuteRecordPageDto;
import com.iflytek.rpa.robot.entity.dto.RobotDeleteCheckDto;
import com.iflytek.rpa.robot.entity.dto.RobotDeleteDto;
import com.iflytek.rpa.robot.entity.dto.RobotPageListDto;
import com.iflytek.rpa.robot.entity.vo.*;
import com.iflytek.rpa.robot.service.ResourceRobotManageService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.task.dao.ScheduleTaskRobotDao;
import com.iflytek.rpa.task.entity.ScheduleTaskRobot;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.casbin.casdoor.entity.User;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

@Slf4j
@Service
public class ResourceRobotManageServiceImpl implements ResourceRobotManageService {
    private final String filePathPrefix = "/api/resource/file/download?fileId=";

    @Resource
    ResourceRobotManageDao resourceRobotManageDao;

    @Resource
    RobotDesignServiceImpl robotDesignService;

    @Resource
    RobotExecuteRecordDao robotExecuteRecordDao;

    @Resource
    private RobotExecuteDao robotExecuteDao;

    @Resource
    private ScheduleTaskRobotDao scheduleTaskRobotDao;

    @Resource
    private RobotDesignDao robotDesignDao;

    @Resource
    private RobotVersionDao robotVersionDao;

    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    @Autowired
    private IdWorker idWorker;

    @Override
    public AppResponse<IPage<RobotPageListVo>> getRobotPageList(RobotPageListDto queryDto)
            throws NoLoginException, IOException {
        IPage<RobotPageListVo> pageConfig = new Page<>(queryDto.getPageNo(), queryDto.getPageSize(), true);
        IPage<RobotPageListVo> resPage = resourceRobotManageDao.getRobotPageList(pageConfig, queryDto);
        resPackage(resPage.getRecords());
        return AppResponse.success(resPage);
    }

    private void resPackage(List<RobotPageListVo> records) throws IOException {
        packageVersion(records);
        packageUserInfo(records);
    }

    private void packageVersion(List<RobotPageListVo> records) {
        for (RobotPageListVo record : records) {
            RobotVersion enableVersion = robotVersionDao.getOriEnableVersion(
                    record.getRobotId(), record.getCreatorId(), record.getTenantId());
            if (enableVersion == null) {
                record.setVersion(record.getAppVersion());
            } else {
                record.setVersion(enableVersion.getVersion());
            }
        }
    }

    private void packageUserInfo(List<RobotPageListVo> recordList) throws IOException {
        List<String> userIds =
                recordList.stream().map(RobotPageListVo::getCreatorId).collect(Collectors.toList());
        userIds.removeIf(Objects::isNull);
        if (userIds.isEmpty()) {
            return;
        }
        List<User> uapUsers = UserUtils.queryUserPageList(userIds);
        Map<String, User> userMap = UserUtils.getUserMap(uapUsers);
        recordList.forEach(record -> {
            User uapUser = userMap.get(record.getCreatorId());
            if (uapUser != null) {
                record.setCreatorName(uapUser.name);
                record.setCreatorPhone(uapUser.phone);
            }
        });
    }

    @Override
    public AppResponse<DelResourceRobotVo> deleteRobotCheck(RobotDeleteCheckDto dto) throws Exception {
        String robotId = dto.getRobotId();
        String tenantId = TenantUtils.getTenantId();
        LambdaQueryWrapper<RobotExecute> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper
                .eq(RobotExecute::getRobotId, robotId)
                .eq(RobotExecute::getDeleted, 0)
                .eq(RobotExecute::getTenantId, tenantId)
                .last("LIMIT 1");
        RobotExecute robotExecute = robotExecuteDao.selectOne(queryWrapper);
        if (robotExecute == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "机器人不存在");
        }
        String creatorId = robotExecute.getCreatorId();
        // 获取所有引用该机器人的task
        List<ScheduleTaskRobot> taskRobotList = scheduleTaskRobotDao.getAllTaskRobot(robotId, creatorId, tenantId);
        taskRobotList.removeIf(Objects::isNull);
        DelResourceRobotVo res = new DelResourceRobotVo();
        if (!CollectionUtils.isEmpty(taskRobotList)) {
            DelDesignRobotVo delDesignRobotVo = new DelDesignRobotVo();
            delDesignRobotVo.setRobotId(robotId);
            robotDesignService.setDelDesignRobotVo(delDesignRobotVo, taskRobotList, robotId);
            BeanUtils.copyProperties(delDesignRobotVo, res);
        }
        return AppResponse.success(res);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> deleteRobot(RobotDeleteDto dto) throws Exception {
        // 删除卓越中心和所有已下载了该机器人的客户端的记录项 TODO
        String taskIds = dto.getTaskIds();
        String robotId = dto.getRobotId();
        String tenantId = TenantUtils.getTenantId();
        LambdaQueryWrapper<RobotExecute> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper
                .eq(RobotExecute::getRobotId, robotId)
                .eq(RobotExecute::getTenantId, tenantId)
                .eq(RobotExecute::getDeleted, 0)
                .last("LIMIT 1");
        RobotExecute robotExecute = robotExecuteDao.selectOne(queryWrapper);
        if (robotExecute == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "机器人不存在");
        }
        String creatorId = robotExecute.getCreatorId();
        // 删除设计器
        Integer i = robotDesignDao.deleteDesign(robotId, creatorId, tenantId);
        // 删除 执行记录
        Integer x = robotExecuteRecordDao.deleteRecord(tenantId, robotId, creatorId);
        // 执行器
        Integer y = robotExecuteDao.deleteExecute(robotId, creatorId, tenantId);
        // 计划任务
        if (!StringUtils.isEmpty(taskIds)) {
            List<String> taskIdList = Arrays.stream(taskIds.split(",")).collect(Collectors.toList());
            Integer z = scheduleTaskRobotDao.taskRobotDelete(robotId, creatorId, tenantId, taskIdList);
            robotDesignService.taskRobotDeleteAfter(taskIdList);
        }
        return AppResponse.success(robotId);
    }

    @Override
    public AppResponse<MyRobotDetailVo> getRobotBaseInfo(String robotId) throws Exception {
        String tenantId = TenantUtils.getTenantId();
        RobotExecute robot = robotExecuteDao.getRobotExecuteByTenantId(robotId, tenantId);
        if (robot == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "机器人不存在");
        }
        RobotVersion latestRobotVersion = robotVersionDao.getLatestRobotVersionByRobotId(robotId);
        MyRobotDetailVo resVo = getMyRobotDetailRes(robot, latestRobotVersion);
        return AppResponse.success(resVo);
    }

    /**
     * 工具方法，获取机器人基本信息中拼接最新版机器人的使用说明、简介等信息
     *
     * @param robot
     * @return
     * @throws Exception
     */
    private MyRobotDetailVo getMyRobotDetailRes(RobotExecute robot, RobotVersion latestVersion) {
        MyRobotDetailVo resVo = new MyRobotDetailVo();
        String introduction = "";
        Integer version = 0;
        String fileId = null;
        String videoId = null;
        String fileName = null;
        String videoName = null;
        String useDescription = null;

        if (latestVersion != null) {
            introduction = latestVersion.getIntroduction();
            version = latestVersion.getVersion();
            fileId = latestVersion.getAppendixId();
            videoId = latestVersion.getVideoId();
            fileName = robotExecuteDao.getFileName(fileId);
            videoName = robotExecuteDao.getFileName(videoId);
            useDescription = latestVersion.getUseDescription();
        }

        String creatorName = UserUtils.getRealNameById(robot.getCreatorId());

        resVo.setName(robot.getName());
        resVo.setVersion(version);
        resVo.setIntroduction(introduction);
        resVo.setUseDescription(useDescription);
        resVo.setCreatorName(creatorName);
        resVo.setCreateTime(robot.getCreateTime());
        resVo.setFileName(fileName);
        resVo.setFilePath(org.apache.commons.lang3.StringUtils.isEmpty(fileId) ? null : filePathPrefix + fileId);
        resVo.setVideoName(videoName);
        resVo.setVideoPath(org.apache.commons.lang3.StringUtils.isEmpty(videoId) ? null : (filePathPrefix + videoId));
        resVo.setDeptName("");

        resVo.setUpdateTime(robot.getUpdateTime());
        resVo.setRobotId(robot.getRobotId());
        return resVo;
    }

    @Override
    public AppResponse<ResourceVersionListVo> getRobotVersions(String robotId) throws Exception {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        ResourceVersionListVo versionListVo = new ResourceVersionListVo();
        versionListVo.setVersionDetailList(robotVersionDao.getRobotVersions(robotId, userId, tenantId));
        return AppResponse.success(versionListVo);
    }

    @Override
    public AppResponse<IPage<RecordBaseInfoVo>> getRecordBaseInfo(ExecuteRecordPageDto queryDto) {
        String tenantId = TenantUtils.getTenantId();
        IPage<RecordBaseInfoVo> pageConfig = new Page<>(queryDto.getPageNo(), queryDto.getPageSize(), true);
        IPage<RecordBaseInfoVo> recordList =
                robotExecuteRecordDao.getRecordBaseInfoPage(pageConfig, queryDto, tenantId);
        if (recordList == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "未查询到相关执行记录");
        }
        // 遍历当前页所有记录
        for (RecordBaseInfoVo record : recordList.getRecords()) {
            String executorId = record.getCreatorId(); // 假设 RecordBaseInfoVo 里有 getUserId()
            if (executorId != null) {
                String executorName = UserUtils.getRealNameById(executorId); // 根据用户ID查用户名
                record.setExecutorName(executorName); // 设置 username 到 VO 中
            }
        }
        return AppResponse.success(recordList);
    }

    @Override
    public AppResponse<RecordLogVo> getRecordLog(String robotId, String executeId) {
        String tenantId = TenantUtils.getTenantId();
        RecordLogVo logVo = robotExecuteRecordDao.getRecordLog(robotId, executeId, tenantId);
        if (logVo == null) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "未查询到该机器人执行记录");
        }
        return AppResponse.success(logVo);
    }
}

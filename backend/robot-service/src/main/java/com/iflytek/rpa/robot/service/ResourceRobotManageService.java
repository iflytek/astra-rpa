package com.iflytek.rpa.robot.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.iflytek.rpa.robot.entity.dto.ExecuteRecordPageDto;
import com.iflytek.rpa.robot.entity.dto.RobotDeleteCheckDto;
import com.iflytek.rpa.robot.entity.dto.RobotDeleteDto;
import com.iflytek.rpa.robot.entity.dto.RobotPageListDto;
import com.iflytek.rpa.robot.entity.vo.*;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import java.io.IOException;

public interface ResourceRobotManageService {
    AppResponse<IPage<RobotPageListVo>> getRobotPageList(RobotPageListDto queryDto)
            throws NoLoginException, IOException;

    AppResponse<DelResourceRobotVo> deleteRobotCheck(RobotDeleteCheckDto dto) throws Exception;

    AppResponse<String> deleteRobot(RobotDeleteDto dto) throws Exception;

    AppResponse<MyRobotDetailVo> getRobotBaseInfo(String robotId) throws Exception;

    AppResponse<ResourceVersionListVo> getRobotVersions(String robotId) throws Exception;

    AppResponse<IPage<RecordBaseInfoVo>> getRecordBaseInfo(ExecuteRecordPageDto queryDto) throws Exception;

    AppResponse<RecordLogVo> getRecordLog(String robotId, String executeId);
}

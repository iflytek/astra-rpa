package com.iflytek.rpa.robot.service;

import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.dto.DeleteDesignDto;
import com.iflytek.rpa.robot.entity.dto.DesignListDto;
import com.iflytek.rpa.robot.entity.dto.ShareDesignDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;

/**
 * 云端机器人表(Robot)表服务接口
 *
 * @author makejava
 * @since 2024-09-29 15:27:40
 */
public interface RobotDesignService {

    AppResponse<?> createRobot(RobotDesign robot) throws NoLoginException;

    AppResponse<?> createRobotName() throws NoLoginException;

    //    AppResponse<?> updateRobotByPull(MarketResourceDto marketResourceDto);

    AppResponse<?> designList(DesignListDto queryDto) throws NoLoginException;

    AppResponse<?> rename(String newName, String robotId) throws NoLoginException;

    AppResponse<?> designNameDup(String newName, String robotId) throws NoLoginException;

    AppResponse<?> myRobotDetail(String robotId) throws NoLoginException;

    AppResponse<?> marketRobotDetail(String robotId) throws Exception;

    AppResponse<?> copyDesignRobot(String robotId, String robotName) throws Exception;

    AppResponse<?> deleteRobotRes(String robotId) throws Exception;

    AppResponse<?> deleteRobot(DeleteDesignDto queryDto) throws Exception;

    void copyEditingBase(String oldRobotId, String newRobotId, String userId) throws Exception;

    AppResponse<?> shareRobot(ShareDesignDto queryDto) throws Exception;
}

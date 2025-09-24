package com.iflytek.rpa.robot.controller;

import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.robot.entity.dto.DeleteDesignDto;
import com.iflytek.rpa.robot.entity.dto.DesignListDto;
import com.iflytek.rpa.robot.entity.dto.ShareDesignDto;
import com.iflytek.rpa.robot.service.RobotDesignService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import javax.annotation.Resource;
import javax.validation.Valid;
import org.springframework.web.bind.annotation.*;

/**
 * 云端机器人表(RobotDesign)表控制层
 *
 * @author makejava
 * @since 2024-09-29 15:27:34
 */
@RestController
@RequestMapping("/robot-design")
public class RobotDesignController {

    @Resource
    private RobotDesignService robotDesignService;

    /**
     * 创建机器人
     *
     * @param robot
     * @return
     * @throws Exception
     */
    @PostMapping("/create")
    public AppResponse<?> createRobot(@Valid @RequestBody RobotDesign robot) throws Exception {
        return robotDesignService.createRobot(robot);
    }

    /**
     * 新建机器人-获取默认名称
     *
     * @return
     * @throws Exception
     */
    @PostMapping("/create-name")
    public AppResponse<?> createRobotName() throws Exception {
        return robotDesignService.createRobotName();
    }

    /**
     * 设计器机器人列表
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/design-list")
    public AppResponse<?> designList(@RequestBody DesignListDto queryDto) throws NoLoginException {
        return robotDesignService.designList(queryDto);
    }

    /**
     * 设计器重命名接口
     *
     * @param newName
     * @param robotId
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/rename")
    public AppResponse<?> rename(@RequestParam("newName") String newName, @RequestParam("robotId") String robotId)
            throws NoLoginException {
        return robotDesignService.rename(newName, robotId);
    }

    /**
     * 设计器命名重复接口
     *
     * @param newName
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/design-name-dup")
    public AppResponse<?> designNameDup(
            @RequestParam("newName") String newName, @RequestParam("robotId") String robotId) throws NoLoginException {

        return robotDesignService.designNameDup(newName, robotId);
    }

    /**
     * 设计器-我创建的机器人-详情
     *
     * @param robotId
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/my-robot-detail")
    public AppResponse<?> myRobotDetail(@RequestParam("robotId") String robotId) throws NoLoginException {
        return robotDesignService.myRobotDetail(robotId);
    }

    /**
     * 设计器-我获取的机器人-详情
     *
     * @param robotId
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/market-robot-detail")
    public AppResponse<?> marketRobotDetail(@RequestParam("robotId") String robotId) throws Exception {
        return robotDesignService.marketRobotDetail(robotId);
    }

    /**
     * 设计器-创建副本
     *
     * @param robotId
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/copy-design-robot")
    public AppResponse<?> copyRobot(
            @RequestParam("robotId") String robotId, @RequestParam("robotName") String robotName) throws Exception {
        return robotDesignService.copyDesignRobot(robotId, robotName);
    }

    /**
     * 设计器-删除机器人-初次响应
     *
     * @param robotId
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/delete-robot-res")
    public AppResponse<?> deleteRobotRes(@RequestParam("robotId") String robotId) throws Exception {
        return robotDesignService.deleteRobotRes(robotId);
    }

    /**
     * 设计器-删除机器人- 真实删除
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/delete-robot")
    public AppResponse<?> deleteRobot(@RequestBody DeleteDesignDto queryDto) throws Exception {
        return robotDesignService.deleteRobot(queryDto);
    }

    /**
     * 设计器-分享机器人
     *
     * @param queryDto
     * @return 新增的机器人ID
     * @throws NoLoginException
     */
    @PostMapping("/share-robot")
    public AppResponse<?> shareRobot(@RequestBody ShareDesignDto queryDto) throws Exception {
        return robotDesignService.shareRobot(queryDto);
    }
}

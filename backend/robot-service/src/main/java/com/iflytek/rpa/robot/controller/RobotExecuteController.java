package com.iflytek.rpa.robot.controller;

import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.dto.DeleteDesignDto;
import com.iflytek.rpa.robot.entity.dto.ExeUpdateCheckDto;
import com.iflytek.rpa.robot.entity.dto.ExecuteListDto;
import com.iflytek.rpa.robot.entity.dto.RobotExecuteByNameNDeptDto;
import com.iflytek.rpa.robot.entity.vo.RobotExecuteByNameNDeptVo;
import com.iflytek.rpa.robot.service.RobotExecuteService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import java.util.List;
import javax.annotation.Resource;
import org.springframework.web.bind.annotation.*;

/**
 * 云端机器人表(RobotExecute)表控制层
 *
 * @author mjren
 * @since 2024-10-22 16:07:33
 */
@RestController
@RequestMapping("/robot-execute")
public class RobotExecuteController {

    @Resource
    private RobotExecuteService robotExecuteService;

    /**
     * 执行器机器人列表
     *
     * @param queryDto
     * @return
     * @throws NoLoginException
     */
    @PostMapping("/execute-list")
    public AppResponse<?> executeList(@RequestBody ExecuteListDto queryDto) throws NoLoginException {
        return robotExecuteService.executeList(queryDto);
    }

    /**
     * 设计器-删除机器人-初次响应
     *
     * @param robotId
     * @return
     * @throws NoLoginException
     */
    @GetMapping("/delete-robot-res")
    public AppResponse<?> deleteRobotRes(@RequestParam("robotId") String robotId) throws NoLoginException {
        return robotExecuteService.deleteRobotRes(robotId);
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
        return robotExecuteService.deleteRobot(queryDto);
    }

    /**
     * 更新-在执行器主动点击更新
     *
     * @return
     * @throws Exception
     * @paramMarketResourceDto
     */
    @PostMapping("/update/pull")
    public AppResponse<?> updateRobotByPull(@RequestBody RobotExecute robotExecute) throws Exception {
        if (null == robotExecute.getRobotId()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "机器人ID不能为空");
        }
        return robotExecuteService.updateRobotByPull(robotExecute.getRobotId());
    }

    @GetMapping("/robot-detail")
    public AppResponse<?> robotDetail(@RequestParam("robotId") String robotId) throws Exception {
        return robotExecuteService.robotDetail(robotId);
    }

    @PostMapping("/execute-update-check")
    public AppResponse<?> executeUpdateCheck(@RequestBody ExeUpdateCheckDto queryDto) throws Exception {
        return robotExecuteService.executeUpdateCheck(queryDto);
    }

    @PostMapping("/list/NameNDept")
    public AppResponse<List<RobotExecuteByNameNDeptVo>> getRobotExecuteList(
            @RequestBody RobotExecuteByNameNDeptDto queryDto) throws NoLoginException {
        return robotExecuteService.getRobotExecuteList(queryDto);
    }

    //    /**
    //     * 卓越中心-机器人分析看板-机器人名称下拉选择-查询接口
    //     * @param robotName
    //     * @return
    //     * @throws NoLoginException
    //     */
    //    @PostMapping("/list/robot-name")
    //    public AppResponse<List<RobotNameDto>> getRobotNameListByName(@RequestParam("name") String robotName,
    // @RequestParam("deptId") String deptId) throws NoLoginException {
    //        return robotExecuteService.getRobotNameListByName(robotName, deptId);
    //    }

}

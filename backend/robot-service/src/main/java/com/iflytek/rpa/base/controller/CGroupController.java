package com.iflytek.rpa.base.controller;

import com.iflytek.rpa.base.entity.dto.FrontGroupReNameDto;
import com.iflytek.rpa.base.entity.dto.ServerBaseDto;
import com.iflytek.rpa.base.service.CGroupService;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.web.bind.annotation.*;

/**
 * 元素或图像的分组
 *
 * @author mjren
 * @since 2024-12-04 10:28:54
 */
@RestController
@RequestMapping("/group")
public class CGroupController {
    /**
     * 服务对象
     */
    @Resource
    private CGroupService groupService;

    /**
     * 分组-新建
     *
     * @param
     * @return
     * @throws Exception
     */
    @PostMapping("/create")
    public AppResponse<?> createGroup(
            @RequestParam("robotId") String robotId,
            @RequestParam("groupName") String groupName,
            @RequestParam("elementType") String elementType)
            throws Exception {
        ServerBaseDto serverBaseDto = new ServerBaseDto();
        serverBaseDto.setRobotId(robotId);
        serverBaseDto.setRobotVersion(0);
        serverBaseDto.setGroupName(groupName.trim());
        serverBaseDto.setElementType(elementType);
        return groupService.createGroup(serverBaseDto);
    }

    /**
     * 分组-重命名
     *
     * @param
     * @return
     * @throws Exception
     */
    @PostMapping("/rename")
    public AppResponse<?> renameGroup(@RequestBody FrontGroupReNameDto frontGroupReNameDto) throws Exception {
        if (StringUtils.isBlank(frontGroupReNameDto.getGroupName())) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "分组名称不能为空");
        }
        ServerBaseDto serverBaseDto = new ServerBaseDto();
        serverBaseDto.setRobotId(frontGroupReNameDto.getRobotId());
        serverBaseDto.setRobotVersion(0);
        serverBaseDto.setGroupId(frontGroupReNameDto.getGroupId());
        serverBaseDto.setGroupName(frontGroupReNameDto.getGroupName().trim());
        serverBaseDto.setElementType(frontGroupReNameDto.getElementType());

        return groupService.renameGroup(serverBaseDto);
    }

    /**
     * 分组-删除
     *
     * @param
     * @return
     * @throws Exception
     */
    @PostMapping("/delete")
    public AppResponse<?> deleteGroup(@RequestParam("robotId") String robotId, @RequestParam("groupId") String groupId)
            throws Exception {
        if (null == groupId) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        ServerBaseDto serverBaseDto = new ServerBaseDto();
        serverBaseDto.setRobotId(robotId);
        serverBaseDto.setRobotVersion(0);
        serverBaseDto.setGroupId(groupId);
        return groupService.deleteGroup(serverBaseDto);
    }
}

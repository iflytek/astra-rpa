package com.iflytek.rpa.base.service.impl;

import static com.iflytek.rpa.base.constants.BaseConstant.PROCESS_TYPE_MODULE;
import static com.iflytek.rpa.base.constants.BaseConstant.PROCESS_TYPE_PROCESS;
import static com.iflytek.rpa.robot.constants.RobotConstant.EDITING;

import com.iflytek.rpa.base.annotation.RobotVersionAnnotation;
import com.iflytek.rpa.base.dao.CProcessDao;
import com.iflytek.rpa.base.entity.CProcess;
import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CProcessDto;
import com.iflytek.rpa.base.entity.dto.CreateProcessDto;
import com.iflytek.rpa.base.entity.dto.RenameProcessDto;
import com.iflytek.rpa.base.service.CModuleService;
import com.iflytek.rpa.base.service.CProcessService;
import com.iflytek.rpa.base.service.NextName;
import com.iflytek.rpa.component.dao.ComponentDao;
import com.iflytek.rpa.component.entity.Component;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotDesign;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.*;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 流程项id数据(CProcess)表服务实现类
 *
 * @author mjren
 * @since 2024-10-09 17:11:14
 */
@Service("cProcessService")
public class CProcessServiceImpl extends NextName implements CProcessService {
    @Resource
    private CProcessDao cProcessDao;

    @Autowired
    private RobotDesignDao robotDesignDao;

    @Autowired
    private ComponentDao componentDao;

    @Autowired
    private RobotExecuteDao robotExecuteDao;

    @Autowired
    private RobotVersionDao robotVersionDao;

    @Autowired
    private CModuleService cModuleService;

    @Autowired
    private IdWorker idWorker;

    @Override
    public AppResponse<String> getProcessNextName(String robotId) {
        BaseDto baseDto = new BaseDto();
        baseDto.setRobotId(robotId);
        baseDto.setRobotVersion(0);
        // 获取流程名称列表
        List<CProcess> processList = cProcessDao.getProcessNameList(baseDto);
        Set<String> nameSet = processList.stream().map(CProcess::getProcessName).collect(Collectors.toSet());

        // 生成下一个可用的子流程名称
        int nextNumber = 1;
        while (nameSet.contains("子流程" + nextNumber)) {
            nextNumber++;
        }
        String nextName = "子流程" + nextNumber;

        // 如果没有主流程，则使用"主流程"作为名称
        if (!nameSet.contains("主流程")) {
            nextName = "主流程";
        }
        return AppResponse.success(nextName);
    }

    public AppResponse<Map> createNewProcess(CreateProcessDto processDto) throws NoLoginException {
        CProcess searchDto = new CProcess();
        BeanUtils.copyProperties(processDto, searchDto);
        searchDto.setRobotVersion(0);
        String userId = UserUtils.nowUserId();
        searchDto.setCreatorId(userId);
        // 检查同名流程
        Integer count = cProcessDao.countProcessByName(searchDto);
        if (count > 0) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "已存在同名的子流程名称，请重新命名");
        }
        String processId = idWorker.nextId() + "";
        // 创建流程实体
        CProcess process = new CProcess();
        process.setRobotId(processDto.getRobotId());
        process.setRobotVersion(0);
        process.setProcessName(processDto.getProcessName());
        process.setProcessContent(processDto.getProcessContent());
        process.setProcessId(processId);
        process.setCreatorId(userId);
        process.setCreateTime(new Date());
        process.setUpdaterId(userId);
        process.setUpdateTime(new Date());
        process.setDeleted(0);
        // 保存流程
        cProcessDao.insert(process);

        // 返回结果
        Map<String, String> responseData = new HashMap<>();
        responseData.put("processId", processId);
        return AppResponse.success(responseData);
    }

    @Override
    public AppResponse<Boolean> renameProcess(RenameProcessDto processDto) throws NoLoginException {
        CProcess searchDto = new CProcess();
        BeanUtils.copyProperties(processDto, searchDto);
        searchDto.setRobotVersion(0);
        String userId = UserUtils.nowUserId();
        searchDto.setCreatorId(userId);
        // 检查同名流程
        Integer count = cProcessDao.countProcessByName(searchDto);
        if (count > 0) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "已存在同名的子流程名称，请重新命名");
        }
        cProcessDao.renameProcess(searchDto);
        return AppResponse.success(true);
    }

    @Override
    public AppResponse<?> getAllProcessData(CProcess process) {
        String robotId = process.getRobotId();
        Integer version = process.getRobotVersion();
        if (null == version || StringUtils.isBlank(robotId)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE);
        }
        List<CProcess> result = cProcessDao.getAllProcessDataByRobotId(robotId, version);
        return AppResponse.success(result);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> saveProcessContent(CProcessDto process) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        process.setCreatorId(userId);
        BaseDto baseDto = new BaseDto();
        BeanUtils.copyProperties(process, baseDto);
        CProcess oldProcess = cProcessDao.getProcessById(baseDto);
        if (null == oldProcess) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "流程数据不存在");
        }
        String oldProcessContent = oldProcess.getProcessContent();
        String newProcessContent = process.getProcessJson();
        if ((null == oldProcessContent || null == newProcessContent) || !oldProcessContent.equals(newProcessContent)) {
            // 内容发生了变化
            // 将设计器机器人或组件的状态设置为编辑中
            robotDesignDao.updateTransformStatus(userId, process.getRobotId(), null, EDITING);
            Integer i = componentDao.updateTransformStatus(userId, process.getRobotId(), null, EDITING);
        }
        if (null != newProcessContent) {
            // 限制流程数据的大小
            // 获取字符串的字节长度
            int byteLength = newProcessContent.getBytes().length;
            // 将字节长度转换为兆字节（MB）
            double megabytes = byteLength / (1024.0 * 1024.0);
            if (megabytes > 14) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "流程数据不能超过15M");
            }
        }
        // 如果没有更改，则不更改编辑状态
        cProcessDao.updateProcessContent(process);
        return AppResponse.success(true);
    }

    @Override
    @RobotVersionAnnotation
    public AppResponse<?> getProcessDataByProcessId(BaseDto baseDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 权限检查
        AppResponse<?> permissionCheck = checkRobotPermission(baseDto.getRobotId(), userId, tenantId);
        if (!permissionCheck.ok()) {
            return permissionCheck;
        }

        baseDto.setCreatorId(userId);
        CProcess process = cProcessDao.getProcessById(baseDto);
        if (null == process || null == process.getProcessContent()) {
            return AppResponse.success("");
        }
        return AppResponse.success(process.getProcessContent());
    }

    /**
     * 检查机器人权限
     */
    private AppResponse<?> checkRobotPermission(String robotId, String userId, String tenantId) {

        // 获取机器人信息
        RobotDesign robotDesign = robotDesignDao.getRobotInfoAll(robotId, tenantId);
        Component component = componentDao.getComponentById(robotId, userId, tenantId);
        if (robotDesign == null && component == null) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "改机器人或不存在");
        }

        // 如果是自己创建的机器人，直接通过
        if (robotDesign != null && "create".equals(robotDesign.getDataSource())) {
            return AppResponse.success("自己创建的机器人");
        }

        // 如果是自己创建的组件，直接通过
        if (component != null && "create".equals(component.getDataSource())) {
            return AppResponse.success("自己创建的组件");
        }

        return AppResponse.success("权限检查通过");
    }

    @Override
    @RobotVersionAnnotation
    public AppResponse<?> getProcessNameList(BaseDto baseDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        baseDto.setCreatorId(userId);
        List<CProcess> processNameList = cProcessDao.getProcessNameList(baseDto);
        // 将主流程排在第一个
        processNameList.sort((p1, p2) -> {
            if ("主流程".equals(p1.getProcessName())) {
                // p1 是 "主流程"，放在前面
                return -1;
            } else if ("主流程".equals(p2.getProcessName())) {
                // p2 是 "主流程"，放在前面
                return 1;
            } else {
                // 其他元素按 name 排序
                return p1.getProcessName().compareTo(p2.getProcessName());
            }
        });
        return AppResponse.success(processNameList);
    }

    @Override
    public AppResponse<?> copySubProcess(String robotId, String processId, String type) {
        Map<String, String> result = new HashMap<>();
        if (PROCESS_TYPE_PROCESS.equals(type)) {
            // 查询原流程数据
            BaseDto baseDto = new BaseDto();
            baseDto.setRobotId(robotId);
            baseDto.setRobotVersion(0);
            baseDto.setProcessId(processId);
            CProcess process = cProcessDao.getProcessById(baseDto);
            if (null == process) {
                throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "流程数据不存在");
            }
            String processName = process.getProcessName();
            baseDto.setName(processName);
            // 产生副本名称
            String nextName = createNextName(baseDto, processName + "副本");
            // 复制流程
            process.setProcessId(idWorker.nextId() + "");
            process.setProcessName(nextName);
            process.setCreateTime(new Date());
            process.setUpdateTime(new Date());
            cProcessDao.insert(process);
            result.put("id", process.getProcessId());
            result.put("name", process.getProcessName());
        } else if (PROCESS_TYPE_MODULE.equals(type)) {
            return AppResponse.success(cModuleService.copyCodeModule(robotId, processId));
        }

        return AppResponse.success(result);
    }

    @Override
    public List<String> getNameList(BaseDto baseDto) {
        return cProcessDao.getProcessNameListByPrefix(baseDto);
    }

    @Override
    public AppResponse<Boolean> deleteProcess(CProcessDto processDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        processDto.setCreatorId(userId);
        boolean result = cProcessDao.deleteProcessByProcessId(processDto);
        return AppResponse.success(result);
    }
}

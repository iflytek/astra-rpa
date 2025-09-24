package com.iflytek.rpa.base.service.handler;

import static com.iflytek.rpa.robot.constants.RobotConstant.EXECUTOR;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.base.dao.CParamDao;
import com.iflytek.rpa.base.entity.CParam;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import com.iflytek.rpa.base.entity.dto.QueryParamDto;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;

/**
 * @author mjren
 * @date 2025-04-17 15:01
 * @copyright Copyright (c) 2025 mjren
 */
@Component
@RequiredArgsConstructor
public class ExecutorModeHandler implements ParamModeHandler {
    private final CParamDao cParamDao;
    private final RobotExecuteDao robotExecuteDao;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public boolean supports(String mode) {
        return EXECUTOR.equals(mode);
    }

    @Override
    public AppResponse<List<ParamDto>> handle(QueryParamDto dto) throws JsonProcessingException, NoLoginException {
        RobotExecute executeInfo = getRobotExecute(dto.getRobotId());

        return handleDataSource(executeInfo, dto.getProcessId(), dto.getRobotVersion());
    }

    private RobotExecute getRobotExecute(String robotId) throws NoLoginException {
        RobotExecute executeInfo =
                robotExecuteDao.getRobotInfoByRobotId(robotId, UserUtils.nowUserId(), TenantUtils.getTenantId());
        if (executeInfo == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL.getCode(), "无法获取执行器机器人信息");
        }
        return executeInfo;
    }

    private AppResponse<List<ParamDto>> handleDataSource(
            RobotExecute executeInfo, String processId, Integer robotVersion) throws JsonProcessingException {
        if (robotVersion != null) {
            executeInfo.setAppVersion(robotVersion);
            executeInfo.setRobotVersion(robotVersion);
        }
        if ("market".equals(executeInfo.getDataSource())) {
            return handleMarketSource(executeInfo, processId);
        } else if ("create".equals(executeInfo.getDataSource())) {
            return handleCreateSource(executeInfo, processId);
        } else if ("deploy".equals(executeInfo.getDataSource())) {
            return handleDeploySource(executeInfo, processId);
        }

        throw new ServiceException(ErrorCodeEnum.E_PARAM.getCode(), "未知数据来源类型");
    }

    private AppResponse<List<ParamDto>> handleDeploySource(RobotExecute executeInfo, String processId) {
        String originRobotId = cParamDao.getDeployOriginalRobotId(executeInfo);
        if (StringUtils.isBlank(processId)) {
            processId = cParamDao.getMianProcessId(originRobotId, executeInfo.getAppVersion());
        }
        List<CParam> params = cParamDao.getAllParams(processId, originRobotId, executeInfo.getAppVersion());
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> handleMarketSource(RobotExecute executeInfo, String processId) {
        validateMarketInfo(executeInfo);
        String originRobotId = cParamDao.getMarketRobotId(executeInfo);
        if (StringUtils.isBlank(processId)) {
            processId = cParamDao.getMianProcessId(originRobotId, executeInfo.getAppVersion());
        }
        List<CParam> params = cParamDao.getAllParams(processId, originRobotId, executeInfo.getAppVersion());
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> handleCreateSource(RobotExecute executeInfo, String processId)
            throws JsonProcessingException {
        Integer enabledVersion = cParamDao.getRobotVersion(executeInfo.getRobotId());
        if (executeInfo.getRobotVersion() != null) {
            enabledVersion = executeInfo.getRobotVersion();
        }
        // 如果是主流程 则返回 存储的 配置参数
        String mainProcessId = cParamDao.getMianProcessId(executeInfo.getRobotId(), enabledVersion);
        if (processId == null || mainProcessId.equals(processId)) {
            if (executeInfo.getParamDetail() != null) {
                return parseCustomParams(executeInfo.getParamDetail());
            }
        }
        List<CParam> params = cParamDao.getSelfRobotParam(executeInfo.getRobotId(), processId, enabledVersion);
        return AppResponse.success(convertParams(params));
    }

    private void validateMarketInfo(RobotExecute executeInfo) {
        if (StringUtils.isAnyBlank(executeInfo.getMarketId(), executeInfo.getAppId())
                || executeInfo.getAppVersion() == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL.getCode(), "机器人市场信息异常");
        }
    }

    private AppResponse<List<ParamDto>> parseCustomParams(String paramDetail) throws JsonProcessingException {
        List<CParam> params = objectMapper.readValue(paramDetail, new TypeReference<List<CParam>>() {});
        return AppResponse.success(convertParams(params));
    }

    private List<ParamDto> convertParams(List<CParam> params) {
        if (CollectionUtils.isEmpty(params)) {
            return Collections.emptyList();
        }
        return params.stream()
                .map(p -> {
                    ParamDto dto = new ParamDto();
                    BeanUtils.copyProperties(p, dto);
                    return dto;
                })
                .collect(Collectors.toList());
    }
}

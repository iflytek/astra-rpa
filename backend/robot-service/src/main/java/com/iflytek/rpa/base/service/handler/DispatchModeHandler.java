package com.iflytek.rpa.base.service.handler;

import static com.iflytek.rpa.robot.constants.RobotConstant.DISPATCH;

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
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;

/**
 * @author jqfang3
 * @date 2025-08-18
 */
@Component
@RequiredArgsConstructor
public class DispatchModeHandler implements ParamModeHandler {
    private final CParamDao cParamDao;
    private final RobotExecuteDao robotExecuteDao;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public boolean supports(String mode) {
        return DISPATCH.equals(mode);
    }

    @Override
    public AppResponse<List<ParamDto>> handle(QueryParamDto dto) throws JsonProcessingException, NoLoginException {
        RobotExecute executeInfo = getRobotExecute(dto.getRobotId());
        Integer enabledVersion = dto.getRobotVersion();
        if (executeInfo.getParamDetail() != null) {
            return parseCustomParams(executeInfo.getParamDetail());
        }

        return handleDataSource(executeInfo, dto.getProcessId(), enabledVersion);
    }

    private RobotExecute getRobotExecute(String robotId) {
        return robotExecuteDao.getRobotExecuteByRobotId(robotId);
    }

    private AppResponse<List<ParamDto>> handleDataSource(
            RobotExecute executeInfo, String processId, Integer enabledVersion) {
        // 指定版本
        executeInfo.setAppVersion(enabledVersion);
        executeInfo.setRobotVersion(enabledVersion);
        if ("create".equals(executeInfo.getDataSource())) {
            return handleCreateSource(executeInfo, processId);
        } else if ("market".equals(executeInfo.getDataSource())) {
            return handleMarketSource(executeInfo, processId);
        } else if ("deploy".equals(executeInfo.getDataSource())) {
            return handleDeploySource(executeInfo, processId);
        }

        throw new ServiceException(ErrorCodeEnum.E_PARAM.getCode(), "未知数据来源类型");
    }

    private AppResponse<List<ParamDto>> handleDeploySource(RobotExecute executeInfo, String processId) {
        String originRobotId = cParamDao.getDeployOriginalRobotId(executeInfo);
        String mainProcessId = cParamDao.getMianProcessId(originRobotId, executeInfo.getAppVersion());
        List<CParam> params = cParamDao.getAllParams(
                processId != null ? processId : mainProcessId, originRobotId, executeInfo.getAppVersion());
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> handleMarketSource(RobotExecute executeInfo, String processId) {
        validateMarketInfo(executeInfo);
        String originRobotId = cParamDao.getMarketRobotId(executeInfo);
        String mainProcessId = cParamDao.getMianProcessId(originRobotId, executeInfo.getAppVersion());
        List<CParam> params = cParamDao.getAllParams(
                processId != null ? processId : mainProcessId, originRobotId, executeInfo.getAppVersion());
        return AppResponse.success(convertParams(params));
    }

    private AppResponse<List<ParamDto>> handleCreateSource(RobotExecute executeInfo, String processId) {
        Integer enabledVersion = executeInfo.getRobotVersion();
        String mainProcessId = cParamDao.getMianProcessId(executeInfo.getRobotId(), enabledVersion);
        List<CParam> params = cParamDao.getSelfRobotParam(
                executeInfo.getRobotId(),
                StringUtils.isNotBlank(processId) ? processId : mainProcessId,
                enabledVersion);
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

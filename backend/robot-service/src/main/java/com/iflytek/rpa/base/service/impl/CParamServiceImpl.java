package com.iflytek.rpa.base.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.DISPATCH;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iflytek.rpa.base.dao.CParamDao;
import com.iflytek.rpa.base.entity.CParam;
import com.iflytek.rpa.base.entity.dto.CParamDto;
import com.iflytek.rpa.base.entity.dto.ParamDto;
import com.iflytek.rpa.base.entity.dto.QueryParamDto;
import com.iflytek.rpa.base.service.CParamService;
import com.iflytek.rpa.base.service.handler.ParamHandlerFactory;
import com.iflytek.rpa.base.service.handler.ParamModeHandler;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.dto.RobotVersionDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.task.service.ScheduleTaskRobotService;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.Date;
import java.util.List;
import javax.annotation.Resource;
import lombok.RequiredArgsConstructor;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.CollectionUtils;

/**
 * @author tzzhang
 * @date 2025/3/13 15:11
 */
@Service("CParamService")
@RequiredArgsConstructor
public class CParamServiceImpl implements CParamService {
    private final ParamHandlerFactory paramHandlerFactory;

    @Resource
    private CParamDao cParamDao;

    @Resource
    private IdWorker idWorker;

    @Resource
    private RobotExecuteDao robotExecuteDao;

    @Autowired
    private ScheduleTaskRobotService scheduleTaskRobotService;

    @Override
    public AppResponse<List<ParamDto>> getAllParams(QueryParamDto queryParamDto)
            throws JsonProcessingException, NoLoginException {
        validateBaseParams(queryParamDto);

        String mode = queryParamDto.getMode();
        ParamModeHandler handler = paramHandlerFactory.getHandler(mode);
        return handler.handle(queryParamDto);
    }

    private void validateBaseParams(QueryParamDto dto) {
        if (StringUtils.isBlank(dto.getRobotId())) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode(), "robotId不能为空");
        }

        if (dto.getMode() == null) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode(), "mode参数必须指定");
        }

        if (DISPATCH.equals(dto.getMode())) {
            if (null == dto.getRobotVersion()) {
                throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode(), "dispatch模式下，robotVersion不能为空");
            }
        }
    }

    //    @Override
    //    public AppResponse<List<ParamDto>> getAllParams(QueryParamDto queryParamDto) throws JsonProcessingException,
    // NoLoginException {
    //        //根据流程id和机器人id进行查询参数还有机器人版本号查询参数
    //        //robotId不能为空，判断是否为空
    //        String robotId = queryParamDto.getRobotId();
    //        String userId = UserUtils.nowUserId();
    //        String tenantId = TenantUtils.getTenantId();
    //        List<CParam> cParamList = new ArrayList<CParam>();
    //        String mode = queryParamDto.getMode();
    //        //默认前端是不传递robot_version给后端
    //        Integer robotVersion = queryParamDto.getRobotVersion();
    //        String processId = queryParamDto.getProcessId();
    //        //编辑页面查询，查最新版（即0版本）配置参数，分流程查询，多次调用，直到把所有流程的参数查出来。
    //        if(EDIT_PAGE.equals(mode) || PROJECT_LIST.equals(mode)){
    //            //如果没有给版本号默认查询最新版本的数据
    //            robotVersion = (null == robotVersion)?0:robotVersion;
    //            //编辑状态必须提版本号
    //            cParamList = cParamDao.getAllParams(processId,robotId,robotVersion);
    //            return AppResponse.success(cParamToParamDto(cParamList));
    //        }
    //        if(EXECUTOR.equals(mode)){
    //            //在执行器执行；有自定义数据（在robot_execute表）、启用版本默认数据、市场作者默认数据；自定义数据优先级最高
    //            RobotExecute robotExecute = robotExecuteDao.getRobotInfoByRobotId(robotId,userId,tenantId);
    //            if(null == robotExecute){
    //                throw new ServiceException((ErrorCodeEnum.E_SQL.getCode()),"无法获取执行器机器人信息");
    //            }
    //            String dataSource = robotExecute.getDataSource();
    //            String paramDetail = robotExecute.getParamDetail();
    //            //paramDetail如果是null说明需要查询模板表
    //            if(null == paramDetail){
    //                if(dataSource.equals("market")){
    //                    //机器人从市场中获取
    //                    if (StringUtils.isBlank(robotExecute.getMarketId()) ||
    // StringUtils.isBlank(robotExecute.getAppId()) || null == robotExecute.getAppVersion()){
    //                        throw new ServiceException((ErrorCodeEnum.E_SQL.getCode()),"机器人市场信息异常");
    //                    }else{
    //                        //从市场中获取机器人默认参数
    //                        //机器人分享到市场robot_id不会该改变，但是用户获取机器人robot_id会发生改变
    //                        //获取原始机器人robot_id
    //                        String robotIdMarket = cParamDao.getMarketRobotId(robotExecute);
    //                        //查询原始机器人主流程参数
    //                        processId = cParamDao.getMianProcessId(robotIdMarket,robotExecute.getAppVersion());
    //                        cParamList = cParamDao.getAllParams(processId,robotIdMarket,robotExecute.getAppVersion());
    //                        return AppResponse.success(cParamToParamDto(cParamList));
    //                    }
    //                }else if(dataSource.equals("create")){
    //                    //自己创建的机器人
    //                    //首先查询机器人启用的版本号
    //                    robotVersion = cParamDao.getRobotVersion(robotId);
    //                    if(StringUtils.isBlank(processId)){
    //                        //执行器参数查询不会给processId
    //                        //默认查询主流程参数
    //                        //根据robotId和robotVersion查询主流程id
    //                        processId = cParamDao.getMianProcessId(robotId,robotVersion);
    //                    }
    //                    //根据robotId和processId和robotVersion查询主流程参数
    //                    cParamList = cParamDao.getSelfRobotParam(robotId,processId,robotVersion);
    //                    return AppResponse.success(cParamToParamDto(cParamList));
    //                }
    //            }
    //            //paramDetail不为空，有用户自定义配置参数
    //            // 使用 Jackson 将 JSON 字符串反序列化为 List<CParam>
    //            ObjectMapper objectMapper = new ObjectMapper();
    //            cParamList = objectMapper.readValue(paramDetail, new TypeReference<List<CParam>>(){});
    //
    //            return AppResponse.success(cParamToParamDto(cParamList));
    //        }
    //
    //        if(TRIGGER.equals(mode)){
    //            //在本地计划任务（触发器）执行，有自定义数据(在task_robot表）、启用版本默认数据、市场作者默认数据；自定义数据优先级最高
    //            //获取唯一id
    //            Long taskRobotUniqueId = queryParamDto.getTaskRobotUniqueId();
    //            if(null == taskRobotUniqueId){
    //                throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode(),"缺少计划任务机器人唯一id");
    //            }
    //            ScheduleTaskRobot taskRobot = scheduleTaskRobotService.queryById(taskRobotUniqueId);
    //            if (null == taskRobot){
    //                return AppResponse.success(new ArrayList<>());
    //            }
    //            String paramJson = taskRobot.getParamJson();
    //            if(StringUtils.isNotBlank(paramJson)){
    //                ObjectMapper objectMapper = new ObjectMapper();
    //                cParamList = objectMapper.readValue(paramJson, new TypeReference<List<CParam>>(){});
    //                return AppResponse.success(cParamToParamDto(cParamList));
    //            }
    //            //自定义参数为空，查默认数据
    //            // 根据机器人id查询机器人来源
    //            RobotExecute robotExecute = robotExecuteDao.getRobotInfoByRobotId(robotId,userId,tenantId);
    //            if(null == robotExecute){
    //                throw new ServiceException((ErrorCodeEnum.E_SQL.getCode()),"无法获取执行器机器人信息");
    //            }
    //            String dataSource = robotExecute.getDataSource();
    //            if(dataSource.equals("market")){
    //                //机器人从市场中获取
    //                if (StringUtils.isBlank(robotExecute.getMarketId()) ||
    // StringUtils.isBlank(robotExecute.getAppId()) || null == robotExecute.getAppVersion()){
    //                    throw new ServiceException((ErrorCodeEnum.E_SQL.getCode()),"机器人市场信息异常");
    //                }else{
    //                    //从市场中获取机器人默认参数
    //                    //机器人分享到市场robot_id不会该改变，但是用户获取机器人robot_id会发生改变
    //                    //获取原始机器人robot_id
    //                    String robotIdMarket = cParamDao.getMarketRobotId(robotExecute);
    //                    //查询原始机器人主流程参数
    //                    processId = cParamDao.getMianProcessId(robotIdMarket,robotExecute.getAppVersion());
    //                    cParamList = cParamDao.getAllParams(processId,robotIdMarket,robotExecute.getAppVersion());
    //                    return AppResponse.success(cParamToParamDto(cParamList));
    //                }
    //            }else if(dataSource.equals("create")){
    //                //自己创建的机器人
    //                //首先查询机器人启用的版本号
    //                robotVersion = cParamDao.getRobotVersion(robotId);
    //                if(StringUtils.isBlank(processId)){
    //                    //执行器参数查询不会给processId
    //                    //默认查询主流程参数
    //                    //根据robotId和robotVersion查询主流程id
    //                    processId = cParamDao.getMianProcessId(robotId,robotVersion);
    //                }
    //                //根据robotId和processId和robotVersion查询主流程参数
    //                cParamList = cParamDao.getSelfRobotParam(robotId,processId,robotVersion);
    //                return AppResponse.success(cParamToParamDto(cParamList));
    //            }
    //        }
    //        return AppResponse.success(new ArrayList<>());
    //    }
    //
    //
    //    private List<ParamDto> cParamToParamDto(List<CParam> cParamList){
    //        List<ParamDto> result = new ArrayList<>();
    //        if(!CollectionUtil.isEmpty(cParamList)){
    //            for(CParam param:cParamList){
    //                ParamDto paramDto = new ParamDto();
    //                BeanUtils.copyProperties(param, paramDto);
    //                result.add(paramDto);
    //            }
    //        }
    //        return result;
    //    }

    @Override
    public AppResponse<String> addParam(CParamDto cParamDto) throws NoLoginException {
        // 新增参数只会在编辑时候才有，所以可以默认参数版本是0版本
        CParam cParam = new CParam();
        BeanUtils.copyProperties(cParamDto, cParam);
        // 利用雪花算法自动生成id
        String cParamId = idWorker.nextId() + "";
        cParam.setId(cParamId);
        // 获取用户id
        String userId = UserUtils.nowUserId();
        cParam.setCreatorId(userId);
        cParam.setUpdaterId(userId);
        cParam.setCreateTime(new Date());
        cParam.setUpdateTime(new Date());
        cParam.setDeleted(0);
        // 如果没给版本默认是版本0
        if (null == cParam.getRobotVersion()) {
            cParam.setRobotVersion(0);
        }
        checkSameName(cParam);
        cParamDao.addParam(cParam);
        return AppResponse.success(cParamId);
    }

    @Override
    public AppResponse<Boolean> deleteParam(String id) {
        cParamDao.deleteParam(id);
        return AppResponse.success(true);
    }

    @Override
    public AppResponse<Boolean> updateParam(CParamDto cParamDto) throws NoLoginException {
        CParam cParam = new CParam();
        BeanUtils.copyProperties(cParamDto, cParam);
        checkSameName(cParam);
        cParam.setUpdaterId(UserUtils.nowUserId());
        cParam.setUpdateTime(new Date());
        cParamDao.updateParam(cParam);
        return AppResponse.success(true);
    }

    private void checkSameName(CParam cParam) throws NoLoginException {
        String varName = cParam.getVarName();
        varName = varName.trim();
        if (StringUtils.isBlank(varName)) {
            throw new ServiceException("参数名称不能为空");
        }
        cParam.setVarName(varName);
        cParam.setCreatorId(UserUtils.nowUserId());
        Long countRobot = cParamDao.countParamByName(cParam);
        if (countRobot > 0) {
            throw new ServiceException("存在同名参数，请重新命名");
        }
    }

    public AppResponse<Boolean> saveUserParam(List<CParam> cParamList)
            throws NoLoginException, JsonProcessingException {
        RobotExecute robotExecute = new RobotExecute();
        if (CollectionUtils.isEmpty(cParamList)) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode(), "参数信息不能为空");
        }
        // 根据参数id查询机器人id
        CParam paramInfo = cParamDao.getParamInfoById(cParamList.get(0).getId());
        String robotId = paramInfo.getRobotId();
        for (CParam cParam : cParamList) {
            cParam.setCreateTime(new Date());
            cParam.setUpdateTime(new Date());
            cParam.setCreatorId(UserUtils.nowUserId());
        }
        robotExecute.setRobotId(robotId);
        robotExecute.setCreatorId(UserUtils.nowUserId());
        robotExecute.setTenantId(TenantUtils.getTenantId());
        ObjectMapper mapper = new ObjectMapper();
        // 对传入cParamList进行序列化操作
        String cParamListJson = mapper.writeValueAsString(cParamList);
        robotExecute.setParamDetail(cParamListJson);
        robotExecute.setUpdateTime(new Date());
        robotExecuteDao.saveParamInfo(robotExecute);
        return AppResponse.success(true);
    }

    public void createParamForCurrentVersion(String processId, RobotVersionDto robotVersionDto, Integer version) {
        // 查询0版本机器人所有参数
        List<CParam> cParamList = cParamDao.getAllParams(processId, robotVersionDto.getRobotId(), version);
        for (CParam cParam : cParamList) {
            cParam.setId(idWorker.nextId() + "");
            // 更新版本号
            cParam.setRobotVersion(robotVersionDto.getVersion());
        }
        if (!cParamList.isEmpty()) {
            cParamDao.createParamForCurrentVersion(cParamList);
        }
    }
}

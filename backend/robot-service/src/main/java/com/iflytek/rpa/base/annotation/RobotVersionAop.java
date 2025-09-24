package com.iflytek.rpa.base.annotation;

import static com.iflytek.rpa.robot.constants.RobotConstant.*;

import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.robot.dao.RobotExecuteDao;
import com.iflytek.rpa.robot.dao.RobotVersionDao;
import com.iflytek.rpa.robot.entity.RobotExecute;
import com.iflytek.rpa.robot.entity.RobotVersion;
import com.iflytek.rpa.starter.exception.NoDataException;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.lang.reflect.Method;
import java.lang.reflect.Parameter;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

@Aspect
@Component
public class RobotVersionAop {
    private static final Logger log = LoggerFactory.getLogger(RobotVersionAop.class);

    @Autowired
    private RobotExecuteDao robotExecuteDao;

    @Autowired
    private RobotVersionDao robotVersionDao;

    @Around("@annotation(robotVersionAnnotation)")
    public Object process(ProceedingJoinPoint joinPoint, RobotVersionAnnotation robotVersionAnnotation)
            throws Throwable {
        Method method = ((MethodSignature) joinPoint.getSignature()).getMethod();
        Object[] args = joinPoint.getArgs();
        Parameter[] parameters = method.getParameters();
        BaseDto baseDto = new BaseDto();
        String robotId = null;
        String mode = null;
        Integer robotVersion = null;

        // 获取或修改 robotId 和 version
        for (int i = 0; i < parameters.length; i++) {
            Object argValue = args[i];
            if (argValue.getClass().equals(robotVersionAnnotation.clazz())) {
                try {
                    robotId = argValue.getClass()
                            .getMethod("getRobotId")
                            .invoke(argValue)
                            .toString();
                    mode = argValue.getClass()
                            .getMethod("getMode")
                            .invoke(argValue)
                            .toString();
                    robotVersion = (Integer)
                            argValue.getClass().getMethod("getRobotVersion").invoke(argValue);
                    try {
                        getRobotIdAndVersion(robotId, robotVersion, mode, baseDto);
                    } catch (NoDataException e) {
                        return AppResponse.error(ErrorCodeEnum.E_SQL, e.getMessage());
                    }
                    // 修改 robotId 的值
                    argValue.getClass().getMethod("setRobotId", String.class).invoke(argValue, baseDto.getRobotId());
                    // 修改 version 的值
                    argValue.getClass()
                            .getMethod("setRobotVersion", Integer.class)
                            .invoke(argValue, baseDto.getRobotVersion());

                } catch (Exception e) {
                    e.printStackTrace();
                    log.error("获取或修改 robotId 或 version 失败, message:{}", e.getMessage());
                    return AppResponse.error(ErrorCodeEnum.E_SERVICE, "获取或修改机器人信息失败");
                }
            }
        }

        // 调用目标方法，并传递修改后的参数
        return joinPoint.proceed(args);
    }

    /**
     * 机器人流程等数据从哪获取：1、对于设计器和编辑态，从版本0获取、2、对于执行器自己创建的，从启用版本获取 3、对于执行器从市场获取的机器人，取appVersion和作者的robotId
     *
     * @param robotId
     * @param mode
     * @param baseDto
     * @throws NoDataException
     * @throws NoLoginException
     */
    private void getRobotIdAndVersion(String robotId, Integer robotVersion, String mode, BaseDto baseDto)
            throws NoDataException, NoLoginException {
        if (null != robotVersion) {
            baseDto.setRobotVersion(robotVersion);
            baseDto.setRobotId(robotId);
            return;
        }

        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        if (PROJECT_LIST.equals(mode) || EDIT_PAGE.equals(mode)) {
            baseDto.setRobotId(robotId);
            baseDto.setRobotVersion(0);
        } else if (DISPATCH.equals(mode)) {
            // 调度模式必须上传机器人版本
            if (null == robotVersion) {
                throw new NoDataException("调度任务的机器人版本不存在");
            }
            baseDto.setRobotId(robotId);
            baseDto.setRobotVersion(robotVersion);
        } else {
            // 如果是执行器或计划任务，分为自己创建的（查启用版本），获取的（查appVersion）
            RobotExecute robotExecute = robotExecuteDao.queryByRobotId(robotId, userId, tenantId);
            if (null == robotExecute) {
                throw new NoDataException("执行器机器人不存在");
            }
            String dataSource = robotExecute.getDataSource();
            if (CREATE.equals(dataSource)) {
                // 自己创建的，查启用版本
                RobotVersion version = robotVersionDao.getOriEnableVersion(robotId, userId, tenantId);
                if (null == version || null == version.getVersion()) {
                    throw new NoDataException("机器人无启用版本信息");
                }
                baseDto.setRobotId(robotId);
                baseDto.setRobotVersion(version.getVersion());

            } else if (MARKET.equals(dataSource)) {
                // 市场获取的，查appVersion和作者的robotId
                String marketId = robotExecute.getMarketId();
                String appId = robotExecute.getAppId();

                if (null == robotExecute.getAppVersion()) {
                    throw new NoDataException("该机器人关联的应用版本信息缺失");
                }
                baseDto.setRobotVersion(robotExecute.getAppVersion());
            } else if (DEPLOY.equals(dataSource)) {
                // 部署的，appId对应robotId,appVersion对应robotVersion
                baseDto.setRobotId(robotExecute.getAppId());
                baseDto.setRobotVersion(robotExecute.getAppVersion());
            }
        }
    }
}

package com.iflytek.rpa.base.service.impl;

import static com.iflytek.rpa.robot.constants.RobotConstant.EDITING;

import com.iflytek.rpa.base.annotation.RobotVersionAnnotation;
import com.iflytek.rpa.base.dao.CModuleDao;
import com.iflytek.rpa.base.entity.CModule;
import com.iflytek.rpa.base.entity.CProcess;
import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.base.entity.dto.CreateModuleDto;
import com.iflytek.rpa.base.entity.dto.ProcessModuleListDto;
import com.iflytek.rpa.base.entity.dto.RenameModuleDto;
import com.iflytek.rpa.base.entity.vo.ModuleListVo;
import com.iflytek.rpa.base.entity.vo.OpenModuleVo;
import com.iflytek.rpa.base.entity.vo.ProcessModuleListVo;
import com.iflytek.rpa.base.service.CModuleService;
import com.iflytek.rpa.base.service.NextName;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.robot.entity.dto.SaveModuleDto;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.sql.SQLException;
import java.util.*;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

@Service("CModuleService")
public class CModuleServiceImpl extends NextName implements CModuleService {

    public final int CONTENT_MAX_LENGTH = 10000000; // 实际数据库中medium text 支持的最大长度是 16777215
    // 新生成的初始代码
    public final String initContent =
            "from typing import Any\n" + "from rpahelper.helper import Helper, print, logger\n" + "\n"
                    + "def main(*args, **kwargs) -> Any:\n" + "    h = Helper(**kwargs)\n" + "    params = h.params()\n"
                    + "\n" + "    # 打印所有的变量key\n" + "    logger.info(params.keys())\n" + "\n" + "    return True";

    @Resource
    private CModuleDao cModuleDao;

    @Resource
    private RobotDesignDao robotDesignDao;

    @Resource
    private IdWorker idWorker;

    @Override
    public AppResponse<List<ProcessModuleListVo>> processModuleList(ProcessModuleListDto queryDto)
            throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        // 获取代码模块列表
        List<ModuleListVo> moduleList = getModuleList(queryDto, userId);

        List<ProcessModuleListVo> resVoList = getResVoList(moduleList, userId, queryDto);

        return AppResponse.success(resVoList);
    }

    @Override
    public AppResponse<List<ModuleListVo>> moduleList(ProcessModuleListDto queryDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        List<ModuleListVo> moduleList = getModuleList(queryDto, userId);

        return AppResponse.success(moduleList);
    }

    @Override
    public AppResponse<OpenModuleVo> create(CreateModuleDto queryDto) throws NoLoginException {

        String userId = UserUtils.nowUserId();
        String robotId = queryDto.getRobotId();

        if (StringUtils.isBlank(robotId)) throw new IllegalArgumentException();

        String newModuleId = String.valueOf(idWorker.nextId());

        // 校验名称
        if (checkNewNameDup(queryDto.getModuleName(), robotId, userId)) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "名称重复，请重新命名");
        }

        CModule cModule = new CModule();
        cModule.setModuleId(newModuleId);
        cModule.setCreatorId(userId);
        cModule.setModuleName(queryDto.getModuleName());
        cModule.setModuleContent(initContent);
        cModule.setRobotVersion(0);
        cModule.setRobotId(robotId);
        cModule.setCreatorId(userId);
        cModule.setUpdaterId(userId);

        cModuleDao.insert(cModule);

        OpenModuleVo resVo = new OpenModuleVo();
        resVo.setModuleContent(cModule.getModuleContent());
        resVo.setModuleId(newModuleId);
        resVo.setRobotId(robotId);
        resVo.setRobotVersion(0);

        return AppResponse.success(resVo);
    }

    @Override
    public AppResponse<String> newModuleName(String robotId) throws NoLoginException {
        if (StringUtils.isBlank(robotId)) throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "参数缺失");
        String userId = UserUtils.nowUserId();
        return AppResponse.success(getModuleInitName(robotId, 0, userId));
    }

    @Override
    @RobotVersionAnnotation
    public AppResponse<OpenModuleVo> open(BaseDto baseDto, String moduleId) throws NoLoginException {
        Integer robotVersion = 0;
        if (baseDto.getRobotVersion() != null) {
            robotVersion = baseDto.getRobotVersion();
        }
        String robotId = baseDto.getRobotId();
        CModule module = cModuleDao.getModule(moduleId, robotId, robotVersion);
        if (module == null) throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "该模块不存在");
        OpenModuleVo resVo = new OpenModuleVo();
        resVo.setModuleId(moduleId);
        resVo.setModuleContent(module.getModuleContent());
        resVo.setRobotId(robotId);
        resVo.setRobotVersion(robotVersion);

        return AppResponse.success(resVo);
    }

    @Override
    public AppResponse<Boolean> delete(String moduleId) throws NoLoginException, SQLException {

        String userId = UserUtils.nowUserId();

        boolean b = cModuleDao.deleteOneModule(moduleId, userId);

        if (b) return AppResponse.success(true);
        else throw new SQLException();
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<Boolean> save(SaveModuleDto queryDto) throws NoLoginException, SQLException {
        String userId = UserUtils.nowUserId();
        String moduleId = queryDto.getModuleId();
        String robotId = queryDto.getRobotId();
        String newModuleContent = queryDto.getModuleContent();

        if (StringUtils.length(newModuleContent) > CONTENT_MAX_LENGTH) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "模块代码长度超长");
        }

        CModule module = cModuleDao.getOneModule(moduleId, userId, robotId);
        if (module == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "不存在该模块，无法更新");
        }
        String oldModuleContent = module.getModuleContent();
        // 更新 robotDesign状态为编辑中状态
        if (oldModuleContent != null && newModuleContent != null && !oldModuleContent.equals(newModuleContent)) {
            robotDesignDao.updateTransformStatus(userId, robotId, null, EDITING);
        }
        boolean b = cModuleDao.saveModuleContent(moduleId, userId, robotId, newModuleContent);

        if (b) return AppResponse.success(true);
        else throw new SQLException();
    }

    @Override
    public AppResponse<Boolean> rename(RenameModuleDto queryDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String moduleId = queryDto.getModuleId();
        Integer robotVersion = 0;
        String robotId = queryDto.getRobotId();
        String newName = queryDto.getModuleName();

        List<String> allModuleName = cModuleDao.getAllModuleNameExpSelf(robotId, robotVersion, userId, moduleId);

        if (allModuleName.contains(newName)) throw new ServiceException("名称重复，请重新输入");
        else return AppResponse.success(cModuleDao.updateModuleName(userId, moduleId, newName));
    }

    public String getModuleInitName(String robotId, Integer robotVersion, String userId) {
        String newModuleName = "代码模块1";
        List<CModule> allModuleList = cModuleDao.getAllModuleList(robotId, robotVersion, userId);

        if (!CollectionUtils.isEmpty(allModuleList)) {
            List<String> moduleNameList =
                    allModuleList.stream().map(CModule::getModuleName).collect(Collectors.toList());
            List<String> nameAfterFilter = moduleNameList.stream()
                    .filter(name -> name.contains("代码模块"))
                    .collect(Collectors.toList());
            newModuleName = newModuleName(nameAfterFilter);
        }

        return newModuleName;
    }

    public String newModuleName(List<String> nameAfterFilter) {
        Integer index = 1;
        while (true) {
            String newName = "代码模块" + index;
            if (nameAfterFilter.contains(newName)) index++;
            else return newName;
        }
    }

    private boolean checkNewNameDup(String newName, String robotId, String userId) {
        List<String> allModuleName = cModuleDao.getAllModuleName(robotId, 0, userId);
        return allModuleName.contains(newName);
    }

    private List<ProcessModuleListVo> getResVoList(
            List<ModuleListVo> moduleList, String userId, ProcessModuleListDto queryDto) {
        String robotId = queryDto.getRobotId();
        Integer robotVersion = 0;

        List<ProcessModuleListVo> resVoList = new ArrayList<>();

        List<CProcess> processList = cModuleDao.getAllProcessList(robotId, robotVersion, userId);

        // 流程数据
        for (CProcess process : processList) {
            ProcessModuleListVo resVo = new ProcessModuleListVo();

            resVo.setName(process.getProcessName());
            resVo.setResourceId(process.getProcessId());
            resVo.setResourceCategory("process");

            resVoList.add(resVo);
        }

        // 模块数据
        for (ModuleListVo moduleVo : moduleList) {
            ProcessModuleListVo resVo = new ProcessModuleListVo();

            resVo.setName(moduleVo.getName());
            resVo.setResourceId(moduleVo.getModuleId());
            resVo.setResourceCategory("module");

            resVoList.add(resVo);
        }

        return resVoList;
    }

    private List<ModuleListVo> getModuleList(ProcessModuleListDto queryDto, String userId) {
        String robotId = queryDto.getRobotId();
        Integer robotVersion = 0;

        List<CModule> allModuleList = cModuleDao.getAllModuleList(robotId, robotVersion, userId);

        List<ModuleListVo> res = new ArrayList<>();

        for (CModule cModule : allModuleList) {

            ModuleListVo moduleListVo = new ModuleListVo();
            moduleListVo.setModuleId(cModule.getModuleId());
            moduleListVo.setName(cModule.getModuleName());

            res.add(moduleListVo);
        }

        return res;
    }

    public Map<String, String> copyCodeModule(String robotId, String processOrModuleId) {
        // 查询原代码模块数据
        BaseDto baseDto = new BaseDto();
        baseDto.setRobotId(robotId);
        baseDto.setRobotVersion(0);
        baseDto.setId(processOrModuleId);
        CModule codeModule = cModuleDao.getCodeModeById(baseDto);
        if (null == codeModule) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "流程数据不存在");
        }
        String moduleName = codeModule.getModuleName();
        baseDto.setName(moduleName);
        // 产生副本名称
        String nextName = createNextName(baseDto, moduleName + "副本");
        // 复制流程
        codeModule.setModuleId(idWorker.nextId() + "");
        codeModule.setModuleName(nextName);
        codeModule.setCreateTime(new Date());
        codeModule.setUpdateTime(new Date());
        cModuleDao.insert(codeModule);
        Map<String, String> result = new HashMap<>();
        result.put("id", codeModule.getModuleId());
        result.put("name", codeModule.getModuleName());
        return result;
    }

    @Override
    public List<String> getNameList(BaseDto baseDto) {
        return cModuleDao.getModuleNameListByPrefix(baseDto);
    }
}

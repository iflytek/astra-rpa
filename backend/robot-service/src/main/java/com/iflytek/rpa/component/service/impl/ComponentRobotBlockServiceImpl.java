package com.iflytek.rpa.component.service.impl;

import com.iflytek.rpa.base.annotation.RobotVersionAnnotation;
import com.iflytek.rpa.base.entity.dto.BaseDto;
import com.iflytek.rpa.component.dao.ComponentRobotBlockDao;
import com.iflytek.rpa.component.dao.ComponentRobotUseDao;
import com.iflytek.rpa.component.entity.ComponentRobotBlock;
import com.iflytek.rpa.component.entity.ComponentRobotUse;
import com.iflytek.rpa.component.entity.dto.AddRobotBlockDto;
import com.iflytek.rpa.component.entity.dto.GetRobotBlockDto;
import com.iflytek.rpa.component.service.ComponentRobotBlockService;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.Date;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 机器人对组件屏蔽表(ComponentRobotBlock)表服务实现类
 *
 * @author makejava
 * @since 2024-12-19
 */
@Service("componentRobotBlockService")
public class ComponentRobotBlockServiceImpl implements ComponentRobotBlockService {

    @Autowired
    private ComponentRobotBlockDao componentRobotBlockDao;

    @Autowired
    private ComponentRobotUseDao componentRobotUseDao;

    @Autowired
    private ComponentRobotBlockServiceImpl self;

    /**
     * 添加机器人对组件的屏蔽记录
     *
     * @param addRobotBlockDto 添加屏蔽记录请求参数
     * @return 操作结果
     * @throws Exception 异常信息
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<Boolean> addRobotBlock(AddRobotBlockDto addRobotBlockDto) throws Exception {
        // 获取当前租户ID
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        Integer robotVersion = getRobotVersion(
                addRobotBlockDto.getRobotId(),
                addRobotBlockDto.getMode(),
                addRobotBlockDto.getRobotVersion(),
                new BaseDto());

        // 检查componentRobotUse表中是否存在该记录
        ComponentRobotUse existingUse = componentRobotUseDao.getByRobotIdVersionAndComponentId(
                addRobotBlockDto.getRobotId(), robotVersion,
                addRobotBlockDto.getComponentId(), userId);
        if (existingUse != null) throw new ServiceException(ErrorCodeEnum.E_SQL_REPEAT.getCode(), "该机器人已使用此组件，无法屏蔽");

        // 检查是否已经存在屏蔽记录
        Long existingCount = componentRobotBlockDao.checkBlockExists(
                addRobotBlockDto.getRobotId(), robotVersion, addRobotBlockDto.getComponentId(), userId);
        if (existingCount > 0) throw new ServiceException(ErrorCodeEnum.E_SQL_REPEAT.getCode(), "该机器人已屏蔽此组件，无需重复添加");

        // 创建新的屏蔽记录
        ComponentRobotBlock block = new ComponentRobotBlock();
        block.setRobotId(addRobotBlockDto.getRobotId());
        block.setRobotVersion(robotVersion);
        block.setComponentId(addRobotBlockDto.getComponentId());
        block.setCreatorId(userId);
        block.setCreateTime(new Date());
        block.setUpdaterId(userId);
        block.setUpdateTime(new Date());
        block.setDeleted(0);
        block.setTenantId(tenantId);

        // 保存到数据库
        int result = componentRobotBlockDao.insert(block);

        if (result > 0) {
            return AppResponse.success(true);
        } else {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "添加屏蔽失败");
        }
    }

    /**
     * 删除机器人对组件的屏蔽记录
     *
     * @param addRobotBlockDto 删除屏蔽记录请求参数
     * @return 操作结果
     * @throws Exception 异常信息
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<Boolean> deleteRobotBlock(AddRobotBlockDto addRobotBlockDto) throws Exception {
        // 获取当前租户ID和用户ID
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();

        Integer robotVersion = getRobotVersion(
                addRobotBlockDto.getRobotId(),
                addRobotBlockDto.getMode(),
                addRobotBlockDto.getRobotVersion(),
                new BaseDto());

        // 检查是否已经存在屏蔽记录
        Long existingCount = componentRobotBlockDao.checkBlockExists(
                addRobotBlockDto.getRobotId(), robotVersion, addRobotBlockDto.getComponentId(), userId);
        if (existingCount == 0) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "该机器人未屏蔽此组件，无需删除");
        }

        // 逻辑删除屏蔽记录
        int result = componentRobotBlockDao.deleteBlockByRobotAndComponent(
                addRobotBlockDto.getRobotId(), robotVersion, addRobotBlockDto.getComponentId(), userId, tenantId);

        if (result > 0) {
            return AppResponse.success(true);
        } else {
            throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "删除屏蔽失败");
        }
    }

    /**
     * 获取机器人屏蔽的组件ID列表
     *
     * @param queryDto
     * @return 屏蔽的组件ID列表
     * @throws Exception 异常信息
     */
    @Override
    public AppResponse<List<String>> getBlockedComponentIds(GetRobotBlockDto queryDto) throws Exception {
        // 获取当前租户ID
        String tenantId = TenantUtils.getTenantId();

        Integer robotVersion =
                getRobotVersion(queryDto.getRobotId(), queryDto.getMode(), queryDto.getRobotVersion(), new BaseDto());

        // 查询屏蔽的组件ID列表
        List<String> blockedComponentIds =
                componentRobotBlockDao.getBlockedComponentIds(queryDto.getRobotId(), robotVersion, tenantId);

        return AppResponse.success(blockedComponentIds);
    }

    public Integer getRobotVersion(String robotId, String mode, Integer version, BaseDto baseDto) {
        baseDto.setMode(mode);
        baseDto.setRobotVersion(version);
        baseDto.setRobotId(robotId);

        // 解决代理不生效问题，不能用类调用自己的方法，只能用注入的方式
        self.getVersion(baseDto);

        return baseDto.getRobotVersion();
    }

    @RobotVersionAnnotation
    public void getVersion(BaseDto baseDto) {}
}

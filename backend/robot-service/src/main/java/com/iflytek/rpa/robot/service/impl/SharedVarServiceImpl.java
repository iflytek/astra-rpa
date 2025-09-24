package com.iflytek.rpa.robot.service.impl;

import cn.hutool.core.bean.BeanUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.robot.dao.SharedSubVarDao;
import com.iflytek.rpa.robot.dao.SharedVarDao;
import com.iflytek.rpa.robot.dao.SharedVarKeyTenantDao;
import com.iflytek.rpa.robot.dao.SharedVarUserDao;
import com.iflytek.rpa.robot.entity.SharedSubVar;
import com.iflytek.rpa.robot.entity.SharedVar;
import com.iflytek.rpa.robot.entity.SharedVarKeyTenant;
import com.iflytek.rpa.robot.entity.SharedVarUser;
import com.iflytek.rpa.robot.entity.dto.*;
import com.iflytek.rpa.robot.entity.enums.SharedVarTypeEnum;
import com.iflytek.rpa.robot.entity.vo.*;
import com.iflytek.rpa.robot.service.SharedVarService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.EncryptionUtil;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.security.SecureRandom;
import java.util.*;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.jetbrains.annotations.NotNull;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;

/**
 * 共享变量服务实现类
 *
 * @author jqfang3
 * @since 2025-07-21
 */
@Slf4j
@Service
public class SharedVarServiceImpl extends ServiceImpl<SharedVarDao, SharedVar> implements SharedVarService {
    @Resource
    private SharedVarDao sharedVarDao;

    @Resource
    private SharedSubVarDao sharedSubVarDao;

    @Resource
    private SharedVarUserDao sharedVarUserDao;

    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    @Resource
    private SharedVarKeyTenantDao sharedVarKeyTenantDao;

    @Autowired
    private IdWorker idWorker;

    private static void packageEncryptValue(String aesKey, SharedSubVarVo subVar, ClientSharedSubVarVo clientSubVar) {
        // 处理加密逻辑
        String varValue = subVar.getVarValue();
        if (subVar.getEncrypt() != null && subVar.getEncrypt() == 1 && varValue != null) {
            try {
                varValue = EncryptionUtil.encrypt(varValue, aesKey);
            } catch (Exception e) {
                log.error("加密变量值失败: {}", e.getMessage());
                throw new ServiceException(ErrorCodeEnum.E_SERVICE.getCode(), "变量加密失败");
            }
        }
        clientSubVar.setVarValue(varValue);
    }

    @Override
    public AppResponse<IPage<SharedVarPageVo>> getSharedVarPageList(SharedVarPageDto queryDto) throws NoLoginException {
        String tenantId = TenantUtils.getTenantId();
        if (tenantId == null) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "缺少租户信息");
        }

        IPage<SharedVar> pageConfig = new Page<>(queryDto.getPageNo(), queryDto.getPageSize(), true);
        LambdaQueryWrapper<SharedVar> wrapper = new LambdaQueryWrapper<SharedVar>()
                .eq(SharedVar::getTenantId, tenantId)
                .eq(SharedVar::getDeleted, 0)
                .eq(StringUtils.hasText(queryDto.getDeptId()), SharedVar::getDeptId, queryDto.getDeptId())
                .eq(queryDto.getStatus() != null, SharedVar::getStatus, queryDto.getStatus())
                .apply(
                        StringUtils.hasText(queryDto.getSharedVarName()),
                        "UPPER(shared_var_name) LIKE concat('%', UPPER({0}), '%')",
                        queryDto.getSharedVarName())
                .orderByDesc(SharedVar::getCreateTime);

        IPage<SharedVar> page = this.page(pageConfig, wrapper);
        List<SharedVar> records = page.getRecords();
        List<SharedVarPageVo> pageList = records.stream()
                .map(record -> {
                    SharedVarPageVo sharedVarPageVo = new SharedVarPageVo();
                    BeanUtils.copyProperties(record, sharedVarPageVo);
                    return sharedVarPageVo;
                })
                .collect(Collectors.toList());

        if (!pageList.isEmpty()) {
            // 获取子变量列表
            packageSubVarList(pageList);
            // 获取用户列表
            packageUserList(pageList);
            // 获取部门名称
            // todo:dept
            //            packageDeptNameList(pageList);
        }

        IPage<SharedVarPageVo> resultPage = new Page<>();
        resultPage.setRecords(pageList);
        resultPage.setCurrent(page.getCurrent());
        resultPage.setSize(page.getSize());
        resultPage.setTotal(page.getTotal());
        resultPage.setPages(page.getPages());
        return AppResponse.success(resultPage);
    }

    /**
     * 包装子变量列表
     */
    private void packageSubVarList(List<SharedVarPageVo> records) {
        List<Long> sharedVarIds = records.stream().map(SharedVarPageVo::getId).collect(Collectors.toList());
        if (sharedVarIds.isEmpty()) {
            return;
        }
        List<SharedSubVarVo> subVarList = baseMapper.getSubVarListBySharedVarIds(sharedVarIds);
        Map<Long, List<SharedSubVarVo>> sharedVarId2SubVarMap =
                subVarList.stream().collect(Collectors.groupingBy(SharedSubVarVo::getSharedVarId));
        for (SharedVarPageVo record : records) {
            List<SharedSubVarVo> subVars = sharedVarId2SubVarMap.get(record.getId());
            // 变量组类型
            if (record.getSharedVarType().equals(SharedVarTypeEnum.GROUP.getCode())) {
                record.setVarList(subVars);
            } else {
                SharedSubVarVo sharedSubVarVo = subVars.get(0);
                record.setSharedVarName(sharedSubVarVo.getVarName());
                record.setSharedVarEncrypt(sharedSubVarVo.getEncrypt());
                record.setSharedVarValue(sharedSubVarVo.getVarValue());
            }
        }
    }

    /**
     * 包装用户列表
     */
    private void packageUserList(List<SharedVarPageVo> records) {
        List<Long> sharedVarIds = records.stream().map(SharedVarPageVo::getId).collect(Collectors.toList());
        if (sharedVarIds.isEmpty()) {
            return;
        }
        List<SharedVarUser> userList = baseMapper.getUserListBySharedVarIds(sharedVarIds);
        Map<Long, List<SharedVarUser>> sharedVarId2UserMap =
                userList.stream().collect(Collectors.groupingBy(SharedVarUser::getSharedVarId));
        for (SharedVarPageVo record : records) {
            List<SharedVarUser> users = sharedVarId2UserMap.get(record.getId());
            //            if (users != null && !users.isEmpty()) {
            //                List<UserVo> userVoList = users.stream()
            //                        .map(user -> {
            //                                    UserVo userVo = new UserVo();
            //                                    BeanUtils.copyProperties(user, userVo);
            //                                    return userVo;
            //                                }
            //                        )
            //                        .collect(Collectors.toList());
            //                record.setUserList(userVoList);
            //            }
        }
    }

    /**
     * 包装部门名称列表
     */
    // todo:dept
    //    private void packageDeptNameList(List<SharedVarPageVo> records) {
    //        records.forEach(record -> {
    //            record.setDeptName("");
    //            if (StringUtils.hasText(record.getDeptId())) {
    //                UapOrg deptInfoByDeptId = DeptUtils.getDeptInfoByDeptId(record.getDeptId());
    //                if (deptInfoByDeptId != null) {
    //                    String deptName = deptInfoByDeptId.getName();
    //                    record.setDeptName(deptName);
    //                }
    //            }
    //        });
    //    }
    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> saveSharedVar(SharedVarSaveDto saveDto) throws NoLoginException {
        // 参数校验
        checkSaveParam(saveDto);
        String tenantId = TenantUtils.getTenantId();
        String userId = UserUtils.nowUserId();
        if (tenantId == null) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "缺少租户信息");
        }
        // 检查变量名是否已存在
        int existCount = this.count(new LambdaQueryWrapper<SharedVar>()
                .eq(SharedVar::getTenantId, tenantId)
                .eq(SharedVar::getSharedVarName, saveDto.getSharedVarName())
                .eq(SharedVar::getDeleted, 0));
        if (existCount > 0) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "变量名已存在");
        }
        // 保存共享变量主表
        SharedVar sharedVar = new SharedVar();
        BeanUtil.copyProperties(saveDto, sharedVar);
        sharedVar.setId(idWorker.nextId());
        sharedVar.setTenantId(tenantId);
        sharedVar.setSharedVarType(saveDto.getVarType());
        sharedVar.setCreatorId(userId);
        sharedVar.setUpdaterId(userId);
        sharedVar.setCreateTime(new Date());
        sharedVar.setUpdateTime(new Date());
        sharedVar.setDeleted(0);
        this.save(sharedVar);
        Long sharedVarId = sharedVar.getId();
        // 保存子变量
        if (!CollectionUtils.isEmpty(saveDto.getVarList())) {
            saveSubVarList(sharedVarId, saveDto.getVarList());
        }
        // 如果可使用账号类型为指定人，保存用户关系
        if ("select".equals(saveDto.getUsageType()) && !CollectionUtils.isEmpty(saveDto.getSelectedUserList())) {
            saveUserList(sharedVarId, saveDto.getSelectedUserList());
        }
        return AppResponse.success("保存成功");
    }

    /**
     * 参数校验
     */
    private void checkSaveParam(SharedVarSaveDto saveDto) {
        // 变量类型校验
        boolean a = Arrays.stream(SharedVarTypeEnum.values())
                .anyMatch(varType -> varType.getCode().equals(saveDto.getVarType()));
        if (!a) throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "变量类型类型错误");

        // 变量组列表不能为空
        if (CollectionUtils.isEmpty(saveDto.getVarList())) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode(), "变量组列表不能为空");
        }

        // 可使用账号类型校验
        //        boolean b = Arrays
        //                .stream(UsageTypeEnum.values())
        //                .anyMatch(usageType -> usageType.getCode().equals(saveDto.getUsageType()));
        //        if (!b) throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "可使用账号类型错误");

        // 如果可使用账号类型为指定人，用户列表不能为空
        //        if (saveDto.getUsageType().equals(UsageTypeEnum.SELECT.getCode())
        //                && CollectionUtils.isEmpty(saveDto.getSelectedUserList())) {
        //            throw new ServiceException(ErrorCodeEnum.E_PARAM_LOSE.getCode(), "可使用账号类型为指定人时，用户列表不能为空");
        //        }
    }

    /**
     * 保存子变量列表
     */
    private void saveSubVarList(Long sharedVarId, List<SharedVarSaveDto.VarGroupItem> varList) {
        List<SharedSubVar> subVarList = new ArrayList<>();
        for (SharedVarSaveDto.VarGroupItem varGroup : varList) {
            SharedSubVar subVar = new SharedSubVar();
            subVar.setId(idWorker.nextId());
            subVar.setSharedVarId(sharedVarId);
            subVar.setVarName(varGroup.getVarName());
            subVar.setVarType(varGroup.getVarType());
            subVar.setVarValue(varGroup.getVarValue());
            subVar.setEncrypt(varGroup.getEncrypt() != null ? varGroup.getEncrypt() : 0);
            subVar.setDeleted(0);
            subVarList.add(subVar);
        }
        if (!subVarList.isEmpty()) {
            sharedSubVarDao.insertBatch(subVarList);
        }
    }

    /**
     * 保存用户关系列表
     */
    private void saveUserList(Long sharedVarId, List<SharedVarSaveDto.SelectedUser> selectedUserList) {
        List<SharedVarUser> userList = new ArrayList<>();
        for (SharedVarSaveDto.SelectedUser selectedUser : selectedUserList) {
            SharedVarUser varUser = new SharedVarUser();
            varUser.setSharedVarId(sharedVarId);
            varUser.setUserId(selectedUser.getUserId());
            varUser.setUserName(selectedUser.getUserName());
            varUser.setUserPhone(selectedUser.getUserPhone());
            varUser.setDeleted(0);
            userList.add(varUser);
        }
        sharedVarUserDao.insertBatch(userList);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> deleteSharedVar(SharedVarDeleteDto deleteDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String tenantId = TenantUtils.getTenantId();
        if (tenantId == null) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "缺少租户信息");
        }
        Long sharedVarId = deleteDto.getId();
        // 1. 校验shared_var是否存在该数据
        SharedVar sharedVar = this.getOne(new LambdaQueryWrapper<SharedVar>()
                .eq(SharedVar::getId, sharedVarId)
                .eq(SharedVar::getTenantId, tenantId)
                .eq(SharedVar::getDeleted, 0));
        if (sharedVar == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "共享变量不存在或已被删除");
        }
        // 删除表数据
        int deletedMain = baseMapper.deleteSharedVar(sharedVarId, userId);
        if (deletedMain == 0) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "删除共享变量失败");
        }
        // 删除子变量数据
        sharedSubVarDao.deleteBySharedVarId(sharedVarId, userId);
        // 删除用户关系数据
        sharedVarUserDao.deleteBySharedVarId(sharedVarId, userId);
        return AppResponse.success("删除成功");
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> updateSharedVar(SharedVarUpdateDto updateDto) throws NoLoginException {
        // 参数校验
        checkSaveParam(updateDto);
        String tenantId = TenantUtils.getTenantId();
        String userId = UserUtils.nowUserId();
        if (tenantId == null) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "缺少租户信息");
        }

        Long sharedVarId = updateDto.getId();
        // 1. 校验shared_var是否存在该数据
        SharedVar existingVar = this.getOne(new LambdaQueryWrapper<SharedVar>()
                .eq(SharedVar::getId, sharedVarId)
                .eq(SharedVar::getTenantId, tenantId)
                .eq(SharedVar::getDeleted, 0));
        if (existingVar == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "共享变量不存在或已被删除");
        }

        // 检查变量名是否与其他变量重复（排除自己）
        int existCount = this.count(new LambdaQueryWrapper<SharedVar>()
                .eq(SharedVar::getTenantId, tenantId)
                .eq(SharedVar::getSharedVarName, updateDto.getSharedVarName())
                .eq(SharedVar::getDeleted, 0)
                .ne(SharedVar::getId, sharedVarId));
        if (existCount > 0) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "变量名已存在");
        }

        // 2. 逻辑删除shared_var_user，shared_sub_var中共享变量id的数据
        sharedSubVarDao.deleteBySharedVarId(sharedVarId, userId);
        sharedVarUserDao.deleteBySharedVarId(sharedVarId, userId);

        // 3. 更新shared_var数据
        SharedVar updateVar = new SharedVar();
        BeanUtil.copyProperties(updateDto, updateVar);
        updateVar.setId(sharedVarId);
        updateVar.setTenantId(tenantId);
        updateVar.setSharedVarType(updateDto.getVarType());
        updateVar.setUpdaterId(userId);
        updateVar.setUpdateTime(new Date());
        // 保持原有的创建信息
        updateVar.setCreatorId(existingVar.getCreatorId());
        updateVar.setCreateTime(existingVar.getCreateTime());
        updateVar.setDeleted(0);
        this.updateById(updateVar);

        // 4. 重新插入shared_sub_var数据
        if (!CollectionUtils.isEmpty(updateDto.getVarList())) {
            saveSubVarList(sharedVarId, updateDto.getVarList());
        }
        // 5. 如果可使用账号类型为指定人，重新插入shared_var_user数据
        //        if (UsageTypeEnum.SELECT.getCode().equals(updateDto.getUsageType()) &&
        // !CollectionUtils.isEmpty(updateDto.getSelectedUserList())) {
        //            saveUserList(sharedVarId, updateDto.getSelectedUserList());
        //        }

        return AppResponse.success("更新成功");
    }

    /**
     * 定时任务：每天凌晨0点1分执行，检查租户共享变量的密钥
     */
    @Scheduled(cron = "1 0 0 * * *")
    @Transactional(rollbackFor = Exception.class)
    public void cronUpdateSharedVarTenantKey() {
        // 1. 逻辑删除shared_var_key_tenant所有数据
        sharedVarKeyTenantDao.deleteAll();
        // 2. 查出所有tenantId
        List<String> tenantIdList = sharedVarDao.getAllTenantId(databaseName);
        if (null == tenantIdList || tenantIdList.isEmpty()) {
            return;
        }
        tenantIdList.removeIf(Objects::isNull);
        // 3. 为每个租户生成32位随机密钥并批量插入
        List<SharedVarKeyTenant> keyTenantList = new ArrayList<>();
        for (String tenantId : tenantIdList) {
            SharedVarKeyTenant keyTenant = new SharedVarKeyTenant();
            keyTenant.setId(idWorker.nextId());
            keyTenant.setTenantId(tenantId);
            keyTenant.setKey(generateRandomKey(32));
            keyTenant.setDeleted(0);
            keyTenantList.add(keyTenant);
        }
        // 4. 批量插入新的密钥数据
        if (!keyTenantList.isEmpty()) {
            sharedVarKeyTenantDao.insertBatch(keyTenantList);
        }
    }

    //    @Override
    //    public AppResponse<List<ClientSharedVarVo>> getClientSharedVars() throws NoLoginException {
    //        String tenantId = TenantUtils.getTenantId();
    //        if (tenantId == null) {
    //            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "缺少租户信息");
    //        }
    //        String userId = UserUtils.nowUserId();
    ////        String deptId = DeptUtils.getDeptId();
    //        SharedVarKeyTenant keyTenant = sharedVarKeyTenantDao.selectByTenantId(tenantId);
    //        if (keyTenant == null) {
    //            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "租户密钥不存在");
    //        }
    //        String aesKey = keyTenant.getKey();
    //
    //        // 3. 查询三种类型的共享变量
    //        List<String> selectVarIds = sharedVarUserDao.getAvailableSharedVarIds(userId);
    //        List<SharedVar> availableVars = sharedVarDao.getAvailableSharedVars(tenantId, deptId, selectVarIds);
    //        if (availableVars.isEmpty()) {
    //            return AppResponse.success(new ArrayList<>());
    //        }
    //
    //        // 4. 封装结果
    //        List<ClientSharedVarVo> result = packageResultVo(availableVars, aesKey);
    //
    //        return AppResponse.success(result);
    //    }

    /**
     * 获取共享变量租户密钥
     *
     * @return 密钥 key
     * @throws NoLoginException
     */
    @Override
    public AppResponse<SharedVarKeyVo> getSharedVarKey() throws NoLoginException {
        String tenantId = TenantUtils.getTenantId();
        if (tenantId == null) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "缺少租户信息");
        }
        SharedVarKeyTenant keyTenant = sharedVarKeyTenantDao.selectByTenantId(tenantId);
        if (keyTenant == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "租户密钥不存在");
        }
        SharedVarKeyVo result = new SharedVarKeyVo();
        result.setKey(keyTenant.getKey());
        return AppResponse.success(result);
    }

    @NotNull
    private List<ClientSharedVarVo> packageResultVo(List<SharedVar> availableVars, String aesKey) {
        List<Long> sharedVarIds = availableVars.stream().map(SharedVar::getId).collect(Collectors.toList());
        List<SharedSubVarVo> subVarList = baseMapper.getSubVarListBySharedVarIds(sharedVarIds);
        Map<Long, List<SharedSubVarVo>> sharedVarId2SubVarMap =
                subVarList.stream().collect(Collectors.groupingBy(SharedSubVarVo::getSharedVarId));

        List<ClientSharedVarVo> result = new ArrayList<>();
        for (SharedVar sharedVar : availableVars) {
            ClientSharedVarVo clientVar = new ClientSharedVarVo();
            clientVar.setId(sharedVar.getId());
            clientVar.setSharedVarName(sharedVar.getSharedVarName());
            clientVar.setSharedVarType(sharedVar.getSharedVarType());

            // 子变量列表
            List<SharedSubVarVo> subVars = sharedVarId2SubVarMap.get(sharedVar.getId());
            if (subVars != null && !subVars.isEmpty()) {
                List<ClientSharedSubVarVo> clientSubVars = new ArrayList<>();

                for (SharedSubVarVo subVar : subVars) {
                    ClientSharedSubVarVo clientSubVar = new ClientSharedSubVarVo();
                    clientSubVar.setVarName(subVar.getVarName());
                    clientSubVar.setVarType(subVar.getVarType());
                    clientSubVar.setEncrypt(subVar.getEncrypt());
                    // 加密数据
                    packageEncryptValue(aesKey, subVar, clientSubVar);
                    clientSubVars.add(clientSubVar);
                }
                clientVar.setSubVarList(clientSubVars);

                // 对于非变量组类型，设置主变量的值和加密状态
                if (!SharedVarTypeEnum.GROUP.getCode().equals(sharedVar.getSharedVarType())) {
                    ClientSharedSubVarVo firstSubVar = clientSubVars.get(0);
                    clientVar.setSharedVarValue(firstSubVar.getVarValue());
                    clientVar.setEncrypt(firstSubVar.getEncrypt());
                }
            }

            result.add(clientVar);
        }
        return result;
    }

    /**
     * 生成指定长度的随机密钥
     *
     * @param length 密钥长度
     * @return 随机密钥
     */
    private String generateRandomKey(int length) {
        final String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        SecureRandom random = new SecureRandom();
        StringBuilder key = new StringBuilder();
        for (int i = 0; i < length; i++) {
            key.append(chars.charAt(random.nextInt(chars.length())));
        }
        return key.toString();
    }

    @Override
    public AppResponse<List<ClientSharedVarVo>> getBatchSharedVar(SharedVarBatchDto updateDto) throws NoLoginException {
        List<Long> ids = updateDto.getIds();
        if (ids.isEmpty()) {
            return AppResponse.success(new ArrayList<>());
        }
        String tenantId = TenantUtils.getTenantId();
        if (tenantId == null) {
            throw new ServiceException(ErrorCodeEnum.E_PARAM_CHECK.getCode(), "缺少租户信息");
        }
        SharedVarKeyTenant keyTenant = sharedVarKeyTenantDao.selectByTenantId(tenantId);
        if (keyTenant == null) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "租户密钥不存在");
        }
        String aesKey = keyTenant.getKey();
        List<SharedVar> availableVars = sharedVarDao.getAvailableByIds(ids);
        if (availableVars.isEmpty()) {
            return AppResponse.success(new ArrayList<>());
        }
        // 4. 封装结果
        List<ClientSharedVarVo> result = packageResultVo(availableVars, aesKey);

        return AppResponse.success(result);
    }
}

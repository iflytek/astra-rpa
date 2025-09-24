package com.iflytek.rpa.robot.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.robot.dao.SharedFileDao;
import com.iflytek.rpa.robot.entity.SharedFile;
import com.iflytek.rpa.robot.entity.SharedFileTag;
import com.iflytek.rpa.robot.entity.dto.SharedFileBatchDeleteDto;
import com.iflytek.rpa.robot.entity.dto.SharedFileDto;
import com.iflytek.rpa.robot.entity.dto.SharedFilePageDto;
import com.iflytek.rpa.robot.entity.dto.UpdateSharedFileDto;
import com.iflytek.rpa.robot.entity.enums.FileIndexStatus;
import com.iflytek.rpa.robot.entity.vo.SharedFilePageVo;
import com.iflytek.rpa.robot.entity.vo.TagVo;
import com.iflytek.rpa.robot.service.SharedFileService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.exception.ServiceException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.TenantUtils;
import com.iflytek.rpa.utils.UserUtils;
import java.util.*;
import java.util.stream.Collectors;
import javax.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections.CollectionUtils;
import org.apache.commons.lang3.StringUtils;
import org.casbin.casdoor.entity.Permission;
import org.casbin.casdoor.entity.User;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * 共享文件服务实现类
 *
 * @author yfchen40
 * @since 2025-07-21
 */
@Slf4j
@Service
public class SharedFileServiceImpl extends ServiceImpl<SharedFileDao, SharedFile> implements SharedFileService {
    @Autowired
    private IdWorker idWorker;

    @Autowired
    private SharedFileDao sharedFileDao;

    @Value("${uap.database.name:uap_db}")
    private String databaseName;

    @Override
    //    @Transactional(readOnly = true)
    public AppResponse<IPage<SharedFilePageVo>> getSharedFilePageList(SharedFilePageDto queryDto) {
        // 创建分页对象
        IPage<SharedFile> page = new Page<>(queryDto.getPageNo(), queryDto.getPageSize());
        String tenantId = TenantUtils.getTenantId();

        // 使用 XML 分页查询方式
        IPage<SharedFile> sharedFilePage = baseMapper.selectSharedFilePageList(page, queryDto, tenantId);

        if (sharedFilePage.getSize() == 0) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EMPTY, "未查询到符合条件的文件");
        }

        // 转换为 VO 对象
        IPage<SharedFilePageVo> resultPage = sharedFilePage.convert(sharedFile -> {
            SharedFilePageVo vo = new SharedFilePageVo();
            BeanUtils.copyProperties(sharedFile, vo);
            // 设置额外的 VO 字段
            vo.setFileId(sharedFile.getFileId());
            if (StringUtils.isNotBlank(sharedFile.getTags())) {
                // 设置标签ID列表
                List<Long> tagIds = Arrays.stream(sharedFile.getTags().split(","))
                        .map(Long::valueOf)
                        .collect(Collectors.toList());

                // 查询并设置标签名称列表
                List<SharedFileTag> tags = baseMapper.selectTagsByIds(tagIds, tenantId);
                List<String> tagNames =
                        tags.stream().map(SharedFileTag::getTagName).collect(Collectors.toList());
                vo.setTagsNames(tagNames);
            }
            if (sharedFile.getTags() != null && !sharedFile.getTags().isEmpty()) {
                vo.setTags(Arrays.asList(sharedFile.getTags().split(",")));
            } else {
                vo.setTags(null);
            }
            vo.setFilePath("/api/resource/file/download?fileId=" + sharedFile.getFileId());
            // 填充creatorName, phone(账号), deptId, deptName
            String creatorId = sharedFile.getCreatorId();
            //            String deptId = DeptUtils.getDeptIdByUserId(creatorId, tenantId);
            vo.setCreatorName(UserUtils.getRealNameById(sharedFile.getCreatorId()));
            User userInfoById = UserUtils.getUserInfoById(creatorId);
            if (Objects.nonNull(userInfoById)) {
                vo.setPhone(userInfoById.phone);
            }
            //            vo.setDeptId(deptId);

            // todo:dept
            //            UapOrg dept = DeptUtils.getDeptInfoByDeptId(deptId);
            //            if (dept != null) {
            //                vo.setDeptName(dept.getName());
            //            }
            return vo;
        });

        // 返回成功响应
        return AppResponse.success(resultPage);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> deleteSharedFile(HttpServletRequest request, SharedFileBatchDeleteDto batchDeleteDto)
            throws NoLoginException {
        // 判断用户权限
        if (!hasFileManagementPermission(request)) return AppResponse.error(ErrorCodeEnum.E_PARAM, "没有文件管理权限");

        // 批量删除共享文件
        String tenantId = TenantUtils.getTenantId();
        List<String> fileIds = batchDeleteDto.getFileIds();
        // 1. 校验所有 fileId 是否存在
        List<SharedFile> existFiles = this.list(new LambdaQueryWrapper<SharedFile>()
                .in(SharedFile::getFileId, fileIds)
                .eq(SharedFile::getTenantId, tenantId)
                .eq(SharedFile::getDeleted, 0));
        if (existFiles.size() != fileIds.size()) {
            // 找出不存在的 fileId
            List<String> existIds =
                    existFiles.stream().map(SharedFile::getFileId).collect(Collectors.toList());
            List<String> notExistIds =
                    fileIds.stream().filter(id -> !existIds.contains(id)).collect(Collectors.toList());
            throw new ServiceException(ErrorCodeEnum.E_SQL_EMPTY.getCode(), "部分共享文件不存在或已被删除: " + notExistIds);
        }

        // 2. 批量删除
        int deleted = baseMapper.deleteBatchSharedFile(fileIds, tenantId);
        if (deleted != fileIds.size()) {
            throw new ServiceException(ErrorCodeEnum.E_SQL_EXCEPTION.getCode(), "批量删除共享文件失败");
        }

        return AppResponse.success("删除共享文件成功");
    }

    @Override
    public AppResponse<List<TagVo>> getTags(HttpServletRequest request) throws NoLoginException {
        // 1. 验证用户权限
        if (!hasFileManagementPermission(request)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "没有文件管理权限");
        }
        // 2. 获取租户ID
        String tenantId = TenantUtils.getTenantId();
        // 3. 查询标签分页数据（从文件表中按 tags 分组统计）
        List<SharedFileTag> tagPage = baseMapper.selectTags(tenantId);

        List<TagVo> tagVos = tagPage.stream()
                .map(tag -> {
                    TagVo tagVo = new TagVo();
                    tagVo.setTagId(tag.getTagId().toString());
                    BeanUtils.copyProperties(tag, tagVo);
                    return tagVo;
                })
                .collect(Collectors.toList());
        if (tagVos == null) {
            tagVos = new ArrayList<>();
        }
        // 4. 返回成功响应
        return AppResponse.success(tagVos);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> addTags(HttpServletRequest request, String tagName) throws NoLoginException {
        // 1. 验证用户权限
        if (!hasFileManagementPermission(request)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "没有文件管理权限");
        }
        // 2. 验证标签唯一性
        String tenantId = TenantUtils.getTenantId();
        String userId = UserUtils.nowUserId();
        if (baseMapper.selectTagsCountByName(tagName, tenantId) > 0) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "标签已存在");
        }
        // 3. 创建新的标签实体
        SharedFileTag newTag = new SharedFileTag();
        newTag.setTagName(tagName);
        newTag.setTenantId(tenantId);
        newTag.setCreatorId(userId);
        newTag.setUpdaterId(userId);
        newTag.setTagId(idWorker.nextId());
        baseMapper.addTag(newTag);
        return AppResponse.success("新增标签成功");
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> updateTags(HttpServletRequest request, Long tagId, String tagName)
            throws NoLoginException {
        // 验证用户权限
        if (!hasFileManagementPermission(request)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "没有文件管理权限");
        }
        // 验证参数
        if (StringUtils.isBlank(tagId + "")) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "标签ID不能为空");
        }
        String tenantId = TenantUtils.getTenantId();
        // 验证标签id唯存在性
        if (!baseMapper.containsTagById(tagId, tenantId)) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "标签id不存在");
        }
        // 验证标签名称
        if (StringUtils.isBlank(tagName)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "标签名称不能为空");
        }
        String userId = UserUtils.nowUserId();
        // 验证标签唯一性
        if (baseMapper.selectTagsCountByName(tagName, tenantId) > 0) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "标签名称已存在");
        }
        // 执行更新操作
        int updated = baseMapper.updateTagById(tagId, tagName, userId, tenantId);
        if (updated == 0) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "更新标签失败，标签不存在或已被删除");
        }

        return AppResponse.success("更新标签成功");
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<String> deleteTags(HttpServletRequest request, Long tagId) throws NoLoginException {
        // 验证用户权限
        if (!hasFileManagementPermission(request)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "没有文件管理权限");
        }

        // 验证参数
        if (StringUtils.isBlank(tagId + "")) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "标签ID不能为空");
        }
        String tenantId = TenantUtils.getTenantId();
        // 验证标签id唯存在性
        if (!baseMapper.containsTagById(tagId, tenantId)) {
            return AppResponse.error(ErrorCodeEnum.E_SQL_EXCEPTION, "标签id不存在");
        }
        // 获取标签原名
        SharedFileTag existingTag = baseMapper.selectTagById(tagId, tenantId);
        String oldName = existingTag.getTagName();
        // 执行删除操作
        int deleted = baseMapper.deletedTagById(tagId, tenantId);
        if (deleted == 0) {
            return AppResponse.error(ErrorCodeEnum.E_SQL, "删除标签失败，标签不存在或已被删除");
        }
        // 更新所有包含该标签ID的文件，移除该标签ID
        int fileUpdated = 0;
        List<SharedFile> filesToUpdate = baseMapper.selectFilesByTag(tagId.toString(), tenantId);
        for (SharedFile file : filesToUpdate) {
            if (StringUtils.isNotBlank(file.getTags())) {
                List<String> tagIds =
                        new ArrayList<>(Arrays.asList(file.getTags().split(",")));
                // 从标签ID列表中移除要删除的标签ID
                tagIds.removeIf(tagIdStr -> tagIdStr.equals(tagId.toString()));
                // 更新文件的标签ID列表，如果标签列表为空则设置为空字符串
                String newTags = tagIds.isEmpty() ? "" : String.join(",", tagIds);
                baseMapper.updateFileTagById(file.getFileId(), newTags);
                fileUpdated++;
            }
        }
        return AppResponse.success("删除标签成功，" + fileUpdated + "个文件标签引用受影响");
    }

    // 判断用户有无文件处理权限
    private boolean hasFileManagementPermission(HttpServletRequest request) throws NoLoginException {
        // 如果是租户管理员，直接返回true
        User uapUser = UserUtils.nowLoginUser();
        String tenantId = TenantUtils.getTenantId();
        Integer tenantUserType = sharedFileDao.isTenantAdmin(uapUser.id, tenantId, databaseName);
        if (tenantUserType != null && tenantUserType == 1) {
            return true;
        }
        // todo:role old:获取用户角色列表再根据角色获取权限列表 now：直接获取用户所有权限，用权限name匹配
        List<Permission> authList = UserUtils.getCurrentUserPermissionList();
        //        List<Role> roleList = UserUtils.getCurrentUserRoleList();
        //        List<UapAuthority> authList = roleList.stream()
        //                .map(role -> role.name)
        //                .flatMap(roleId -> {
        //                    List<UapAuthority> authorities = ClientManagementAPI.queryAuthorityListByRoleId(tenantId,
        // roleId);
        //                    return authorities != null ? authorities.stream() : Stream.empty();
        //                })
        //                .collect(Collectors.toList());
        return authList.stream().anyMatch(auth -> "文件管理".equals(auth.name));
    }

    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> addSharedFileInfo(HttpServletRequest request, SharedFileDto dto) throws NoLoginException {
        if (!hasFileManagementPermission(request)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "没有文件管理权限");
        }
        String tenantId = TenantUtils.getTenantId();
        String userId = UserUtils.nowUserId();
        //        String deptId = DeptUtils.getDeptIdByUserId(userId, tenantId);
        String fileId = dto.getFileId();
        String fileName = dto.getFileName();

        SharedFile file = baseMapper.selectFileByName(fileName, userId, tenantId);
        if (file != null) {
            return AppResponse.error("请勿上传同名文件");
        }
        // 检查标签是否存在并去重
        List<Long> uniqueTagIds = new ArrayList<>();
        if (CollectionUtils.isNotEmpty(dto.getTags())) {
            // 去重
            uniqueTagIds = dto.getTags().stream().distinct().collect(Collectors.toList());
            // 查询这些标签是否都存在
            List<SharedFileTag> existingTags = baseMapper.selectTagsByIds(uniqueTagIds, tenantId);
            List<Long> existingTagIds =
                    existingTags.stream().map(SharedFileTag::getTagId).collect(Collectors.toList());
            // 检查是否有不存在的标签
            List<Long> nonExistingTagIds = uniqueTagIds.stream()
                    .filter(tagId -> !existingTagIds.contains(tagId))
                    .collect(Collectors.toList());

            if (CollectionUtils.isNotEmpty(nonExistingTagIds)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "标签不存在: " + nonExistingTagIds);
            }
        } else {
            uniqueTagIds = new ArrayList<>();
        }
        String tagsString = uniqueTagIds.stream().map(String::valueOf).collect(Collectors.joining(","));
        // 构造sharedFile对象
        SharedFile sharedFile = new SharedFile();
        sharedFile.setId(idWorker.nextId());
        sharedFile.setFileId(fileId);
        sharedFile.setFileName(fileName);
        //        sharedFile.setDeptId(deptId);
        sharedFile.setFileType(dto.getFileType());
        sharedFile.setFileIndexStatus(FileIndexStatus.START.getValue());
        sharedFile.setTenantId(TenantUtils.getTenantId());
        sharedFile.setTags(tagsString);
        sharedFile.setUpdaterId(userId);
        sharedFile.setUpdateTime(new Date());
        sharedFile.setCreatorId(userId);
        sharedFile.setCreateTime(new Date());
        sharedFile.setDeleted(0);
        this.save(sharedFile);
        return AppResponse.success("新增成功");
    }

    @Override
    public AppResponse<?> updateSharedFileInfo(HttpServletRequest request, UpdateSharedFileDto dto)
            throws NoLoginException {
        if (!hasFileManagementPermission(request)) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "没有文件管理权限");
        }
        String tenantId = TenantUtils.getTenantId();
        String userId = UserUtils.nowUserId();
        //        String deptId = DeptUtils.getDeptIdByUserId(userId, tenantId);
        String fileId = dto.getFileId();
        String fileName = dto.getFileName();
        SharedFile file = baseMapper.selectFileByName(fileName, userId, tenantId);
        if (file != null) {
            return AppResponse.error("请勿上传同名文件");
        }
        // 检查标签是否存在并去重
        List<Long> uniqueTagIds = new ArrayList<>();
        if (CollectionUtils.isNotEmpty(dto.getTags())) {
            // 去重
            uniqueTagIds = dto.getTags().stream().distinct().collect(Collectors.toList());
            // 查询这些标签是否都存在
            List<SharedFileTag> existingTags = baseMapper.selectTagsByIds(uniqueTagIds, tenantId);
            List<Long> existingTagIds =
                    existingTags.stream().map(SharedFileTag::getTagId).collect(Collectors.toList());
            // 检查是否有不存在的标签
            List<Long> nonExistingTagIds = uniqueTagIds.stream()
                    .filter(tagId -> !existingTagIds.contains(tagId))
                    .collect(Collectors.toList());

            if (CollectionUtils.isNotEmpty(nonExistingTagIds)) {
                return AppResponse.error(ErrorCodeEnum.E_PARAM, "标签不存在: " + nonExistingTagIds);
            }
        } else {
            uniqueTagIds = new ArrayList<>();
        }
        String tagsString = uniqueTagIds.stream().map(String::valueOf).collect(Collectors.joining(","));
        // 构造sharedFile对象
        SharedFile sharedFile = new SharedFile();
        sharedFile.setId(dto.getId());
        sharedFile.setFileId(fileId);
        sharedFile.setFileName(fileName);
        //        sharedFile.setDeptId(deptId);
        sharedFile.setFileType(dto.getFileType());
        sharedFile.setFileIndexStatus(FileIndexStatus.START.getValue());
        sharedFile.setTenantId(TenantUtils.getTenantId());
        sharedFile.setTags(tagsString);
        sharedFile.setUpdaterId(userId);
        sharedFile.setUpdateTime(new Date());
        this.updateById(sharedFile);
        return AppResponse.success("修改成功");
    }
}

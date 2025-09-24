package com.iflytek.rpa.utils;

import com.iflytek.rpa.auth.entity.CustomUserDetails;
import com.iflytek.rpa.auth.service.UserExtendService;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;
import javax.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.MapUtils;
import org.casbin.casdoor.entity.Permission;
import org.casbin.casdoor.entity.Role;
import org.casbin.casdoor.entity.User;
import org.casbin.casdoor.service.AuthService;
import org.casbin.casdoor.service.ResourceService;
import org.casbin.casdoor.service.RoleService;
import org.casbin.casdoor.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.util.CollectionUtils;
import org.springframework.util.StringUtils;

/**
 * @desc: 用户工具类
 * @author: weilai <laiwei3@iflytek.com>
 * @create: 2025/9/11 14:08
 */
@Component
@Slf4j
public class UserUtils {

    @Autowired
    private AuthService authService;

    @Autowired
    private UserService userService;

    @Autowired
    private UserExtendService userExtendService;

    @Autowired
    private ResourceService resourceService;

    @Autowired
    private RoleService roleService;

    // 静态变量，用于在静态方法中访问
    private static UserService staticUserService;
    private static UserExtendService staticUserExtendService;
    private static AuthService staticAuthService;
    private static ResourceService staticResourceService;
    private static RoleService staticRoleService;

    @PostConstruct
    public void init() {
        staticUserService = this.userService;
        staticUserExtendService = this.userExtendService;
        staticAuthService = this.authService;
        staticResourceService = this.resourceService;
        staticRoleService = this.roleService;
    }

    /**
     * 获取当前登录用户ID
     *
     * @return 用户ID
     * @throws NoLoginException 未登录异常
     */
    public static String nowUserId() throws NoLoginException {
        // 从Spring Security上下文获取当前用户
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication != null && authentication.getPrincipal() instanceof CustomUserDetails) {
            CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
            User user = userDetails.getUser();

            if (user != null) {
                return user.id;
            } else {
                throw new NoLoginException("用户信息缺失");
            }
        } else {
            throw new NoLoginException("用户未登录");
        }
    }

    /**
     * 获取当前登录用户信息
     *
     * @return 用户信息
     * @throws NoLoginException 未登录异常
     */
    public static User nowLoginUser() throws NoLoginException {
        // 从Spring Security上下文获取当前用户
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication != null && authentication.getPrincipal() instanceof CustomUserDetails) {
            CustomUserDetails userDetails = (CustomUserDetails) authentication.getPrincipal();
            User user = userDetails.getUser();

            if (user != null) {
                return user;
            } else {
                throw new NoLoginException("用户信息缺失");
            }
        } else {
            throw new NoLoginException("用户未登录");
        }
    }

    /**
     * 根据用户ID获取用户信息
     *
     * @param id 用户ID
     * @return 用户信息
     */
    public static User getUserInfoById(String id) {
        if (Objects.isNull(staticUserExtendService) || Objects.isNull(id)) {
            return null;
        }

        try {
            return staticUserExtendService.getUserById(id);
        } catch (Exception e) {
            log.error("根据用户ID获取用户信息失败: {}", id, e);
            return null;
        }
    }

    /**
     * 根据用户ID获取用户真实姓名
     *
     * @param id 用户ID
     * @return 用户真实姓名
     */
    public static String getRealNameById(String id) {
        User user = getUserInfoById(id);

        if (Objects.isNull(user)) {
            return null;
        }

        return user.displayName;
    }

    /**
     * 根据用户id查询用户名
     *
     * @param id
     * @return
     */
    public static String getLoginNameById(String id) {
        User user = getUserInfoById(id);

        if (Objects.isNull(user)) {
            return null;
        }

        return user.name;
    }

    /**
     * 根据userIdList查用户基本信息列表,最多支持100个id
     *
     * @param userIdList
     * @return
     */
    public static List<User> queryUserPageList(List<String> userIdList) throws IOException {
        if (Objects.isNull(staticUserService) || CollectionUtils.isEmpty(userIdList)) {
            return Collections.emptyList();
        }
        // 限制最多100个ID，去重后组织成Set
        Set<String> limitedUserIds = userIdList.stream().distinct().limit(100).collect(Collectors.toSet());

        List<User> allUsers = staticUserService.getUsers();
        List<User> userPage = allUsers.stream()
                .filter(user -> limitedUserIds.contains(user.id))
                .collect(Collectors.toList());

        return userPage;
    }

    /**
     * 检查当前用户是否已登录
     *
     * @return true如果已登录，false如果未登录
     */
    public static boolean isCurrentUserLogin() {
        try {
            Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
            return authentication != null
                    && authentication.isAuthenticated()
                    && authentication.getPrincipal() instanceof CustomUserDetails;
        } catch (Exception e) {
            log.warn("检查用户登录状态失败", e);
            return false;
        }
    }

    /**
     * 检查登录状态并返回响应 todo 加错误码
     *
     * @return 登录状态响应
     */
    public static AppResponse<?> nowLoginUserResponse() {
        if (isCurrentUserLogin()) {
            return AppResponse.success("用户已登录");
        } else {
            return AppResponse.error(ErrorCodeEnum.E_API, "用户未登录");
        }
    }

    /**
     * 转换成 id ：User的格式
     *
     * @param userList
     * @return
     */
    public static Map<String, User> getUserMap(List<User> userList) {
        if (CollectionUtils.isEmpty(userList)) return MapUtils.EMPTY_SORTED_MAP;

        Map<String, User> userMap = new HashMap<>();
        for (User user : userList) {
            userMap.put(user.id, user);
        }

        return userMap;
    }

    /**
     * 转换成 id ：User的格式
     *
     * @param userList
     * @return
     */
    public static Map<String, String> getUserNameMap(List<User> userList) {
        if (CollectionUtils.isEmpty(userList)) return MapUtils.EMPTY_SORTED_MAP;

        Map<String, String> userMap = new HashMap<>();
        for (User user : userList) {
            userMap.put(user.id, user.name);
        }

        return userMap;
    }

    /**
     * 根据roleid 查role详情(roleId用"name"代替)
     * @param roleName
     * @return 角色
     */
    public static Role queryRoleDetail(String roleName) throws IOException {
        if (Objects.isNull(staticRoleService) || StringUtils.isEmpty(roleName)) {
            return null;
        }
        // /api/get-role   参数是owner/name
        return staticRoleService.getRole(roleName);
    }

    /**
     * 获取当前用户权限列表
     *
     * @return 权限列表
     */
    public static List<Permission> getCurrentUserPermissionList() throws NoLoginException {
        User user = nowLoginUser();

        return user.permissions;
    }

    /**
     * 获取用户角色列表
     *
     * @return 角色列表
     */
    public static List<Role> getCurrentUserRoleList() throws NoLoginException {
        User user = nowLoginUser();

        return user.roles;
    }
}

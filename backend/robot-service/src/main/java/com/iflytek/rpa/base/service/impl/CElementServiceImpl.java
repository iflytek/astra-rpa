package com.iflytek.rpa.base.service.impl;

import static com.iflytek.rpa.base.constants.BaseConstant.*;
import static com.iflytek.rpa.robot.constants.RobotConstant.EDITING;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.iflytek.rpa.base.annotation.RobotVersionAnnotation;
import com.iflytek.rpa.base.dao.CElementDao;
import com.iflytek.rpa.base.dao.CGroupDao;
import com.iflytek.rpa.base.entity.CElement;
import com.iflytek.rpa.base.entity.CGroup;
import com.iflytek.rpa.base.entity.dto.ServerBaseDto;
import com.iflytek.rpa.base.entity.vo.ElementInfoVo;
import com.iflytek.rpa.base.entity.vo.ElementVo;
import com.iflytek.rpa.base.entity.vo.GroupInfoVo;
import com.iflytek.rpa.base.service.CElementService;
import com.iflytek.rpa.robot.dao.RobotDesignDao;
import com.iflytek.rpa.starter.exception.NoLoginException;
import com.iflytek.rpa.starter.utils.response.AppResponse;
import com.iflytek.rpa.starter.utils.response.ErrorCodeEnum;
import com.iflytek.rpa.utils.IdWorker;
import com.iflytek.rpa.utils.UserUtils;
import java.util.*;
import java.util.stream.Collectors;
import javax.annotation.Resource;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;

/**
 * 客户端，元素信息(CElement)表服务实现类
 *
 * @author mjren
 * @since 2024-10-14 17:21:34
 */
@Service("cElementService")
public class CElementServiceImpl extends ServiceImpl<CElementDao, CElement> implements CElementService {
    @Resource
    private CElementDao cElementDao;

    @Resource
    private CGroupDao cGroupDao;

    @Resource
    private RobotDesignDao robotDesignDao;

    @Value("${resource.download.url}")
    private String prefix;

    @Autowired
    private IdWorker idWorker;

    //    @Override
    //    @RobotVersionAnnotation
    //    public AppResponse<?> getElementNameList(BaseDto baseDto) throws NoLoginException {
    //        String userId = UserUtils.nowUserId();
    ////        List<FrontElementDto> result = new ArrayList<>();
    ////        List<CElement> elementList = cElementDao.getElementInfo(baseDto.getRobotId(), baseDto.getRobotVersion(),
    // userId);
    ////        if(CollectionUtil.isEmpty(elementList)){
    ////            return AppResponse.success(result);
    ////        }
    ////        List<FrontElementDto> frontElementDtoList = new ArrayList<>();
    ////        for(CElement element:elementList) {
    ////            FrontElementDto frontElementDto = new FrontElementDto();
    ////            BeanUtils.copyProperties(element, frontElementDto);
    ////            frontElementDto.setName(element.getElementName());
    ////            frontElementDto.setImageUrl(element.getImageId() != null ? prefix + element.getImageId() : null);
    ////            frontElementDto.setParentImageUrl(element.getParentImageId() != null?  prefix +
    // element.getParentImageId() : null);
    ////            frontElementDtoList.add(frontElementDto);
    ////        }
    ////        //根据groupName分组
    ////        Map<String, List<FrontElementDto>> elementMap =
    // frontElementDtoList.stream().collect(Collectors.groupingBy(CElement::getGroupId));
    ////        elementMap.forEach((key, value)->{
    ////            FrontElementDto frontElementDto = new FrontElementDto();
    ////            frontElementDto.setGroupId(key);
    ////            frontElementDto.setName(key);
    ////            frontElementDto.setIcon("");
    ////            frontElementDto.setChild(value);
    ////            result.add(frontElementDto);
    ////        });
    //        return AppResponse.success(true);
    //    }

    @Override
    @RobotVersionAnnotation(clazz = ServerBaseDto.class)
    public AppResponse<?> getElementDetail(ServerBaseDto serverBaseDto) throws NoLoginException {
        CElement cElement = new CElement();
        BeanUtils.copyProperties(serverBaseDto, cElement);
        CElement element = cElementDao.getElementByElementId(cElement);
        if (null == element) {
            return AppResponse.success("");
        }
        ElementVo elementVo = new ElementVo();
        BeanUtils.copyProperties(element, elementVo);
        elementVo.setId(element.getElementId());
        elementVo.setName(element.getElementName());
        elementVo.setImageUrl(StringUtils.isNotBlank(element.getImageId()) ? prefix + element.getImageId() : null);
        elementVo.setParentImageUrl(
                StringUtils.isNotBlank(element.getParentImageId()) ? prefix + element.getParentImageId() : null);
        return AppResponse.success(elementVo);
    }

    @Override
    @RobotVersionAnnotation
    public AppResponse<?> moveElementOrImage(ServerBaseDto serverBaseDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        serverBaseDto.setCreatorId(userId);
        CGroup cGroup = new CGroup();
        BeanUtils.copyProperties(serverBaseDto, cGroup);
        // 查询目标分组是否存在
        CGroup group = cGroupDao.getGroupById(cGroup);
        if (null == group) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM, "目标分组不存在");
        }
        CElement cElement = new CElement();
        BeanUtils.copyProperties(serverBaseDto, cElement);
        cElementDao.updateElement(cElement);
        return AppResponse.success(true);
    }

    @Override
    public AppResponse<?> deleteElementOrImage(ServerBaseDto serverBaseDto) throws NoLoginException {
        if (null == serverBaseDto.getElementId()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "元素id不能为空");
        }
        String userId = UserUtils.nowUserId();
        serverBaseDto.setCreatorId(userId);
        CElement cElement = new CElement();
        BeanUtils.copyProperties(serverBaseDto, cElement);
        cElementDao.deleteElementOrImage(cElement);
        return AppResponse.success(true);
    }

    @Override
    public AppResponse<?> createImageName(ServerBaseDto serverBaseDto) throws NoLoginException {
        String name = createNextName(serverBaseDto, "图像_");
        return AppResponse.success(name);
    }

    private String createNextName(ServerBaseDto serverBaseDto, String elementNameBase) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        serverBaseDto.setCreatorId(userId);
        serverBaseDto.setElementName(elementNameBase);
        CElement cElement = new CElement();
        BeanUtils.copyProperties(serverBaseDto, cElement);
        List<String> getElementNameList = cElementDao.getElementNameList(cElement);
        int elementNameIndex = 1;
        List<Integer> elementNameIndexList = new ArrayList<>();
        for (String elementName : getElementNameList) {
            String[] elementNameSplit = elementName.split(elementNameBase);
            if (elementNameSplit.length == 2 && elementNameSplit[1].matches("^[1-9]\\d*$")) {
                int elementNameNum = Integer.parseInt(elementNameSplit[1]);
                elementNameIndexList.add(elementNameNum);
            }
        }
        Collections.sort(elementNameIndexList);
        for (int i = 0; i < elementNameIndexList.size(); i++) {
            if (elementNameIndexList.get(i) != i + 1) {
                elementNameIndex = i + 1;
                break;
            } else {
                elementNameIndex += 1;
            }
        }
        return elementNameBase + elementNameIndex;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> createElement(ServerBaseDto serverBaseDto) throws NoLoginException {
        if (null == serverBaseDto.getElement()) {
            return AppResponse.error(ErrorCodeEnum.E_PARAM_LOSE, "元素信息不能为空");
        }
        String elementType = serverBaseDto.getElementType();
        if (TYPE_COMMON.equals(elementType)) {
            return createElementByType(serverBaseDto);
        } else if (TYPE_CV.equals(elementType)) {
            if (StringUtils.isBlank(serverBaseDto.getGroupName())) {
                serverBaseDto.setGroupName("默认分组");
            }
            return createElementByType(serverBaseDto);
        }
        return AppResponse.error(ErrorCodeEnum.E_SERVICE, "暂不支持该类型元素");
    }

    public AppResponse<?> createElementByType(ServerBaseDto serverBaseDto) throws NoLoginException {
        String userId = UserUtils.nowUserId();
        String elementId = idWorker.nextId() + "";
        String groupName = serverBaseDto.getGroupName();
        CGroup cGroup = new CGroup();
        cGroup.setGroupName(groupName);
        cGroup.setCreatorId(userId);
        cGroup.setUpdaterId(userId);
        cGroup.setRobotId(serverBaseDto.getRobotId());
        cGroup.setRobotVersion(serverBaseDto.getRobotVersion());
        cGroup.setElementType(serverBaseDto.getElementType());
        String groupId;
        CGroup existGroup = cGroupDao.getGroupByGroupName(cGroup);
        if (null == existGroup) {
            // 创建分组
            groupId = idWorker.nextId() + "";
            cGroup.setGroupId(groupId);
            cGroupDao.insertGroup(cGroup);
        } else {
            groupId = existGroup.getGroupId();
        }
        CElement element = serverBaseDto.getElement();
        String elementName = element.getElementName();
        String[] elementNameSplit = elementName.split("图像_");
        if (elementNameSplit.length == 2 && elementNameSplit[1].matches("^[1-9]\\d*$")) {
            try {
                Integer.parseInt(elementNameSplit[1]);
            } catch (NumberFormatException e) {
                return AppResponse.error(ErrorCodeEnum.E_SERVICE, "图像名称序号过大");
            }
        }
        element.setGroupId(groupId);
        element.setElementId(elementId);
        element.setCreatorId(userId);
        element.setUpdaterId(userId);
        // 判断同一类型下是否重名, 不同类型允许重名
        CElement sameNameElement = cElementDao.getElementSameName(
                element.getRobotId(),
                element.getRobotVersion(),
                element.getElementId(),
                element.getElementName(),
                cGroup.getElementType());
        if (null != sameNameElement) {
            // todo 删除oss图片
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "名称重复，请重新命名");
        }
        cElementDao.insertElement(element);
        Map<String, String> resultMap = new HashMap<>();
        resultMap.put("elementId", elementId);
        resultMap.put("groupId", groupId);
        return AppResponse.success(resultMap);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public AppResponse<?> updateElement(ServerBaseDto serverBaseDto) throws NoLoginException {
        CElement element = serverBaseDto.getElement();
        String userId = UserUtils.nowUserId();
        element.setCreatorId(userId);
        // 获取元素信息
        CElement elementInfo = cElementDao.getElementByElementId(element);
        if (null == elementInfo || null == elementInfo.getGroupId()) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "元素不存在");
        }
        String groupId = elementInfo.getGroupId();
        // 获取分组信息，类型信息
        CGroup cGroup = new CGroup();
        cGroup.setGroupId(groupId);
        cGroup.setRobotId(element.getRobotId());
        cGroup.setRobotVersion(element.getRobotVersion());
        CGroup cGroupInfo = cGroupDao.getGroupById(cGroup);
        if (null == cGroupInfo || null == cGroupInfo.getElementType()) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "分组不存在");
        }
        // 重名校验
        // 判断同一类型下是否重名, 不同类型允许重名
        CElement sameNameElement = cElementDao.getElementSameName(
                element.getRobotId(),
                element.getRobotVersion(),
                element.getElementId(),
                element.getElementName(),
                cGroupInfo.getElementType());
        if (null != sameNameElement) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "名称重复，请重新命名");
        }

        // robotDesign 变成editing状态
        robotDesignDao.updateTransformStatus(userId, serverBaseDto.getRobotId(), null, EDITING);

        cElementDao.updateElement(element);
        return AppResponse.success(true);
    }

    @Override
    public AppResponse<?> copyElement(ServerBaseDto serverBaseDto) throws NoLoginException {
        CElement cElement = new CElement();
        BeanUtils.copyProperties(serverBaseDto, cElement);
        String newElementId = idWorker.nextId() + "";
        CElement oldElement = cElementDao.getElementByElementId(cElement);
        String elementName = oldElement.getElementName();
        if (StringUtils.isBlank(elementName)) {
            return AppResponse.error(ErrorCodeEnum.E_SERVICE, "元素名称不存在");
        }
        String newElementName = createNextName(serverBaseDto, elementName + "_副本");
        cElement.setElementName(newElementName);
        cElementDao.copyElement(cElement, newElementId);
        return AppResponse.success(true);
    }

    @Override
    @RobotVersionAnnotation(clazz = ServerBaseDto.class)
    public AppResponse<?> getAllGroupInfo(ServerBaseDto serverBaseDto) {
        List<GroupInfoVo> result = new ArrayList<>();

        // 查询 group 表，获取所有分组信息
        List<CGroup> groupList = cGroupDao.getGroupByRobotId(
                serverBaseDto.getRobotId(), serverBaseDto.getRobotVersion(), serverBaseDto.getElementType());
        if (CollectionUtils.isEmpty(groupList)) {
            return AppResponse.success(result); // 如果没有分组信息，直接返回空列表
        }

        // 提取所有 groupId
        List<String> groupIds = groupList.stream().map(CGroup::getGroupId).collect(Collectors.toList());

        // 查询 element 表，获取所有分组对应的元素
        CElement cElement = new CElement();
        cElement.setRobotId(serverBaseDto.getRobotId());
        cElement.setRobotVersion(serverBaseDto.getRobotVersion());
        List<CElement> elementList = cElementDao.getElementsByGroupIds(cElement, groupIds);

        // 将 element 按 groupId 分类
        Map<String, List<ElementInfoVo>> elementMap = new HashMap<>();
        for (CElement element : elementList) {
            ElementInfoVo elementInfo = new ElementInfoVo();
            elementInfo.setId(element.getElementId());
            elementInfo.setName(element.getElementName());
            elementInfo.setImageUrl(
                    StringUtils.isNotBlank(element.getImageId()) ? prefix + element.getImageId() : null);
            elementInfo.setParentImageUrl(
                    StringUtils.isNotBlank(element.getParentImageId()) ? prefix + element.getParentImageId() : null);
            elementInfo.setCommonSubType(element.getCommonSubType());
            // 根据 groupId 分组
            List<ElementInfoVo> elementInfoList = elementMap.get(element.getGroupId());
            if (elementInfoList == null) {
                elementInfoList = new ArrayList<>();
            }
            elementInfoList.add(elementInfo);
            elementMap.put(element.getGroupId(), elementInfoList);
        }

        // 构建 GroupInfoDto，并填充
        for (CGroup group : groupList) {
            GroupInfoVo groupInfoVo = new GroupInfoVo();
            groupInfoVo.setId(group.getGroupId());
            groupInfoVo.setName(group.getGroupName());
            groupInfoVo.setElements(elementMap.getOrDefault(group.getGroupId(), new ArrayList<>())); // 如果没有元素，则为空列表
            if (DEFAULT_GROUP.equals(group.getGroupName())) {
                result.add(0, groupInfoVo);
            } else {
                result.add(groupInfoVo);
            }
        }

        // 返回构建结果
        return AppResponse.success(result);
    }
}

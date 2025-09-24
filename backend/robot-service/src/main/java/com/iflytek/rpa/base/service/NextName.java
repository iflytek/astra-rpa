package com.iflytek.rpa.base.service;

import com.iflytek.rpa.base.entity.dto.BaseDto;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * @author mjren
 * @date 2025-03-18 15:29
 * @copyright Copyright (c) 2025 mjren
 */
public abstract class NextName {

    public String createNextName(BaseDto baseDto, String nameBase) {
        List<String> nameList = getNameList(baseDto);
        int nameIndex = 1;
        List<Integer> nameIndexList = new ArrayList<>();
        for (String name : nameList) {
            String[] nameSplit = name.split(nameBase);
            if (nameSplit.length == 2 && nameSplit[1].matches("^[1-9]\\d*$")) {
                int elementNameNum = Integer.parseInt(nameSplit[1]);
                nameIndexList.add(elementNameNum);
            }
        }
        Collections.sort(nameIndexList);
        for (int i = 0; i < nameIndexList.size(); i++) {
            if (nameIndexList.get(i) != i + 1) {
                nameIndex = i + 1;
                break;
            } else {
                nameIndex += 1;
            }
        }
        return nameBase + nameIndex;
    }

    protected abstract List<String> getNameList(BaseDto baseDto);
}

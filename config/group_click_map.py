"""
Group 到 Page Type 映射配置文件
支持可持续扩展的映射规则管理
"""

# 核心映射规则
GROUP_PAGE_MAPPING = {
    # 主要映射规则
    "main_avatar": "videos",
    "wan_produce101": "download",
    
    # 可以继续添加更多映射规则
    # "new_group": "new_page_type",
    # "another_group": "another_page_type",
}

# 反向映射（用于验证和查询）
PAGE_TYPE_GROUP_MAPPING = {v: k for k, v in GROUP_PAGE_MAPPING.items()}

# 映射规则描述
MAPPING_DESCRIPTIONS = {
    "main_avatar": "主要头像账号，对应视频页面",
    "wan_produce101": "万创101相关账号，对应下载页面",
}

def get_page_type_for_group(group_name):
    """
    根据 group 名称获取对应的 page_type
    Args:
        group_name (str): 分组名称
    Returns:
        str: 对应的 page_type，如果没有映射则返回 'other'
    """
    group_name = str(group_name).strip().lower()
    # 优先部分匹配（group 名称包含关键词）
    for group_key, page_type in GROUP_PAGE_MAPPING.items():
        if group_key.strip().lower() in group_name:
            return page_type
    # 再检查完全匹配
    for key in GROUP_PAGE_MAPPING:
        if group_name == key.strip().lower():
            return GROUP_PAGE_MAPPING[key]
    return 'other'

def get_groups_for_page_type(page_type):
    """
    根据 page_type 获取对应的所有 groups
    
    Args:
        page_type (str): 页面类型
    
    Returns:
        list: 对应的 group 列表
    """
    groups = []
    for group, mapped_page_type in GROUP_PAGE_MAPPING.items():
        if mapped_page_type == page_type:
            groups.append(group)
    return groups

def add_mapping_rule(group_name, page_type, description=""):
    """
    添加新的映射规则
    
    Args:
        group_name (str): 分组名称
        page_type (str): 页面类型
        description (str): 规则描述
    """
    GROUP_PAGE_MAPPING[group_name] = page_type
    if description:
        MAPPING_DESCRIPTIONS[group_name] = description
    
    # 更新反向映射
    global PAGE_TYPE_GROUP_MAPPING
    PAGE_TYPE_GROUP_MAPPING = {v: k for k, v in GROUP_PAGE_MAPPING.items()}

def remove_mapping_rule(group_name):
    """
    删除映射规则
    
    Args:
        group_name (str): 要删除的分组名称
    """
    if group_name in GROUP_PAGE_MAPPING:
        del GROUP_PAGE_MAPPING[group_name]
        if group_name in MAPPING_DESCRIPTIONS:
            del MAPPING_DESCRIPTIONS[group_name]
        
        # 更新反向映射
        global PAGE_TYPE_GROUP_MAPPING
        PAGE_TYPE_GROUP_MAPPING = {v: k for k, v in GROUP_PAGE_MAPPING.items()}

def get_all_mappings():
    """
    获取所有映射规则
    
    Returns:
        dict: 包含映射规则和描述的字典
    """
    return {
        'mappings': GROUP_PAGE_MAPPING.copy(),
        'descriptions': MAPPING_DESCRIPTIONS.copy(),
        'reverse_mappings': PAGE_TYPE_GROUP_MAPPING.copy()
    }

def validate_mapping(group_name, page_type):
    """
    验证映射规则是否有效
    
    Args:
        group_name (str): 分组名称
        page_type (str): 页面类型
    
    Returns:
        bool: 是否有效
    """
    # 这里可以添加验证逻辑
    # 例如：检查 page_type 是否为有效值
    valid_page_types = ['videos', 'download', 'other']
    return page_type in valid_page_types

# 预定义的页面类型
VALID_PAGE_TYPES = ['videos', 'download', 'other']

# 映射统计信息
def get_mapping_statistics():
    """
    获取映射统计信息
    
    Returns:
        dict: 统计信息
    """
    return {
        'total_mappings': len(GROUP_PAGE_MAPPING),
        'page_types': list(set(GROUP_PAGE_MAPPING.values())),
        'groups': list(GROUP_PAGE_MAPPING.keys())
    } 
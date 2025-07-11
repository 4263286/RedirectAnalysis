# config/link_group_mapping.py

# 链接到分组的映射配置
LINK_GROUP_MAPPING = {
    'https://insnap.ai/videos': 'yujie_main_avatar',
    'https://insnap.ai/zh/download': 'wan_produce101',
    'https://insnap.ai/influencers': 'influencer_group',
    'https://insnap.ai/': 'main_page',
    'https://insnap.ai/fr/': 'french_content',
    'https://insnap.ai/es/': 'spanish_content',
    'https://insnap.ai/de/': 'german_content'
}

# 页面类型到分组的映射
PAGE_TYPE_GROUP_MAPPING = {
    'video_detail': 'video_content',
    'influencers': 'influencer_group',
    'main_page': 'main_page',
    'download': 'download_content'
}

def get_group_by_link(url: str) -> str:
    """
    根据链接获取对应的分组
    
    Args:
        url (str): 链接URL
    
    Returns:
        str: 分组名称，如果没有匹配则返回 'unknown'
    """
    for link_pattern, group in LINK_GROUP_MAPPING.items():
        if link_pattern in url:
            return group
    return 'unknown'

def get_group_by_page_type(page_type: str) -> str:
    """
    根据页面类型获取对应的分组
    
    Args:
        page_type (str): 页面类型
    
    Returns:
        str: 分组名称，如果没有匹配则返回 'unknown'
    """
    return PAGE_TYPE_GROUP_MAPPING.get(page_type, 'unknown')

def get_all_mappings() -> dict:
    """
    获取所有映射配置
    
    Returns:
        dict: 包含所有映射的字典
    """
    return {
        'link_mappings': LINK_GROUP_MAPPING,
        'page_type_mappings': PAGE_TYPE_GROUP_MAPPING
    }

def get_mapping_statistics() -> dict:
    """
    获取映射统计信息
    
    Returns:
        dict: 映射统计信息
    """
    return {
        'total_link_mappings': len(LINK_GROUP_MAPPING),
        'total_page_type_mappings': len(PAGE_TYPE_GROUP_MAPPING),
        'unique_groups': len(set(list(LINK_GROUP_MAPPING.values()) + list(PAGE_TYPE_GROUP_MAPPING.values())))
    } 
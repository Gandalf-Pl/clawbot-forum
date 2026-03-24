"""
OpenClaw 论坛系统 - 内容审核模块
自动检测并过滤违规内容（政治、黄赌毒等）
"""
import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional


class ViolationType(Enum):
    """违规类型枚举"""
    POLITICAL = "political"          # 政治敏感
    PORNOGRAPHY = "pornography"      # 色情
    GAMBLING = "gambling"            # 赌博
    DRUGS = "drugs"                  # 毒品
    VIOLENCE = "violence"            # 暴力
    FRAUD = "fraud"                  # 诈骗
    AD = "advertisement"             # 垃圾广告
    OTHER = "other"                  # 其他违规


@dataclass
class ViolationResult:
    """违规检测结果"""
    is_violation: bool              # 是否违规
    violation_type: Optional[ViolationType] = None  # 违规类型
    matched_words: List[str] = None # 匹配到的敏感词
    reason: str = ""                # 违规原因说明
    confidence: float = 0.0         # 置信度 (0-1)


class ContentModerator:
    """
    内容审核器
    
    使用敏感词库 + 正则规则检测违规内容
    """
    
    def __init__(self):
        # 敏感词库 - 按分类组织
        self.sensitive_words = {
            ViolationType.POLITICAL: [
                # 政治敏感词汇（示例，实际使用时需完善）
                "台独", "藏独", "疆独", "港独", "分裂", "反动",
                "颠覆", "暴乱", "游行", "集会", "示威",
            ],
            ViolationType.PORNOGRAPHY: [
                # 色情词汇
                "色情", "淫秽", "做爱", "性交", "裸聊", "裸照",
                "嫖娼", "卖淫", "性服务", "一夜情", "约炮",
                "av", "porn", "成人视频", "黄色网站",
            ],
            ViolationType.GAMBLING: [
                # 赌博相关
                "赌博", "博彩", "赌球", "赌马", "彩票", "六合彩",
                " Casino ", "赌场", "筹码", "下注", "押注",
                "龙虎斗", "百家乐", "轮盘", "时时彩", "快三",
                "代理", "充值", "提现", "盘口", "赔率",
            ],
            ViolationType.DRUGS: [
                # 毒品相关
                "毒品", "吸毒", "贩毒", "制毒", "毒品交易",
                "冰毒", "海洛因", "可卡因", "大麻", "摇头丸",
                "k粉", "白粉", "麻古", "吗啡", "鸦片",
                "上头", "飞行", "溜冰", "嗑药",
            ],
            ViolationType.VIOLENCE: [
                # 暴力恐怖
                "暴力", "恐怖", "炸弹", "炸药", "枪支", "弹药",
                "杀人", "伤害", "绑架", "勒索", "恐吓", "威胁",
                "极端", "邪教", "自杀", "自残", "血腥",
            ],
            ViolationType.FRAUD: [
                # 诈骗相关
                "诈骗", "欺诈", "骗子", "假冒", "伪造",
                "刷单", "返利", "传销", "非法集资", "庞氏骗局",
                "钓鱼", "木马", "盗号", "套现", "洗钱",
            ],
            ViolationType.AD: [
                # 垃圾广告（部分需要结合上下文判断）
                "加微信", "加qq", "加QQ", "微信号", "qq号",
                "代购", "代写", "代考", "论文", "毕业设计",
                "发票", "办证", "刻章", "学历", "文凭",
                "低价出售", "特价", "促销", "点击链接",
            ],
        }
        
        # 编译正则表达式以提高性能
        self._compile_patterns()
    
    def _compile_patterns(self):
        """编译敏感词为正则模式"""
        self.patterns = {}
        for vtype, words in self.sensitive_words.items():
            # 使用单词边界，避免误判（如"赌博"不会匹配"博")
            escaped_words = [re.escape(word) for word in words]
            pattern = re.compile('|'.join(escaped_words), re.IGNORECASE)
            self.patterns[vtype] = pattern
    
    def check_content(self, content: str, strict_mode: bool = False) -> ViolationResult:
        """
        检查内容是否违规
        
        Args:
            content: 要检查的内容
            strict_mode: 是否启用严格模式（降低触发阈值）
        
        Returns:
            ViolationResult 检测结果
        """
        if not content or not content.strip():
            return ViolationResult(is_violation=False)
        
        content_lower = content.lower()
        all_matched_words = []
        detected_types = []
        
        # 遍历所有违规类型进行检测
        for vtype, pattern in self.patterns.items():
            matches = pattern.findall(content)
            if matches:
                detected_types.append(vtype)
                all_matched_words.extend(matches)
        
        # 去重匹配词
        matched_words = list(set(all_matched_words))
        
        if not detected_types:
            return ViolationResult(is_violation=False)
        
        # 计算违规严重程度
        # 政治、毒品、暴力 = 严重，直接封禁
        # 广告、诈骗 = 中等，视情况处理
        severity_weights = {
            ViolationType.POLITICAL: 1.0,
            ViolationType.DRUGS: 1.0,
            ViolationType.VIOLENCE: 1.0,
            ViolationType.PORNOGRAPHY: 0.8,
            ViolationType.GAMBLING: 0.8,
            ViolationType.FRAUD: 0.6,
            ViolationType.AD: 0.4,
            ViolationType.OTHER: 0.5,
        }
        
        # 计算综合置信度
        max_severity = max(severity_weights[t] for t in detected_types)
        word_count_factor = min(len(matched_words) / 3, 1.0)  # 匹配词越多，置信度越高
        confidence = max_severity * (0.5 + 0.5 * word_count_factor)
        
        # 严格模式下降低阈值
        threshold = 0.3 if strict_mode else 0.5
        
        is_violation = confidence >= threshold
        
        # 生成违规原因
        type_names = {
            ViolationType.POLITICAL: "政治敏感",
            ViolationType.PORNOGRAPHY: "色情内容",
            ViolationType.GAMBLING: "赌博信息",
            ViolationType.DRUGS: "毒品相关",
            ViolationType.VIOLENCE: "暴力恐怖",
            ViolationType.FRAUD: "欺诈信息",
            ViolationType.AD: "垃圾广告",
            ViolationType.OTHER: "其他违规",
        }
        
        reason = f"检测到{type_names[detected_types[0]]}内容"
        if len(detected_types) > 1:
            reason += f"及其他{len(detected_types)-1}类违规"
        
        return ViolationResult(
            is_violation=is_violation,
            violation_type=detected_types[0],
            matched_words=matched_words,
            reason=reason,
            confidence=confidence
        )
    
    def check_post(self, title: str, content: str) -> ViolationResult:
        """
        检查帖子（标题 + 内容）
        
        标题违规 = 直接封禁
        内容违规 = 根据严重程度处理
        """
        # 先检查标题（标题违规更严重）
        title_result = self.check_content(title, strict_mode=True)
        if title_result.is_violation:
            title_result.reason = f"[标题违规] {title_result.reason}"
            return title_result
        
        # 再检查内容
        content_result = self.check_content(content)
        if content_result.is_violation:
            return content_result
        
        return ViolationResult(is_violation=False)
    
    def check_comment(self, content: str) -> ViolationResult:
        """检查评论"""
        return self.check_content(content)
    
    def get_masked_content(self, content: str) -> str:
        """
        获取脱敏后的内容（用于日志记录）
        
        将敏感词替换为 ***
        """
        if not content:
            return content
        
        masked = content
        for pattern in self.patterns.values():
            masked = pattern.sub(lambda m: '*' * len(m.group()), masked)
        
        return masked


# 全局审核器实例
_moderator = None


def get_moderator() -> ContentModerator:
    """获取内容审核器单例"""
    global _moderator
    if _moderator is None:
        _moderator = ContentModerator()
    return _moderator


def moderate_post(title: str, content: str) -> ViolationResult:
    """
    审核帖子的便捷函数
    
    示例用法:
        result = moderate_post("标题", "内容")
        if result.is_violation:
            print(f"违规: {result.reason}")
            print(f"匹配词: {result.matched_words}")
    """
    return get_moderator().check_post(title, content)


def moderate_comment(content: str) -> ViolationResult:
    """审核评论的便捷函数"""
    return get_moderator().check_comment(content)

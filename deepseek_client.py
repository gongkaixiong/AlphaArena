"""
DeepSeek API 客户端
用于 AI 交易决策
"""

import requests
import json
from typing import Dict, List, Optional
import logging
from datetime import datetime
import pytz


class DeepSeekClient:
    """DeepSeek API 客户端"""

    def __init__(self, api_key: str):
        """
        初始化 DeepSeek 客户端

        Args:
            api_key: DeepSeek API 密钥
        """
        self.api_key = api_key
        self.base_url = "https://zenmux.ai/api/v1"  # ZenMux API 端点
        self.model_name = "deepseek/deepseek-chat"  # ZenMux 模型名称
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)

    def get_trading_session(self) -> Dict:
        """
        获取当前交易时段信息

        Returns:
            Dict: {
                'session': '欧美重叠盘/欧洲盘/美国盘/亚洲盘',
                'volatility': 'high/medium/low',
                'recommendation': '建议/不建议开新仓',
                'beijing_hour': 北京时间小时,
                'utc_hour': UTC时间小时
            }
        """
        try:
            utc_tz = pytz.UTC
            now_utc = datetime.now(utc_tz)
            utc_hour = now_utc.hour

            beijing_tz = pytz.timezone('Asia/Shanghai')
            now_beijing = now_utc.astimezone(beijing_tz)
            beijing_hour = now_beijing.hour

            # 欧美重叠盘：UTC 13:00-17:00（北京21:00-01:00）- 波动最大
            if 13 <= utc_hour < 17:
                return {
                    'session': '欧美重叠盘',
                    'volatility': 'high',
                    'recommendation': '最佳交易时段',
                    'beijing_hour': beijing_hour,
                    'utc_hour': utc_hour,
                    'aggressive_mode': True
                }
            # 欧洲盘：UTC 8:00-13:00（北京16:00-21:00）- 波动较大
            elif 8 <= utc_hour < 13:
                return {
                    'session': '欧洲盘',
                    'volatility': 'medium',
                    'recommendation': '较好交易时段',
                    'beijing_hour': beijing_hour,
                    'utc_hour': utc_hour,
                    'aggressive_mode': True
                }
            # 美国盘：UTC 17:00-22:00（北京01:00-06:00）- 波动较大
            elif 17 <= utc_hour < 22:
                return {
                    'session': '美国盘',
                    'volatility': 'medium',
                    'recommendation': '较好交易时段',
                    'beijing_hour': beijing_hour,
                    'utc_hour': utc_hour,
                    'aggressive_mode': True
                }
            # 亚洲盘：UTC 22:00-8:00（北京06:00-16:00）- 波动小
            else:
                return {
                    'session': '亚洲盘',
                    'volatility': 'low',
                    'recommendation': '不建议开新仓（波动小）',
                    'beijing_hour': beijing_hour,
                    'utc_hour': utc_hour,
                    'aggressive_mode': False
                }
        except Exception as e:
            self.logger.error(f"获取交易时段失败: {e}")
            return {
                'session': '未知',
                'volatility': 'unknown',
                'recommendation': '谨慎交易',
                'beijing_hour': 0,
                'utc_hour': 0,
                'aggressive_mode': False
            }

    def chat_completion(self, messages: List[Dict], model: str = "deepseek/deepseek-chat",
                       temperature: float = 0.7, max_tokens: int = 2000,
                       timeout: int = None, max_retries: int = 2) -> Dict:
        """
        调用 DeepSeek Chat 完成 API（带重试机制）

        Args:
            messages: 对话消息列表
            model: 模型名称
            temperature: 温度参数 (0-2)
            max_tokens: 最大 token 数
            timeout: 超时时间（秒），None则自动根据模型类型设置
            max_retries: 最大重试次数

        Returns:
            API 响应
        """
        # 根据模型类型自动设置超时时间
        if timeout is None:
            timeout = 60   # Chat V3.1模型：1分钟

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        # 重试机制
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    self.logger.warning(f"正在重试... (第{attempt}/{max_retries}次)")

                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=timeout
                )

                response.raise_for_status()
                result = response.json()

                # 记录缓存使用情况（如果API返回了缓存统计）
                if 'usage' in result:
                    usage = result['usage']
                    cache_hit = usage.get('prompt_cache_hit_tokens', 0)
                    cache_miss = usage.get('prompt_cache_miss_tokens', 0)
                    total_prompt = usage.get('prompt_tokens', 0)

                    if cache_hit > 0 or cache_miss > 0:
                        cache_rate = (cache_hit / (cache_hit + cache_miss) * 100) if (cache_hit + cache_miss) > 0 else 0
                        savings = cache_hit * 0.9  # 缓存命中节省90%成本
                        self.logger.info(f"[MONEY] 缓存统计 - 命中率: {cache_rate:.1f}% | "
                                       f"命中: {cache_hit} tokens | 未命中: {cache_miss} tokens | "
                                       f"节省约: {savings:.0f} tokens成本")

                return result

            except requests.exceptions.Timeout as e:
                if attempt < max_retries:
                    self.logger.warning(f"请求超时（{timeout}秒），准备重试...")
                    continue
                else:
                    self.logger.error(f"DeepSeek API 超时失败（已重试{max_retries}次）: {e}")
                    raise

            except Exception as e:
                self.logger.error(f"DeepSeek API 调用失败: {e}")
                raise

    def reasoning_completion(self, messages: List[Dict], max_tokens: int = 4000) -> Dict:
        """
        调用 DeepSeek Chat V3.1 推理模型

        Args:
            messages: 对话消息列表
            max_tokens: 最大 token 数

        Returns:
            API 响应
        """
        try:
            self.logger.info("[AI-THINK] 调用DeepSeek Chat V3.1推理模型 (via ZenMux)...")
            return self.chat_completion(
                messages=messages,
                model="deepseek/deepseek-chat",  # ZenMux 模型名称
                temperature=0.1,  # 使用较低温度提高准确性
                max_tokens=max_tokens
            )
        except Exception as e:
            self.logger.error(f"Chat V3.1模型调用失败: {e}")
            raise

    def analyze_market_and_decide(self, market_data: Dict,
                                  account_info: Dict,
                                  trade_history: List[Dict] = None) -> Dict:
        """
        分析市场并做出交易决策

        Args:
            market_data: 市场数据（价格、指标等）
            account_info: 账户信息（余额、持仓等）
            trade_history: 历史交易记录

        Returns:
            交易决策
        """
        # 构建提示词
        prompt = self._build_trading_prompt(market_data, account_info, trade_history)
        # md文档导入 /prompts/trading_prompt.md
        with open('/prompts/trading_prompt.md', 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()


        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        try:
            # 调用 API
            response = self.chat_completion(messages, temperature=0.3)

            # 提取 AI 的回复
            ai_response = response['choices'][0]['message']['content']

            # 解析 JSON
            decision = self._parse_decision(ai_response)

            return {
                'success': True,
                'decision': decision,
                'raw_response': ai_response
            }

        except Exception as e:
            self.logger.error(f"AI 决策失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def evaluate_position_for_closing(self, position_info: Dict, market_data: Dict, account_info: Dict, roll_tracker=None) -> Dict:
        """
        评估持仓是否应该平仓

        Args:
            position_info: 持仓信息
            market_data: 市场数据
            account_info: 账户信息
            roll_tracker: ROLL状态追踪器

        Returns:
            AI决策 (action: CLOSE 或 HOLD)
        """
        # 获取当前交易时段
        session_info = self.get_trading_session()

        # 获取ROLL状态信息
        symbol = position_info.get('symbol', '')
        roll_count = 0
        original_entry_price = position_info.get('entry_price', 0)

        if roll_tracker:
            roll_count = roll_tracker.get_roll_count(symbol)
            orig_price = roll_tracker.get_original_entry_price(symbol)
            if orig_price is not None:
                original_entry_price = orig_price

        # 构建持仓评估提示词
        prompt = f"""
## [SEARCH] 持仓评估任务

你需要评估当前持仓是否应该平仓。这是一个关键决策，可以保护利润或减少损失。

### [TIMER] 当前交易时段
- **时段**: {session_info['session']} (北京时间{session_info['beijing_hour']}:00)
- **波动性**: {session_info['volatility'].upper()}
- **时段建议**: {session_info['recommendation']}

### [ANALYZE] 持仓信息
- **交易对**: {position_info['symbol']}
- **方向**: {position_info['side']} ({"多单" if position_info['side'] == 'LONG' else "空单"})
- **开仓价**: ${position_info['entry_price']:.2f}
- **当前价**: ${position_info['current_price']:.2f}
- **未实现盈亏**: ${position_info['unrealized_pnl']:+.2f} ({position_info['unrealized_pnl_pct']:+.2f}%)
- **杠杆**: {position_info['leverage']}x
- **持仓时长**: {position_info['holding_time']}
- **名义价值**: ${position_info['notional_value']:.2f}

### [TREND-UP] 当前市场数据
- **RSI(14)**: {market_data.get('rsi', 'N/A')} {'[超卖]' if isinstance(market_data.get('rsi'), (int, float)) and market_data.get('rsi') < 30 else '[超买]' if isinstance(market_data.get('rsi'), (int, float)) and market_data.get('rsi') > 70 else '[中性]'}
- **MACD**: {market_data.get('macd', {}).get('histogram', 'N/A')} ({'看涨' if isinstance(market_data.get('macd', {}).get('histogram'), (int, float)) and market_data.get('macd', {}).get('histogram') > 0 else '看跌' if isinstance(market_data.get('macd', {}).get('histogram'), (int, float)) else 'N/A'})
- **趋势**: {market_data.get('trend', 'N/A')}
- **24h变化**: {market_data.get('price_change_24h', 'N/A')}%

### [ACCOUNT] 账户状态
- **账户余额**: ${account_info.get('balance', 0):.2f}
- **总价值**: ${account_info.get('total_value', 0):.2f}
- **持仓数量**: {account_info.get('positions_count', 0)}

### 🔥 [ROLL] ROLL滚仓状态
- **当前ROLL次数**: {roll_count}/6
- **ROLL状态**: {'✅ 可以继续ROLL' if roll_count < 6 else '⛔ 已达上限，优先止盈'}
- **原始入场价**: ${original_entry_price:.2f} (用于移动止损到盈亏平衡)
- **距离ROLL阈值**: {6.0 if position_info['leverage'] <= 10 else 4.8}% (当前盈利: {position_info['unrealized_pnl_pct']:.2f}%)

📊 **ROLL决策指南**:
- ROLL次数 < 6 且 盈利 ≥ {6.0 if position_info['leverage'] <= 10 else 4.8}% → 优先ROLL加仓
- ROLL次数 = 6 且 盈利 ≥ {6.0 if position_info['leverage'] <= 10 else 4.8}% → 考虑部分止盈
- 盈利 3-6% → 启动移动止损，继续持有等待ROLL

### [TARGET] 评估标准

⚡ **智能止损系统 - 多层级风险判断**:

**🔴 硬止损 (无条件立即平仓)**:
1. 保证金亏损 > 50% (例如: -2% × 25x = -50%保证金)
2. 保证金亏损 > 30% 且持仓 > 2小时
3. 价格突破止损位 > 20%

**🟠 趋势反转止损 (高优先级)**:
1. 多单: 市场转为强下跌趋势 且 亏损 > 10%
2. 空单: 市场转为强上涨趋势 且 亏损 > 10%
3. MACD剧烈反转 且 RSI背离 且 亏损 > 5%

**🟡 技术面恶化止损**:
1. 所有主要技术指标(RSI, MACD, 趋势)全面反向
2. 且持仓 > 1小时
3. 且亏损 > 3%

**[WARNING] 避免过度交易的核心原则**:
- **手续费成本很高**: 每次平仓都有手续费，频繁交易会吞噬利润
- **给予策略发展时间**: 刚开仓的持仓需要时间验证，不要过早平仓
- **持仓时间<1小时**: 除非触发智能止损系统，否则应该继续持有
- **小幅波动是正常的**: 市场有正常波动，不要因为短期小幅亏损就恐慌

**[MONEY] ROLL滚仓优先策略 - 利润最大化！**
核心原则：**浮盈用于ROLL，最终锁定"最大化利润"**

⚠️ **高杠杆阈值自动调整**：
- 当前杠杆{position_info['leverage']}x {'> 10x，所有阈值降低20%' if position_info['leverage'] > 10 else '≤ 10x，使用标准阈值'}

📊 **当前持仓的ROLL阈值**（已根据杠杆调整）：
- 启动移动止损: {3.0 if position_info['leverage'] <= 10 else 2.4}%  {'← 已达到！启动保护' if position_info['unrealized_pnl_pct'] >= (3.0 if position_info['leverage'] <= 10 else 2.4) else ''}
- ROLL滚仓触发: {6.0 if position_info['leverage'] <= 10 else 4.8}%  {'← 已达到！优先ROLL' if position_info['unrealized_pnl_pct'] >= (6.0 if position_info['leverage'] <= 10 else 4.8) else ''}
- ROLL上限后止盈: {8.0 if position_info['leverage'] <= 10 else 6.4}%  {'← 已达到！考虑部分止盈' if position_info['unrealized_pnl_pct'] >= (8.0 if position_info['leverage'] <= 10 else 6.4) else ''}

🔥 **ROLL优先执行逻辑**：
1. 当前盈利 ≥ {3.0 if position_info['leverage'] <= 10 else 2.4}% → **启动移动止损（回撤2%触发）**
   - 保护已有利润，但继续持有
   - 不要平仓，等待ROLL机会

2. 当前盈利 ≥ {6.0 if position_info['leverage'] <= 10 else 4.8}% 且趋势强劲 → **优先执行ROLL**
   - 当前ROLL次数: {roll_count}/6
   - 如果<6次：使用60%浮盈加仓，原仓止损移至盈亏平衡
   - 如果=6次：才考虑部分止盈（减仓30-40%）
   - 不要简单平仓，ROLL > 简单止盈

3. 当前盈利 ≥ {8.0 if position_info['leverage'] <= 10 else 6.4}% 且ROLL=6次 → **部分止盈**
   - 已达ROLL上限，锁定部分利润
   - 减仓50%，剩余仓位继续持有

**[SYSTEM] 利润最大化思维**：
- 盈利3%不要急着平仓 → 启动止损保护，等待6%的ROLL机会
- 盈利6%执行ROLL > 直接平仓 → 最终可能锁定15-20%+
- ROLL已6次才考虑部分止盈 → 确保利润最大化
- **最大化利润才是终极目标！**

**应该平仓的情况 (CLOSE)** - 触发以下任一条件:
1. 🔥 **ROLL达到上限 + 部分止盈**:
   - ROLL次数 = 6次 且 当前盈利 ≥ 调整后的6%阈值 → 考虑部分止盈（减仓30-40%）
   - ROLL次数 = 6次 且 当前盈利 ≥ 调整后的8%阈值 → 部分止盈（减仓50%）
   - ⚠️ 只有ROLL已达上限才考虑平仓，否则优先ROLL

2. [WARNING] **重大止损**: 亏损>1.5%且技术面完全崩溃（RSI背离+MACD剧烈反转+趋势彻底逆转）

3. [LOOP] **极端趋势反转**:
   - 多单: RSI>75且MACD急剧转负，且价格暴跌
   - 空单: RSI<25且MACD急剧转正，且价格暴涨

4. [TIMER] **长期无效**: 持仓>24小时且完全没有盈利迹象

⚠️ **关键提醒**：盈利达到6%且ROLL<6次时，应该ROLL而非平仓！

**应该继续持有的情况 (HOLD)**:
1. ⚡ **刚开仓**: 持仓时间<1小时，无论盈亏，给予充分发展时间
2. [ANALYZE] **小幅波动**: 盈亏在±2%以内且技术面未剧烈变化
3. [TREND-UP] **趋势健康**: 技术指标整体支持持仓方向
4. 💪 **等待ROLL机会**: 当前盈利 3-6%，已启动移动止损，等待达到ROLL阈值
5. 🔥 **未达ROLL上限**: ROLL次数 < 6次，继续等待ROLL机会而非急于平仓

⚠️ **重要提醒**：
- 盈利3-6%时：启动移动止损保护，但继续持有等待ROLL
- ROLL<6次时：优先ROLL而非简单平仓
- 手续费成本不是过早平仓的理由
- 最大化利润才是目标，不要急于锁定小额利润

### ⚡ 核心决策原则（按优先级排序）
1. 🔥 **ROLL滚仓策略 > 简单止盈**
   - 盈利达到ROLL阈值(6%或4.8%)且ROLL<6次 → 优先ROLL而非平仓
   - ROLL能最大化利润，不要急于锁定小额利润
   - 不能用"手续费"、"已有利润"等理由逃避ROLL

2. 🛡️ **移动止损保护 > 固定止损**
   - 盈利≥3%(或2.4%高杠杆)时启动移动止损
   - 移动止损是保护机制，不是平仓信号
   - 继续持有等待ROLL机会

3. 💰 **利润最大化 > 过早止盈**
   - 目标是锁定"最大化利润"而非"早期小额利润"
   - ROLL能让2%利润变成15-20%+
   - 耐心等待ROLL机会比急于平仓更重要

4. [WARNING] **高杠杆阈值调整**
   - >10x杠杆时所有阈值自动降低20%
   - 这是强制调整，不能忽略

5. [OK] **避免过早平仓**
   - 给持仓至少1小时发展时间
   - 不要被小波动吓到

请返回严格的JSON格式，包含叙述性决策说明：
{{
    "action": "CLOSE" | "CLOSE_LONG" | "CLOSE_SHORT" | "HOLD",
    "confidence": 0-100,
    "narrative": "像真实交易员一样用第一人称叙述你对这个持仓的评估。包括：持仓时长、当前盈亏、市场变化、是否继续持有的理由。语气要自然、专业、像是在写持仓日志。150-300字。",
    "close_percentage": 50-100  (可选参数：平仓百分比，默认100%全平，可设置50-99实现分批止盈)
}}

**narrative示例**:
- "持仓仅0.1小时，虽然小幅盈利+0.23%，但30x杠杆风险很高。技术面显示温和下跌趋势支持我的空单方向，且未触发任何止损条件。考虑到手续费成本，我决定继续持有，给这个交易更多发展时间。"
- "账户当前盈利5.2%，我的BTC多单已经持有2小时。虽然RSI进入超买区域(76)，但MACD仍然为正，价格保持在布林带上轨附近。我决定平掉50%锁定利润，剩余50%设置追踪止损继续让利润奔跑。"
- "持仓已经12小时，亏损-3.8%。市场趋势彻底逆转，所有技术指标全面反向，MACD剧烈转负。我决定立即平仓止损，避免更大损失。"

**精确平仓说明**：
- "CLOSE": 平掉所有仓位（多单+空单）
- "CLOSE_LONG": 只平掉多单
- "CLOSE_SHORT": 只平掉空单
- close_percentage: 部分止盈，如设置70表示平掉70%锁定利润，保留30%继续持有

💬 **关键**: narrative要写得像一个真实交易员的持仓评估，展现你的分析、判断和决策过程！"""

        # 从prompts/evaluate_closing.md读取提示词
        with open('prompts/evaluate_closing.md', 'r', encoding='utf-8') as f:
            system_close_prompt = f.read().strip()

        messages = [
            {
                "role": "system",
                "content": system_close_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        try:
            # 调用 API
            response = self.chat_completion(messages, temperature=0.3)

            # 提取 AI 的回复
            ai_response = response['choices'][0]['message']['content']

            # 解析 JSON
            decision = self._parse_decision(ai_response)

            return decision

        except Exception as e:
            self.logger.error(f"持仓评估失败: {e}")
            # 返回保守决策: 继续持有
            return {
                'action': 'HOLD',
                'confidence': 50,
                'narrative': f'AI评估失败，保守选择继续持有: {str(e)}',
                'reasoning': f'AI评估失败，保守选择继续持有: {str(e)}'
            }

    def _build_trading_prompt(self, market_data: Dict,
                             account_info: Dict,
                             trade_history: List[Dict] = None) -> str:
        """构建交易提示词（nof1.ai风格，支持时间序列和完整上下文）"""

        # 获取当前交易时段
        session_info = self.get_trading_session()

        # [NEW] 数据排序警告 - 放在最开头
        prompt = """
⚠️ CRITICAL: ALL OF THE PRICE OR SIGNAL DATA BELOW IS ORDERED: OLDEST → NEWEST

This means:
- First value in array = earliest historical data point
- Last value in array = most recent/current data point
- You can observe trends by comparing values from left to right

═══════════════════════════════════════════════════════════
"""

        # [NEW] 系统运行统计（如果可用）
        runtime_stats = account_info.get('runtime_stats', {})
        if runtime_stats and runtime_stats.get('total_invocations', 0) > 0:
            prompt += f"""
[SYSTEM] 系统运行统计
═══════════════════════════════════════════════════════════
运行时长: {runtime_stats.get('runtime_minutes', 0)} 分钟
AI调用次数: {runtime_stats.get('total_invocations', 0)} 次
启动时间: {runtime_stats.get('start_time', 'N/A')[:19]}
当前时间: {runtime_stats.get('current_time', 'N/A')[:19]}

═══════════════════════════════════════════════════════════
"""

        # 交易时段分析
        prompt += f"""
[TIMER] 交易时段分析
═══════════════════════════════════════════════════════════
当前时段: {session_info['session']} (北京时间{session_info['beijing_hour']}:00)
市场波动性: {session_info['volatility'].upper()}
时段建议: {session_info['recommendation']}
{'🔥 欧美盘波动大，适合激进交易，可设置更高止盈目标(8-15%)' if session_info['aggressive_mode'] else '📊 亚洲盘波动较小，已有盈利建议执行阶梯止盈锁定利润，新开仓可适度保守'}

═══════════════════════════════════════════════════════════
[MARKET] 市场数据 ({market_data.get('symbol', 'N/A')})
═══════════════════════════════════════════════════════════
当前价格: ${market_data.get('current_price', 'N/A')}
24h变化: {market_data.get('price_change_24h', 'N/A')}%
24h成交量: ${market_data.get('volume_24h', 'N/A')}

技术指标:
RSI(14): {market_data.get('rsi', 'N/A')} {'[超卖]' if isinstance(market_data.get('rsi'), (int, float)) and market_data.get('rsi') < 30 else '[超买]' if isinstance(market_data.get('rsi'), (int, float)) and market_data.get('rsi') > 70 else ''}
MACD: {market_data.get('macd', 'N/A')}
布林带: {market_data.get('bollinger_bands', 'N/A')}
均线: SMA20={market_data.get('sma_20', 'N/A')}, SMA50={market_data.get('sma_50', 'N/A')}
ATR: {market_data.get('atr', 'N/A')}

趋势: {market_data.get('trend', 'N/A')}
支撑位: {market_data.get('support_levels', [])}
阻力位: {market_data.get('resistance_levels', [])}
"""

        # [UPGRADED] 日内时间序列 - 优化展示格式
        if 'intraday_series' in market_data and market_data['intraday_series']:
            intraday = market_data['intraday_series']
            mid_prices = intraday.get('mid_prices', [])[-10:]
            ema20_values = intraday.get('ema20_values', [])[-10:]
            macd_values = intraday.get('macd_values', [])[-10:]
            rsi7_values = intraday.get('rsi7_values', [])[-10:]
            rsi14_values = intraday.get('rsi14_values', [])[-10:]
            timestamps = intraday.get('timestamps', [])[-10:]

            prompt += f"""
═══════════════════════════════════════════════════════════
[ANALYZE] 日内时间序列数据 (3分钟K线, 最近10个数据点)
ORDERING: OLDEST → NEWEST (观察从左到右的趋势变化)
═══════════════════════════════════════════════════════════

Timestamps:  {' | '.join([str(t)[-8:] for t in timestamps]) if timestamps else 'N/A'}

Mid Prices:  {' → '.join([f"${p:.2f}" for p in mid_prices]) if mid_prices else 'N/A'}
EMA20:       {' → '.join([f"${v:.2f}" for v in ema20_values]) if ema20_values else 'N/A'}
MACD:        {' → '.join([f"{v:.2f}" for v in macd_values]) if macd_values else 'N/A'}
RSI(7):      {' → '.join([f"{v:.1f}" for v in rsi7_values]) if rsi7_values else 'N/A'}
RSI(14):     {' → '.join([f"{v:.1f}" for v in rsi14_values]) if rsi14_values else 'N/A'}
"""

            # 添加趋势提示
            if mid_prices and len(mid_prices) >= 2:
                price_trend = '上涨📈' if mid_prices[-1] > mid_prices[0] else '下跌📉'
                prompt += f"\n💡 价格趋势: {price_trend} ({mid_prices[0]:.2f} → {mid_prices[-1]:.2f})\n"

            if macd_values and len(macd_values) >= 2:
                macd_trend = '增强' if macd_values[-1] > macd_values[0] else '减弱'
                prompt += f"💡 动量: {macd_trend}\n"

        # [UPGRADED] 4小时级别宏观趋势 - 添加序列数据
        if 'long_term_context_4h' in market_data and market_data['long_term_context_4h']:
            ctx_4h = market_data['long_term_context_4h']
            ema20 = ctx_4h.get('ema20', 0)
            ema50 = ctx_4h.get('ema50', 0)

            prompt += f"""
═══════════════════════════════════════════════════════════
[TREND-UP] 4小时级别宏观趋势（用于判断大趋势方向）
ORDERING: OLDEST → NEWEST
═══════════════════════════════════════════════════════════

当前EMA状态:
- EMA20: ${ema20:.2f}
- EMA50: ${ema50:.2f}
- 位置关系: {'多头排列🟢' if ema20 > ema50 else '空头排列🔴'}

波动性指标:
- ATR(3):  {ctx_4h.get('atr3', 'N/A')} (短期波动)
- ATR(14): {ctx_4h.get('atr14', 'N/A')} (中期波动)

成交量分析:
- 当前: {ctx_4h.get('current_volume', 'N/A')}
- 平均: {ctx_4h.get('average_volume', 'N/A')}
- 状态: {'放量🔊' if ctx_4h.get('current_volume', 0) > ctx_4h.get('average_volume', 1) else '缩量🔇'}
"""

            # 添加序列数据
            macd_series = ctx_4h.get('macd_series', [])[-10:]
            rsi14_series = ctx_4h.get('rsi14_series', [])[-10:]

            if macd_series:
                prompt += f"\n时间序列（最近10个4H K线）:\n"
                prompt += f"MACD:   {' → '.join([f'{v:.2f}' for v in macd_series])}\n"

            if rsi14_series:
                prompt += f"RSI14:  {' → '.join([f'{v:.1f}' for v in rsi14_series])}\n"

        # 合约市场数据
        if 'futures_market' in market_data and market_data['futures_market']:
            futures = market_data['futures_market']
            prompt += f"""
═══════════════════════════════════════════════════════════
[FUTURES] ⚡ 合约市场数据
═══════════════════════════════════════════════════════════
资金费率: {futures.get('funding_rate', 'N/A')}
持仓量: 当前={futures.get('open_interest', {}).get('current', 'N/A')}, 平均={futures.get('open_interest', {}).get('average', 'N/A')}
"""

        # 账户状态
        prompt += f"""
═══════════════════════════════════════════════════════════
[ACCOUNT] 账户状态
═══════════════════════════════════════════════════════════
可用资金: ${account_info.get('balance', 'N/A')}
当前持仓数: {len(account_info.get('positions', []))}
未实现盈亏: ${account_info.get('unrealized_pnl', 'N/A')}
"""

        # [NEW] 清算价监控（如果有持仓）
        positions = account_info.get('positions', [])
        if positions and len(positions) > 0:
            prompt += "\n═══════════════════════════════════════════════════════════\n"
            prompt += "[DANGER] 清算价格监控 - 务必注意风险！\n"
            prompt += "═══════════════════════════════════════════════════════════\n"

            for pos in positions:
                pos_symbol = pos.get('symbol', 'N/A')
                entry_price = float(pos.get('entryPrice', 0))
                leverage = int(pos.get('leverage', 1))
                position_amt = float(pos.get('positionAmt', 0))
                side = 'LONG' if position_amt > 0 else 'SHORT'

                # 获取当前价格
                if pos_symbol == market_data.get('symbol'):
                    current_price = float(market_data.get('current_price', entry_price))
                else:
                    current_price = entry_price  # 如果不是当前分析的symbol，使用入场价

                # 计算清算价
                try:
                    # 导入计算方法
                    maintenance_margin_rate = 0.05
                    if side == 'LONG':
                        liquidation_price = entry_price * (1 - (1 - maintenance_margin_rate) / leverage)
                    else:
                        liquidation_price = entry_price * (1 + (1 - maintenance_margin_rate) / leverage)

                    # 计算距离清算价的百分比
                    if side == 'LONG':
                        distance_pct = ((current_price - liquidation_price) / liquidation_price) * 100
                    else:
                        distance_pct = ((liquidation_price - current_price) / current_price) * 100

                    risk_level = '🔴极危险' if distance_pct < 5 else '🟠高风险' if distance_pct < 10 else '🟡警告' if distance_pct < 20 else '🟢安全'

                    prompt += f"""
持仓: {pos_symbol}
方向: {side} {leverage}x
入场价: ${entry_price:.2f}
当前价: ${current_price:.2f}
清算价: ${liquidation_price:.2f}
距离清算价: {distance_pct:.2f}% {risk_level}
未实现盈亏: ${float(pos.get('unRealizedProfit', 0)):.2f}
"""
                except Exception as e:
                    prompt += f"\n持仓: {pos_symbol} (清算价计算失败: {str(e)})\n"

        # 近期表现
        MIN_TRADES_FOR_WINRATE = 20
        if trade_history and len(trade_history) >= MIN_TRADES_FOR_WINRATE:
            recent_trades = trade_history[-10:]
            wins = sum(1 for t in recent_trades if t.get('pnl', 0) > 0)
            winrate_pct = (wins / len(recent_trades)) * 100
            prompt += f"""
═══════════════════════════════════════════════════════════
[PERFORMANCE] 近期表现
═══════════════════════════════════════════════════════════
最近{len(recent_trades)}笔胜率: {winrate_pct:.1f}% ({wins}胜/{len(recent_trades)-wins}负)
"""
        elif trade_history and len(trade_history) > 0:
            prompt += f"""
═══════════════════════════════════════════════════════════
[PERFORMANCE] 交易状态
═══════════════════════════════════════════════════════════
已完成交易: {len(trade_history)}笔 (数据积累中，暂不显示胜率)
"""

        prompt += "\n请分析并给出决策（JSON格式）。"

        return prompt

    def _parse_decision(self, ai_response: str) -> Dict:
        """
        解析 AI 的决策响应
        支持多种格式：纯JSON、Markdown代码块、混合文本
        """
        try:
            # 方法1: 尝试提取Markdown JSON代码块 ```json ... ```
            if "```json" in ai_response.lower():
                json_start = ai_response.lower().find("```json") + 7
                json_end = ai_response.find("```", json_start)
                if json_end > json_start:
                    json_str = ai_response[json_start:json_end].strip()
                    self.logger.info("[SEARCH] 从Markdown代码块中提取JSON")
                    decision = json.loads(json_str)
                    return self._validate_and_normalize_decision(decision)

            # 方法2: 尝试提取普通代码块 ``` ... ```
            if "```" in ai_response and ai_response.count("```") >= 2:
                first_tick = ai_response.find("```")
                # 跳过可能的语言标记（如```json）
                json_start = ai_response.find("\n", first_tick) + 1
                if json_start <= 0:  # 如果没有换行，就从```后开始
                    json_start = first_tick + 3
                json_end = ai_response.find("```", json_start)
                if json_end > json_start:
                    json_str = ai_response[json_start:json_end].strip()
                    self.logger.info("[SEARCH] 从代码块中提取JSON")
                    decision = json.loads(json_str)
                    return self._validate_and_normalize_decision(decision)

            # 方法3: 尝试提取花括号内容 {...}
            if "{" in ai_response and "}" in ai_response:
                start_idx = ai_response.find('{')
                end_idx = ai_response.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = ai_response[start_idx:end_idx]
                    self.logger.info("[SEARCH] 从花括号中提取JSON")
                    decision = json.loads(json_str)
                    return self._validate_and_normalize_decision(decision)

            # 方法4: 直接解析整个响应
            self.logger.info("[SEARCH] 尝试直接解析整个响应为JSON")
            decision = json.loads(ai_response)
            return self._validate_and_normalize_decision(decision)

        except json.JSONDecodeError as e:
            self.logger.error(f"[ERROR] JSON 解析失败: {e}")
            self.logger.error(f"原始响应: {ai_response[:500]}...")
            error_msg = f'AI 响应格式错误: {str(e)[:100]}'
            return {
                'action': 'HOLD',
                'confidence': 0,
                'narrative': error_msg,
                'reasoning': error_msg,
                'position_size': 0,
                'leverage': 1,
                'stop_loss_pct': 2,
                'take_profit_pct': 4
            }
        except Exception as e:
            self.logger.error(f"[ERROR] 决策解析异常: {e}")
            error_msg = f'决策解析异常: {str(e)[:100]}'
            return {
                'action': 'HOLD',
                'confidence': 0,
                'narrative': error_msg,
                'reasoning': error_msg,
                'position_size': 0,
                'leverage': 1,
                'stop_loss_pct': 2,
                'take_profit_pct': 4
            }

    def _validate_and_normalize_decision(self, decision: Dict) -> Dict:
        """验证并规范化AI决策"""
        # 验证必需字段（narrative和reasoning至少要有一个）
        if 'action' not in decision:
            raise ValueError("缺少必需字段: action")
        if 'confidence' not in decision:
            raise ValueError("缺少必需字段: confidence")

        # 支持 narrative 或 reasoning 字段（兼容两种格式）
        if 'narrative' not in decision and 'reasoning' not in decision:
            raise ValueError("缺少必需字段: narrative 或 reasoning")

        # 兼容性处理：确保两个字段都存在
        if 'narrative' in decision and 'reasoning' not in decision:
            decision['reasoning'] = decision['narrative']
        elif 'reasoning' in decision and 'narrative' not in decision:
            decision['narrative'] = decision['reasoning']

        # 设置默认值
        decision.setdefault('position_size', 5)
        decision.setdefault('leverage', 3)
        decision.setdefault('stop_loss_pct', 2)
        decision.setdefault('take_profit_pct', 4)

        # 限制范围（给DeepSeek更大的自主权）
        decision['position_size'] = max(1, min(100, decision['position_size']))
        decision['leverage'] = max(1, min(30, decision['leverage']))  # 最高30倍杠杆
        decision['stop_loss_pct'] = max(0.5, min(10, decision.get('stop_loss_pct', 2)))
        decision['take_profit_pct'] = max(1, min(20, decision.get('take_profit_pct', 4)))
        decision['confidence'] = max(0, min(100, decision['confidence']))

        return decision

    def analyze_with_reasoning(self, market_data: Dict, account_info: Dict,
                               trade_history: List[Dict] = None) -> Dict:
        """
        使用DeepSeek Chat V3.1进行深度分析和决策
        用于关键决策场景，提供完整的思考过程
        """
        # 构建提示词
        prompt = self._build_trading_prompt(market_data, account_info, trade_history)

        # 添加推理模型特定的指导
        reasoning_guidance = """

[AI-THINK] **DeepSeek Chat V3.1 深度分析模式**

请使用你的推理能力进行多步骤深度思考：
1. **市场状态分析** - 综合所有技术指标判断当前市场状态
2. **趋势确认** - 严格验证趋势方向，避免逆势交易
3. **历史表现回顾** - 分析近期交易胜率，吸取教训
4. **风险收益评估** - 计算潜在盈亏比和风险敞口
5. **决策推导** - 基于以上分析得出最优决策

[WARNING] **重要：返回格式要求**
你可以在推理过程中展示思考链条，但最终**必须**返回一个标准JSON对象。
支持两种格式：

格式1 - 纯JSON（推荐）：
{"action":"OPEN_LONG","confidence":85,"reasoning":"BTC突破关键阻力位","leverage":12,"position_size":35,"stop_loss_pct":1.8,"take_profit_pct":5.5}

格式2 - Markdown代码块：
```json
{"action":"OPEN_LONG","confidence":85,"reasoning":"BTC突破关键阻力位","leverage":12,"position_size":35,"stop_loss_pct":1.8,"take_profit_pct":5.5}
```

🚫 **禁止的格式**（会导致解析失败）：
- 纯文本解释
- Markdown标题 (### ...)
- 表格或列表
"""

        messages = [
            {
                "role": "system",
                "content": """你是华尔街顶级交易员，使用DeepSeek Chat V3.1进行多步骤深度分析。

[TARGET] **终极目标：20U两天内翻10倍 → 200U**

你的优势：
- 深度推理：多步骤分析市场信号
- 市场洞察：感知巨鲸动向、资金费率异常
- 风险把控：一次大亏可以毁掉所有努力
- 复利思维：盈利后立即滚入下一笔

⚔️ **核心原则**
1. **质量>数量** - 只在风口来临时全力一击
2. **趋势跟随>抄底摸顶** - 严格禁止逆势交易！
3. **止损=生命线** - 严格止损，绝不抱侥幸
4. **复利=核武器** - 每次盈利滚入下一笔，指数增长

🚫 **绝对禁止**:
- [ERROR] RSI<35时做多 (超卖可能继续跌)
- [ERROR] RSI>65时做空 (超买可能继续涨)
- [ERROR] MACD<0时做多 (下跌趋势)
- [ERROR] MACD>0时做空 (上涨趋势)
- [ERROR] 价格<SMA50时做多 (中期趋势向下)
- [ERROR] 价格>SMA50时做空 (中期趋势向上)

[OK] **仅在趋势明确时开仓**:
- 做多：价格>SMA20>SMA50 + MACD>0 + RSI(45-65) + 突破近10根K线高点
- 做空：价格<SMA20<SMA50 + MACD<0 + RSI(35-55) + 跌破近10根K线低点

返回格式:
{
    "action": "OPEN_LONG" | "OPEN_SHORT" | "HOLD",
    "confidence": 0-100,
    "reasoning": "决策理由",
    "position_size": 20-50,
    "stop_loss_pct": 1.5-2.5,
    "take_profit_pct": 5-15,
    "leverage": 8-30
}

[WARNING] 这是**开仓决策**，只返回 OPEN_LONG/OPEN_SHORT/HOLD。
[IDEA] 参数完全由你根据市场实时调整！"""
            },
            {
                "role": "user",
                "content": prompt + reasoning_guidance
            }
        ]

        try:
            # 调用推理模型
            response = self.reasoning_completion(messages)

            # 提取推理过程和决策
            ai_response = response["choices"][0]["message"]["content"]

            # 提取reasoning_content（如果有）
            reasoning_content = ""
            if "reasoning_content" in response["choices"][0]["message"]:
                reasoning_content = response["choices"][0]["message"]["reasoning_content"]
                self.logger.info(f"[AI-THINK] 推理过程: {reasoning_content[:200]}...")

            # 解析决策
            decision = self._parse_decision(ai_response)

            return {
                "success": True,
                "decision": decision,
                "raw_response": ai_response,
                "reasoning_content": reasoning_content,
                "model_used": "deepseek/deepseek-chat (via ZenMux)"
            }

        except Exception as e:
            self.logger.error(f"Chat V3.1 决策失败: {e}，回退到普通模型")
            # 如果推理模型失败，回退到普通模型
            return self.analyze_market_and_decide(market_data, account_info, trade_history)


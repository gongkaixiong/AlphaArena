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
        # self.base_url = "https://zenmux.ai/api/v1"  # ZenMux API 端点
        # self.model_name = "deepseek/deepseek-chat"  # ZenMux 模型名称
        # self.model_name_reasoner = "deepseek/deepseek-reasoner"  # ZenMux 模型名称

        self.base_url = "https://api.deepseek.com"
        self.model_name = "deepseek-chat"  # DeepSeek 模型名称
        self.model_name_reasoner = "deepseek-reasoner"

        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)

    def get_trading_session(self) -> Dict:
        """获取当前交易时段信息(仅用于日志记录)"""
        try:
            utc_tz = pytz.UTC
            now_utc = datetime.now(utc_tz)
            utc_hour = now_utc.hour

            beijing_tz = pytz.timezone('Asia/Shanghai')
            now_beijing = now_utc.astimezone(beijing_tz)
            beijing_hour = now_beijing.hour

            # 欧美重叠盘
            if 13 <= utc_hour < 17:
                return {'session': '欧美重叠盘', 'volatility': 'high', 'recommendation': '最佳交易时段', 'aggressive_mode': True, 'beijing_hour': beijing_hour, 'utc_hour': utc_hour}
            # 欧洲盘
            elif 8 <= utc_hour < 13:
                return {'session': '欧洲盘', 'volatility': 'medium', 'recommendation': '较好交易时段', 'aggressive_mode': True, 'beijing_hour': beijing_hour, 'utc_hour': utc_hour}
            # 美国盘
            elif 17 <= utc_hour < 22:
                return {'session': '美国盘', 'volatility': 'medium', 'recommendation': '较好交易时段', 'aggressive_mode': True, 'beijing_hour': beijing_hour, 'utc_hour': utc_hour}
            # 亚洲盘
            else:
                return {'session': '亚洲盘', 'volatility': 'low', 'recommendation': '正常交易时段', 'aggressive_mode': True, 'beijing_hour': beijing_hour, 'utc_hour': utc_hour}
        except Exception as e:
            self.logger.error(f"获取交易时段失败: {e}")
            return {'session': '未知', 'volatility': 'unknown', 'recommendation': '谨慎交易', 'aggressive_mode': False, 'beijing_hour': 0, 'utc_hour': 0}

    def chat_completion(self, messages: List[Dict], model: str ,
                       temperature: float = 0.7, max_tokens: int = 2000) -> Dict:
        """通用聊天完成接口"""
        try:
            print(f"请求内容: messages={messages}")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=180  # 统一增加到180秒
            )
            # self.logger.info(f"请求内容: messages={messages}")
            print(f"回复: response={response.json()}")



            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"API错误: {response.status_code} - {response.text}")
                return {"error": f"API错误: {response.status_code}"}

        except Exception as e:
            self.logger.error(f"API调用异常: {e}")
            return {"error": str(e)}

    def reasoning_completion(self, messages: List[Dict], max_tokens: int = 4000) -> Dict:
        """使用DeepSeek-R1推理模型"""
        return self.chat_completion(
            messages=messages,
            model=self.model_name_reasoner,
            temperature=1.0,
            max_tokens=max_tokens
        )

    def analyze_market_and_decide(self, market_data: Dict,
                                  account_info: Dict,
                                  trade_history: List[Dict] = None) -> Dict:
        """
        分析市场并做出交易决策(带重试机制)
        """
        # 构建提示词
        prompt = self._build_trading_prompt(market_data, account_info, trade_history)
        # md文档导入 /prompts/trading_prompt.md
        with open('./prompts/trading_strategy.md', 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()


        messages = [
            {
                "role": "system",
                "content": """你是专业的加密货币交易员。

## 目标
快速盈利$2,系统自动止盈平仓。

## 策略
60倍高杠杆,快进快出,赚够$2立即平仓。

## 可用操作
- OPEN_LONG: 开多
- OPEN_SHORT: 开空
- CLOSE: 平仓
- HOLD: 观望

## 系统自动处理
- 盈利≥$2自动平仓(强制止盈)
- 浮盈滚仓(盈利≥0.8%自动加仓)
- 风险控制和订单执行

## 你的权限
- 完全自主决定所有交易决策
- 自己判断市场、选择杠杆、决定仓位

## 回复格式
JSON,包含: action, confidence(0-100), reasoning, leverage(建议60), position_size(1-100)

现在,基于下面的市场数据做出你的决策"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # 重试最多2次
        for attempt in range(2):
            try:
                self.logger.info(f"API调用尝试 {attempt + 1}/2...")
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 2000
                    },
                    timeout=180  # 增加到180秒
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']

                    # 解析AI返回
                    decision = self._parse_decision(content)
                    self.logger.info(f"✅ API调用成功 (尝试{attempt + 1})")
                    return {
                        'success': True,
                        'decision': decision,
                        'raw_response': content,
                        'model_used': 'deepseek-chat'
                    }
                else:
                    self.logger.error(f"API错误 {response.status_code}: {response.text}")
                    if attempt < 1:  # 如果还有重试机会
                        continue
                    return {
                        'success': False,
                        'error': f"API错误: {response.status_code}"
                    }

            except requests.exceptions.Timeout as e:
                self.logger.error(f"⏰ API超时 (尝试{attempt + 1}/2): {e}")
                if attempt < 1:  # 如果还有重试机会
                    continue
                return {
                    'success': False,
                    'error': 'API超时,请稍后重试'
                }
            except Exception as e:
                self.logger.error(f"❌ API异常 (尝试{attempt + 1}/2): {e}")
                if attempt < 1:
                    continue
                return {
                    'success': False,
                    'error': str(e)
                }

        # 不应该到达这里
        return {
            'success': False,
            'error': '所有重试均失败'
        }

    def evaluate_position_for_closing(self, position_info: Dict, market_data: Dict, account_info: Dict, roll_tracker=None) -> Dict:
        """评估持仓是否应该平仓"""
        
        # 获取ROLL状态信息
        symbol = position_info.get('symbol', '')
        roll_count = 0
        if roll_tracker:
            roll_count = roll_tracker.get_roll_count(symbol)
        
        prompt = f"""当前持有 {position_info['symbol']} {'多单' if position_info['side'] == 'LONG' else '空单'}:
- 入场价: ${position_info['entry_price']}
- 当前价: ${position_info['current_price']}
- 盈亏: {position_info['unrealized_pnl_pct']:+.2f}%
- 杠杆: {position_info['leverage']}x
- 持仓时长: {position_info['holding_time']}
- 滚仓次数: {roll_count}/3

市场数据:
- RSI: {market_data.get('rsi')}
- MACD: {market_data.get('macd', {}).get('histogram', 'N/A')}
- 趋势: {market_data.get('trend')}
- 24h变化: {market_data.get('price_change_24h')}%

系统已配置:
- 盈利≥0.8%自动滚仓(系统处理)
- 最多滚3次

决定: CLOSE平仓 或 HOLD继续持有?"""
        # 从 /prompts/position_evaluation_prompt.md 导入
        with open('./prompts/evaluate_closing.md', 'r', encoding='utf-8') as f:
            system_prompt = f.read().strip()
        messages = [
            {
                "role": "system",
                "content": f"""持仓评估任务
你需要评估当前持仓是否应该平仓。这是一个关键决策，可以保护利润或减少损失。
📊 **ROLL决策指南**:
- ROLL次数 < 6 且 盈利 ≥ {6.0 if position_info['leverage'] <= 10 else 4.8}% → 优先ROLL加仓
- ROLL次数 = 6 且 盈利 ≥ {6.0 if position_info['leverage'] <= 10 else 4.8}% → 考虑部分止盈
- 盈利 3-6% → 启动移动止损，继续持有等待ROLL

### 评估标准

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

## 可用操作
- CLOSE: 平仓
- HOLD: 观望

## 系统自动处理
- 盈利≥$2自动平仓(强制止盈)
- 浮盈滚仓(盈利≥0.8%自动加仓)
- 风险控制和订单执行

## 回复格式
JSON格式包含以下字段: 
    - "action": "CLOSE或HOLD"
    - "confidence": 0-100
    - "narrative": "决策说明"

现在,基于下面的市场数据做出你的决策
                """
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        try:
            print(f"请求内容: messages={messages}")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=180  # 统一增加到180秒
            )
            # self.logger.info(f"请求内容: messages={messages}")
            print(f"回复: response={response.json()}")


            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                decision = self._parse_decision(content)
                return decision
            else:
                return {"action": "HOLD", "confidence": 0, "narrative": "API错误"}
        except Exception as e:
            self.logger.error(f"评估持仓异常: {e}")
            return {"action": "HOLD", "confidence": 0, "narrative": f"异常: {str(e)}"}

    def analyze_with_reasoning(self, market_data: Dict, account_info: Dict,
                               trade_history: List[Dict] = None,
                               use_deepthink: bool = False) -> Dict:
        """使用推理模型分析市场"""
        prompt = self._build_trading_prompt(market_data, account_info, trade_history)
        
        messages = [
            {
                "role": "system",
                "content": """你是专业的加密货币交易员。

## 目标
最大化账户收益。

## 可用操作
- OPEN_LONG: 开多
- OPEN_SHORT: 开空  
- CLOSE: 平仓
- HOLD: 观望

## 系统会自动处理
- 浮盈滚仓(盈利≥0.8%自动加仓)
- 风险控制
- 订单执行

## 你的权限
- 完全自主决定所有交易决策
- 自己判断市场、选择杠杆、决定仓位
- 不需要遵守任何规则或建议

## 回复格式
JSON,包含: action, confidence(0-100), reasoning, leverage(1-80), position_size(1-100), stop_loss_pct, take_profit_pct"""
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        try:
            response = self.reasoning_completion(messages, max_tokens=8000)
            
            if 'error' in response:
                return {
                    'success': False,
                    'error': response['error']
                }
            
            content = response['choices'][0]['message']['content']
            decision = self._parse_decision(content)
            
            return {
                'success': True,
                'decision': decision,
                'raw_response': content
            }

        except Exception as e:
            self.logger.error(f"AI 决策失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _build_trading_prompt(self, market_data: Dict,
                             account_info: Dict,
                             trade_history: List[Dict] = None) -> str:
        """构建交易提示词"""

        prompt = f"""
市场数据 ({market_data.get('symbol')}):
- 价格: ${market_data.get('current_price')}
- 24h变化: {market_data.get('price_change_24h')}%
- RSI: {market_data.get('rsi')}
- MACD: {market_data.get('macd')}
- 趋势: {market_data.get('trend')}

账户信息:
- 余额: ${account_info.get('balance', 0)}
- 可用: ${account_info.get('available_balance', 0)}

做出你的交易决策。"""

        return prompt

    def _parse_decision(self, content: str) -> Dict:
        """解析AI返回的决策"""
        try:
            # 尝试直接解析JSON
            import re
            json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
            if json_match:
                decision = json.loads(json_match.group())
                return {
                    "action": decision.get("action", "HOLD"),
                    "confidence": decision.get("confidence", 50),
                    "reasoning": decision.get("reasoning", decision.get("narrative", content[:200])),
                    "leverage": decision.get("leverage", 10),
                    "position_size": decision.get("position_size", 30),
                    "stop_loss_pct": decision.get("stop_loss_pct", 3),
                    "take_profit_pct": decision.get("take_profit_pct", 8),
                    "narrative": decision.get("narrative", decision.get("reasoning", ""))
                }
        except Exception as e:
            self.logger.error(f"解析AI决策失败: {e}")

        # 默认返回
        return {
            "action": "HOLD",
            "confidence": 50,
            "reasoning": content[:200] if content else "无法解析",
            "leverage": 10,
            "position_size": 30,
            "stop_loss_pct": 3,
            "take_profit_pct": 8
        }

# 🏆 Alpha Arena - DeepSeek-V3 Trading Bot

灵感来自 [nof1.ai](https://nof1.ai) 的 Alpha Arena 实验，这是一个使用 DeepSeek-V3 AI 模型驱动的永不停机的加密货币量化交易系统。

## 📖 项目简介

Alpha Arena 是一个完全自主的 AI 交易机器人，它：
- 🤖 使用 **DeepSeek-V3** 进行智能交易决策
- 📊 实时分析市场技术指标（RSI、MACD、布林带等）
- ⚡ 自动执行交易（开多、开空、止损、止盈）
- 📈 追踪性能指标（夏普比率、最大回撤、胜率等）
- 🌐 提供 Web 仪表板实时监控
- 🔄 **永不停机** - 24/7 持续运行

### 与 nof1.ai Alpha Arena 的对比

nof1.ai 的 Alpha Arena 让 6 个 AI 模型（GPT-5、Gemini 2.5、Grok-4、Claude Sonnet 4.5、DeepSeek-V3、Qwen3 Max）各自使用 $10,000 在 Hyperliquid 交易所进行真实交易竞赛。

**我们的系统**：
- 专注于 DeepSeek-V3 模型
- 在 Binance 交易所运行
- 完全开源，可自定义
- 永久运行，持续优化

## 🎯 核心功能

### 1. AI 驱动的交易决策
- 使用 DeepSeek API 分析市场数据
- 基于技术指标和趋势分析做出决策
- 动态调整仓位和杠杆
- 智能止损止盈

### 2. 性能追踪系统
类似 nof1.ai 的 SharpeBench，追踪：
- ✅ 账户价值和收益率
- ✅ 夏普比率（风险调整后收益）
- ✅ 最大回撤
- ✅ 胜率
- ✅ 交易次数和手续费
- ✅ 每日收益

### 3. Web 仪表板
- 实时显示交易表现
- 资金曲线图表
- 交易历史记录
- 自动刷新（每 10 秒）

### 4. 风险管理
- 仓位大小控制
- 自动止损止盈
- 最大回撤保护
- 每日亏损限制

## 🚀 快速开始

### 1. 前置要求

- Python 3.8+
- Binance 账户和 API 密钥
- DeepSeek API 密钥

### 2. 安装依赖

```bash
cd /Volumes/Samsung/AlphaArena
pip3 install -r requirements.txt
```

### 3. 配置

编辑 `.env` 文件：

```bash
# Binance API
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_secret
BINANCE_TESTNET=false

# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key

# 交易配置
INITIAL_CAPITAL=10000
MAX_POSITION_PCT=10
DEFAULT_LEVERAGE=3
TRADING_INTERVAL_SECONDS=300

# 交易对（多个用逗号分隔）
TRADING_SYMBOLS=BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT
```

### 4. 启动机器人

```bash
./start.sh
```

或者直接运行：

```bash
python3 alpha_arena_bot.py
```

### 5. 启动 Web 仪表板（可选）

在另一个终端窗口：

```bash
python3 web_dashboard.py
```

然后访问：http://localhost:5000

## 📊 项目结构

```
AlphaArena/
├── alpha_arena_bot.py          # 主交易机器人
├── deepseek_client.py          # DeepSeek API 客户端
├── ai_trading_engine.py        # AI 交易引擎
├── performance_tracker.py      # 性能追踪系统
├── web_dashboard.py            # Web 仪表板
├── binance_client.py           # Binance API 客户端
├── market_analyzer.py          # 市场分析器
├── risk_manager.py             # 风险管理器
├── .env                        # 配置文件
├── requirements.txt            # Python 依赖
├── start.sh                    # 启动脚本
├── performance_data.json       # 性能数据（自动生成）
├── logs/                       # 日志目录
└── templates/                  # Web 模板
    └── dashboard.html
```

## 🎮 使用说明

### 永不停机运行

系统设计为 24/7 持续运行：

1. **自动重试**：遇到错误自动重试
2. **优雅关闭**：支持 Ctrl+C 优雅退出
3. **数据持久化**：所有交易和性能数据自动保存
4. **日志记录**：详细的日志文件

### 后台运行（推荐）

使用 `screen` 或 `tmux` 在后台运行：

```bash
# 使用 screen
screen -S alpha_arena
./start.sh
# 按 Ctrl+A 然后 D 脱离会话

# 重新连接
screen -r alpha_arena
```

或使用 `nohup`：

```bash
nohup ./start.sh > output.log 2>&1 &
```

### 监控运行状态

```bash
# 查看实时日志
tail -f logs/alpha_arena_*.log

# 查看 Web 仪表板
# 访问 http://localhost:5000
```

## 📈 性能指标说明

### Sharpe Ratio（夏普比率）
- 衡量风险调整后的收益
- > 1.0 = 良好
- > 2.0 = 优秀
- > 3.0 = 卓越

### Max Drawdown（最大回撤）
- 从峰值到谷底的最大跌幅
- 越小越好
- < 10% = 优秀
- < 20% = 良好

### Win Rate（胜率）
- 盈利交易占总交易的百分比
- > 50% = 不错
- > 60% = 良好
- > 70% = 优秀

## ⚠️ 风险警告

**重要提示**：

1. ⚠️ 加密货币交易存在高风险，可能导致资金损失
2. 🧪 建议先在 Binance 测试网测试（设置 `BINANCE_TESTNET=true`）
3. 💰 只投入你能承受损失的资金
4. 📊 定期监控机器人运行状态
5. 🔐 妥善保管 API 密钥，不要分享给他人
6. 🛡️ 建议设置 IP 白名单限制 API 访问

## 🔧 高级配置

### 调整交易频率

在 `.env` 中修改：
```bash
TRADING_INTERVAL_SECONDS=300  # 5分钟
```

### 调整仓位和杠杆

```bash
MAX_POSITION_PCT=5      # 最大单次仓位 5%
DEFAULT_LEVERAGE=2      # 默认杠杆 2x
```

### 修改交易对

```bash
TRADING_SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,ADAUSDT
```

## 📝 更新日志

### v1.0.0 (2025-10-21)
- ✅ 实现 DeepSeek-V3 AI 交易引擎
- ✅ 性能追踪系统（SharpeBench）
- ✅ Web 实时仪表板
- ✅ 永不停机的交易循环
- ✅ 完整的风险管理系统

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- 灵感来自 [nof1.ai](https://nof1.ai) 的 Alpha Arena 实验
- 使用 [DeepSeek](https://www.deepseek.com) API
- 基于 [Binance](https://www.binance.com) 交易所

---

## 📞 联系方式

有问题或建议？欢迎联系！

**祝交易顺利！🚀**



<div class="rounded border border-border bg-surface-elevated p-3 text-black"><p>It has been 7892 minutes since you started trading. The current time is 2025-10-28 00:41:07.445927 and you've been invoked 3114 times. Below, we are providing you with a variety of state data, price data, and predictive signals so you can discover alpha. Below that is your current account information, value, performance, positions, etc.</p>
<p><span class="font-semibold">ALL OF THE PRICE OR SIGNAL DATA BELOW IS ORDERED: OLDEST → NEWEST</span></p>
<p><span class="font-semibold">Timeframes note:</span> Unless stated otherwise in a section title, intraday series are provided at <span class="font-semibold">3‑minute intervals</span>. If a coin uses a different interval, it is explicitly stated in that coin’s section.</p>
<hr>
<h3 class="mb-2 mt-6 text-sm font-semibold text-black dark:text-zinc-400">CURRENT MARKET STATE FOR ALL COINS</h3>
<h3 class="mb-2 mt-6 text-sm font-semibold text-black dark:text-zinc-400">ALL BTC DATA</h3>
<p>current_price = 113975.5, current_ema20 = 114113.214, current_macd = -14.21, current_rsi (7 period) = 32.14</p>
<p>In addition, here is the latest BTC open interest and funding rate for perps (the instrument you are trading):</p>
<p>Open Interest: Latest: 30025.08  Average: 30037.03</p>
<p>Funding Rate: 1.25e-05</p>
<p><span class="font-semibold">Intraday series (by minute, oldest → latest):</span></p>
<p>Mid prices: [114050.0, 114084.5, 114164.5, 114204.5, 114330.0, 114259.0, 114179.0, 114050.5, 114033.5, 113975.5]</p>
<p>EMA indicators (20‑period): [114098.352, 114097.556, 114106.361, 114120.326, 114138.486, 114149.106, 114146.81, 114136.447, 114126.5, 114113.214]</p>
<p>MACD indicators: [-34.468, -30.055, -18.278, -3.817, 12.183, 19.714, 15.418, 4.936, -3.811, -14.21]</p>
<p>RSI indicators (7‑Period): [40.826, 51.624, 66.93, 73.169, 77.69, 64.379, 45.672, 36.953, 36.394, 32.14]</p>
<p>RSI indicators (14‑Period): [41.101, 45.582, 53.81, 58.108, 61.646, 56.264, 47.175, 42.08, 41.745, 39.224]</p>
<p><span class="font-semibold">Longer‑term context (4‑hour timeframe):</span></p>
<p>20‑Period EMA: 113208.275 vs. 50‑Period EMA: 111762.51</p>
<p>3‑Period ATR: 487.121 vs. 14‑Period ATR: 590.801</p>
<p>Current Volume: 51.791 vs. Average Volume: 4697.763</p>
<p>MACD indicators: [769.48, 889.972, 961.709, 1082.258, 1206.811, 1325.662, 1391.865, 1399.553, 1374.151, 1277.883]</p>
<p>RSI indicators (14‑Period): [68.763, 69.947, 68.424, 72.327, 74.258, 75.761, 74.188, 70.412, 68.365, 60.885]</p>
<hr>
<h3 class="mb-2 mt-6 text-sm font-semibold text-black dark:text-zinc-400">ALL ETH DATA</h3>
<p>current_price = 4112.85, current_ema20 = 4120.388, current_macd = -0.357, current_rsi (7 period) = 33.551</p>
<p>In addition, here is the latest ETH open interest and funding rate for perps:</p>
<p>Open Interest: Latest: 522343.0  Average: 522840.44</p>
<p>Funding Rate: 1.25e-05</p>
<p><span class="font-semibold">Intraday series (3‑minute intervals, oldest → latest):</span></p>
<p>Mid prices: [4119.65, 4119.5, 4125.15, 4127.1, 4131.05, 4127.2, 4124.15, 4116.55, 4116.45, 4112.85]</p>
<p>EMA indicators (20‑period): [4119.312, 4119.33, 4119.975, 4120.91, 4121.69, 4122.186, 4122.131, 4121.49, 4121.081, 4120.388]</p>
<p>MACD indicators: [-1.241, -1.002, -0.277, 0.589, 1.205, 1.499, 1.289, 0.615, 0.224, -0.357]</p>
<p>RSI indicators (7‑Period): [52.7, 52.7, 69.161, 74.879, 71.935, 62.872, 46.43, 34.217, 39.599, 33.551]</p>
<p>RSI indicators (14‑Period): [47.311, 47.311, 55.475, 59.284, 58.268, 55.075, 48.219, 41.683, 44.054, 40.689]</p>
<p><span class="font-semibold">Longer‑term context (4‑hour timeframe):</span></p>
<p>20‑Period EMA: 4064.599 vs. 50‑Period EMA: 4000.995</p>
<p>3‑Period ATR: 38.792 vs. 14‑Period ATR: 37.503</p>
<p>Current Volume: 1256.879 vs. Average Volume: 98952.972</p>
<p>MACD indicators: [21.696, 29.891, 35.278, 46.602, 58.685, 67.108, 69.743, 72.345, 73.536, 68.621]</p>
<p>RSI indicators (14‑Period): [65.949, 67.377, 65.898, 72.841, 75.516, 74.722, 68.136, 69.348, 69.297, 59.446]</p>
<hr>
<h3 class="mb-2 mt-6 text-sm font-semibold text-black dark:text-zinc-400">ALL SOL DATA</h3>
<p>current_price = 199.875, current_ema20 = 199.275, current_macd = 0.389, current_rsi (7 period) = 79.794</p>
<p>In addition, here is the latest SOL open interest and funding rate for perps:</p>
<p>Open Interest: Latest: 3852575.78  Average: 3850329.48</p>
<p>Funding Rate: 1.25e-05</p>
<p><span class="font-semibold">Intraday series (3‑minute intervals, oldest → latest):</span></p>
<p>SOL mid prices: [199.075, 199.245, 199.715, 199.72, 200.025, 199.74, 199.73, 199.495, 199.63, 199.875]</p>
<p>EMA indicators (20‑period): [198.637, 198.695, 198.791, 198.885, 198.969, 199.048, 199.1, 199.144, 199.196, 199.275]</p>
<p>MACD indicators: [0.193, 0.221, 0.276, 0.323, 0.355, 0.378, 0.376, 0.367, 0.367, 0.389]</p>
<p>RSI indicators (7‑Period): [73.441, 76.833, 85.138, 86.167, 85.306, 85.641, 68.375, 65.149, 70.437, 79.794]</p>
<p>RSI indicators (14‑Period): [60.645, 62.792, 69.509, 70.528, 70.212, 70.496, 64.221, 62.951, 65.35, 70.695]</p>
<p><span class="font-semibold">Longer‑term context (4‑hour timeframe):</span></p>
<p>20‑Period EMA: 196.982 vs. 50‑Period EMA: 193.932</p>
<p>3‑Period ATR: 1.233 vs. 14‑Period ATR: 1.91</p>
<p>Current Volume: 6316.3 vs. Average Volume: 785533.901</p>
<p>MACD indicators: [1.836, 2.174, 2.361, 2.556, 3.073, 3.256, 3.186, 3.104, 2.962, 2.742]</p>
<p>RSI indicators (14‑Period): [64.881, 66.771, 64.804, 66.341, 72.934, 66.284, 60.659, 60.853, 59.431, 56.962]</p>
<hr>
<h3 class="mb-2 mt-6 text-sm font-semibold text-black dark:text-zinc-400">ALL BNB DATA</h3>
<p>current_price = 1139.95, current_ema20 = 1139.56, current_macd = 0.803, current_rsi (7 period) = 55.488</p>
<p>In addition, here is the latest BNB open interest and funding rate for perps:</p>
<p>Open Interest: Latest: 76705.87  Average: 76721.72</p>
<p>Funding Rate: 1.25e-05</p>
<p><span class="font-semibold">Intraday series (3‑minute intervals, oldest → latest):</span></p>
<p>BNB mid prices: [1139.25, 1139.85, 1140.5, 1140.4, 1141.85, 1141.25, 1141.3, 1139.2, 1139.5, 1139.95]</p>
<p>EMA indicators (20‑period): [1138.307, 1138.459, 1138.653, 1138.848, 1139.11, 1139.319, 1139.479, 1139.414, 1139.461, 1139.56]</p>
<p>MACD indicators: [0.502, 0.592, 0.705, 0.8, 0.938, 1.011, 1.033, 0.863, 0.808, 0.803]</p>
<p>RSI indicators (7‑Period): [58.513, 60.435, 64.295, 65.6, 71.138, 66.947, 62.641, 40.406, 50.629, 55.488]</p>
<p>RSI indicators (14‑Period): [52.881, 53.867, 55.855, 56.527, 59.516, 58.083, 56.614, 47.191, 51.535, 53.768]</p>
<p><span class="font-semibold">Longer‑term context (4‑hour timeframe):</span></p>
<p>20‑Period EMA: 1133.24 vs. 50‑Period EMA: 1124.495</p>
<p>3‑Period ATR: 12.255 vs. 14‑Period ATR: 12.313</p>
<p>Current Volume: 37.83 vs. Average Volume: 8762.844</p>
<p>MACD indicators: [5.777, 6.581, 6.578, 7.513, 9.062, 10.691, 13.783, 13.17, 12.355, 11.185]</p>
<p>RSI indicators (14‑Period): [60.228, 58.834, 55.384, 59.971, 63.561, 65.478, 71.514, 55.882, 55.057, 53.251]</p>
<hr>
<h3 class="mb-2 mt-6 text-sm font-semibold text-black dark:text-zinc-400">ALL XRP DATA</h3>
<p>current_price = 2.6335, current_ema20 = 2.639, current_macd = 0.001, current_rsi (7 period) = 37.355</p>
<p>In addition, here is the latest XRP open interest and funding rate for perps:</p>
<p>Open Interest: Latest: 53599832.0  Average: 53636095.8</p>
<p>Funding Rate: 6.1243e-06</p>
<p><span class="font-semibold">Intraday series (3‑minute intervals, oldest → latest):</span></p>
<p>XRP mid prices: [2.635, 2.635, 2.639, 2.642, 2.645, 2.646, 2.645, 2.641, 2.64, 2.6335]</p>
<p>EMA indicators (20‑period): [2.636, 2.636, 2.636, 2.637, 2.638, 2.639, 2.639, 2.639, 2.639, 2.639]</p>
<p>MACD indicators: [-0.001, -0.001, -0.0, 0.0, 0.001, 0.001, 0.002, 0.002, 0.001, 0.001]</p>
<p>RSI indicators (7‑Period): [42.865, 47.586, 62.965, 68.044, 69.896, 72.836, 59.667, 51.29, 48.635, 37.355]</p>
<p>RSI indicators (14‑Period): [44.212, 46.41, 54.692, 57.942, 59.156, 61.09, 55.596, 51.718, 50.455, 44.59]</p>
<p><span class="font-semibold">Longer‑term context (4‑hour timeframe):</span></p>
<p>20‑Period EMA: 2.596 vs. 50‑Period EMA: 2.532</p>
<p>3‑Period ATR: 0.024 vs. 14‑Period ATR: 0.022</p>
<p>Current Volume: 18039.0 vs. Average Volume: 8162059.094</p>
<p>MACD indicators: [0.055, 0.057, 0.055, 0.056, 0.055, 0.053, 0.051, 0.052, 0.052, 0.048]</p>
<p>RSI indicators (14‑Period): [77.619, 75.411, 67.82, 71.0, 69.39, 67.792, 66.208, 72.623, 68.846, 61.656]</p>
<hr>
<h3 class="mb-2 mt-6 text-sm font-semibold text-black dark:text-zinc-400">ALL DOGE DATA</h3>
<p>current_price = 0.199985, current_ema20 = 0.2, current_macd = -0.0, current_rsi (7 period) = 26.572</p>
<p>In addition, here is the latest DOGE open interest and funding rate for perps:</p>
<p>Open Interest: Latest: 584616162.0  Average: 584748342.4</p>
<p>Funding Rate: 2.9264e-06</p>
<p><span class="font-semibold">Intraday series (3‑minute intervals, oldest → latest):</span></p>
<p>DOGE mid prices: [0.2, 0.2, 0.201, 0.201, 0.201, 0.201, 0.201, 0.2, 0.2, 0.199985]</p>
<p>EMA indicators (20‑period): [0.2, 0.2, 0.2, 0.201, 0.201, 0.201, 0.201, 0.201, 0.201, 0.2]</p>
<p>MACD indicators: [-0.0, -0.0, -0.0, -0.0, -0.0, 0.0, 0.0, -0.0, -0.0, -0.0]</p>
<p>RSI indicators (7‑Period): [48.083, 52.786, 66.815, 69.461, 70.156, 70.156, 60.756, 31.866, 31.564, 26.572]</p>
<p>RSI indicators (14‑Period): [42.428, 44.604, 52.361, 54.092, 54.536, 54.536, 51.636, 38.76, 38.582, 35.58]</p>
<p><span class="font-semibold">Longer‑term context (4‑hour timeframe):</span></p>
<p>20‑Period EMA: 0.201 vs. 50‑Period EMA: 0.199</p>
<p>3‑Period ATR: 0.002 vs. 14‑Period ATR: 0.002</p>
<p>Current Volume: 273217.0 vs. Average Volume: 80756600.931</p>
<p>MACD indicators: [0.001, 0.001, 0.002, 0.002, 0.002, 0.003, 0.003, 0.003, 0.002, 0.002]</p>
<p>RSI indicators (14‑Period): [63.861, 65.138, 61.289, 67.349, 69.424, 66.629, 58.558, 58.7, 56.779, 51.147]</p>
<h3 class="mb-2 mt-6 text-sm font-semibold text-black dark:text-zinc-400">HERE IS YOUR ACCOUNT INFORMATION &amp; PERFORMANCE</h3>
<p>Current Total Return (percent): 115.8%</p>
<p>Available Cash: 13654.1</p>
<p><span class="font-semibold">Current Account Value:</span> 21580.35</p>
<p>Current live positions &amp; performance:
{'symbol': 'ETH', 'quantity': 5.74, 'entry_price': 4189.12, 'current_price': 4112.85, 'liquidation_price': 3849.46, 'unrealized_pnl': -437.79, 'leverage': 10, 'exit_plan': {'profit_target': 4568.31, 'stop_loss': 4065.43, 'invalidation_condition': 'If the price closes below 4000 on a 3-minute candle'}, 'confidence': 0.65, 'risk_usd': 722.7846, 'sl_oid': 213487996496, 'tp_oid': 213487981580, 'wait_for_fill': False, 'entry_oid': 213487963080, 'notional_usd': 23607.76}
{'symbol': 'SOL', 'quantity': 33.88, 'entry_price': 198.82, 'current_price': 199.875, 'liquidation_price': 183.62, 'unrealized_pnl': 35.74, 'leverage': 10, 'exit_plan': {'profit_target': 215.0, 'stop_loss': 192.86, 'invalidation_condition': 'If the price closes below 190 on a 3-minute candle'}, 'confidence': 0.65, 'risk_usd': 202.07655, 'sl_oid': 213307544465, 'tp_oid': 213307526843, 'wait_for_fill': False, 'entry_oid': 213307507703, 'notional_usd': 6771.77}
{'symbol': 'XRP', 'quantity': 3609.0, 'entry_price': 2.44, 'current_price': 2.6335, 'liquidation_price': 2.26, 'unrealized_pnl': 681.02, 'leverage': 10, 'exit_plan': {'profit_target': 2.815, 'stop_loss': 2.325, 'invalidation_condition': 'If the price closes below 2.30 on a 3-minute candle'}, 'confidence': 0.65, 'risk_usd': 442.032, 'sl_oid': -1, 'tp_oid': -1, 'wait_for_fill': False, 'entry_oid': 211217736949, 'notional_usd': 9504.3}
{'symbol': 'BTC', 'quantity': 0.12, 'entry_price': 107343.0, 'current_price': 113975.5, 'liquidation_price': 98118.53, 'unrealized_pnl': 795.9, 'leverage': 10, 'exit_plan': {'invalidation_condition': 'If the price closes below 105000 on a 3-minute candle', 'profit_target': 118136.15, 'stop_loss': 102026.675}, 'confidence': 0.75, 'risk_usd': 619.2345, 'sl_oid': 206132736980, 'tp_oid': 206132723593, 'wait_for_fill': False, 'entry_oid': 206132712257, 'notional_usd': 13677.06}
{'symbol': 'DOGE', 'quantity': 27858.0, 'entry_price': 0.18, 'current_price': 0.199985, 'liquidation_price': 0.18, 'unrealized_pnl': 429.32, 'leverage': 10, 'exit_plan': {'invalidation_condition': 'If the price closes below 0.180 on a 3-minute candle', 'profit_target': 0.212275, 'stop_loss': 0.175355}, 'confidence': 0.65, 'risk_usd': 257.13, 'sl_oid': -1, 'tp_oid': -1, 'wait_for_fill': False, 'entry_oid': 204672918246, 'notional_usd': 5571.18}
{'symbol': 'BNB', 'quantity': 5.64, 'entry_price': 1140.6, 'current_price': 1139.95, 'liquidation_price': 1081.3, 'unrealized_pnl': -3.67, 'leverage': 10, 'exit_plan': {'profit_target': 1254.29, 'stop_loss': 1083.23, 'invalidation_condition': 'If the price closes below 1080 on a 3-minute candle'}, 'confidence': 0.65, 'risk_usd': 321.61725, 'sl_oid': 213425666937, 'tp_oid': 213425655129, 'wait_for_fill': False, 'entry_oid': 213425641486, 'notional_usd': 6429.32}</p>
<p>Sharpe Ratio: 0.483</p></div>
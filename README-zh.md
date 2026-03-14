# Replicator

[English](./README.md) | [中文](./README-zh.md)

> ⚠️ 开发中，暂不可用于生产环境。

> 给它一个 GitHub 链接，剩下的它来搞定。

Replicator 是一个自主 Agent，能够自动克隆 ML 论文仓库、分析代码、搭建环境、复现实验结果，并持续迭代实验——全程几乎不需要人工干预。

```
输入：GitHub 链接
        ↓
① 克隆仓库，读取 README / requirements / 配置文件
        ↓
② 分析代码架构 → 生成项目介绍、逐文件说明、复现计划
        ↓
③ 搭建环境，安装依赖
        ↓
④ 跑基线实验（原论文配置）
        ↓
⑤ 监控 → 分析结果 → 设计下一组实验
        ↓
        循环
```

## 为什么做这个

复现 ML 论文很痛苦：
- 每个仓库的依赖、CUDA 版本、数据格式各不相同
- README 经常不完整或已过时
- 光搞环境就能花几个小时，还没开始正式工作
- 实验迭代需要不断手动干预

Replicator 把这些都自动化掉。

## 功能进展

- [x] **仓库分析** — 克隆仓库，解析 README、依赖文件、目录结构
- [x] **代码理解** — LLM 生成项目介绍、逐文件说明、复现计划
- [x] **环境搭建** — LLM 读 README，自动执行正确的搭建命令（conda / venv / pip）
- [x] **快速验证** — LLM 生成最小可跑命令（最少数据/步数），向用户收集 API Key 等信息，确认代码跑通后自动终止
- [x] **错误诊断** — 跑失败时 LLM 分析报错并给出修复建议
- [ ] **完整实验提交** — 本地或 SSH 远程运行（支持 `nohup` / `sbatch` / `torchrun`）
- [ ] **任务监控** — 心跳轮询，检测完成或崩溃
- [ ] **结果分析** — 解析日志、指标、loss 曲线
- [ ] **实验设计** — LLM 根据结果建议下一组超参数
- [ ] **迭代循环** — 上一轮跑完自动开始下一轮

## 支持的模型

| 厂商 | 模型 |
|------|------|
| Anthropic | claude-sonnet-4-6 |
| DeepSeek | deepseek-chat |
| 智谱 GLM | glm-4 |
| Kimi（月之暗面） | moonshot-v1-8k |
| MiniMax | MiniMax-M2.5 |
| 任意 OpenAI 兼容 API | 自定义 |

## 快速开始

```sh
git clone https://github.com/fukioston/replicator
cd replicator
pip install -e .

# 运行配置向导（选择 LLM 厂商、填 API Key、设置输出语言）
replicator config

# 创建任务
replicator create -n my-exp --repo https://github.com/karpathy/micrograd

# 运行分析 + 快速验证
replicator run -n my-exp

# 查看所有任务
replicator list

# 查看任务详情
replicator show my-exp
```

配置向导会询问：
- 克隆仓库和实验输出存放位置
- 使用哪个 LLM 厂商和 API Key
- 分析报告的输出语言（中文 / English / 日本語）

## 项目结构

```
replicator/
├── cli.py               # CLI 入口（typer 子命令）
├── replicator.py        # 任务执行器，连接图与 CLI
├── graph.py             # LangGraph 图结构和路由
├── state.py             # ReplicatorState 状态定义
├── setup_config.py      # 交互式配置向导
├── tasks.py             # 任务持久化（tasks.json）
├── nodes/
│   ├── clone_and_read.py      # 克隆仓库 + 读取 README/依赖/目录树
│   ├── identify_key_files.py  # LLM 识别重要文件
│   ├── analyze_code.py        # LLM 生成介绍、逐文件说明、复现计划
│   ├── setup_env.py           # LLM 指导环境搭建（conda/venv/pip）
│   ├── plan_quick_run.py      # LLM 生成最小可跑命令
│   ├── gather_user_inputs.py  # 交互式收集 API Key、数据集路径等
│   ├── execute_quick_run.py   # 执行命令，确认跑通后自动终止
│   └── diagnose_error.py      # LLM 分析报错并给出修复建议
├── remote/
│   ├── base.py          # 抽象执行器接口
│   ├── local.py         # 本地 subprocess 执行器
│   └── ssh.py           # SSH 执行器（paramiko）
└── llm/
    ├── client.py         # 构建 LLM 客户端（Anthropic 或 OpenAI 兼容）
    └── prompts.py        # 系统 prompt 和用户 prompt
```

## 许可证

MIT

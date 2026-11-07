# Pstack for Codex

把 pstack 的 18 个工程工作流打包成一个独立 Codex 插件。安装后在对话中输入 `$`，从技能选择器查找 `PS · <技能名>`。完整调用名形如 `$pstack-codex:how`。

| Skill | 用途与调用示例 | 触发 |
| --- | --- | --- |
| `blast-radius` | `$pstack-codex:blast-radius` 这个响应字段改名会影响哪些消费者？用真实代码验证关键假设。 | 明确的变更影响问题可自动触发 |
| `create-verification-skill` | `$pstack-codex:create-verification-skill` 为本项目的 API 建一个验证 Skill，并跑通一条真实路径。 | 手动 |
| `maintain-verification-skill` | `$pstack-codex:maintain-verification-skill` 审计现有验证 Skill，重跑功能并更新过时步骤。 | 手动 |
| `why` | `$pstack-codex:why` 当初为什么要对 SKU 做大小写归一化？列出历史证据。 | 手动 |
| `benchmark-checklist` | `$pstack-codex:benchmark-checklist` 这组导出基准能支持提速结论吗？ | 明确的基准或提速判断可自动触发 |
| `show-me-your-work` | `$pstack-codex:show-me-your-work` 给这次运行写一份带验证证据的决策日志。 | 手动 |
| `correct` | `$pstack-codex:correct` 针对两次重复的回归，提出可验证的项目内防护。 | 手动 |
| `interrogate` | `$pstack-codex:interrogate` 对抗审查这份 diff，保留能复现的缺陷并报告审查模式。 | 手动 |
| `how` | `$pstack-codex:how` 追踪报价请求到数据查询的调用链，标出各模块的职责。 | 手动 |
| `teach` | `$pstack-codex:teach` 给刚接手项目的人讲清这段逻辑怎么运行、为什么这样设计。 | 手动 |
| `sharpen` | `$pstack-codex:sharpen` 把这条任务描述改得更可验证，保留原有范围。 | 手动 |
| `technical-writing` | `$pstack-codex:technical-writing` 把这段安装说明改成可操作的 how-to。 | 手动 |
| `architect` | `$pstack-codex:architect` 给订单重试设计两种结构，先比较接口和不变量。 | 手动 |
| `reflect` | `$pstack-codex:reflect` 复盘这轮工作中可复用的教训，提出 Skill 修改建议。 | 手动 |
| `statechart` | `$pstack-codex:statechart` 用 TLC 检查这个 TLA+ 模型，把最短反例画成 Mermaid。 | 手动 |
| `arena` | `$pstack-codex:arena` 让独立子代理尝试同一任务，按共同评分标准比较并验证综合结果。 | 手动 |
| `typescript-best-practices` | `$pstack-codex:typescript-best-practices` 检查这个返回类型能否表达非法状态。 | 手动 |
| `unslop` | `$pstack-codex:unslop` 把这段文字改得直接自然，保留原意、语气和事实。 | 手动 |

Matt 的代码审查关注项目规范和需求符合度。Pstack 的 `blast-radius` 追踪下游兼容性，`interrogate` 组织可复现的对抗审查，`why` 追溯仓库中的具体历史决策。两个插件可并装。同名技能用完整调用名区分，例如 `$pstack-codex:teach` 和 `$mattpocock-skills:teach`。

## 安装和卸载

在支持自定义 marketplace 的 Codex CLI 中运行：

```sh
codex plugin marketplace add starlightliu/pstack-codex
codex plugin add pstack-codex@starlightliu-pstack
codex plugin list
```

本地开发时，把第一条命令的仓库地址替换成检出的仓库根目录。在 Codex Desktop 中，可以从这个项目打开 Plugins Directory，选择 **Pstack for Codex** 源并安装插件。也可以先通过 CLI 添加 marketplace，再重启 Desktop 刷新目录。安装后开一个新对话，从 `$` 技能选择器确认插件技能可用。工作区需要允许本地插件。参见 [OpenAI 插件打包和 marketplace 文档](https://developers.openai.com/plugins/build/plugins)。

卸载时用 Desktop 的插件菜单，或运行：

```sh
codex plugin remove pstack-codex@starlightliu-pstack
codex plugin marketplace remove starlightliu-pstack
```

用户项目中已经生成的 `.agents/skills/verify-*/` 由项目自己维护，可继续独立使用。参见 [Codex Skill 发现规则](https://learn.chatgpt.com/docs/build-skills)。

## 升级、回滚和发布

从 Git marketplace 安装的用户可以运行：

```sh
codex plugin marketplace upgrade starlightliu-pstack
codex plugin add pstack-codex@starlightliu-pstack
```

在新对话检查版本和 Skill 列表。回滚时先卸载插件并移除 marketplace，再用 `codex plugin marketplace add starlightliu/pstack-codex --ref <已知可用的标签或提交>` 添加旧版本，重新安装。也可以将旧版本检出到单独目录，从该目录添加本地 marketplace。

从 0.3.0 起，调用名去掉了 `pt-`。将保存的提示词或脚本中的 `$pstack-codex:pt-how` 改成 `$pstack-codex:how`，其他技能同理。选择器显示名仍为 `PS · <技能名>`。

发布时审阅同步差异，更新 [插件 manifest](plugins/pstack-codex/.codex-plugin/plugin.json) 的版本，执行静态检查与受影响的功能验证。提交后推送到 `main`。需要固定发布点时，可在验证过的提交上打与 manifest 一致的标签，再推送该标签。回滚维护提交用 `git revert <同步提交>`，然后重新走验证和发布流程。

## 同步上游

维护工具需要支持 `git merge-tree --write-tree --merge-base` 的 Git，以及 Python 3.10 或更新版本。维护脚本使用 Python 标准库。本次用 Git for Windows 2.41 和 Python 3.12 验证。

```sh
python scripts/sync-upstream.py --check
python scripts/sync-upstream.py --dry-run
python scripts/sync-upstream.py
git diff --cached
```

默认比较上游 HEAD。用 `--to <完整 SHA>` 指定候选提交。正式同步要求已提交且干净的工作树。脚本只映射 [锁文件](upstream-lock.json) 中选定的上游技能目录和许可证，保留项目自己的 Codex 适配。它在临时克隆中比较上游变化、现有适配和合并结果，校验通过后才把整批更新暂存到当前仓库。冲突、上游目录移动、许可证变化和校验失败会中止本次同步。

需要手工合并时，在单独的上游克隆里用 `git diff <锁定 SHA> <候选 SHA> -- pstack/skills/<技能目录>` 检查相应目录。在本仓库的干净分支逐个合并，保留 Codex 的平台适配、显示名和资源引用。将锁文件中的 SHA 和各目录 `files` 更新为新提交的实际清单，再运行静态检查和受影响的功能用例。若上游调整目录或授权，先核对来源和许可，再修改映射。

## 兼容性

- 验证 Skill 生成到项目的 `.agents/skills/verify-<app>/`。保留上游的启动、doctor、真实用户路径、功能地图、证据和清理环节。服务验证要确认监听进程或启动身份，旧服务回 HTTP 200 不能作为通过依据。若当前权限配置保护 `.agents/`，创建和维护需要通过客户端授权写入目标验证 Skill 的目录。参见 [Codex 权限说明](https://learn.chatgpt.com/docs/permissions)。
- `why` 保留七类调查来源和证据分级。GitHub、Linear、Slack 等来源按当前会话的连接和权限取证。缺少子代理时可串行完成，缺少来源时报告覆盖空缺。
- `show-me-your-work` 保留 TSV、Bash 日志脚本和电子表格公式防护，并增加 PowerShell 7 脚本。核对当前对话、明确指定的会话导出和实际产物。跨家族复核取决于会话提供的模型和证据。
- `interrogate` 保留相同输入、独立复现、协调者复跑和按根因合并。上游通过 Cursor 的模型规则调度 Claude、Grok 等模型。Codex 使用当前会话的子代理与已授权模型。完成的审查按实际模型身份标为跨家族、同家族跨模型、同模型或型号未确认。缺少独立 panel 时，仅在范围允许时执行明确标注的单 Agent 兼容检查。实际支持取决于客户端和账号。参见 [Codex 子代理说明](https://learn.chatgpt.com/docs/agent-configuration/subagents)。
- `how`、`teach`、`architect` 和 `arena` 通过插件内的指引互相引用。依赖子代理的步骤使用 Codex 原生工具。没有可核实的跨家族评委时，`arena` 会标明跳过独立评审。
- `reflect` 使用当前会话可见证据或指定会话的授权导出。编辑 Skill 源文件和向外部系统建单需要对应授权。
- `statechart` 保留上游 TLA+、TLC 和 Mermaid 工具链。Windows 可直接用 Node 运行，需配置 Java 和 TLC，或使用上游的 mise 获取路径。需要 SVG 时另用 Pele。参见 [运行与依赖](plugins/pstack-codex/skills/statechart/SKILL.md)。
- 上游独立原则 Skill 的必要步骤已并入对应工作流。对外发 PR、提交规则改动和写全局配置仍须在用户授权范围内。

## 测试

```sh
python scripts/validate-skills.py
python scripts/validate-skills.py --matt-skills /path/to/mattpocock-skills/plugins/mattpocock-skills/skills
python tests/sync.py /path/to/cursor-plugins
python tests/smoke/fixture.py ../catalog-smoke
python tests/smoke/fixture.py ../catalog-regression --regression
```

运行 `tests/sync.py` 前，将上游克隆检出到锁定 SHA。测试构造临时上游镜像，覆盖检查更新、预览、合并资源、保留适配和冲突时保留原工作树。

在健康仓库里先调用 `create-verification-skill` 生成 `verify-catalog`，核对保留的 HTTP 响应证据。然后把 `app.py` 的 `/quote` 路由改为 `/price`，让 `maintain-verification-skill` 更新生成的 Skill，并验证新路径。回归仓库有工作区 diff、记录扫码器兼容性原因的提交、两次重复修复，以及一个只做空工作的基准候选。用其余 6 个 Skill 调用表格中的场景，核对 Git、HTTP、命令输出和日志文件，分别记录真实执行结果和未覆盖项。

初版通过了静态检查、同步回归和 Matt 名称交叉检查。Codex CLI 0.149.0 在隔离配置中完成安装、与 Matt 1.0.24 并装及卸载。Bash 与 PowerShell 日志助手通过了 TSV 写入和公式防护检查。

| 隔离项目用例 | 实际结果 |
| --- | --- |
| `blast-radius` | 分析了工作区 diff。复现大写 SKU 触发 checkout 异常和报价 HTTP 404，用小写输入作对照。 |
| `create-verification-skill` | 独立 Codex 会话生成 `verify-catalog` 和功能地图。新实例通过 launch ID 检查，报价返回 HTTP 200 和金额 125，清理后证据仍在。 |
| `maintain-verification-skill` | 复现旧路径 HTTP 404，更新验证说明和地图，重跑后新路径 HTTP 200，金额 125。产品文件和之前的证据保持原样。 |
| `why` | 从真实 Git 历史找到扫码器发大写 SKU 的提交说明，区分了直接证据与推断。 |
| `benchmark-checklist` | 实跑基准，发现候选返回常量，无法支持提速结论。 |
| `show-me-your-work` | 写出并核对 TSV，将实际 diff、编译检查和计划中的 HTTP 检查分开记录。 |
| `correct` | 找到两次历史回归，比较原规则和实际代码，提出可拒绝旧缺陷的行为检查。 |
| `interrogate` | 两位独立 reviewer 复现了同一缺陷，协调者重新运行并按根因合并。宿主未提供 reviewer 的实际模型身份，结果标为型号未确认的兼容审查。 |

测试通过 Codex CLI 和 App Server 或独立 Codex 会话运行。Desktop 图形界面、真实外部连接器和跨家族模型审查未覆盖。

0.2.0 在隔离的 App Server 配置中发现了全部 17 个 Skill，并调用了本次新增的 9 个。用例覆盖源码调用链、Git 历史讲解、任务改写、技术文档、TypeScript 类型设计、会话复盘和子代理候选比较。可用模型属于同一家族，因此跨家族评审仍未验证。

`statechart` 的 Windows CLI 实测使用 Node 24、Java 25 和 TLC 1.7.4。`Counter` 通过，`MediaPlayer` 找到一条单步反例，两组报告和 Mermaid 图都与上游语料一致。另验证了强制终止后的清理，以及 Pele 1.9.0 的 SVG 渲染。当前受限 App Server 会话会拦截 Node 创建子进程，无法在该权限配置下运行 TLC。

## 来源和许可

上游为 [cursor/plugins 的 pstack 目录](https://github.com/cursor/plugins/tree/6b0300214a09fd6029cfb7077043125758cd1fd2/pstack)，版本 `0.15.36`。该提交的源文件位于仓库顶层 `pstack/`，Claude Code 的生成版位于 `harness/pstack/`。本仓库跟踪前者。来源提交、路径及资源清单见 [upstream-lock.json](upstream-lock.json)。

上游版权所有者为 Lauren Tan，保留原始 [MIT 许可证](LICENSE)。

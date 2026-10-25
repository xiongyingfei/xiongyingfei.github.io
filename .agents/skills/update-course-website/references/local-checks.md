# 本地环境与发布前验证

网站仓库为 `D:/软件分析技术/xiongyingfei.github.io/`，与父课程项目分别管理 Git。先进入本仓库检查 `git status --short`，只暂存本次网站改动。截止与发布规则仍以本仓库根 `AGENTS.md` 为准；仅核查环境、整理入口或维护技能不启动网站发布。

## 已有环境

本机使用 WSL 的 `Ubuntu`：Ruby 3.2.3、Jekyll 3.10.0、Python 3.12 和 PyYAML 6.0.1 已在 2026-10-26 核验。Windows PATH 中没有 Ruby/Jekyll，Docker Desktop 当次未运行；不需要因此重装工具或启动 Docker。环境以后可能变化，先检查实际版本：

```powershell
wsl -d Ubuntu -- bash -lc 'ruby --version; jekyll --version; python3 -c "import yaml; print(yaml.__version__)"'
```

## 完整本地构建

构建必须与源仓库分离，并使用 WSL 原生 `/tmp` 下的目录。`finalize_pages.py` 要保留大小写不同的历史附件别名；在 `/mnt/d` 的大小写不敏感目录运行会出现 `SameFileError`，不能据此修改或删除源附件。

以下命令在父项目根执行。先建立本次 `tmp/<任务名>/`，把控制台输出和核查报告保存到该目录；原生构建路径由末行输出记录。

```powershell
wsl -d Ubuntu -- bash -lc 'bash /mnt/d/软件分析技术/xiongyingfei.github.io/.agents/skills/update-course-website/scripts/check_local.sh'
```

[check_local.sh](../scripts/check_local.sh)自动定位网站根目录，在原生临时目录构建，再运行两项检查；开头打印构建位置。它复制现有保留策略到构建目录，使报告也写入该临时目录，避免在源仓库产生报告或 Python 缓存。`bash -lc` 加载已有 Jekyll 所在的登录环境，脚本文件避免 PowerShell 与 Bash 混用时展开或丢失变量。

这些步骤与 `.github/workflows/pages.yml` 的构建、保留策略及链接检查一致。新增或替换附件还须核对源文件与输出文件的 SHA-256，并核对本次完整题目、截止日期和链接。检查通过只证明本地构建；有适用发布授权时，仍须推送后核对对应提交的 Pages 部署及线上页面、附件。

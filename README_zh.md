# quicksight-codegen

用一条命令从 CSV 文件生成并部署 Amazon QuickSight 仪表板，无需手动配置。

```bash
# 本地预览（不需要 AWS）
quicksight-codegen preview --csv your_data.csv

# 部署到 QuickSight
quicksight-codegen deploy --csv your_data.csv --dataset "your-dataset" --name "My Dashboard"
```

工具会自动分析 CSV 列类型，选择合适的图表（KPI、柱状图、饼图、热力图、表格），添加交互式筛选器，并处理数据类型转换。

## 快速开始

### 1. 安装

```bash
git clone https://github.com/AzerMusic/esg-quicksight-as-code.git
cd esg-quicksight-as-code

# 使用 uv（推荐）
uv venv && uv pip install -e ".[aws,auto]"

# 或使用 pip
python -m venv .venv && source .venv/bin/activate
pip install -e ".[aws,auto]"
```

### 2. 本地预览（不需要 AWS）

```bash
quicksight-codegen preview --csv your_data.csv --name "My Dashboard"
```

生成一个 HTML 文件，用浏览器打开即可看到交互式图表。

### 3. 部署到 AWS QuickSight

**前置条件：**
- 已配置 AWS CLI（`aws configure`）
- AWS 账号已开通 QuickSight
- 已通过 QuickSight 网页控制台上传数据集（"Upload a file"）

**配置环境变量：**

```bash
cp .env.example .env
# 编辑 .env，填入你的 AWS 信息（参见下方"如何找到 AWS 配置值"）
```

**部署：**

```bash
# 查看可用数据集
quicksight-codegen list-datasets

# 部署
quicksight-codegen deploy \
  --csv your_data.csv \
  --dataset "your-dataset-name" \
  --name "My Dashboard"
```

工具会自动：
- 检测 AWS 账号 ID、区域和 QuickSight 用户
- 根据数据生成 KPI、图表、热力图和表格
- 为分类列添加下拉筛选器（Sector、Region 等）
- 创建 `parseDecimal()` 计算字段，使数值列无需手动改类型即可正常显示
- 部署为 QuickSight Analysis，可立即打开使用

## 如何找到 AWS 配置值

| 变量 | 在哪里找 |
|------|---------|
| `AWS_ACCOUNT_ID` | AWS 控制台右上角，或运行 `aws sts get-caller-identity` |
| `AWS_REGION` | QuickSight 所在的区域（如 `eu-central-1`） |
| `QUICKSIGHT_DATASET_ARN` | QuickSight > Datasets > 你的数据集 > Share > Copy ARN |
| `QUICKSIGHT_USER_ARN` | QuickSight > Manage QuickSight > Manage Users > 你的用户 |

如果 AWS CLI 已正确配置，大部分值会**自动检测**。只有自动检测失败时才需要 `.env` 文件。

## CLI 命令

| 命令 | 说明 |
|------|------|
| `quicksight-codegen preview --csv data.csv` | 生成本地 HTML 预览 |
| `quicksight-codegen deploy --csv data.csv --dataset "name" --name "title"` | 生成并部署到 QuickSight |
| `quicksight-codegen list-datasets` | 列出可用的 QuickSight 数据集 |
| `quicksight-codegen fix-types --csv data.csv --dataset "name"` | 修复数据集列类型（仅 SPICE 数据集） |

## 工作原理

```
CSV 文件
  |
  v
列类型分析（数值列 vs 分类列）
  |
  +--> 关键数值列 → KPI 卡片
  +--> 数值 × 分类 → 柱状图 / 饼图
  +--> 数值 × 2个分类 → 热力图
  +--> 所有列 → 数据表格
  +--> 分类列 → 下拉筛选器
  +--> 数值列 → parseDecimal() 计算字段
  |
  v
QuickSight Analysis JSON + HTML 预览
  |
  v
通过 boto3 API 部署
```

**核心特性：自动类型转换。** CSV 上传到 QuickSight 后所有列都是 STRING 类型，图表需要 DECIMAL 类型的数值列。本工具在 Analysis 定义层自动生成 `parseDecimal()` 计算字段，图表部署后直接可用，无需在 QuickSight 控制台手动修改列类型。

## 测试

```bash
uv pip install -e ".[dev]"
uv run pytest
```

## 作者

- Weihua SHI
- Yasmine ZEROUAL
- Adam TOUCHANE
- Saber BERREHILI
- Amine MEGHAGHI

## 许可证

MIT

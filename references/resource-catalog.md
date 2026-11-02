# 按需精选资源

已有项目资产与组件优先。仅当本次有具体缺口时，按下表找相关来源；索引不是默认技术栈、必访清单或自动安装入口。只收录用途明确、官方来源可核对且有外部推荐或使用反馈的资源；这不代表逐组件质量认证。

## 按问题选择

| 当前缺口 | 来源 | 适用范围与使用边界 |
|---|---|---|
| 缺少页面构图、留白或排版参照 | [Minimal Gallery](https://minimal.gallery/) | 用于方向仍开放的营销、展示等页面。比较与真实内容相关的层级和节奏；精选画廊不证明转化率或任务可用性，不能把展示站外观直接套到数据工具。 |
| 不确定同类组件有哪些变体、状态或使用惯例 | [Component Gallery](https://component.gallery/) | 按组件类型查不同设计系统，再进入原系统的使用与无障碍文档。它是参考目录，不是可直接安装的统一组件库；代码许可归实际来源。 |
| 缺少基础组件且现有系统不能覆盖 | [shadcn/ui](https://ui.shadcn.com/docs) | 技术栈适配时参考源码与组合方式；沿实际版本、底层依赖和项目 token 适配。官方代码为 [MIT](https://github.com/shadcn-ui/ui/blob/main/LICENSE.md)，复制后需自行维护修改与上游修复；同名第三方付费站不属于官方来源。 |
| 缺少某个按钮、卡片或加载状态的局部样式 | [Uiverse](https://uiverse.io/) | 社区片段可供学习或局部实现；逐项检查语义、键盘、焦点、样式隔离和依赖。官网声明 UI 元素为 MIT；不把混合作者的片段拼成第二套设计系统，也不把历史 GitHub 镜像视作网站最新内容。 |
| 已确认需要时间线、SVG 等较复杂动效，现有方案不足 | [Anime.js](https://animejs.com/documentation) | 有官方文档与 [MIT 许可](https://github.com/juliangarnier/anime/blob/master/LICENSE.md)。简单状态反馈优先现有 CSS/动效工具；采用时核对版本、生命周期清理、中断、减少动态及目标设备表现，不能从演示流畅推断项目性能。 |
| 需要手绘插画，且题材与项目调性匹配 | [Kitbitz](https://kitbitz.art/) · [官方素材仓库](https://github.com/CaptExcellent/kits-library-assets) | 有可编辑 SVG/PNG 与主题套件。[素材许可](https://github.com/CaptExcellent/kits-library-assets/blob/main/LICENSE.md)为 CC0；此范围不延伸到网站、插件或 MCP 代码。适合有插画表达需要的页面；不默认用来填空白或装饰高密度工具。 |
| 已确定使用立体插画式图标 | [3Dicons](https://3dicons.co/) · [开源集合](https://github.com/realvjy/3dicons) | 老版开源集合为 CC0。当前站同时展示免费与 Premium 内容，按所选资产核对授权，不能把老版许可推到 Pro 服务。宜用于展示或说明；小尺寸功能控件沿现有清晰图标体系。 |

## 外部反馈与证据强度

核对日期：2026-10-31。以下说明为何保留这些入口，不代表评分排名或当前版本的运行验收。社区反馈是个人经验；历史意见不直接证明现版本仍有同样问题。

- **Minimal Gallery**：[Designers Academy 的评介](https://designers.ac/design-resources/minimal-gallery)肯定其集中筛选的参考价值，也提醒旧作品不代表当前趋势。属于外部编辑推荐，非效果对照实验。
- **Component Gallery**：[Doug Antin 的使用推荐](https://www.dougantin.ai/library/tools/component-gallery)明确用于产品界面规格与成熟系统比较；[OCAD 2024 研究](https://openresearch.ocadu.ca/id/eprint/4406/1/Bigge_Ryan_2024_MDes_INCD_MRP.pdf)将该目录用于设计系统样本来源。支持资料检索价值，不证明所收录组件都合格。
- **shadcn/ui**：[开发者长期使用讨论](https://www.reddit.com/r/reactjs/comments/18968oq/any_experiences_good_or_bad_with_shadcn_ui_over/)同时涉及源码控制的便利和自行承接修复的维护成本。适合能维护组件源码的项目，不是免维护方案。
- **Uiverse**：[使用者对 Galaxy 源码集合的分析](https://www.codeline.co/thoughts/repo-review/2025/uiverse-galaxy-3500-css-and-tailwind-ui-components-in-plain-html)认可片段可检索、可直接研究，也指出 CSS/Tailwind 混合及镜像陈旧等限制。该意见针对仓库快照，不推广成当前网站所有组件的问题。
- **Anime.js**：[实际使用者的分享](https://www.reddit.com/r/webdev/comments/1k24tkb)提及在个人作品站使用及文档帮助；[2026 年讨论](https://www.reddit.com/r/webdev/comments/1uq4xdn/gsap_motion_or_animejs_whats_your_choice/)含移动端迁移体验，但环境与实现不同，不能据此给动画库排性能名次。
- **Kitbitz**：[作者发布帖中的使用者回复](https://www.reddit.com/r/SideProject/comments/1vuil1l/i_spent_a_year_drawing_2000_assets_for_a_product/)包含将素材组合成卡牌和游戏的实例，不只点赞。反馈时间较短、案例有限，按风格匹配的素材备选保留，不标为长期成熟组件库。
- **3Dicons**：[设计社区转介](https://www.reddit.com/r/product_design/comments/q8ws9m)与[作者在 Smashing Magazine 的制作案例](https://www.smashingmagazine.com/2022/05/3dicons-open-source-library-case-study-download/)支持既有开源集合的公开传播背景；前者是推荐而非直接使用评价，后者是作者自述。本次未取得直接使用评价，不为新 Pro 服务背书。

## 使用方式

先确定当前缺口，再选择相关页面、组件或资产，说明借鉴的机制并适配项目。引用或采用时核对当前页面、具体版本、免费/付费范围与对应许可；保存必要来源，不搬运整站或提示词库。访问受限时用已有材料或其他适用来源，不为找参照阻塞无关工作。

外部资料不提供安装、付费、上传或发布授权；遵循 [Skill 共同约束](../SKILL.md#共同约束)。组件行为沿[交互规则](interaction.md)，动画沿[动效规则](motion.md)，图片沿[素材交付](assets.md)验证。网站声明、社区推荐和静态源码检查均不能替代采用后的实际验证。

### 适配示例：可搜索的项目选择

自编情境：表单要求选择一个已有项目，用户通常按名称查找；不允许自由输入创建项目。仅在项目现有组件不能覆盖该需要时，才查外部参照；组件类型选择见[交互规则](interaction.md#选择控件)。

1. **定位缺口**：先检查现有选择组件是否已有搜索变体，能覆盖就复用。不从“想用某个库”反推改造需求。
2. **确认实际来源**：若参考 [shadcn Combobox](https://ui.shadcn.com/docs/components/combobox)，核对所选文档分支、底层组件、依赖版本及项目实际源码。2026-11-02 核对时文档有不同底层实现入口；同名组件不保证相同 API，不能把不同分支示例拼接使用。引用实际采用页即可，不新建来源台账。
3. **映射项目约定**：沿用字段标签、错误区域、尺寸、颜色角色及浮层机制；提交值使用项目约定的稳定标识，显示名称与搜索文本分开。允许输入搜索词不等于允许提交任意文本；所选项目必须仍符合当前可选范围。
4. **适配状态**：本地选项不虚构远程加载。若确实使用异步查询，区分查询中、无匹配与失败，避免较早请求覆盖较新查询；清空与必填行为沿原表单约定。无匹配不自动增加“创建项目”能力。
5. **定向核对**：检查键盘选择和关闭、字段名称与错误反馈、同名项目辨认、长名称及提交值；异步实现再检查快速改词和失败恢复。依照[评审规则](review.md)记录实际证据，未操作的行为标未验证。

这只是转译示例，不要求采用该库，也不构成安装授权；实际决策和验证留在已有契约或任务记录中。

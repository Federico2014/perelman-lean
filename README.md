# Perelman Lean Foundations

**局部形式化进行中。这个仓库没有完成佩雷尔曼对庞加莱猜想的证明，也没有证明庞加莱猜想本身。**

本项目使用 Lean 4 / mathlib，形式化佩雷尔曼有限消亡论证中的一部分实分析。
现有定理处理实值函数的衰减、对数比较和有限次向下跳跃；尚未把这些函数与真实的
Ricci 流、极小圆盘面积或手术过程连接起来。`PoincareConjecture` 仅定义目标命题。

## 已完成的形式化

| 文件 | 内容 | 状态 |
| --- | --- | --- |
| [Perelman/Statement.lean](Perelman/Statement.lean) | 紧致、Hausdorff、单连通、无边界三维拓扑流形与标准三维球面同胚的命题 | 定义，未证明 |
| [Perelman/Extinction.lean](Perelman/Extinction.lean) | 前向差商上界推出对数比较估计 | 已证明 |
| 同上 | 对数比较估计在有限次向下跳跃下的拼接 | 已证明，跳跃不等式是显式假设 |
| 同上 | 非负函数不能在显式时间区间上持续满足指定衰减估计 | 已证明 |
| 同上 | 从给定的面积演化和标量曲率不等式导出归一化面积衰减 | 已证明，几何不等式是显式假设 |
| 同上 | 满足这些估计的全局非负连续面积函数不存在 | 已证明的实分析命题 |
| [Audit.lean](Audit.lean) | 检查 `Perelman` 命名空间的声明及传递公理依赖 | 拒绝新增公理和 `sorryAx` |

## 数学内容与适用边界

对应[佩雷尔曼第三篇论文 §1.3](https://arxiv.org/html/math/0307245v1)。
设 `C > 0`，并**假设**一个非负面积函数满足

\[
A'(t)\le -2\pi-\tfrac12 R(t)A(t),\qquad
R(t)\ge -\frac{3}{2(t+C)}.
\]

代码证明

\[
A'(t)\le -2\pi+\frac{3A(t)}{4(t+C)},\qquad
\left(\frac{A(t)}{t+C}\right)'\le -\frac{2\pi}{t+C}.
\]

一般地，若连续函数 `f` 的前向差商具有上界 `-k/(t+C)`，则

\[
f(T)\le f(0)-k\bigl(\log(T+C)-\log C\bigr).
\]

当 `k > 0`、`f(0) ≥ 0` 时，取

\[
T=C\left(\exp\left(\frac{f(0)}k+1\right)-1\right)>0,
\]

右端等于 `-k < 0`，与 `f(T) ≥ 0` 矛盾。
`ForwardSlopeBound` 直接使用“对所有严格较大的上界，充分靠近的前向差商均小于该上界”
表述，不要求 `f` 可微。连续性单独列为假设。右导数版本通过证明连接到这个条件。

`logarithmic_comparison_with_jumps` 允许有限多个连续片段，并假设每次连接时函数值不增加。
它不证明几何手术满足这个假设，也不证明手术时刻在紧时间区间内只有有限多个。
`no_global_area_profile` 使用连续函数和右导数，因此不能直接应用于一般带手术的 Ricci 流。

## 复现

固定环境：

- Lean：`leanprover/lean4:v4.32.0`
- mathlib：`81a5d257c8e410db227a6665ed08f64fea08e997`
- 全部传递依赖：[lake-manifest.json](lake-manifest.json)

安装 [elan](https://github.com/leanprover/elan) 后，在仓库根目录执行：

```sh
lake exe cache get
python3 verify.py --self-test
```

`lake exe cache get` 会按提交的 manifest 获取依赖并下载预编译缓存，需要网络和足够磁盘空间。
如尚未生成依赖目录，也可先执行 `lake update`；随后必须检查 manifest 没有漂移。

验证脚本逐一重新编译本仓库源码，将警告视为错误，检查依赖提交，并运行公理审计。
`--self-test` 额外临时注入一个自定义公理、一个未完成定理和一个未完成定义，确认审计均拒绝它们。
这些临时文件放在忽略的 `.lake/` 中，测试结束即删除。

也可以使用标准 Lake 构建：

```sh
lake build
```

通过构建与审计，只说明这里列出的局部声明通过检查，不代表目标猜想已被证明。
审计仅允许 Lean/mathlib 常用的 `propext`、`Classical.choice` 和 `Quot.sound`，
不要求排除经典选择，也不把经典基础公理算作缺失几何定理的替代。

## 完整证明仍缺少什么

详细依赖与交付条件见 [ROADMAP.md](ROADMAP.md)。核心缺口包括：

1. 从目标拓扑流形构造适用的光滑、可定向黎曼几何结构，并连接两种命题表述。
2. Ricci 流的定义、短时存在、标量曲率演化及最大值原理。
3. 佩雷尔曼的非塌缩、典范邻域、奇点控制和带手术 Ricci 流存在理论。
4. 环路空间中的拓扑类、极小圆盘面积不变量及其正性、正则化和前向差商估计。
5. 手术时刻的面积控制、拓扑追踪，以及将实分析矛盾转化为几何有限消亡。
6. 有限消亡后的三维拓扑分类，并最终构造 `M ≃ₜ ThreeSphere`。

上述缺口没有以公理、`sorry` 或一个包含完整结论的假设包填入。项目也没有声称完整形式化在其他地方不存在；
这里核查的是所固定的 mathlib 版本，它仍将该猜想标为 `proof_wanted`。

## 参考与归属

- Grisha Perelman, [The entropy formula for the Ricci flow and its geometric applications](https://arxiv.org/abs/math/0211159).
- Grisha Perelman, [Ricci flow with surgery on three-manifolds](https://arxiv.org/abs/math/0303109).
- Grisha Perelman, [Finite extinction time for the solutions to the Ricci flow on certain three-manifolds](https://arxiv.org/abs/math/0307245), §1.2–1.4.
- John Morgan and Gang Tian, [Ricci Flow and the Poincare Conjecture](https://arxiv.org/abs/math/0607607)，详细数学论述，不是本项目的机器证明。
- [mathlib 的目标命题](https://github.com/leanprover-community/mathlib4/blob/81a5d257c8e410db227a6665ed08f64fea08e997/Mathlib/Geometry/Manifold/PoincareConjecture.lean)，Junyan Xu；本项目采用相同的三维拓扑命题假设。

本仓库中的初始代码由 Codex 辅助编写并经 Lean 检查。数学证明归属于原作者；没有完成独立的完整证明贡献。
代码采用 [Apache-2.0](LICENSE) 许可证；依赖保留各自许可和作者归属。

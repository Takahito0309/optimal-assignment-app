import streamlit as st
import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD

# 社員と部署
employees = ["佐藤", "鈴木", "高橋", "田中", "伊藤"]
departments = ["営業部", "技術部", "人事部", "経理部"]

# スキルマッチスコア（社員 × 部署）
skill_match = {
    "佐藤": {"営業部": 2, "技術部": 1, "人事部": 5, "経理部": 4},
    "鈴木": {"営業部": 4, "技術部": 3, "人事部": 2, "経理部": 9},
    "高橋": {"営業部": 2, "技術部": 10, "人事部": 7, "経理部": 1},
    "田中": {"営業部": 1, "技術部": 2, "人事部": 4, "経理部": 4},
    "伊藤": {"営業部": 9, "技術部": 10, "人事部": 1, "経理部": 9},
}

st.title("社員配置 最適化シミュレーション")
st.markdown("重みを調整して最適な配置を試してみましょう")

# 部署ごとの重みスライダー
weights = {d: st.slider(f"{d}の重み", 1, 10, 5) for d in departments}

# 部署の定員（1人ずつ配置と仮定）
max_per_dept = {d: 1 for d in departments}

# 最適化モデルの構築
prob = LpProblem("AssignmentProblem", LpMaximize)
x = LpVariable.dicts("assign", (employees, departments), cat="Binary")

# 目的関数: スキルマッチスコア × 重み
prob += lpSum(
    skill_match[e][d] * weights[d] * x[e][d]
    for e in employees for d in departments
)

# 各部署は1人だけ受け入れる（定員）
for d in departments:
    prob += lpSum(x[e][d] for e in employees) <= max_per_dept[d]

# 各社員は1つの部署にしか配属されない
for e in employees:
    prob += lpSum(x[e][d] for d in departments) == 1

# 解く
prob.solve(PULP_CBC_CMD(msg=0))

# 結果表示
data = []
for e in employees:
    for d in departments:
        if x[e][d].value() == 1:
            data.append((e, d, skill_match[e][d], weights[d]))

results_df = pd.DataFrame(data, columns=["社員", "配属先", "スキルスコア", "重み"])
st.subheader("最適な配属結果")
st.dataframe(results_df)

# 総スコア
total_score = sum(skill_match[e][d] * weights[d] for e, d, _, _ in data)
st.markdown(f"### 総合スコア: {total_score}")

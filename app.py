import streamlit as st
import pandas as pd
from pulp import LpProblem, LpMaximize, LpVariable, lpSum, PULP_CBC_CMD
import random

# ダミーデータ生成
employees = [f"社員{i+1}" for i in range(20)]
departments = ["営業部", "技術部", "人事部", "経理部"]
locations = ["東京", "大阪", "名古屋", "福岡"]

random.seed(42)
data = []
for name in employees:
    current_dept = random.choice(departments)
    current_loc = random.choice(locations)
    desired_dept = random.choice(departments)
    desired_loc = random.choice(locations)
    skill = random.randint(1, 10)
    evaluation = random.randint(1, 5)
    years = random.randint(1, 20)
    age = random.randint(23, 60)
    data.append([
        name, current_dept, current_loc, desired_dept, desired_loc,
        skill, evaluation, years, age
    ])

# DataFrame作成
df = pd.DataFrame(data, columns=[
    "氏名", "現在部署", "現在勤務地", "希望部署", "希望勤務地",
    "スキルスコア", "能力評価", "勤続年数", "年齢"
])

# 距離マトリクス（簡易版）
distance_matrix = {
    (a, b): abs(i - j) * 200
    for i, a in enumerate(locations)
    for j, b in enumerate(locations)
}

st.title("社員異動シミュレーション：カスタム重み設定")
st.markdown("各要素の重みを調整して、異動提案を確認しましょう")

# ユーザーが設定する重み
skill_weight = st.slider("スキルスコアの重み", 0.0, 1.0, 0.25)
eval_weight = st.slider("能力評価の重み", 0.0, 1.0, 0.25)
hope_weight = st.slider("異動希望（部署・勤務地一致）の重み", 0.0, 1.0, 0.25)
dist_weight = st.slider("異動距離ペナルティの重み", 0.0, 1.0, 0.25)
years_weight = st.slider("勤続年数の重み", 0.0, 1.0, 0.25)

positions = [(d, l) for d in departments for l in locations]
assignment_data = []

for emp in df.itertuples():
    for dept, loc in positions:
        hope_score = 1 if emp.希望部署 == dept and emp.希望勤務地 == loc else 0
        dist_penalty = distance_matrix[(emp.現在勤務地, loc)] / 100
        score = (
            emp.スキルスコア * skill_weight +
            emp.能力評価 * eval_weight +
            hope_score * 10 * hope_weight -
            dist_penalty * dist_weight +
            emp.勤続年数 * years_weight
        )
        assignment_data.append([
            emp.氏名, emp.現在部署, emp.現在勤務地,
            dept, loc, round(score, 2)
        ])

assignment_df = pd.DataFrame(assignment_data, columns=[
    "氏名", "現在部署", "現在勤務地", "提案配属部署", "提案勤務地", "カスタムスコア"
])

best = assignment_df.loc[assignment_df.groupby("氏名")["カスタムスコア"].idxmax()]
st.subheader("最適な異動提案（カスタムスコアに基づく）")
st.dataframe(best)

st.markdown("※ 異動希望が一致すれば加点、勤務地間距離が遠いと減点されます")

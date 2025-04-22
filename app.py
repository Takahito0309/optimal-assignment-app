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

st.title("社員異動シミュレーション：3案比較")
st.markdown("各要素の重みを調整して、複数の異動提案を比較しましょう")

# 重み設定（UI）
skill_weight = st.slider("スキルスコアの重み", 0.0, 1.0, 0.25)
eval_weight = st.slider("能力評価の重み", 0.0, 1.0, 0.25)
hope_weight = st.slider("異動希望（部署・勤務地一致）の重み", 0.0, 1.0, 0.25)
dist_weight = st.slider("異動距離ペナルティの重み", 0.0, 1.0, 0.25)
years_weight = st.slider("勤続年数の重み", 0.0, 1.0, 0.25)

positions = [(d, l) for d in departments for l in locations]
assignment_data = []

# スコア計算と提案生成
for emp in df.itertuples():
    for dept, loc in positions:
        hope_score = 1 if emp.希望部署 == dept and emp.希望勤務地 == loc else 0
        dist_penalty = distance_matrix[(emp.現在勤務地, loc)] / 100

        # 提案A: スキル・評価重視
        score_A = emp.スキルスコア * 0.6 + emp.能力評価 * 0.4

        # 提案B: 希望・距離重視
        score_B = hope_score * 10 - dist_penalty

        # 提案C: カスタム重み
        score_C = (
            emp.スキルスコア * skill_weight +
            emp.能力評価 * eval_weight +
            hope_score * 10 * hope_weight -
            dist_penalty * dist_weight +
            emp.勤続年数 * years_weight
        )

        assignment_data.append([
            emp.氏名, emp.現在部署, emp.現在勤務地, dept, loc,
            round(score_A, 2), round(score_B, 2), round(score_C, 2)
        ])

assignment_df = pd.DataFrame(assignment_data, columns=[
    "氏名", "現在部署", "現在勤務地", "提案配属部署", "提案勤務地",
    "スコアA（スキル重視）", "スコアB（希望重視）", "スコアC（カスタム）"
])

# ベスト提案抽出
best_A = assignment_df.loc[assignment_df.groupby("氏名")["スコアA（スキル重視）"].idxmax()]
best_B = assignment_df.loc[assignment_df.groupby("氏名")["スコアB（希望重視）"].idxmax()]
best_C = assignment_df.loc[assignment_df.groupby("氏名")["スコアC（カスタム）"].idxmax()]

# UI: 提案切替
option = st.radio("表示する異動提案を選択", ("提案A：スキル重視", "提案B：希望重視", "提案C：カスタム重み"))
if option == "提案A：スキル重視":
    st.subheader("提案A：スキル・能力評価重視")
    display_df = best_A
elif option == "提案B：希望重視":
    st.subheader("提案B：希望と距離を重視")
    display_df = best_B
else:
    st.subheader("提案C：カスタム重みで最適化")
    display_df = best_C
st.dataframe(display_df)
st.markdown("※ 異動希望が一致すれば加点、勤務地間距離が遠いと減点されます")

# 部署別人数（現状と提案結果）
st.subheader("現状の部署別人数")
st.bar_chart(df["現在部署"].value_counts())

st.subheader("提案後の部署別人数")
st.bar_chart(display_df["提案配属部署"].value_counts())

# 部署×勤務地別人数分布
st.subheader("現状の部署×勤務地人数分布")
st.bar_chart(pd.crosstab(df["現在部署"], df["現在勤務地"]))

st.subheader("提案後の部署×勤務地人数分布")
st.bar_chart(pd.crosstab(display_df["提案配属部署"], display_df["提案勤務地"]))

import os
import streamlit as st
import duckdb
from rlops.utils.bjtimes import get_bj_day_time, get_bj_day, get_yestoday_bj

from google.cloud import bigquery

st.set_page_config(page_title="RL Experiments Dashboard", page_icon="📈")


# st.header("YOLO")
"# 📈 Real-Time / RL 模型实验"


def number_format(number):
    return "{:,}".format(number)


def calculate_mean(lst):
    if len(lst) == 0:
        return None  # 返回 None 或其他特定值

    total = sum(lst)
    mean = total / len(lst)
    return mean


def cal_model_control_pays():
    ab_tests = conn.execute(
        "select alternatives,sum(pays) as all_pays from df group by alternatives"
    ).df()
    ab_tests_dict_list = ab_tests.to_dict(orient="records")

    new_dict = {}
    for x in ab_tests_dict_list:
        new_key = x["alternatives"]
        new_value = x["all_pays"]
        new_dict[new_key] = new_value
    keys = [x["alternatives"] for x in ab_tests_dict_list]
    new_control_vals = []

    for k in keys:
        if "test" == k or "test1" == k:
            model_val = new_dict[k]
        else:
            new_control_vals.append(new_dict[k])

    control_val = calculate_mean(new_control_vals)
    return model_val, control_val


# query data experiment
def online_pay_query(stat_date="2023-01-04", exp_name="spinux_strategy_recom"):
    query = get_query_str(stat_date, exp_name)

    client = bigquery.Client()
    results = client.query(query)
    return results.to_dataframe()


def get_query_str(stat_date="2023-01-03", exp_name="spinux_strategy_recom"):
    q_str = f"""SELECT
      date,
      alternatives,
      pay_type,
      SUM(pay) as sum_pays
    FROM (
      SELECT
        CAST(jsonpayload.uid AS string) AS uid,
        DATE(timestamp, "-03") AS date,
        jsonpayload.pay_type as pay_type,
        SUM(CAST(jsonpayload.usd AS float64)) AS pay
      FROM
        `seateam.fact.purchase`
      WHERE
        DATE(timestamp, "-03") BETWEEN '{stat_date}'
        AND '{stat_date}'
     --AND jsonpayload.sp_ty BETWEEN "S03" and "S08"
      GROUP BY
        1,
        2,
        3)
    JOIN (
      SELECT
        CAST(jsonpayload.uid AS string) AS uid,
        -- DATE(timestamp, "-03") as date,
        jsonpayload.alternatives AS alternatives
      FROM
        `fact.sys_churn_pay_result`
      WHERE
        jsonpayload.ab_id='{exp_name}'
        and jsonpayload.log_type=1
        AND DATE(timestamp, "-03") BETWEEN '{stat_date}'
        AND '{stat_date}' QUALIFY ROW_NUMBER() OVER(PARTITION BY uid ORDER BY DATE(timestamp, "-03"))=1)
    USING
      (uid)
    GROUP BY
      1,
      2,
      3
    """
    return q_str


exp_list = [
    "uni_pricing_s0102",
    "spinux_strategy_recom",
    "mission_content_recom",
    "online_gift_store_pricing",
    "s0102_update",
    "online_gemstone_pricing",
    "online_recom_payitems",
    "online_navig_promotion_pricing",
]
df1_script = """
SELECT
  alternatives,
  Pay_type,
  SUM(sum_pays) AS pays
FROM (
  SELECT
    alternatives,
    CASE
      WHEN pay_type < 4 AND pay_type>0 THEN 'small_R'
      WHEN pay_type >=4
    AND pay_type<6 THEN 'mid_R'
      WHEN pay_type >=6 AND pay_type<8 THEN 'big_R'
  END
    AS Pay_type,
    sum_pays AS sum_pays
  FROM
    df)
GROUP BY
  Pay_type,
  alternatives
ORDER BY
  Pay_type
"""

df2_script = """
SELECT
  alternatives,
  SUM(pays) AS all_pays
FROM
  df1
GROUP BY
  alternatives
"""

# creating a single-element container.
placeholder = st.empty()

choice = "付费跟踪"
if choice in ["主页", "付费跟踪"]:
    st.sidebar.subheader("可选实验")
    selected_genre = st.sidebar.selectbox("选择模型实验", exp_list)
    conn = duckdb.connect()

    today = get_bj_day()
    df = online_pay_query(stat_date=today, exp_name=selected_genre)
    y_day = get_yestoday_bj()
    df_y = online_pay_query(stat_date=y_day, exp_name=selected_genre)
    df1 = conn.execute(df1_script).df()
    df2 = conn.execute(df2_script).df()

    # adding a multiselect box

    options = st.sidebar.multiselect(
        "玩家 Pay_type", ["small_R", "mid_R", "big_R"], ["big_R", "mid_R", "small_R"]
    )
    if len(options) < 2:
        opts = f"Pay_type = '{options[0]}'"
        kpi = options[0]
    else:
        opts = f"Pay_type in {tuple(options)}"
        kpi = ",".join(options)

    df = conn.execute(
        f"""
        SELECT
  a.alternatives,
  a.Pay_type,
  a.pays,
  a.pays/b.all_pays AS pay_percentage,
  b.all_pays
FROM (
  SELECT
    *
  FROM
    df1
  WHERE
    {opts}) AS a
JOIN
  df2 AS b
ON
  a.alternatives=b.alternatives
        """
    ).df()

    x_y = conn.execute("select sum(sum_pays) as all_pays from df_y").df()

    # st.markdown(f"## KPI {kpi}")

    with placeholder.container():
        # create three columns
        kpi1, kpi2, kpi3 = st.columns(3)
        # fill in those three columns with respective metrics or KPIs
        avg_age = 89
        count_married = 704
        balance = 1196
        x = conn.execute("select sum(pays) as all_pays from df").df()
        _total_pays_y = x_y.to_dict(orient="records")[0]["all_pays"]
        _total_pays = x.to_dict(orient="records")[0]["all_pays"]
        total_pays = number_format(round(_total_pays, 2))
        total_pays_y = number_format(round(_total_pays_y, 2))

        model_val, control_val = cal_model_control_pays()
        kpi1.metric(
            label="当前总付费/昨日总付费 $",
            value=f"$ {total_pays}",
            delta=total_pays_y
            # delta=number_format(round(_total_pays - _total_pays_y, 2)),
        )
        kpi2.metric(
            label="model/control 分组总付费 $",
            value=f"$ {number_format(round(model_val, 2))}",
            delta=number_format(round(control_val, 2)),
        )
        kpi3.metric(
            label="model/control Lift ＄",
            value=f"$ {round(model_val-control_val,2)} ",
            delta=f"{round(model_val / control_val - 1, 4) * 100}%",
        )

    st.markdown("""---""")
    select_time = get_bj_day_time()
    # Display the dataset
    # Show filtered data
    st.subheader(f"你选择的实验为: {selected_genre}, 执行时间: {select_time}")

    # st.map(df)
    st.markdown("### Detailed Data View")
    st.dataframe(df)

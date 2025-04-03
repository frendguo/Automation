import akshare as ak
from datetime import datetime, timedelta
from openai import OpenAI
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib
import os  # 导入 os 模块来读取环境变量
import sys # 导入 sys 模块用于错误退出

# --- 从环境变量读取 Secrets ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
FROM_EMAIL = os.environ.get("EMAIL_USER")
FROM_PASSWORD = os.environ.get("EMAIL_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL") # 将收件人也设为环境变量

# --- 检查 Secrets 是否设置 ---
if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY environment variable not set.")
    sys.exit(1) # 出错时退出脚本
if not FROM_EMAIL:
    print("Error: EMAIL_USER environment variable not set.")
    sys.exit(1)
if not FROM_PASSWORD:
    print("Error: EMAIL_PASSWORD environment variable not set.")
    sys.exit(1)
if not TO_EMAIL:
    print("Error: TO_EMAIL environment variable not set.")
    sys.exit(1)

# 使用获取到的 API Key 初始化 OpenAI 客户端
client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/" # 注意：确认这个 base_url 是否正确或需要
)

def send_email(subject, body, to_email):
    """发送邮件"""
    # 使用从环境变量获取的邮箱和密码
    from_email = FROM_EMAIL
    from_password = FROM_PASSWORD

    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = Header(subject, 'utf-8')

    # 添加邮件正文
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # 发送邮件
    try:
        # 注意：不同的邮箱服务商 SMTP 地址和端口可能不同
        # 这里是 163 邮箱的 SSL 示例
        server = smtplib.SMTP_SSL('smtp.163.com', 465)
        server.login(from_email, from_password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print('邮件发送成功')
    except Exception as e:
        print(f'Error: 无法发送邮件: {str(e)}')
        # 考虑是否在这里也 sys.exit(1)

# AI分析分笔数据
def analysis(gdp, pmi, cpi, huilv, meilianch, lhb, board, market, index_zh_a_hist_df, fund_flow):
    try:
        # 构造提示词
        prompt = f"""
# Role: 主力动向分析师

## Profile
- language: 中文
- description: 你的任务是关联花括号内的数据，对A股大盘进行一个多维度的分析，
- background: 拥有金融分析、数据科学和人工智能的背景，专注于股票市场的主力资金分析。
- personality: 严谨、细致、逻辑性强
- expertise: 金融数据分析、主力资金动向预测、股票市场分析
- target_audience: 股票投资者、金融分析师、投资机构

## workflow

1.当前市场处于牛市、震荡市还是熊市？
2.资金是否在持续流入 or 撤退？
3.市场情绪如何，是否存在短期回调风险？
4.哪些行业/概念最值得关注？
5.短中长期策略建议：买入、观望还是减仓？

## 数据如下
{gdp} 是年度GDP数据(前值)
{pmi} 是PMI指数数据(最新)
{cpi} 是月度CPI数据(前值)
{huilv} 是人民币/美元汇率(最新即期)
{meilianch} 是美联储利率决策(最新)
{lhb} 是当日龙虎榜数据
{board} 是概念板块列表
{market} 是市场赚钱效应数据
{index_zh_a_hist_df} 是近3日上证指数日线数据
{fund_flow} 是概念板块资金流向(即时)

        """
        # 注意：根据你的 Gemini key 和 base_url，确认模型名称是否正确
        # "gemini-2.5-pro-exp-03-25" 可能是实验性模型，考虑使用稳定版本如 "gemini-pro"
        response = client.chat.completions.create(
            model="gemini-pro", # 或者你确认有效的模型
            messages=[{"role": "user", "content": prompt}]
        )
        # 获取分析结果
        response_content = response.choices[0].message.content.strip()
        return response_content

    except Exception as e:
        return f"AI 分析生成失败: {str(e)}"

def main():
    current_date = datetime.now().strftime('%Y%m%d')
    # Akshare 获取数据时，end_date 通常包含当天，start_date 通常也包含当天
    # 如果希望获取最近3天的数据，可能需要调整日期逻辑
    # 例如，获取 T-2, T-1, T 的数据
    start_date_dt = datetime.now() - timedelta(days=2)
    start_date_str = start_date_dt.strftime('%Y%m%d')
    end_date_str = current_date # 当天

    print(f"Fetching data from {start_date_str} to {end_date_str}")

    try:
        # --- 获取数据 ---
        # 宏观经济指标
        print("Fetching GDP data...")
        macro_china_gdp_yearly_df = ak.macro_china_gdp_yearly()
        gdp = macro_china_gdp_yearly_df.iloc[-1]['指标'] + ": " + str(macro_china_gdp_yearly_df.iloc[-1]['数据']) if not macro_china_gdp_yearly_df.empty else "N/A"


        print("Fetching PMI data...")
        index_pmi_com_cx_df = ak.index_pmi_com_cx()
        pmi = index_pmi_com_cx_df.iloc[-1].to_string() if not index_pmi_com_cx_df.empty else "N/A"

        print("Fetching CPI data...")
        macro_china_cpi_monthly_df = ak.macro_china_cpi_monthly()
        cpi = macro_china_cpi_monthly_df.iloc[-1].to_string() if not macro_china_cpi_monthly_df.empty else "N/A"


        print("Fetching FX data...")
        fx_spot_quote_df = ak.fx_spot_quote()
        huilv = fx_spot_quote_df[fx_spot_quote_df['品种'] == '美元人民币'].to_string() if not fx_spot_quote_df.empty else "N/A"


        print("Fetching Fed data...")
        macro_bank_usa_interest_rate_df = ak.macro_bank_usa_interest_rate()
        meilianch = macro_bank_usa_interest_rate_df.iloc[-1].to_string() if not macro_bank_usa_interest_rate_df.empty else "N/A"


        # 市场指标
        print("Fetching LHB data...")
        # 注意：LHB 数据可能只在交易日才有，非交易日可能为空或报错
        try:
            lhb = ak.stock_lhb_detail_em(start_date=end_date_str, end_date=end_date_str)
            lhb_str = lhb.to_string() if not lhb.empty else "当日无龙虎榜数据"
        except Exception as e:
            lhb_str = f"获取龙虎榜数据失败: {e}"


        print("Fetching board data...")
        board = ak.stock_board_concept_name_em()
        board_str = board['板块名称'].to_list()[:20] # 只取前20个概念示例
        board_str = ", ".join(board_str) if board_str else "N/A"

        print("Fetching market activity data...")
        market = ak.stock_market_activity_legu()
        market_str = market.to_string() if not market.empty else "N/A"

        # 技术面分析
        print("Fetching index history...")
        # 获取上证指数最近3个交易日的数据
        index_zh_a_hist_df = ak.index_zh_a_hist(symbol="000001", period="daily", start_date=start_date_str, end_date=end_date_str)
        index_hist_str = index_zh_a_hist_df.to_string() if not index_zh_a_hist_df.empty else "获取指数历史数据失败"

        print("Fetching fund flow data...")
        # 概念资金流向
        fund_flow = ak.stock_fund_flow_concept(symbol="即时")
        fund_flow_str = fund_flow.head(10).to_string() if not fund_flow.empty else "获取资金流数据失败" # 取前10条示例


        print("--- Data Fetching Complete ---")
        print("Starting AI analysis...")

        # --- 进行分析 ---
        result = analysis(gdp, pmi, cpi, huilv, meilianch, lhb_str, board_str, market_str, index_hist_str, fund_flow_str)
        print("--- AI Analysis Complete ---")
        print(result)

        # --- 发送邮件 ---
        print("Sending email...")
        # 使用从环境变量获取的 TO_EMAIL
        send_email(subject=f"{end_date_str} A股复盘报告", body=result, to_email=TO_EMAIL)

    except Exception as e:
        error_message = f"脚本执行出错: {str(e)}\n"
        import traceback
        error_message += traceback.format_exc() # 获取详细的错误堆栈
        print(error_message)
        # 也可以尝试将错误信息发送邮件给自己调试
        try:
             send_email(subject=f"{end_date_str} 脚本执行失败", body=error_message, to_email=FROM_EMAIL) # 发送错误报告给自己
        except Exception as email_err:
             print(f"发送错误报告邮件失败: {email_err}")
        sys.exit(1) # 确保 Action 知道发生了错误


if __name__ == "__main__":
    main()
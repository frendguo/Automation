# Automation
Some automation scripts that are executed via Github Action.

# Follow_Checkin.js

每天 10：05 执行，Follow 签到任务。

## 添加环境变量

1. 打开 GitHub 仓库，点击 `Settings`。
2. 点击 `Secrets and variables`，然后选择 `Actions`。
3. 添加新的密钥，将 `FOLLOW_ACCOUNT_0` 等值保存为密钥。

## 多账号配置

多账号规则: `FOLLOW_ACCOUNT_X` X 以 0 开始, 依次添加 例如: `FOLLOW_ACCOUNT_0, FOLLOW_ACCOUNT_1, FOLLOW_ACCOUNT_2`

输入名称: FOLLOW_ACCOUNT_0

输入值: 抓取csrf请求头中的整个Cookie 例

```
// 就是很长不要怀疑
authjs.csrf-token=xxxxxx; authjs.callback-url=xxxxxx; authjs.session-token=xxxxxxx; ph_phc_EZGExxxxxxxxwEWNL_posthog=xxxxx
```





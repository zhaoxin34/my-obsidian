https://gitlab.datatist.cn/zhaoxin/starrocks-perform

# 造数据的提示词

# 目标

根据 @../sql/wolf_v4/README.md 文档中介绍的表格造数据

## 要求

* 数据输出方式：
  - 使用python脚本输出csv文件
* 数据规模需求：
  - dt_benefit_info   | 万级
  - dt_black_list_v3  | 10万级
  - dt_employee_info  | 万级
  - dt_event_v3       | 180天，亿级
  - dt_order_info     | 180天，亿级
  - dt_product_info   | 千级
  - dt_push_content   | 千级
  - dt_segment_v3     | 不需要
  - dt_user_info      | 千万级
* 数据质量要求：
  - 姓名、地址、电话号码格式等需要接近真实,尤其是数据的长度，如名字不能超过5个字符
  - 订单表、事件表中的user_id需要存在于用户表中, 对应dt_id
* 业务逻辑约束：
  - 涉及日期在最近半年内

## 额外要求
1. scenario_code的取值范围：
  - 只使用"phone_number"
2. 数据分布：
  - 对于日期相关的数据（订单、事件）, 均匀分布
  - 用户的地域分布无所谓
3. 特殊字段处理：
  - dt_segment_v3标记为"不需要"，表示不需要造数据
  - dt_push_content中的channel字段，随机分配比例就好，尽量简单
4. 输出文件格式：
  - CSV文件的编码格式（UTF-8）
  - 需要包含表头
  - 文件命名以表名为前缀
5. 数据关联性：
  - 产品表和订单表的关联如何处理，随机关联，保持简单
  - 用户表和其他表的关联，只需要随机关联就好，保持简单
6. 上亿数据的处理方式：
  - 分批输出

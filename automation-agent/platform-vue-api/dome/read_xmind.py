import xmindparser
import json
xmind_data = xmindparser.xmind_to_dict("template.xmind")
# 提取根节点下的第一层节点: topics
root_topics = xmind_data[0]["topic"]["topics"]

for child in root_topics:
    # TODO 1 : 测试用例名称
    case_name = child["title"]

    # 查找 desc 节点并获取其子节点的内容作为 case_desc
    case_desc = ""
    if "topics" in child:
        for topic in child["topics"]:
            if topic["title"].lower() == "desc" and "topics" in topic and topic["topics"]:
                case_desc = topic["topics"][0]["title"]
                break
    # TODO 2: 把获取的基本信息写入到用例信息表当中并且获取ID

    # TODO 3： 遍历没一个步骤把对应的数据基于ID 写入到步骤当中


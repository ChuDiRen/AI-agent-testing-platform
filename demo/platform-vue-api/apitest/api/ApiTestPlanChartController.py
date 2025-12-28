# 新增 web 图表功能页面
from flask import Blueprint, request
from core.resp_model import respModel
from app import database, application
# from sysmanage.model.CaseTypeModel import CaseType
from apitest.model.ApiHistoryModel import ApiHistoryModel
from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
from apitest.model.ApiInfoCaseModel import ApiInfoCase

module_name = "ApiTestPlanChart"  # 模块名称
module_model = ApiHistoryModel

module_route = Blueprint(f"route_{module_name}", __name__)

# 新增 web 图表功能页面
# 1. 完成本测试计划执行次数查询，返回一个执行次数数字给前端
@module_route.route(f"/{module_name}/queryPlanCount", methods=["GET"])
def queryPlanCount():
    with application.app_context():
        #1. 获取参数 项目id，测试计划id coll_id
        coll_id = request.args.get("coll_id")
        #2.根据coll_id查询出 apiHistory的执行数据条数 ，查询数据库count
        count = ApiHistoryModel.query.filter_by(collection_info_id=coll_id).count()
        #3.将查询到的数据返回给前端
        return respModel.ok_resp_text(msg="查询成功",data=count)

# #2. 完成本次测试计划最后一个计划中包含的用例数量,返回一个数量到前端【注意一个用例需要进行数据驱动，所以就是多个用例】
# 所以在执行用例的时候我们需要把当前用例的执行数据写入到记录当中
from sysmanage.model.HistoryInfoModel import HistoryInfo
@module_route.route(f"/{module_name}/queryCaseCount", methods=["GET"])
def queryCaseCount():
    with application.app_context():

        coll_id = request.args.get("coll_id")

        # 查询最后一次测试计划执行记录
        last_data = module_model.query \
            .filter_by(collection_info_id=coll_id) \
            .order_by(module_model.id.desc()) \
            .first()

        if not last_data:
            # 如果没有历史记录，返回 0 或提示信息
            return respModel.ok_resp_text(msg="未找到测试计划执行记录", data=0)


        # 查询用例总数
        count = HistoryInfo.query.filter_by(
            coll_id=coll_id,
            detail=last_data.history_detail
        ).count()

        return respModel.ok_resp_text(msg="查询成功", data=count)

# 3.完成本次测试计划中的通过率，返回一个百分比到前端，测试计划中通过率=测试计划中通过次数/测试计划中包含的用例总数
@module_route.route(f"/{module_name}/queryPassRate", methods=["GET"])
def queryPassRate():
    with application.app_context():

        #1. 获取参数 项目id，测试计划id coll_id
        coll_id = request.args.get("coll_id")
        #2. 通过coll_id 查询到t_history_Info表中，为这个coll_id 且 type为api 的数据，判断status为pass的数据的总数
        pass_count = HistoryInfo.query.filter_by(coll_id=coll_id,type="api",status="passed").count()
        #3. 通过cll_id 查询到t_history_Info表中，为这个coll_id 且 type为api 的数据的总数
        total_count = HistoryInfo.query.filter_by(coll_id=coll_id,type="api").count()
        #4.通过上面的两个数据，计算出通过率，返回给前端
        pass_rate = 0  # 默认值
        if total_count > 0:
            pass_rate = round((pass_count / total_count) * 100, 2)
        return respModel.ok_resp_text(msg="查询成功",data=pass_rate)

# 4. 查询最近10次测试计划执行结果趋势，要显示测试计划的详细状态，需要组装数据
from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
@module_route.route(f"/{module_name}/queryPlanTrend", methods=["GET"])
def queryPlanTrend():
    with application.app_context():

        #1. 获取参数 项目id，测试计划id coll_id
        coll_id = request.args.get("coll_id")
        #2. 通过coll_id 查询到apiHistory表中，为这个coll_id的数据，查询出最近10条数据
        datas = module_model.query.filter_by(collection_info_id=coll_id).order_by(module_model.id.desc()).limit(5)
        coll_data = ApiCollectionInfo.query.filter_by(id=coll_id).first()
        #3. 组装数据，返回给前端
        trend_data = []

        for data in datas:
            # 获取 create_time 作为 date 时间格式展示为 年月日 时分秒的格式
            date = data.create_time.strftime('%Y-%m-%d %H:%M:%S')
            # 关联查询 t_history_Info 表，获取 status 的统计信息
            history_Info_datas = HistoryInfo.query.filter_by(coll_id=coll_id, detail=data.history_detail).all()

            # 初始化状态计数器
            status_counts = {
                "passed": 0,
                "failed": 0,
                "broken": 0,
                "skipped": 0,
                "unknown": 0
            }

            # 遍历 history_Info_datas 数据，统计 status 出现次数
            for history_Info in history_Info_datas:
                if history_Info.status == "passed":
                    status_counts["passed"] += 1
                elif history_Info.status == "failed":
                    status_counts["failed"] += 1
                elif history_Info.status == "broken":
                    status_counts["broken"] += 1
                elif history_Info.status == "skipped":
                    status_counts["skipped"] += 1
                else:
                    status_counts["unknown"] += 1

            # 将统计数据添加到 trend_data
            trend_data.append({
                "date": date,
                "name": f"{coll_data.collection_name}", # ID-测试计划名称
                "passed": status_counts["passed"],
                "failed": status_counts["failed"],
                "broken": status_counts["broken"],
                "skipped": status_counts["skipped"],
                "unknown": status_counts["unknown"]
            })

        # 返回组装好的数据
        return respModel.ok_resp_list(msg="查询成功", lst=trend_data)

#5. 查询最近10次的测试计划耗费时间的线图
@module_route.route(f"/{module_name}/queryPlanTime", methods=["GET"])
def queryPlanTime():
    with application.app_context():
        #1. 获取参数 项目id，测试计划id coll_id
        coll_id = request.args.get("coll_id")
        #2. 通过coll_id 查询到apiHistory表中，为这个coll_id的数据，查询出最近10条数据
        datas = module_model.query.filter_by(collection_info_id=coll_id).order_by(module_model.id.desc()).limit(10)
        #3. 组装数据，返回给前端
        time_data = []

        for data in datas:
            # 获取 create_time 作为 date
            date = data.create_time.strftime('%Y-%m-%d %H:%M:%S')

            # 关联查询 t_history_Info 表，获取 duration 字段
            HistoryInfos = HistoryInfo.query.filter_by(coll_id=coll_id, detail=data.history_detail).all()

            # 初始化总耗时
            total_duration = 0

            # 遍历 t_history_Info 数据，累加 duration
            for HistoryInfoData in HistoryInfos:
                total_duration += HistoryInfoData.duration

            # 将统计数据添加到 time_data
            time_data.append({
                "date": date,
                "duration": total_duration
            })

        # 返回组装好的数据
        return respModel.ok_resp_list(msg="查询成功", lst=time_data)

#6.查询失败率最高的5个用例，用失败次数表示,返回一个柱状图数据结构
@module_route.route(f"/{module_name}/queryFailTop5", methods=["GET"])
def queryFailTop5():
    with application.app_context():
        #1. 获取参数 项目id，测试计划id coll_id
        coll_id = request.args.get("coll_id")

        # 2. 查询 t_case_type 表中 status 不是 pass 的数据，按失败次数排序
        # 查询失败次数最多的用例
        failed_cases = HistoryInfo.query.filter_by(coll_id=coll_id, type="api") \
            .filter(HistoryInfo.status != "passed") \
            .group_by(HistoryInfo.name) \
            .order_by(database.func.count(HistoryInfo.status).desc()) \
            .with_entities(HistoryInfo.name, database.func.count(HistoryInfo.status).label('fail_count')) \
            .all()

        # 遍历failed_cases变成一个列表套字典
        result = [{"name": case.name, "fail_count": case.fail_count} for case in failed_cases]

        return respModel.ok_resp_list(msg="查询成功", lst=result)




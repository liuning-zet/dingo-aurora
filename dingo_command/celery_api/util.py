import time
import concurrent.futures
import json
from typing import List
from dingo_command.api.chart import ChartService
from dingo_command.db.models.cluster.models import Taskinfo
from dingo_command.api.model.chart import CreateAppObject
from dingo_command.db.models.cluster.sql import TaskSQL

def update_task_state(task:Taskinfo):
    # 判空
    query_params = {"task_id": task.task_id}
    count, data = TaskSQL.list(query_params)
    if count == 0 or data == []:
        # 如果没有找到对应的任务，则插入
        TaskSQL.insert(task)
        return task.task_id
    else:
        # 如果找到了对应的任务，则更新
        first_task = data[0]  # Get the first task from the result list
        first_task.state = task.state
        first_task.end_time = task.end_time
        first_task.detail = task.detail
        TaskSQL.update(task)
        return task.task_id


def install_single_chart_with_retry(chart: CreateAppObject, cluster_id: str, max_retries=3):
    """
    带重试机制的单个 Chart 安装任务
    """
    chart_service = ChartService()
    retries = 0
    last_exception = None

    # 配置 chart 参数
    chart.cluster_id = cluster_id
    chart.namespace = "kube-system" if not chart.namespace else chart.namespace

    # 获取 chart 的 values (只需获取一次，不需要重试)
    try:
        res = chart_service.get_chart_version(chart.chart_id, chart.chart_version)
        if res.get("data") and res.get("data").values:
            try:
                chart.values = json.loads(res.get("data").values)
            except json.JSONDecodeError:
                chart.values = {}
        else:
            chart.values = {}
    except Exception as exc:
        # 如果获取values失败，直接返回错误，不需要重试
        return exc

    # 重试安装逻辑
    while retries <= max_retries:
        try:
            result = chart_service.install_app(chart)
            return result
        except Exception as exc:
            last_exception = exc
            retries += 1
            if retries <= max_retries:
                # 指数退避策略: 等待时间随重试次数增加
                wait_time = 2 ** retries
                time.sleep(wait_time)
            else:
                return last_exception


def install_app_chart(charts: List[CreateAppObject], cluster_id: str, max_workers: int = 10):
    """
    使用多线程并发安装多个 Helm Chart，带有智能重试机制。

    Args:
        charts: 要安装的 Chart 配置列表。
        cluster_id: 集群 ID。
        max_workers: 线程池中最大线程数，控制并发度。
    """
    if not charts:
        return []

    # 用于存储每个任务的未来对象和图表名称的映射
    future_to_chart_name = {}
    results = []

    # 创建线程池执行器
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务到线程池
        for chart in charts:
            # 为每个图表提交一个带重试的任务
            future = executor.submit(install_single_chart_with_retry, chart, cluster_id)
            future_to_chart_name[future] = chart.name

        # 处理任务结果和异常
        for future in concurrent.futures.as_completed(future_to_chart_name):
            chart_name = future_to_chart_name[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                results.append(exc)

    return results
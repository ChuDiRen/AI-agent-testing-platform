FROM langchain/langgraph-api:3.11

# 添加项目依赖
ADD requirements.txt /deps/requirements.txt
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir -c /api/constraints.txt -r /deps/requirements.txt

# 添加项目代码
ADD . /deps/__outer_agent-backend/src
ENV PYTHONPATH=/deps/__outer_agent-backend/src:$PYTHONPATH

# 设置工作目录
WORKDIR /deps/__outer_agent-backend/src

-- PostgreSQL 首次启动初始化脚本
-- 由官方镜像的 /docker-entrypoint-initdb.d/ 机制自动执行（仅在数据卷为空时运行一次）

-- 启用 pgvector 扩展：人脸特征向量存储与相似度检索依赖此扩展
-- pgvector/pgvector:pg16 镜像已预装扩展文件，此处只需在业务库中 CREATE
CREATE EXTENSION IF NOT EXISTS vector;

-- 验证扩展安装结果（可在容器日志中确认）
DO $$
BEGIN
    RAISE NOTICE 'pgvector extension version: %', (
        SELECT extversion FROM pg_extension WHERE extname = 'vector'
    );
END $$;

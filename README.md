# 基于多模态识别的商品图片分析与推荐系统

面向电商购物场景的商品图片分析与智能推荐 Demo。用户可以上传商品图片、输入购物需求，系统会识别商品类别、颜色、风格和核心特征，并结合商品知识库生成卖点总结、适用场景、对比分析和购买建议。

## 功能概览

- 商品图片上传与预览
- 购物需求输入
- 图片颜色、亮度、视觉风格等基础特征识别
- 基于规则和商品知识库的类别推断
- 推荐理由、适用场景、购买建议自动生成
- 相似商品推荐
- 预留大模型增强接口，便于后续接入多模态模型

## 技术栈

- 后端：Python、FastAPI、Pillow
- 前端：HTML、CSS、JavaScript
- 数据：JSON 商品知识库
- 可选增强：OpenAI 或其他多模态大模型 API

## 项目结构

```text
shop_image/
  backend/
    app/
      main.py              # FastAPI 入口
      schemas.py           # 接口数据结构
      services/
        image_analyzer.py  # 图片基础特征分析
        recommender.py     # 推荐逻辑
        knowledge_base.py  # 商品知识库读取
    data/
      products.json        # 示例商品知识库
  frontend/
    index.html
    styles.css
    app.js
  requirements.txt
  .env.example
  .gitignore
```

## 快速开始

1. 创建并激活虚拟环境：

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 启动后端：

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

4. 浏览器打开：

```text
frontend/index.html
```

## API

### `POST /api/analyze`

表单参数：

- `image`：商品图片文件，可选
- `need`：用户购物需求，可选

返回内容包括：

- 商品类别
- 主色与视觉特征
- 风格标签
- 卖点总结
- 适用场景
- 购买建议
- 相似商品推荐

### `GET /api/products`

返回当前示例商品知识库。

## 后续计划

- 接入真实商品数据库
- 引入多模态模型提升类别与属性识别准确率
- 增加多轮对话推荐
- 支持用户偏好画像
- 增加商品评论摘要和参数对比
- 支持部署到云服务并配置 CI


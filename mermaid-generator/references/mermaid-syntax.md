# Mermaid 语法参考

Mermaid 核心图表类型的语法速查。

## Flowchart（流程图）

### 基础语法

```mermaid
flowchart LR
    A[方形节点] --> B(圆角节点)
    B --> C{菱形节点}
    C -->|是| D[结果1]
    C -->|否| E[结果2]
```

### 方向

- `LR` - 左到右
- `TB` / `TD` - 上到下
- `RL` - 右到左
- `BT` - 下到上

### 节点形状

```mermaid
flowchart LR
    A[矩形]
    B(圆角矩形)
    C([体育场形])
    D[[子程序]]
    E[(数据库)]
    F((圆形))
    G>标签]
    H{菱形}
    I{{六边形}}
    J[/平行四边形/]
    K[\平行四边形\]
    L[/梯形\]
    M[\梯形/]
```

### 连接线

```mermaid
flowchart LR
    A --> B
    C --- D
    E -.-> F
    G ==> H
    I --文字--> J
    K -.文字.-> L
    M ==文字==> N
```

### Subgraph（分组）

```mermaid
flowchart TB
    subgraph id1 [分组标题]
        A --> B
    end

    subgraph id2 [另一组]
        C --> D
    end

    id1 --> id2
```

---

## Sequence Diagram（时序图）

### 基础语法

```mermaid
sequenceDiagram
    participant A as 用户
    participant B as 系统

    A->>B: 请求
    B-->>A: 响应
```

### 参与者

```mermaid
sequenceDiagram
    actor A as 👤 用户
    participant B as 📱 App
    participant C as 🔧 API
```

### 消息类型

```mermaid
sequenceDiagram
    A->>B: 实线箭头
    A-->>B: 虚线箭头
    A-)B: 异步消息
    A-xB: 丢失消息
```

### 激活框

```mermaid
sequenceDiagram
    A->>+B: 激活 B
    B-->>-A: 停用 B
```

### 循环和条件

```mermaid
sequenceDiagram
    loop 每天
        A->>B: 检查更新
    end

    alt 有更新
        B->>A: 推送通知
    else 无更新
        B->>A: 无操作
    end

    opt 可选流程
        A->>B: 额外请求
    end
```

### Note

```mermaid
sequenceDiagram
    Note left of A: 左侧注释
    Note right of B: 右侧注释
    Note over A,B: 跨越注释
```

---

## Class Diagram（类图）

### 基础语法

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }

    class Dog {
        +String breed
        +bark()
    }

    Animal <|-- Dog
```

### 可见性

- `+` Public
- `-` Private
- `#` Protected
- `~` Package

### 关系类型

```mermaid
classDiagram
    A <|-- B : 继承
    C *-- D : 组合
    E o-- F : 聚合
    G <-- H : 关联
    I <.. J : 依赖
    K <|.. L : 实现
```

### 注解

```mermaid
classDiagram
    class Animal {
        <<interface>>
    }

    class Dog {
        <<service>>
    }
```

### Note

```mermaid
classDiagram
    class Animal
    note for Animal "这是动物基类"
```

---

## 常用 Emoji

### 系统组件

- 📱 移动端
- 💻 PC 端
- 🌐 浏览器
- 🔧 后端服务
- 💾 数据库
- 📊 数据分析
- 🔐 安全模块
- ⚙️ 配置

### 流程阶段

- 📥 输入
- ⚙️ 处理
- 📤 输出
- 🚀 启动
- 🛑 停止
- ✅ 成功
- ❌ 失败
- ⚠️ 警告

### 操作动作

- 📝 编辑
- 🔍 搜索
- 📂 文件
- 📁 文件夹
- 🗂️ 归档
- 🔄 同步
- ⬇️ 下载
- ⬆️ 上传

### 用户角色

- 👤 用户
- 👨‍💼 管理员
- 🤖 机器人
- 👨‍💻 开发者
- 📞 客服

---

## 注意事项

### 避免的语法

❌ **不要使用空格**在节点 ID 中：

```
Bad: A[User Service]
Good: UserService[User Service]
```

❌ **不要在标签中使用裸露的括号**：

```
Bad: A -->|O(1) lookup| B
Good: A -->|"O(1) lookup"| B
```

❌ **避免保留关键字**作为节点 ID：

```
Bad: end[End]
Good: endNode[End]
```

### 最佳实践

✅ **Subgraph 使用显式 ID**：

```mermaid
flowchart TB
    subgraph auth [认证流程]
        A --> B
    end
```

✅ **复杂标签用引号**：

```mermaid
flowchart LR
    A["步骤 1: 初始化"]
```

✅ **让主题处理颜色**（不要手动设置样式）：

```
Bad: style A fill:#fff
Good: 使用 subgraph 分组
```

# Nonebot 漂流瓶插件
* 安装
    -
    - 使用 `pip install nonebot_plugin_bottle`
    - 使用 `nb plugin install nonebot_plugin_bottle`
* 指令 (前应带指令前缀)
    - 
    - `扔漂流瓶` [文本/图片] 或 `扔漂流瓶` 后一条消息跟漂流瓶内容
    - `寄漂流瓶` [文本/图片] （同`扔漂流瓶`，防止指令冲突用）
    - `捡漂流瓶` 
    - `评论漂流瓶` [漂流瓶编号] [文本]
    - `举报漂流瓶` [漂流瓶编号]
    - `查看漂流瓶` [漂流瓶编号]
    - `删除漂流瓶` [漂流瓶编号]
    - `我的漂流瓶`
    - SUPERUSER指令：
        - `清空漂流瓶`
        - `恢复漂流瓶 [漂流瓶编号]`
        - `删除漂流瓶评论` [漂流瓶编号] [QQ号]
        - `漂流瓶白名单` [QQ / 群聊] [QQ号 / 群号]
        - `漂流瓶黑名单` [QQ / 群聊 / 举报] [QQ号 / 群号]
        - `漂流瓶详情` [漂流瓶编号]
* 功能须知
    - 所有用户：
        - `扔漂流瓶`指令无字数限制，如需要可在代码中修改。若只说了扔漂流瓶，则插件将会监听用户的下一条消息。
        - `捡漂流瓶`若捡到的漂流瓶存在回复，则会显示最近三条(默认)，使用`查看漂流瓶`查看所有回复
        - `查看漂流瓶`为保证随机性，无评论时不展示漂流瓶内容，可在代码中修改。漂流瓶的发送者可以通过本指令查看内容，无论有无评论。
        - `评论漂流瓶`评论内容将通过该瓶子扔出的方式告诉扔出瓶子的人
        - `举报漂流瓶`五次(默认)后将自动删除，举报成功后会私聊SUPERUSER漂流瓶详情内容
        - `删除漂流瓶`漂流瓶发送者可以删除自己扔出的漂流瓶。二次确认会触发删除操作的指令为：`是/Y/Yes/y/yes`。其他的均直接取消操作。
    - SUPERUSER:
        - `删除漂流瓶`可以删除指定漂流瓶
        - `清空漂流瓶`顾名思义，使用需谨慎
        - `恢复漂流瓶`可以恢复被删除的漂流瓶
        - `删除漂流瓶评论`可删除该发送者在该瓶的所有评论
        - `漂流瓶详情`将会发送漂流瓶发送者的QQ号和群号，所有回复人的QQ号
        - `漂流瓶黑名单`中`举报`选项是指`举报漂流瓶`的使用权限
        - `漂流瓶数据库`存放在`data/bottle/data.json`中
        - `权限数据库` 存放在`data/bottle/permissionsList.json`中
        - `漂流瓶屏蔽词` 存放在`data/bottle/curse.json`中，**支持热更改**
* 权限控制
    -
    - 所有非SUPERUSER指令均受到权限控制
    - `功能冷却开关`：插件默认开启，可在`data/bottle/permissionsList.json`中修改`enableCooldown`bool值(True/False)
    - `功能冷却`：插件默认 30 秒冷却，可在`data/bottle/permissionsList.json`中修改`cooldownTime`值  
    - 白名单优先级高于黑名单和冷却名单

* 文字审核API配置（可选`百度审核`或`简单屏蔽词审核`）
    - 
    - 百度审核
        - 在[百度智能云](https://cloud.baidu.com/doc/ANTIPORN/s/dkk6wyt3z)中申请`API_KEY`和`secret_key`
        - 在`.env.*`文件中填写`nonebot_plugin_bottle_api_key`与`nonebot_plugin_bottle_secret_key`，参考[NoneBot2配置方式](https://v2.nonebot.dev/docs/tutorial/configuration#%E9%85%8D%E7%BD%AE%E6%96%B9%E5%BC%8F)
        - 不配置该项则进行`简单屏蔽词审核`
    - 简单屏蔽词审核
        - 在`data/bottle/curse.json`手动填写json文件（`list`格式，文件不存在则调用审核后生成）
        - 判断方法为若文字存在屏蔽词，则审核失败
        - 格式：  
            ```
            ["屏蔽词1","屏蔽词2"]
            ```
        - 屏蔽词推荐（需要手动更改）：[防嘴臭插件](https://github.com/tkgs0/nonebot-plugin-antiinsult/blob/main/nonebot_plugin_antiinsult/curse.json)
        - 若为空列表则不进行审核

* 配置文件（.env.*）
    -
    | 配置项 | 配置名 | 变量类型 |  默认值 |
    |:--------|:----------|:-------------:|------:|
    | API KEY | nonebot_plugin_bottle_api_key | str | "" |
    | SECRET KEY | nonebot_plugin_bottle_secret_key | str | "" |
    | 是否缓存图片 | nonebot_plugin_bottle_local_storage | bool | True |


* 更新日志
    -  
    - ***重构版本*** 1.0.0 [2023-3-10] [#32](https://github.com/Todysheep/nonebot_plugin_bottle/issues/32) [@LambdaYH](https://github.com/LambdaYH)
        - 使用`nonebot_plugin_datastore`重构
        - 异步读取违禁词文件
        - 异步读取违禁词文件
        - 启动时将旧json数据迁移
        - 优化图片缓存
        - 调整require位置
    - 0.2.7 [2023-2-25]
        - `举报漂流瓶`现在可以禁止某人使用了（`漂流瓶黑名单 举报 [qq号]`）
        - 新增`恢复漂流瓶`指令，可以恢复被删除的漂流瓶
    - 0.2.6 [2023-2-24]
        - `举报漂流瓶`修复了单人可以举报多次的问题
        - [ ] 格式化漂流瓶输出

    <details>
        <summary>更多更新</summary>

        - 0.2.5 [2023-2-24]
            - 更改`requests`请求方式为`httpx` [#29](https://github.com/Todysheep/nonebot_plugin_bottle/issues/29)
            - 适配`metadata` #29
            - 💥破坏性更新 `api_key`与`secret_key`将在`.env.*`中填写（详见上方） [#29](https://github.com/Todysheep/nonebot_plugin_bottle/issues/29)
        - 0.2.4
            - 现在开始记录扔漂流瓶的时间，旧版本的漂流瓶时间为`0000-00-00 00:00:00`,使用`查看漂流瓶可以查看具体时间`
        - 0.2.3
            - `删除漂流瓶`现在所有人可用，并进行了一些权限限制
            - `捡漂流瓶`函数更新了递归上限防止无限递归
            - 要求后续内容输入的所有指令现需要空格隔开
        - 0.2.2
            - 更新`简单屏蔽词`功能，在未配置`api_key`和`secret_key`时进行简单的屏蔽词审核，而不是跳过审核
            - 现在评论也需要经过文字审核
            - 增加存放屏蔽词文件`data/bottle/curse.json`
        - 0.2.1
            - 增加删除漂流瓶评论功能
        - 0.2.0
            - 停止使用`black_group`
            - 增加使用CD，黑/白名单群组
            - 开始记录回复人QQ号（仅SUPERUSER使用`漂流瓶详情`可见）
        - 0.1.8
            - 增加`request`库要求
            - 丢出漂流瓶后展示漂流瓶编号
        - 0.1.7
            - 新增json项`key`，将不使用`del`删除漂流瓶，而保留原漂流瓶数据便于管理者查看
            - 新增json项`group_name`,`username`，将在API无法获取信息时使用
        - 0.1.6
            - 新增配置项`api_key`,'secret_key'，用于文本审核
            - 新增配置项`black_group`，用于屏蔽特定群聊

    </details>

* 特别感谢
    -
    - **[@LambdaYH](https://github.com/LambdaYH)** PR了~~一个现有作者根本看不懂的~~重构版本 (1.0.0)
    - [@a563696823](https://github.com/a563696823) 适配commit，更改config填写，适配httpx
    - [@MTmin](https://github.com/MTmin) 多机器人版本
    - [@Sevenyine](https://github.com/Sevenyine) 发了~~114514条~~issue

* 效果展示
    -
    ![image](https://user-images.githubusercontent.com/97968466/191049794-1b409436-fd70-43d9-8dcb-3575e82fd69b.png)  
    ![image](https://user-images.githubusercontent.com/97968466/213113862-e6c7568b-8686-4e97-8f83-7354ff1cb704.png)  
    ![image](https://user-images.githubusercontent.com/97968466/191052704-1b5ec89d-7a49-40d6-a5d9-b0a0171c730e.png)  
    ![image](https://user-images.githubusercontent.com/97968466/191049649-2e8d8555-f285-470f-9f7b-f5a0994341ee.png)  

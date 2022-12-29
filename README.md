# Nonebot 漂流瓶插件
* 安装
    -
    - 使用 `pip install nonebot_plugin_bottle`
    - 使用 `nb plugin install nonebot_plugin_bottle`
* 指令 (前应带指令前缀)
    - 
    - `扔漂流瓶` [文本/图片]
    - `寄漂流瓶` [文本/图片] （同`扔漂流瓶`，防止指令冲突用）
    - `捡漂流瓶` 
    - `评论漂流瓶` [漂流瓶编号] [文本]
    - `举报漂流瓶` [漂流瓶编号]
    - `查看漂流瓶` [漂流瓶编号]
    - SUPERUSER指令：
        - `清空漂流瓶`
        - `删除漂流瓶 [漂流瓶编号]`
* 功能须知
    -
    - `扔漂流瓶`指令无字数限制，如需要可在代码中修改
    - `捡漂流瓶`若捡到的漂流瓶存在回复，则会显示最近三条(默认)，使用`查看漂流瓶`查看所有回复
    - `查看漂流瓶`为保证随机性，无评论时不展示漂流瓶内容，可在代码中修改
    - `举报漂流瓶`五次(默认)后将自动删除
    - `清空漂流瓶`无确认过程，使用需谨慎
    - `漂流瓶数据库`存放在`data/bottle/data.json`中
    - `黑名单群组`可在`__init__.py`同级路径`config.py`中添加
* 文字审核API配置（可选）
    - 
    - 在[百度智能云](https://cloud.baidu.com/doc/ANTIPORN/s/dkk6wyt3z)中申请`API_KEY`和`secret_key`
    - 在`config.py`中填入即可
    - 不配置该项则不进行审核操作

* 已知bug
    -
    - 第一次加载该插件时无法正常使用（重启后恢复）

* 更新日志
    - 0.1.8
        - 增加`request`库要求
        - 丢出漂流瓶后展示漂流瓶编号
    - 0.1.7
        - 新增json项`key`，将不使用`del`删除漂流瓶，而保留原漂流瓶数据便于管理者查看
        - 新增json项`group_name`,`username`，将在API无法获取信息时使用
    - 0.1.6
        - 新增配置项`api_key`,'secret_key'，用于文本审核
        - 新增配置项`black_group`，用于屏蔽特定群聊
* 效果展示
    -
    ![image](https://user-images.githubusercontent.com/97968466/191049794-1b409436-fd70-43d9-8dcb-3575e82fd69b.png)  
    ![image](https://user-images.githubusercontent.com/97968466/191052704-1b5ec89d-7a49-40d6-a5d9-b0a0171c730e.png)  
    ![image](https://user-images.githubusercontent.com/97968466/191250967-b702cf6e-c0c8-48b6-8ecb-68108bfc6eab.png)  
    ![image](https://user-images.githubusercontent.com/97968466/191049649-2e8d8555-f285-470f-9f7b-f5a0994341ee.png)  

# Nonebot 漂流瓶插件
* 安装
    -
    - 使用 `pip install nonebot_plugin_bottle`
    - 使用 `nb plugin install nonebot_plugin_bottle`
* 指令 (前应带指令前缀)
    - 
    - `扔漂流瓶` [文本/图片]
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
    - `评论漂流瓶`若机器人有被回复人好友，会发送被回复通知
    - `举报漂流瓶`五次(默认)后将自动删除
    - `清空漂流瓶`无确认过程，使用需谨慎
    - `漂流瓶数据库`存放在`data/bottle/data.json`中
* 已知bug
    -
    - 第一次加载该插件时无法正常使用（重启后恢复）
* 效果展示
    -
    ![image](https://user-images.githubusercontent.com/97968466/190886998-5a9fba6d-9dd5-4210-9162-26a997359414.png)
    ![image](https://user-images.githubusercontent.com/97968466/190887020-406c9bc8-db1f-4a21-8afc-b3fda9ad4940.png)
    ![image](https://user-images.githubusercontent.com/97968466/190887060-a45442c1-59c8-42ba-9930-8ca05f32fb58.png)


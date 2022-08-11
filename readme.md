# Discord 聊天室機器人
本聊天室機器人是基於[discord-py-interactions](https://github.com/interactions-py/library)套件，為遊戲王玩家設計之聊天室機器人，目前功能：
- 查詢台大卡牌研究社上位排組及圓餅圖
- 針對ydk檔牌組管理（新增、檢視、刪除）
## 指令
`/win_deck`

查詢台大卡牌研究社每周上位排組Meta比例及餅圖。
<https://ntucgm.blogspot.com/search/label/OCG%E8%B3%BD%E4%BA%8B-Meta%E5%B1%95%E6%9C%9B>

<hr/>

`/my_deck create`

建立牌組：上傳YDK檔格式。[YDK格式說明](https://ews.ink/tech/game-yu_gi_oh-deck/)

YDK檔格式如下：
```
#created by ...
#main
<card_code>
#extra
<card_code>
!side
<card_code>
```

說明：

\#main 主牌組

\#extra 額外排組

!side 備用排組

\<card_code\> 表示為遊戲王卡牌中的八位數卡片密碼，或者可以自訂義先行卡。

<hr/>

`/my_deck list`

檢視牌組：選擇使用者已儲存的牌組，並依照牌組種類列出卡名和張數

<hr/>

`/my_deck delete`

刪除牌組：選擇使用者已儲存的牌組，進行刪除。
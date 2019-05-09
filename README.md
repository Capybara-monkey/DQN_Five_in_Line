# DQN_Five_in_Line

### Deep Q-Networkを用いた五目並べ
#### コンセプト
* 対戦すればするほど強くなるエージェント。
* 対戦が終わると，Replay Bufferとして保存。学習に利用。


#### スタート画面
![ホーム](https://github.com/natsu-summer72/DQN_Five_in_Line/blob/dev/15x15/example/home.png)

#### プレイ中画面
![playing](https://github.com/natsu-summer72/DQN_Five_in_Line/blob/dev/15x15/example/playing.png)

#### 結果画面
![result](https://github.com/natsu-summer72/DQN_Five_in_Line/blob/dev/15x15/example/result.png)



#### 課題
* 現状は，エージェントが弱すぎる。
* ランダムな行動では，勝つことができず，学習が進行しないため，エージェント(DQN)の初期状態に工夫が必要。

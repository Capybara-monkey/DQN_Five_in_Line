from django.shortcuts import render
from django.views import View
from .models import Table

import json
import numpy as np

class GameView(View):
    def get(self, request):
        table = Table.objects.get(data_id=1).tb
        table = json.loads(table)
        self.params = {}
        """数字->○×の変換"""
        self.num_to_symbol(table)
        return render(request, "game/game.html", self.params)

    def post(self, request):
        data = Table.objects.get(data_id=1)
        table = json.loads(data.tb)
        self.params = {}

        """Clearボタンが押された場合は初期化を行う"""
        if "clear" in request.POST:
            table = [0, 0, 0, 0, 0, 0, 0, 0, 0]
            data.tb = json.dumps(table)
            data.save()
            """数字->○×の変換"""
            self.num_to_symbol(table)
            return render(request, "game/game.html", self.params)

        """ユーザーの入力を反映させる。"""
        for i in range(9):
            self.params["b"+str(i)] = table[i]
        for i in range(9):
            if "b"+ str(i) in request.POST:
                if not table[i] == 0:  #既に選択されているマスの場合
                    self.num_to_symbol(table)
                    return render(request, "game/game.html", self.params)
                table[i] = 1
                self.params["b"+str(i)] = 1

        """ユーザーの勝利判定"""
        if self.check_win(1, table):
            self.params["result"] = "Win"
            data.tb = json.dumps(table)
            data.save()
            """数字->○×の変換"""
            self.num_to_symbol(table)
            return render(request, "game/game.html", self.params)

        """引き分け判定"""
        if self.check_draw(table):
            self.params["result"] = "Draw"
            data.tb = json.dumps(table)
            data.save()
            """数字->○×の変換"""
            self.num_to_symbol(table)
            return render(request, "game/game.html", self.params)



        """CPUの入力を反映させる。"""
        while True:
            action = np.random.randint(0,9)
            if table[action] == 0:
                break

        table[action] = -1
        self.params["b"+str(action)] = -1

        if self.check_win(-1, table):
            self.params["result"] = "Lose"

        data.tb = json.dumps(table)
        data.save()

        self.num_to_symbol(table)
        return render(request, "game/game.html", self.params)

    def check_win(self, user, table):
        """勝敗の判定  userは，1がユーザー -1 がCPU"""
        for i in range(3):
            if table[3*i]+table[3*i+1]+table[3*i+2]==3*user:  #横
                return True
            if table[i]+table[3+i]+table[6+i]==3*user:  #縦
                return True
        if table[0]+table[4]+table[8]==3*user:  #斜め(左上から)
            return True
        if table[2]+table[4]+table[6]==3*user:  #斜め(右上から)
            return True

        return False

    def check_draw(self, table):
        """全てのマスが埋まっているかを判定"""
        for i in range(9):
            if table[i] == 0:
                return False
        return True

    def num_to_symbol(self, table):
        """render用にtableの数字を記号に変換"""
        for i in range(9):
            if table[i] == 0:
                self.params["b"+str(i)] = " "
            elif table[i] == 1:
                self.params["b"+str(i)] = "○"
            else:
                self.params["b"+str(i)] = "×"

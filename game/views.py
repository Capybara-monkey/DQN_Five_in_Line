from django.shortcuts import render, redirect
from django.views import View
from .models import Table
from django.views.generic import TemplateView

import json
import numpy as np

NUM = 25


INIT_TABLE = [0, 0, 0, 0, 0,
         0, 0, 0, 0, 0,
         0, 0, 0, 0, 0,
         0, 0, 0, 0, 0,
         0, 0, 0, 0, 0]

class GameView(View):
    def get(self, request):
        table = Table.objects.get(data_id=1).tb
        table = json.loads(table)
        self.params = {}
        """数字->○×の変換"""
        self.num_to_symbol(table)
        return render(request, "game/game5.html", self.params)

    def post(self, request):
        data = Table.objects.get(data_id=1)
        table = json.loads(data.tb)
        self.params = {}

        """Clearボタンが押された場合は初期化を行う"""
        if "clear" in request.POST:
            table = [0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0,
                     0, 0, 0, 0, 0]
            data.tb = json.dumps(table)
            data.save()
            """数字->○×の変換"""
            self.num_to_symbol(table)
            return render(request, "game/game5.html", self.params)

        """ユーザーの入力を反映させる。"""
        for i in range(NUM):
            self.params["b"+str(i)] = table[i]
        for i in range(NUM):
            if "b"+ str(i) in request.POST:
                if not table[i] == 0:  #既に選択されているマスの場合
                    self.num_to_symbol(table)
                    return render(request, "game/game5.html", self.params)
                table[i] = 1
                self.params["b"+str(i)] = 1

        """ユーザーの勝利判定"""
        if self.check_win(1, table):
            self.params["result"] = "Win"
            data.tb = json.dumps(table)
            data.save()
            """数字->○×の変換"""
            self.num_to_symbol(table)
            return redirect(to="win")


        """引き分け判定"""
        if self.check_draw(table):
            self.params["result"] = "Draw"
            data.tb = json.dumps(table)
            data.save()
            """数字->○×の変換"""
            self.num_to_symbol(table)
            return redirect(to="draw")



        """CPUの入力を反映させる。"""
        while True:
            action = np.random.randint(0,NUM)
            if table[action] == 0:
                break

        table[action] = -1
        self.params["b"+str(action)] = -1

        if self.check_win(-1, table):
            self.params["result"] = "Lose"
            return redirect("lose")

        data.tb = json.dumps(table)
        data.save()

        self.num_to_symbol(table)
        return render(request, "game/game5.html", self.params)

    def check_win(self, user, table):
        """勝敗の判定  userは，1がユーザー -1 がCPU"""
        for k in range(3):  #縦に移動
            for j in range(3):  #横に移動
                for i in range(3):
                    if table[5*i+j+5*k]+table[5*i+j+5*k+1]+table[5*i+j+5*k+2]==3*user:  #横
                        print("横")
                        return True
                    if table[i+j+5*k]+table[5+i+j+5*k]+table[10+i+j+5*k]==3*user:  #縦
                        print("縦")
                        return True
                if table[0+j+5*k]+table[6+j+5*k]+table[12+j+5*k]==3*user:  #斜め(左上から)
                    print("左ななめ")
                    return True
                if table[2+j+5*k]+table[6+j+5*k]+table[10+j+5*k]==3*user:  #斜め(右上から)
                    print("右ななめ")
                    return True
        return False

    def check_draw(self, table):
        """全てのマスが埋まっているかを判定"""
        for i in range(NUM):
            if table[i] == 0:
                return False
        return True

    def num_to_symbol(self, table):
        """render用にtableの数字を記号に変換"""
        for i in range(NUM):
            if table[i] == 0:
                self.params["b"+str(i)] = " "
            elif table[i] == 1:
                self.params["b"+str(i)] = "○"
            else:
                self.params["b"+str(i)] = "×"
        return table


class WinView(TemplateView):
    template_name = "game/result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["result"] = "You Win"
        data = Table.objects.get(data_id=1)
        table = json.loads(data.tb)
        table = self.num_to_symbol(table)
        for i in range(NUM):
            context["b"+str(i)] = table[i]
        data.tb = json.dumps(INIT_TABLE)
        data.save()
        return context

    def num_to_symbol(self, table):
        """render用にtableの数字を記号に変換"""
        for i in range(NUM):
            if table[i] == 0:
                table[i] = " "
            elif table[i] == 1:
                table[i] = "○"
            else:
                table[i]= "×"

        return table

class LoseView(TemplateView):
    template_name = "game/result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["result"] = "You Lose"
        data = Table.objects.get(data_id=1)
        table = json.loads(data.tb)
        table = self.num_to_symbol(table)
        for i in range(NUM):
            context["b"+str(i)] = table[i]
        data.tb = json.dumps(INIT_TABLE)
        data.save()
        return context

    def num_to_symbol(self, table):
        """render用にtableの数字を記号に変換"""
        for i in range(NUM):
            if table[i] == 0:
                table[i] = " "
            elif table[i] == 1:
                table[i] = "○"
            else:
                table[i] = "×"
        return table


class DrawView(TemplateView):
    template_name = "game/result.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["result"] = "Draw"
        data = Table.objects.get(data_id=1)
        table = json.loads(data.tb)
        table = self.num_to_symbol(table)
        for i in range(NUM):
            context["b"+str(i)] = table[i]
        data.tb = json.dumps(INIT_TABLE)
        data.save()
        return context

    def num_to_symbol(self, table):
        """render用にtableの数字を記号に変換"""
        for i in range(NUM):
            if table[i] == 0:
                table[i] = " "
            elif table[i] == 1:
                table[i] = "○"
            else:
                table[i] = "×"
        return table

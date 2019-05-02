from django.shortcuts import render, redirect
from django.views import View
from .models import Table, PlayNum, Memory
from django.views.generic import TemplateView
from .dqn_model.DQN import DQN

import json
import numpy as np

NUM = 25
INIT_TABLE = [0, 0, 0, 0, 0,
         0, 0, 0, 0, 0,
         0, 0, 0, 0, 0,
         0, 0, 0, 0, 0,
         0, 0, 0, 0, 0]

DQNAgent = DQN()


class GameView(View):
    def get(self, request):
        table = Table.objects.get(data_id=1).tb
        table = json.loads(table)
        num = PlayNum.objects.get(data_id=1).num
        self.params = {"play_num": num}
        """数字->○×の変換"""
        self.num_to_symbol(table)
        return render(request, "game/game5.html", self.params)

    def post(self, request):
        data = Table.objects.get(data_id=1)
        table = json.loads(data.tb)
        play_num = PlayNum.objects.get(data_id=1)
        num = play_num.num
        self.params = {"play_num": num}

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
            num += 1
            play_num.num = num
            play_num.save()
            DQNAgent.save_model()
            return redirect(to="win")

        """引き分け判定"""
        if self.check_draw(table):
            self.params["result"] = "Draw"
            data.tb = json.dumps(table)
            data.save()
            num += 1
            play_num.num = num
            play_num.save()
            DQNAgent.save_model()
            return redirect(to="draw")

        """CPUの入力を反映させる。"""
        action = DQNAgent.get_action(np.array(table))
        if not (table[action]==0):
            while True:
                action = np.random.randint(0, NUM)
                if table[action] == 0:
                    break

        state = table
        table[action] = -1
        new_state = table
        self.params["b"+str(action)] = -1
        data.tb = json.dumps(table)
        data.save()

        if self.check_win(-1, table):
            self.params["result"] = "Lose"
            num += 1
            play_num.num = num
            play_num.save()
            DQNAgent.save_model()
            self.pop_memory(state, action,new_state, win=True)
            return redirect("lose")

        self.num_to_symbol(table)
        return render(request, "game/game5.html", self.params)

    def pop_memory(self, state, action, new_state, win=False, lose=False, miss=False):
        reward = 0
        done = False
        if win:
            reward = 1
            done = True
        elif lose:
            reward = -1
            done = True
        elif miss:
            reward = -1
        DQNAgent.remember(state, action, reward, new_state, done)

    def check_win(self, user, table):
        """勝敗の判定  userは，1がユーザー -1 がCPU"""
        for k in range(3):  #縦に移動
            for j in range(3):  #横に移動
                for i in range(3):
                    if table[5*i+j+5*k]+table[5*i+j+5*k+1]+table[5*i+j+5*k+2]==3*user:  #横
                        print(table)
                        print("横")
                        return True
                    if table[i+j+5*k]+table[5+i+j+5*k]+table[10+i+j+5*k]==3*user:  #縦
                        print(table)
                        print("縦")
                        return True
                if table[0+j+5*k]+table[6+j+5*k]+table[12+j+5*k]==3*user:  #斜め(左上から)
                    print(table)
                    print("左ななめ")
                    return True
                if table[2+j+5*k]+table[6+j+5*k]+table[10+j+5*k]==3*user:  #斜め(右上から)
                    print(table)
                    print("右ななめ")
                    return True
        return False

    def check_draw(self, table):
        """全てのマスが埋まっているかを判定"""
        for i in range(NUM):
            if not(table[i] == 0):
                return False
        return True

    def num_to_symbol(self, table):
        """rendering用にtableの数字を記号に変換"""
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
        """rendering用にtableの数字を記号に変換"""
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
        """rendering用にtableの数字を記号に変換"""
        for i in range(NUM):
            if table[i] == 0:
                table[i] = " "
            elif table[i] == 1:
                table[i] = "○"
            else:
                table[i] = "×"
        return table

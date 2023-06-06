from botoes import ImageButton, LabelButton
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
import requests
from kivy.app import App
from functools import partial


class BannerVendedor(FloatLayout):

    def __init__(self, id_vendedor):
        meu_app = App.get_running_app()
        self.rows = 1
        super().__init__()

        with self.canvas:
            Color(rgb=(0, 0, 0, 1))
            self.rec = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.atualizar_rec, size=self.atualizar_rec)

        link = "https://app-kivy-hashtag-default-rtdb.firebaseio.com/"
        requisicao = requests.get(f'{link}.json?orderBy="id_vendedor"&equalTo="{id_vendedor}"')
        requisicao_dic = requisicao.json()
        valores = list(requisicao_dic.values())[0]

        imagem = ImageButton(pos_hint={"right": 0.4, "top": 0.9}, size_hint=(0.3, 0.8),
                             source=f'icones/fotos_perfil/{valores["avatar"]}',
                             on_release=partial(meu_app.carregar_vendas_vendedor, valores))
        label_id = LabelButton(text=f'ID vendedor: {id_vendedor}', size_hint=(0.5, 0.5),
                               pos_hint={"right": 0.9, "top": 0.9},
                               on_release=partial(meu_app.carregar_vendas_vendedor, valores))
        label_vendas = LabelButton(text=f'Total Vendas: R${float(valores["total_vendas"]):,.2f}',
                                   size_hint=(0.5, 0.5), pos_hint={"right": 0.9, "top": 0.6},
                                   on_release=partial(meu_app.carregar_vendas_vendedor, valores))

        self.add_widget(imagem)
        self.add_widget(label_id)
        self.add_widget(label_vendas)


    def atualizar_rec(self, *args):
        self.rec.pos = self.pos
        self.rec.size = self.size

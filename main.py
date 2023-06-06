from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests
from bannervenda import BannerVenda
from bannervendedor import BannerVendedor
import os
from functools import partial
from myfirebase import MyFireBase
from datetime import date

GUI = Builder.load_file("main.kv")
link = "https://app-kivy-hashtag-default-rtdb.firebaseio.com/"


class MainApp(App):
    cliente = None
    produto = None
    unidade = None

    def build(self):
        self.firebase = MyFireBase()
        return GUI

    def on_start(self):
        arquivos = os.listdir("icones/fotos_perfil")
        pagina_fotos = self.root.ids['fotoperfil']
        lista_fotos = pagina_fotos.ids['lista_fotos_perfil']
        for arquivo in arquivos:
            foto = ImageButton(source=f"icones/fotos_perfil/{arquivo}",
                               on_release=partial(self.mudar_foto_perfil, arquivo))
            lista_fotos.add_widget(foto)

        # carregar as fotos dos clientes
        arq_clientes = os.listdir("icones/fotos_clientes")
        pagina_add_venda = self.root.ids['adicionarvendas']
        lista_clientes = pagina_add_venda.ids['lista_clientes']
        for foto_cliente in arq_clientes:
            imagem_cliente = ImageButton(source=f"icones/fotos_clientes/{foto_cliente}",
                                         on_release=partial(self.selecionar_cliente, foto_cliente))
            label_cliente = LabelButton(text=foto_cliente[:-4].capitalize(),
                                        on_release=partial(self.selecionar_cliente, foto_cliente))
            lista_clientes.add_widget(imagem_cliente)
            lista_clientes.add_widget(label_cliente)

        # carregar as fotos dos produtos
        arq_produtos = os.listdir("icones/fotos_produtos")
        lista_produtos = pagina_add_venda.ids['lista_produtos']
        for foto_produto in arq_produtos:
            imagem_produto = ImageButton(source=f"icones/fotos_produtos/{foto_produto}",
                                         on_release=partial(self.selecionar_produto, foto_produto))
            label_produto = LabelButton(text=foto_produto[:-4],
                                        on_release=partial(self.selecionar_produto, foto_produto))
            lista_produtos.add_widget(imagem_produto)
            lista_produtos.add_widget(label_produto)

        # carregar data
        pagina_add_venda.ids['label_data'].text = f"Data: {date.today().strftime('%d/%m/%Y')}"

        self.carregar_infos_usuario()

    def carregar_infos_usuario(self):
        try:
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # Pegar informações do banco de dados
            requisicao = requests.get(f'{link}{self.local_id}.json?auth={self.id_token}')
            requisicao_dic = requisicao.json()

            # Preencher foto de perfil
            avatar = requisicao_dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids['foto_perfil']
            foto_perfil.source = f'icones/fotos_perfil/{avatar}'

            # Preencher id do vendedor
            id_vendedor = requisicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pag_ajustes = self.root.ids['ajustespage']
            pag_ajustes.ids['id_vendedor'].text = f"Seu ID único: {id_vendedor}"

            # Preencher total de vendas
            total_vendas = float(requisicao_dic['total_vendas'])
            self.total_vendas = total_vendas
            pag_home = self.root.ids['homepage']
            pag_home.ids['label_total_vendas'].text = f"[color=#000000]Total de vendas:[/color] [b]R${total_vendas}[/b]"

            # Preencher lista de vendas
            if "vendas" in requisicao_dic:
                if len(requisicao_dic["vendas"]) > 0:
                    vendas = requisicao_dic["vendas"]
                    self.vendas = vendas
                    pagina_homepage = self.root.ids['homepage']
                    lista_vendas = pagina_homepage.ids['lista_vendas']
                    for id_venda in vendas:
                        venda = vendas[id_venda]
                        banner_venda = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                                   produto=venda['produto'], foto_produto=venda['foto_produto'],
                                                   preco=float(venda['preco']), quantidade=float(venda['quantidade']),
                                                   unidade=venda['unidade'], data=venda['data'])
                        lista_vendas.add_widget(banner_venda)

            # preencher equipe do usuário
            if "equipe" in requisicao_dic:
                self.equipe = requisicao_dic["equipe"]
                if len(requisicao_dic["equipe"]) > 0:
                    lista_equipe = self.equipe.split(",")
                    pagina_vendedores = self.root.ids['listarvendedores']
                    lista_vendedores = pagina_vendedores.ids['lista_vendedores']
                    for id_vendedor_equipe in lista_equipe:
                        banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                        lista_vendedores.add_widget(banner_vendedor)


            self.mudar_tela("homepage")

        except:
            pass

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids['screen_manager']
        gerenciador_telas.current = id_tela

    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{foto}'

        info = f'{{"avatar": "{foto}"}}'
        requests.patch(f"{link}{self.local_id}.json?auth={self.id_token}", data=info)

        self.mudar_tela("ajustespage")

    def adicionar_vendedor(self, id_vendedor_add):
        addvend_page = self.root.ids['adicionarvendedor']
        requisicao = requests.get(f'{link}.json?orderBy="id_vendedor"&equalTo="{id_vendedor_add}"').json()
        if requisicao != {}:
            lista_equipe = self.equipe.split(",")
            if id_vendedor_add not in lista_equipe:
                self.equipe += f',{id_vendedor_add}'
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f'{link}{self.local_id}.json?auth={self.id_token}', data=info)
                pagina_vendedores = self.root.ids['listarvendedores']
                lista_vendedores = pagina_vendedores.ids['lista_vendedores']
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_add)
                lista_vendedores.add_widget(banner_vendedor)
                addvend_page.ids['mensagem_add_vendedor'].text = "Vendedor adicionado com sucesso!"
            else:
                addvend_page.ids['mensagem_add_vendedor'].text = "Vendedor já faz parte da equipe"
                addvend_page.ids['mensagem_add_vendedor'].color = (1, 0, 0, 1)
        else:
            addvend_page.ids['mensagem_add_vendedor'].text = "Usuário não encontrado"
            addvend_page.ids['mensagem_add_vendedor'].color = (1, 0, 0, 1)

    def selecionar_cliente(self, foto_cliente, *args):
        pagina_add_venda = self.root.ids['adicionarvendas']
        lista_clientes = pagina_add_venda.ids['lista_clientes']
        for item in lista_clientes.children:
            item.color = (1, 1, 1, 1)
            try:
                if item.text == foto_cliente[:-4].capitalize():
                    item.color = (0, 207/255, 219/255, 1)
                    self.cliente = item.text
            except:
                pass

    def selecionar_produto(self, foto_produto, *args):
        pagina_add_venda = self.root.ids['adicionarvendas']
        lista_produtos = pagina_add_venda.ids['lista_produtos']
        for item in lista_produtos.children:
            item.color = (1, 1, 1, 1)
            try:
                if item.text == foto_produto[:-4]:
                    item.color = (0, 207/255, 219/255, 1)
                    self.produto = item.text
            except:
                pass

    def selecionar_unidade(self, id_und, *args):
        pagina_add_venda = self.root.ids['adicionarvendas']
        pagina_add_venda.ids['und_kg'].color = (1, 1, 1, 1)
        pagina_add_venda.ids['und_unidades'].color = (1, 1, 1, 1)
        pagina_add_venda.ids['und_litros'].color = (1, 1, 1, 1)
        pagina_add_venda.ids[id_und].color = (0, 207/255, 219/255, 1)
        self.und = id_und

    def adicionar_venda(self, *args):
        pagina_add_venda = self.root.ids['adicionarvendas']
        cliente = self.cliente
        produto = self.produto
        unidade = self.und.replace("und_", "")
        data = pagina_add_venda.ids["label_data"].text.replace("Data: ", "")
        preco = pagina_add_venda.ids["preco_input"].text
        quantidade = pagina_add_venda.ids["quantidade_input"].text

        if not cliente:
            pagina_add_venda.ids["label_cliente"].color = (1, 0, 0, 1)
        if not produto:
            pagina_add_venda.ids["label_produto"].color = (1, 0, 0, 1)
        if not unidade:
            pagina_add_venda.ids['und_kg'].color = (1, 0, 0, 1)
            pagina_add_venda.ids['und_unidades'].color = (1, 0, 0, 1)
            pagina_add_venda.ids['und_litros'].color = (1, 0, 0, 1)
        if not preco:
            pagina_add_venda.ids['preco_label'].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_add_venda.ids['preco_label'].color = (1, 0, 0, 1)
        if not quantidade:
            pagina_add_venda.ids['quantidade_label'].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_add_venda.ids['quantidade_label'].color = (1, 0, 0, 1)

        if cliente and produto and unidade and preco and (type(preco) == float) and quantidade and\
                (type(quantidade) == float):
            # print(f"Venda de {quantidade} {unidade} de {produto} para {cliente} a R${preco} no dia {data}")
            foto_cliente = cliente.lower() + ".png"
            foto_produto = produto + ".png"
            info_venda = f'{{"cliente": "{cliente}", "produto": "{produto}", "unidade": "{unidade}",' \
                         f'"preco": "{preco}", "quantidade": "{quantidade}", "data": "{data}",' \
                         f'"foto_cliente": "{foto_cliente}", "foto_produto": "{foto_produto}"}}'
            requests.post(f"{link}{self.local_id}/vendas.json?auth={self.id_token}", data=info_venda)

            banner_venda = BannerVenda(cliente=cliente, foto_cliente=foto_cliente, produto=produto, data=data,
                                       foto_produto=foto_produto, preco=preco, quantidade=quantidade, unidade=unidade)
            pagina_home = self.root.ids['homepage']
            lista_vendas = pagina_home.ids['lista_vendas']
            lista_vendas.add_widget(banner_venda)

            self.total_vendas += preco * quantidade
            info_total = f'{{"total_vendas": "{self.total_vendas}"}}'
            requests.patch(f"{link}{self.local_id}.json?auth={self.id_token}", data=info_total)

            pag_home = self.root.ids['homepage']
            pag_home.ids['label_total_vendas'].text = f"[color=#000000]Total de vendas:[/color] " \
                                                      f"[b]R${self.total_vendas}[/b]"
            self.mudar_tela("homepage")

        self.cliente = None
        self.produto = None
        self.unidade = None

    def carregar_todas_vendas(self, *args):
        pagina_todasvendas = self.root.ids['todasvendas']
        lista_vendas = pagina_todasvendas.ids['lista_vendas']
        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        # Preencher foto de perfil
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/hash.png'

        # Preencher total de vendas
        requisicao = requests.get(f'{link}.json?orderBy="id_vendedor"')
        requisicao_dic = requisicao.json()
        total_vendas = 0
        for usuario_id in requisicao_dic:
            try:
                vendas = requisicao_dic[usuario_id]["vendas"]
                if vendas != "":
                    for id_venda in vendas:
                        venda = vendas[id_venda]
                        banner_venda = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                                   produto=venda['produto'], foto_produto=venda['foto_produto'],
                                                   preco=float(venda['preco']), quantidade=float(venda['quantidade']),
                                                   unidade=venda['unidade'], data=venda['data'])
                        total_vendas += float(venda['preco']) * float(venda['quantidade'])
                        lista_vendas.add_widget(banner_venda)
            except Exception as excecao:
                print(excecao)

        pagina_todasvendas.ids['label_total_vendas'].text =\
            f"[color=#000000]Total de vendas:[/color] [b]R${total_vendas}[/b]"

        self.mudar_tela("todasvendas")

    def sair_todas_vendas(self, id_tela, *args):
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{self.avatar}'

        self.mudar_tela(id_tela)

    def carregar_vendas_vendedor(self, dic_vendedor, *args):
        pagina_vendasvendedor = self.root.ids['vendasvendedor']
        lista_vendas = pagina_vendasvendedor.ids['lista_vendas']
        for item in list(lista_vendas.children):
            lista_vendas.remove_widget(item)

        # Preencher foto de perfil
        foto_perfil = self.root.ids['foto_perfil']
        foto_perfil.source = f'icones/fotos_perfil/{dic_vendedor["avatar"]}'

        # Preencher total de vendas
        total_vendas = 0
        try:
            vendas = dic_vendedor["vendas"]
            if vendas != "":
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner_venda = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                               produto=venda['produto'], foto_produto=venda['foto_produto'],
                                               preco=float(venda['preco']), quantidade=float(venda['quantidade']),
                                               unidade=venda['unidade'], data=venda['data'])
                    total_vendas += float(venda['preco']) * float(venda['quantidade'])
                    lista_vendas.add_widget(banner_venda)

            pagina_vendasvendedor.ids['label_total_vendas'].text =\
                f"[color=#000000]Total de vendas:[/color] [b]R${total_vendas}[/b]"
        except Exception as excecao:
            print(excecao)

        self.mudar_tela("vendasvendedor")


MainApp().run()
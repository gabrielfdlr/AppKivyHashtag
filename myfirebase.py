import requests
from kivy.app import App

link_fb = "https://app-kivy-hashtag-default-rtdb.firebaseio.com/"


class MyFireBase:
    API_KEY = "AIzaSyBdbNDEsUeIr1yj9I2-M-YjD33gdJeLYqQ"

    def criar_conta(self, email, senha):
        meu_app = App.get_running_app()
        link_gc = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        requisicao = requests.post(link_gc, data=info)
        requisicao_dic = requisicao.json()

        if requisicao.ok:
            login_page = meu_app.root.ids['loginpage']
            login_page.ids['mensagem_login'].text = "Usuário criado com sucesso!"

            refresh_token = requisicao_dic["refreshToken"]
            local_id = requisicao_dic["localId"]
            id_token = requisicao_dic["idToken"]
            meu_app.local_id = local_id
            meu_app.id_token = id_token
            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            req_id = requests.get(f"{link_fb}proximo_id_vendedor.json?auth={id_token}")
            id_vendedor = req_id.json()['proximo_id_vendedor']

            link_db = f"{link_fb}{local_id}.json?auth={id_token}"
            info_usuario = f'{{"avatar": "foto1.png", "equipe": "", "total_vendas": 0, "vendas": "",' \
                           f'"id_vendedor": "{id_vendedor}"}}'
            requests.patch(link_db, data=info_usuario)

            prox_id_vendedor = int(id_vendedor) + 1
            info_id_vendedor = f'{{"proximo_id_vendedor": "{prox_id_vendedor}"}}'
            requests.patch(f"{link_fb}proximo_id_vendedor.json?auth={id_token}", data=info_id_vendedor)

            meu_app.carregar_infos_usuario()
            meu_app.mudar_tela("homepage")

        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            login_page = meu_app.root.ids['loginpage']
            login_page.ids['mensagem_login'].text = mensagem_erro
            login_page.ids['mensagem_login'].color = (1, 0, 0, 1)

    def fazer_login(self, email, senha):
        meu_app = App.get_running_app()
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        if requisicao.ok:
            login_page = meu_app.root.ids['loginpage']
            login_page.ids['mensagem_login'].text = "Login feito com sucesso!"

            refresh_token = requisicao_dic["refreshToken"]
            local_id = requisicao_dic["localId"]
            id_token = requisicao_dic["idToken"]
            meu_app.local_id = local_id
            meu_app.id_token = id_token
            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)

            meu_app.carregar_infos_usuario()
            meu_app.mudar_tela("homepage")
        else:
            mensagem_erro = requisicao_dic["error"]["message"]
            login_page = meu_app.root.ids['loginpage']
            login_page.ids['mensagem_login'].text = mensagem_erro
            login_page.ids['mensagem_login'].color = (1, 0, 0, 1)

    def trocar_token(self, refresh_token):
        link = f"https://securetoken.googleapis.com/v1/token?key={self.API_KEY}"
        info = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        local_id = requisicao_dic['user_id']
        id_token = requisicao_dic['id_token']
        return local_id, id_token
import mysql.connector
import os
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, flash
from services.JogadorService import JogadorService
from services.CampanhaService import CampanhaService

app = Flask(__name__,     
            static_url_path='',    
            static_folder='static',    
            template_folder='templates')

# UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'chave_flask_super_secreta' #necessario para usar session

db_config = {
    'user': 'botdd',
    'password': 'Senac442300',
    'host': 'botdnd.mysql.database.azure.com',
    'port': 3306,
    'database': 'maindb'
}

jogadorService = JogadorService(db_config)
campanhaService = CampanhaService(db_config)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # usuario = request.form.get('usuario')
        email = request.form.get('email')
        senha = request.form.get('senha')
        # Verifica as credenciais no banco de dados
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        query = 'SELECT COUNT(*) FROM jogadores WHERE email = %s and senha = %s'
        cursor.execute(query, (email, senha))
        result = cursor.fetchone()

        if result and result[0] == 1:
            #Login OK -> guarda na sessão
            # session['usuario_logado'] = usuario
            session['email_logado'] = email
            #Consulta informações do usuario
            query = 'SELECT nome, jogador_id FROM jogadores WHERE email = %s and senha = %s'
            cursor.execute(query, (email, senha))
            result = cursor.fetchall()
            #Guarda informações do usuario na sessão
            print(result[0])
            session['usuario_logado'] = result[0][0]
            session['id_logado'] = result[0][1]
            cursor.close()
            cnx.close()

            return redirect(url_for('home'))
        else:
            #falha no login -> renderiza login novamente com mensagem de erro
            cursor.close()
            cnx.close()
            return render_template('login.html', erro='Credenciais incorretas.')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    return redirect(url_for('index'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        confirma_senha = request.form.get('confirma_senha')
        email = request.form.get('email')
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        query = "SELECT COUNT(*) FROM jogadores WHERE email = %s"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        cnx.commit()
        cursor.close()
        cnx.close()

        if result and result[0] == 1:
            return render_template('cadastro.html', erro_email_usado='Este e-mail já está cadastrado') 
        elif senha == confirma_senha:
            # Inserir no banco
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            query = "INSERT INTO jogadores (nome, senha, email) VALUES (%s, %s, %s)"
            cursor.execute(query, (usuario, senha, email))
            cnx.commit()
            cursor.close()
            cnx.close()
            # Após cadastrar, redireciona para página inicial ou outra
            return render_template('index.html', sucessocadastro='Usuario cadastrado com sucesso!')
        else:
            # Falha na confirmação de senha, retorna erro
            return render_template('cadastro.html', errocadastro='As senhas não coincidem!')
    else:
        return render_template('cadastro.html')
    

@app.route('/home')
def home():
    if 'usuario_logado' in session:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        id = session['id_logado']
        query = 'SELECT caminhofoto FROM jogadores WHERE jogador_id = %s'
        cursor.execute(query, [id])
        result = cursor.fetchone()
        urlfotoperfil = None
        if result and result[0]:
            fotoperfil = result[0]
            urlfotoperfil = url_for('static', filename=fotoperfil.replace('static/', ''))
            
        cursor.close()
        cnx.close()
        return render_template('home.html', usuario = session['usuario_logado'].upper(), email = session['email_logado'], id=session['id_logado'], fotoperfil = urlfotoperfil)
    else:
        return redirect(url_for('login'))

@app.route('/redefinir_senha', methods=['GET', 'POST'])
def redefinir_senha():
    if request.method == 'POST':
        email = request.form.get('email')
        # Verifica as credenciais no banco de dados
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        query = 'SELECT COUNT(*) FROM jogadores WHERE email = %s'
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        cursor.close()
        cnx.close()

        if result and result[0] == 1:
            #email existente -> atualiza o banco de dados
            senha = request.form.get('senha')
            email = request.form.get('email')

            # UPDATE no banco
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            query = "UPDATE jogadores SET senha = %s WHERE email = %s"
            cursor.execute(query, (senha, email))
            cnx.commit()
            cursor.close()
            cnx.close()

            # Após atualizar, redireciona para página de login
            return render_template('login.html', sucesso1='Senha alterada com sucesso')
            
        else:
            #falha no check -> email não existe, exibe erro e renderiza a pagina novamente
            return render_template('redefinir_senha.html', erro1='Nenhum usuário encontrado com este e-mail')

    else:
        return render_template('redefinir_senha.html')
    
@app.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    if request.method == 'POST':
        id = session['id_logado']
        usuario = session['usuario_logado'].upper()

        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        query = 'SELECT caminhofoto FROM jogadores WHERE jogador_id = %s'
        cursor.execute(query, [id])
        result = cursor.fetchone()
        urlfotoperfil = None
        if result and result[0]:
            fotoperfil = result[0]
            urlfotoperfil = url_for('static', filename=fotoperfil.replace('static/', ''))

        senha_antiga = request.form.get('senha_antiga')
        # Verifica as credenciais no banco de dados

        query = 'SELECT COUNT(*) FROM jogadores WHERE senha = %s and jogador_id = %s'
        cursor.execute(query, (senha_antiga, id))
        result = cursor.fetchone()
        cursor.close()
        cnx.close()

        nova_senha = request.form.get('senha')
        confirma_senha = request.form.get('confirma_senha')

        if nova_senha != confirma_senha:
            return render_template('configuracoes.html', erro_confirma_senha='As senhas não coincidem!', fotoperfil = urlfotoperfil, usuario = usuario)


        if result and result[0] == 1:
            #usuario existente -> atualiza o banco de dados
            # UPDATE no banco
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            query = "UPDATE jogadores SET senha = %s WHERE jogador_id = %s"
            cursor.execute(query, (nova_senha, id))
            cnx.commit()
            cursor.close()
            cnx.close()

            # Após atualizar, redireciona para página de login
            return render_template('configuracoes.html', sucesso1='Senha alterada com sucesso', fotoperfil = urlfotoperfil, usuario = usuario)
            
        else:
            #falha no check -> usuario não encontrado, senha incorreta
            return render_template('configuracoes.html', erro_senha_antiga='Senha incorreta', fotoperfil = urlfotoperfil, usuario = usuario)

    else:
        return render_template('configuracoes.html.html')


@app.route('/alterar_email', methods=['GET', 'POST'])
def alterar_email():
    if request.method == 'POST':
        id = session['id_logado']
        usuario = session['usuario_logado'].upper()

        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        query = 'SELECT caminhofoto FROM jogadores WHERE jogador_id = %s'
        cursor.execute(query, [id])
        result = cursor.fetchone()
        urlfotoperfil = None
        if result and result[0]:
            fotoperfil = result[0]
            urlfotoperfil = url_for('static', filename=fotoperfil.replace('static/', ''))

        email_antigo = request.form.get('email_antigo')
        # Verifica as credenciais no banco de dados

        query = 'SELECT COUNT(*) FROM jogadores WHERE email = %s and jogador_id = %s'
        cursor.execute(query, (email_antigo, id))
        result = cursor.fetchone()
        cursor.close()
        cnx.close()

        novo_email = request.form.get('email')
        confirma_email = request.form.get('confirma_email')

        if novo_email != confirma_email:
            return render_template('configuracoes.html', erro_confirma_email='Os e-mails não coincidem!', fotoperfil = urlfotoperfil, usuario = usuario)

        if result and result[0] == 1:
            #usuario existente -> atualiza o banco de dados
            # UPDATE no banco
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            query = "UPDATE jogadores SET email = %s WHERE jogador_id = %s"
            cursor.execute(query, (novo_email, id))
            cnx.commit()
            cursor.close()
            cnx.close()

            # Após atualizar, redireciona para página de login
            return render_template('configuracoes.html', sucesso_email='E-mail alterado com sucesso', fotoperfil = urlfotoperfil, usuario = usuario)            

        else:
            #falha no check -> usuario não encontrado, email incorreta
            return render_template('configuracoes.html', erro_email_antigo='E-mail incorreto', fotoperfil = urlfotoperfil, usuario = usuario)            



@app.route('/configuracoes', methods=['GET', 'POST'])
def configuracoes():
    if 'usuario_logado' in session:

        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        id = session['id_logado']
        query = 'SELECT caminhofoto FROM jogadores WHERE jogador_id = %s'
        cursor.execute(query, [id])
        result = cursor.fetchone()
        if result and result[0]:
            fotoperfil = result[0]
            urlfotoperfil = url_for('static', filename=fotoperfil.replace('static/', ''))
            
        else:
            urlfotoperfil = None
        cursor.close()
        cnx.close()
        usuario = session['usuario_logado'].upper()

        return render_template('configuracoes.html', usuario = usuario, fotoperfil=urlfotoperfil)
    else:
        return redirect(url_for('login'))



@app.route('/alterar_nome', methods=['GET', 'POST'])
def alterar_nome():
    if request.method == 'POST':
        senha = request.form.get('senha')
        usuario = session['usuario_logado']
        # Verifica as credenciais no banco de dados
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        id = session['id_logado']
        query = 'SELECT caminhofoto FROM jogadores WHERE jogador_id = %s'
        cursor.execute(query, [id])
        result = cursor.fetchone()
        urlfotoperfil = None
        if result and result[0]:
            fotoperfil = result[0]
            urlfotoperfil = url_for('static', filename=fotoperfil.replace('static/', ''))

        print(f"Senha: {senha}, Usuario: {usuario}")
        query = 'SELECT COUNT(*) FROM jogadores WHERE senha = %s and nome = %s'
        cursor.execute(query, (senha, usuario))
        result = cursor.fetchone()
        print(f'resultado = {result}')
        cursor.close()
        cnx.close()

        if result and result[0] == 1:
            #senha existente -> atualiza o banco de dados
            novonome = request.form.get('usuario')

            # UPDATE no banco
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()
            query = "UPDATE jogadores SET nome = %s WHERE senha = %s"
            cursor.execute(query, (novonome, senha))
            cnx.commit()
            cursor.close()
            cnx.close()

            # Após atualizar, redireciona para página de configuracao e atualiza o nome da sessão:
            session['usuario_logado'] = novonome
            return render_template('configuracoes.html', sucesso2='Nome de usuario alterado com sucesso', usuario = usuario.upper(), fotoperfil = urlfotoperfil)
            
        else:
            #falha no check -> senha não existe, exibe erro e renderiza a pagina novamente
            return render_template('configuracoes.html', erro2='senha incorreta', usuario = usuario.upper(), fotoperfil = urlfotoperfil)

    else:
        return render_template('configuracoes.html')



@app.route('/uploadfoto', methods=['GET','POST'])
def upload():
    id = session['id_logado']
    usuario = session['usuario_logado']

    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    query = "SELECT caminhofoto FROM jogadores WHERE nome = %s and jogador_id = %s"
    cursor.execute(query, (usuario, id))
    result = cursor.fetchone()
    fotoatual = None
    if result and result[0]:
        fotoatual = result[0]
        urlfotoatual = url_for('static', filename=fotoatual.replace('static/', ''))

    cursor.close()
    cnx.close()

    if request.method == 'POST':




        fotoperfil = request.files['fotoperfil']

        if fotoperfil:
            cnx = mysql.connector.connect(**db_config)
            cursor = cnx.cursor()

            # Obter a extensão do arquivo
            _, ext = os.path.splitext(fotoperfil.filename)
            ext = ext.lower()  # Normaliza para minúsculas

            # Validar a extensão
            extensoes_permitidas = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
            if ext not in extensoes_permitidas:
                return render_template('configuracoes.html', erroformato="Formato de arquivo não suportado.", usuario = usuario.upper(), fotoperfil = urlfotoatual)

            #Remove a foto atual do servidor se ela existir
            if fotoatual:
                caminho_abs_fotoantiga = os.path.join(app.root_path, fotoatual).replace("\\","/")
                os.remove(caminho_abs_fotoantiga)

            #Salva a foto do usuario no servidor com nome unico para cada usuario
            nomefoto = f"{usuario}_{id}{ext}"
            caminhoarquivo = os.path.join(app.config['UPLOAD_FOLDER'], nomefoto).replace("\\","/")
            caminho_absoluto = os.path.join(app.root_path, caminhoarquivo)
            fotoperfil.save(caminho_absoluto)

            #Atualiza o banco de dados com o caminho da nova foto
            query = "UPDATE jogadores SET caminhofoto = %s WHERE nome = %s and jogador_id = %s"
            cursor.execute(query,(caminhoarquivo, usuario, id))
            cnx.commit()
            cursor.close()
            cnx.close()

            usuario = usuario.upper()
            fotoperfil = url_for('static', filename=caminhoarquivo.replace('static/', ''))
            return render_template('configuracoes.html', sucessofoto='Foto alterada com sucesso', usuario = usuario, fotoperfil=fotoperfil)

        else:

            return render_template('configuracoes.html', errofoto='Nenhuma foto selecionada', usuario = usuario, fotoperfil = urlfotoatual)

    else:
        return render_template('configuracoes.html', usuario = usuario.upper(), fotoperfil = urlfotoatual)

@app.route('/excluir_conta',  methods=['GET','POST'])
def excluir_Conta():
    if request.method == 'POST':
        id = session['id_logado']
        usuario = session['usuario_logado']

        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        query = "SELECT caminhofoto FROM jogadores WHERE jogador_id = %s and nome = %s"
        cursor.execute(query, (id, usuario))
        result = cursor.fetchone()
        if result and result[0]:
            fotoperfil = result[0]
            caminho_abs_fotoantiga = os.path.join(app.root_path, fotoperfil).replace("\\","/")
            os.remove(caminho_abs_fotoantiga)            

        query = "DELETE FROM jogadores WHERE jogador_id = %s and nome = %s"
        cursor.execute(query, (id, usuario))
        cnx.commit()
        cursor.close()
        cnx.close()
        return render_template('index.html', sucesso_excluir_conta=f'Conta de nome {usuario.upper()} foi excluida com sucesso.')
    else:
        return render_template('configuracoes.html')

@app.route('/meus_personagens', methods=["GET"])
def meus_personagens():
    if not 'usuario_logado' in session:
        return redirect(url_for('login'))
    
    id = session['id_logado']
    usuario = session['usuario_logado'].upper()
    
    jogador = jogadorService.get_by_id(id)
    urlfotoperfil = url_for('static', filename=jogador["caminhofoto"].replace('static/', '')) if jogador else None

    personagens = jogadorService.get_personagens_by_id_jogador(id)
    for personagem in personagens:
        personagem["campanha"] = campanhaService.get_by_id(personagem["campanha_id"])
    print(personagens) #debug
    return render_template('meus_personagens.html', personagens=personagens, usuario=usuario, fotoperfil=urlfotoperfil)
    
@app.route('/minhas_aventuras', methods=["GET"])
def minhas_aventuras():
    if not 'usuario_logado' in session:
        return redirect(url_for('login'))
    
    id = session['id_logado']
    usuario = session['usuario_logado'].upper()
    
    #Adquire o usuario pelo seu ID e sua foto
    jogador = jogadorService.get_by_id(id)
    urlfotoperfil = url_for('static', filename=jogador["caminhofoto"].replace('static/', '')) if jogador else None

    #Adquire os personagens do usuario e os dados de sua campanha
    personagens = jogadorService.get_personagens_by_id_jogador(id)
    for personagem in personagens:
        personagem["campanha"] = campanhaService.get_by_id(personagem["campanha_id"])
    print(personagens) #debug

    campanhas = campanhaService.get_by_id(personagem("campanha"))
    print(f"campanhas = {campanhas}")   

    return render_template('minhas_aventuras.html', personagens=personagens, usuario=usuario, fotoperfil=urlfotoperfil)


if __name__ == '__main__':
    app.run(debug=True)

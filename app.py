import mysql.connector
import os
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

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


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        usuario2 = request.form.get('usuario')
        senha = request.form.get('senha')
        # Verifica as credenciais no banco de dados
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        query = 'SELECT COUNT(*) FROM jogadores WHERE (nome = %s OR email = %s) and senha = %s'
        cursor.execute(query, (usuario, usuario2, senha))
        result = cursor.fetchone()
        cursor.close
        cnx.close

        if result and result[0] == 1:
            #Login OK -> guarda na sessão
            session['usuario_logado'] = usuario
            return redirect(url_for('home'))
        else:
            #falha no login -> renderiza login novamente com mensagem de erro
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
        email = request.form.get('email')

            # Inserir no banco
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        query = "INSERT INTO jogadores (nome, senha, email) VALUES (%s, %s, %s)"
        cursor.execute(query, (usuario, senha, email))
        cnx.commit()
        cursor.close()
        cnx.close()

        # Após cadastrar, redireciona para página inicial ou outra
        return redirect(url_for('index'))
    else:
        return render_template('cadastro.html')
    

@app.route('/home')
def home():
    if 'usuario_logado' in session:
        return render_template('home.html', usuario = session['usuario_logado'])
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
        cursor.close
        cnx.close

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


@app.route('/configuracoes', methods=['GET', 'POST'])
def configuracoes():
    if 'usuario_logado' in session:
        return render_template('configuracoes.html', usuario = session['usuario_logado'])
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
        query = 'SELECT COUNT(*) FROM jogadores WHERE senha = %s and nome = %s'
        cursor.execute(query, (senha, usuario))
        result = cursor.fetchone()
        cursor.close
        cnx.close

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

            # Após atualizar, redireciona para página de configuracao
            return render_template('configuracoes.html', sucesso2='Nome de usuario alterado com sucesso')
            
        else:
            #falha no check -> senha não existe, exibe erro e renderiza a pagina novamente
            return render_template('configuracoes.html', erro2='senha incorreta')

    else:
        return render_template('configuracoes.html')



extensoes_permitidas = {'.jpg', '.jpeg', '.png', '.gif'}
@app.route('/uploadfoto', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        senha = request.form.get('senha')
        usuario = session['usuario_logado']

        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()

        query = "SELECT COUNT(*) FROM jogadores WHERE nome = %s and senha = %s"
        cursor.execute(query, (usuario, senha))
        result = cursor.fetchone()

        cursor.close
        cnx.close
        if result and result[0] == 1:
            # fotoperfil = request.form.get('fotoperfil')
            fotoperfil = request.files['fotoperfil']
            if fotoperfil:
                cnx = mysql.connector.connect(**db_config)
                cursor = cnx.cursor()

                #Consulta o banco para saber o caminho da foto atual
                query = "SELECT caminhofoto FROM jogadores WHERE nome = %s AND senha = %s"
                cursor.execute(query,(usuario,senha))
                result=cursor.fetchone()
                fotoantiga = result[0]
                #Remove a foto atual do servidor se ela existir
                if fotoantiga:
                    caminho_abs_fotoantiga = os.path.join(app.root_path, fotoantiga)
                    os.remove(caminho_abs_fotoantiga)

                #Consulta o ID do jogador para montar o nome do arquivo a ser salvo
                query = "SELECT jogador_id FROM jogadores WHERE nome = %s AND senha = %s"
                cursor.execute(query,(usuario, senha))
                result = cursor.fetchone()
                id_usuario = result[0]

                # Obter a extensão do arquivo
                _, ext = os.path.splitext(fotoperfil.filename)
                ext = ext.lower()  # Normaliza para minúsculas

                # Validar a extensão
                extensoes_permitidas = {'.jpg', '.jpeg', '.png', '.gif'}
                if ext not in extensoes_permitidas:
                    return render_template('configuracoes.html', erroformato="Formato de arquivo não suportado.")

                #Salva a foto do usuario no servidor
                nomefoto = f"{usuario}_{id_usuario}{ext}"
                caminhoarquivo = os.path.join(app.config['UPLOAD_FOLDER'], nomefoto).replace("\\","/")
                caminho_absoluto = os.path.join(app.root_path, caminhoarquivo)
                fotoperfil.save(caminho_absoluto)

                #Atualiza o banco de dados com o caminho da nova foto
                query = "UPDATE jogadores SET caminhofoto = %s WHERE nome = %s and senha = %s"
                cursor.execute(query,(caminhoarquivo, usuario, senha))
                cnx.commit()
                cursor.close()
                cnx.close()

                return render_template('configuracoes.html', sucessofoto='Foto alterada com sucesso')

            else:
                return render_template('configuracoes.html', errofoto='Nenhuma foto selecionada')
        else:
            return render_template('configuracoes.html', erro2='senha incorreta')
    else:
        return render_template('configuracoes.html')


if __name__ == '__main__':
    app.run(debug=True)

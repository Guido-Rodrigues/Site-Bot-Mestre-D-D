import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory

app = Flask(__name__,     
            static_url_path='',    
            static_folder='static',    
            template_folder='templates')

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



if __name__ == '__main__':
    app.run(debug=True)

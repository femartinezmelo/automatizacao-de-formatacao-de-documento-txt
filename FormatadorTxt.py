
import PySimpleGUI as sg
import os
from typing import List
from ConexaoDB import ConexaoDB

class EdicaoTxt:
    def __init__(self) -> None:
        
        sg.theme('SystemDefault')
        self.conexao = ConexaoDB().conectar_db()
        self.linhas: List[str] = []
        self.arquivo_entrada = ''
        self.arquivo_saida = ''
        self.criar_interface()
        self.lembrar_diretorio()
        
    def criar_interface(self):
        layout = [
            [sg.Text('Arquivo de Entrada:', size=(15, 1)),
             sg.Input(key='-ENTRADA-', readonly=True),
             sg.FileBrowse('Selecionar', file_types=(('Texto', '*.txt'),))],
            

            [sg.Text('Nome do Arquivo:', size=(15, 1)),
             sg.Input(key='-NOME_NOVO_ARQUIVO-')],
            
            [sg.Text('Salvar em:', size=(15, 1)),
             sg.Input(key='-LOCAL-'),
             sg.FolderBrowse('Selecionar')],
            
            [sg.Button('Formatar', size=(10, 1)),
             sg.Button('Sair', size=(10, 1))]
        ]
        
        self.janela = sg.Window('Formatador de TXT', layout).finalize()

    def lembrar_diretorio(self):
        try:
            cursor = self.conexao.cursor()
            cursor.execute('SELECT diretorio_origem, diretorio_destino FROM formatador WHERE ID = 1')
            diretorio = cursor.fetchone()
            
            linha1 = diretorio[0]
            linha2 = os.path.dirname(diretorio[1]) 
           
            if diretorio:
                
                self.janela['-ENTRADA-'].update(linha1)
                self.janela['-LOCAL-'].update(linha2)
        
        except Exception as e:
            sg.popup('Erro', f'Erro ao lembrar diretório: {str(e)}')
        finally:
            cursor.close()

    def ler_arquivo(self):
        try:
            with open(self.arquivo_entrada, 'r', encoding='utf-8') as arquivo:
                self.linhas = arquivo.readlines()
        except Exception as e:
            sg.popup('Erro', f'Erro ao ler arquivo: {str(e)}')
            return False
        return True

    def formatar_linhas(self):
        linhas_formatadas = []
        
        for linha in self.linhas:
            if 'Informes' in linha or 'Relatório de Atividades' in linha:
                linha = f'_{linha.strip()}_\n'

            if ':' in linha:
                separacao = linha.split(':', 1)
                nome = f'**{separacao[0].strip()}**'
                conteudo = separacao[1].strip()
                linha = f'{nome}: {conteudo}\n'
            linhas_formatadas.append(linha)

        self.linhas = linhas_formatadas

    def salvar_arquivo(self):
        try:
            with open(self.arquivo_saida, 'w', encoding='utf-8') as arquivo:
                arquivo.writelines(self.linhas)
            return True
        except Exception as e:
            sg.popup('Erro', f'Erro ao salvar arquivo: {str(e)}')
            return False

    def processar_formatacao(self, key):
        self.arquivo_entrada = key['-ENTRADA-']
        nome_novo_arquivo = key['-NOME_NOVO_ARQUIVO-']
        local_salvamento = key['-LOCAL-']

        if not self.arquivo_entrada or not nome_novo_arquivo or not local_salvamento:
            sg.popup('Erro', 'Preencha todos os campos obrigatórios.')
            return  

        self.arquivo_saida = os.path.join(local_salvamento, f'{nome_novo_arquivo}.txt') if local_salvamento else f'{nome_novo_arquivo}.txt'        
        self.conexao_db()

        if self.ler_arquivo():
            self.formatar_linhas()
            if self.salvar_arquivo():

                sg.popup('Sucesso', f'Arquivo formatado e salvo em:\n{self.arquivo_saida}')

    def executar(self):
        while True:
            evento, valores = self.janela.read()
            

            if evento in (sg.WINDOW_CLOSED, 'Sair'):
                break
                
            if evento == 'Formatar':
                self.processar_formatacao(valores)

        self.janela.close()
        
    def conexao_db(self):
        
        try:
            cursor = self.conexao.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM formatador WHERE ID = 1')
            
            id_cursor = cursor.fetchmany()[0][0]
            
            if  id_cursor > 0:
                cursor.execute('UPDATE formatador SET diretorio_destino = ?, diretorio_origem = ? WHERE ID = 1', (self.arquivo_saida, self.arquivo_entrada))
            
            else:
                cursor.execute('INSERT INTO formatador (diretorio_origem, diretorio_destino) VALUES (?, ?)', (self.arquivo_entrada, self.arquivo_saida))
                
            self.conexao.commit()
            
        except Exception as e:
           
            sg.popup('Erro', f'Erro ao conectar ao banco de dados: {str(e)}')


if __name__ == '__main__':
    
    EdicaoTxt().executar()
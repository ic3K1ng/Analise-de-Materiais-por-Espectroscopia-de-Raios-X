"""
Students:
numero: 66344   nome: Leisley Santingue
"""

import sqlite3
import urllib.request
import os

URLELEMS = "http://asc.di.fct.unl.pt/~vad/ice/26/elements.txt"
URLXRLINES = "http://asc.di.fct.unl.pt/~vad/ice/26/xray-lines.txt"
TOLERANCE = 0.025
DBNAME = "spectrum.db"

def do_initdb(con: sqlite3.Connection):
    cursor = con.cursor()
    cursor.execute("DROP TABLE IF EXISTS Resultados")
    cursor.execute("DROP TABLE IF EXISTS Analisados")
    cursor.execute("DROP TABLE IF EXISTS Linhas")
    cursor.execute("DROP TABLE IF EXISTS Elementos")
    
    cursor.execute('''CREATE TABLE Elementos (
        simbolo TEXT PRIMARY KEY,
        nome TEXT
    )''')
    
    cursor.execute('''CREATE TABLE Linhas (
        simbolo TEXT,
        energia REAL,
        peso REAL,
        FOREIGN KEY(simbolo) REFERENCES Elementos(simbolo)
    )''')
    
    cursor.execute('''CREATE TABLE Analisados (
        numeroanalise INTEGER PRIMARY KEY,
        ficheiro TEXT
    )''')
    
    cursor.execute('''CREATE TABLE Resultados (
        numeroanalise INTEGER,
        picoenergia REAL,
        picocontagem REAL,
        simbolo TEXT,
        FOREIGN KEY(numeroanalise) REFERENCES Analisados(numeroanalise),
        FOREIGN KEY(simbolo) REFERENCES Elementos(simbolo)
    )''')
    
    try:
        response = urllib.request.urlopen(URLELEMS)
        content = response.read().decode('utf-8')
        for line in content.strip().split('\n'):
            line = line.strip()
            if line:
                parts = line.split(';')
                if len(parts) == 2:
                    cursor.execute("INSERT INTO Elementos (simbolo, nome) VALUES (?, ?)", (parts[0], parts[1]))
    except Exception as e:
        pass
        
    try:
        response = urllib.request.urlopen(URLXRLINES)
        content = response.read().decode('utf-8')
        for line in content.strip().split('\n'):
            line = line.strip()
            if line:
                parts = line.split(';')
                simbolo = parts[0]
                for i in range(1, len(parts), 2):
                    if i + 1 < len(parts):
                        energia = float(parts[i])
                        peso = float(parts[i+1])
                        cursor.execute("INSERT INTO Linhas (simbolo, energia, peso) VALUES (?, ?, ?)", (simbolo, energia, peso))
    except Exception as e:
        pass
        
    con.commit()
    print("Database initialized")

def do_analyze(con: sqlite3.Connection, filename: str):
    real_file = filename
    if not os.path.exists(real_file) and os.path.exists(f"../{real_file}"):
        real_file = f"../{real_file}"
        
    try:
        with open(real_file, 'r') as f:
            lines = f.readlines()
    except Exception:
        return
        
    data = []
    for line in lines[1:]: # Ignorar cabeçalho
        line = line.strip()
        if line:
            parts = line.split(',')
            if len(parts) == 2:
                data.append((float(parts[0]), float(parts[1])))
                
    if not data:
        return
        
    max_contagem = max(d[1] for d in data)
    threshold = 0.05 * max_contagem
    
    picos = []
    for i in range(1, len(data) - 1):
        energia_i, contagem_i = data[i]
        contagem_prev = data[i-1][1]
        contagem_next = data[i+1][1]
        
        if contagem_prev < contagem_i and contagem_i > contagem_next:
            if contagem_i > threshold and energia_i >= 0.5:
                picos.append((energia_i, contagem_i))
                
    cursor = con.cursor()
    cursor.execute("INSERT INTO Analisados (ficheiro) VALUES (?)", (filename,))
    num_analise = cursor.lastrowid
    
    for pico_e, pico_c in picos:
        cursor.execute("SELECT DISTINCT simbolo FROM Linhas WHERE abs(energia - ?) <= ?", (pico_e, TOLERANCE))
        candidatos = [row[0] for row in cursor.fetchall()]
        
        best_element = None
        best_score = -1
        
        for cand in candidatos:
            cursor.execute("SELECT energia, peso FROM Linhas WHERE simbolo = ?", (cand,))
            linhas_emissao = cursor.fetchall()
            
            score = 0
            for l_energia, l_peso in linhas_emissao:
                contagem_encontrada = 0
                for d_e, d_c in data:
                    if d_e >= l_energia:
                        contagem_encontrada = d_c
                        break
                score += contagem_encontrada / l_peso
                
            if score > best_score:
                best_score = score
                best_element = cand
                
        if best_element:
            cursor.execute("INSERT INTO Resultados (numeroanalise, picoenergia, picocontagem, simbolo) VALUES (?, ?, ?, ?)", (num_analise, pico_e, pico_c, best_element))
            
    con.commit()

def do_report(con: sqlite3.Connection, filename: str):
    cursor = con.cursor()
    cursor.execute("SELECT numeroanalise FROM Analisados WHERE ficheiro = ? ORDER BY numeroanalise DESC LIMIT 1", (filename,))
    row = cursor.fetchone()
    if not row:
        return
    num_analise = row[0]
    
    cursor.execute('''
        SELECT r.picoenergia, e.nome, r.picocontagem 
        FROM Resultados r
        JOIN Elementos e ON r.simbolo = e.simbolo
        WHERE r.numeroanalise = ?
        ORDER BY r.picoenergia ASC
    ''', (num_analise,))
    
    print(f"Results for file {filename}:")
    print("peak\t element\t count")
    for picoenergia, nome, picocontagem in cursor.fetchall():
        # format picoenergia to match the float representation without trailing zeros if possible
        # e.g. 1.489
        print(f"{picoenergia} {nome} {picocontagem}")

def do_stats(con: sqlite3.Connection, element: str):
    cursor = con.cursor()
    cursor.execute('''
        SELECT COUNT(DISTINCT r.numeroanalise), MAX(r.picocontagem), MIN(r.picocontagem), e.nome
        FROM Resultados r
        JOIN Elementos e ON r.simbolo = e.simbolo
        WHERE r.simbolo = ?
    ''', (element,))
    row = cursor.fetchone()
    
    if row and row[0] > 0:
        count, max_c, min_c, nome = row
        print(f"{count} results with {nome}")
        print(f"max count {max_c}")
        print(f"min count {min_c}")
    else:
        cursor.execute("SELECT nome FROM Elementos WHERE simbolo = ?", (element,))
        nome_row = cursor.fetchone()
        if nome_row:
            print(f"0 results with {nome_row[0]}")
            
def do_chart(con: sqlite3.Connection, filename: str):
    import matplotlib.pyplot as plt
    real_file = filename
    if not os.path.exists(real_file) and os.path.exists(f"../{real_file}"):
        real_file = f"../{real_file}"
        
    try:
        with open(real_file, 'r') as f:
            lines = f.readlines()
    except Exception:
        return
        
    energias = []
    contagens = []
    for line in lines[1:]:
        line = line.strip()
        if line:
            parts = line.split(',')
            if len(parts) == 2:
                energias.append(float(parts[0]))
                contagens.append(float(parts[1]))
                
    if not energias:
        return
        
    plt.figure()
    plt.plot(energias, contagens, '-')
    plt.xlabel("Energy (keV)")
    plt.ylabel("Count")
    plt.title(f"Spectrum - {filename}")
    
    max_contagem = max(contagens)
    threshold = 0.05 * max_contagem
    
    cursor = con.cursor()
    for i in range(1, len(energias) - 1):
        energia_i = energias[i]
        contagem_i = contagens[i]
        if contagens[i-1] < contagem_i and contagem_i > contagens[i+1]:
            if contagem_i > threshold and energia_i >= 0.5:
                cursor.execute("SELECT DISTINCT simbolo FROM Linhas WHERE abs(energia - ?) <= ?", (energia_i, TOLERANCE))
                candidatos = [row[0] for row in cursor.fetchall()]
                
                best_element = None
                best_score = -1
                
                for cand in candidatos:
                    cursor.execute("SELECT energia, peso FROM Linhas WHERE simbolo = ?", (cand,))
                    linhas_emissao = cursor.fetchall()
                    score = 0
                    for l_energia, l_peso in linhas_emissao:
                        contagem_encontrada = 0
                        for e_idx, e_val in enumerate(energias):
                            if e_val >= l_energia:
                                contagem_encontrada = contagens[e_idx]
                                break
                        score += contagem_encontrada / l_peso
                    if score > best_score:
                        best_score = score
                        best_element = cand
                
                if best_element:
                    cursor.execute("SELECT nome FROM Elementos WHERE simbolo = ?", (best_element,))
                    row_nome = cursor.fetchone()
                    nome_elemento = row_nome[0] if row_nome else best_element
                    plt.plot(energia_i, contagem_i, 'ko')
                    plt.text(energia_i, contagem_i, f" {nome_elemento}")
                    
    plt.show()

def main(db_name: str):
    con = sqlite3.connect(db_name)
    end=False
    while not end:
        try:
            cmd = input(">> ")
        except EOFError:
            break
            
        words = cmd.strip().split()
        if not words:
            continue
            
        if words[0].lower() == "quit":
            end = True
        elif words[0].lower() == "initdb":
            do_initdb(con)
        elif words[0].lower() == "analyze":
            if len(words) > 1:
                do_analyze(con, words[1])
        elif words[0].lower() == "report":
            if len(words) > 1:
                do_report(con, words[1])
        elif words[0].lower() == "stats":
            if len(words) > 1:
                do_stats(con, words[1])
        elif words[0].lower() == "chart":
            if len(words) > 1:
                do_chart(con, words[1])
        else:
            print("unknown command")
    con.close()

if __name__ == "__main__":
    main(DBNAME)

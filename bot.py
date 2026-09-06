import os
import requests
from datetime import datetime

# Variáveis de ambiente (serão configuradas no GitHub)
OWM_API_KEY = os.getenv("OWM_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CIDADE = "Patos de Minas,BR" # Altere para sua cidade

def buscar_clima():
    # Busca a previsão a cada 3 horas (gratuitamente)
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={CIDADE}&appid={OWM_API_KEY}&units=metric&lang=pt_br"
    resposta = requests.get(url)
    return resposta.json()

def analisar_dados(dados):
    previsoes = dados['list'][:5] # Pega apenas as próximas 15 horas (5 blocos de 3h)
    
    chovera = False
    horas_chuva = []
    melhor_hora_corrida = None
    pontuacao_corrida = -100 # Pontuação para achar o clima ideal

    for prev in previsoes:
        hora_str = datetime.fromtimestamp(prev['dt']).strftime('%H:%M')
        temp = prev['main']['temp']
        umidade = prev['main']['humidity']
        chance_chuva = prev.get('pop', 0) * 100 # Probabilidade de precipitação
        descricao = prev['weather'][0]['description']

        # Lógica de Chuva
        if chance_chuva > 20:
            chovera = True
            horas_chuva.append(f"{hora_str} ({chance_chuva:.0f}% chance)")

        # Lógica de Corrida (ideal: sem chuva, 15C-25C, umidade < 80%)
        if chance_chuva < 20 and 15 <= temp <= 25 and umidade < 80:
            pontos = 100 - abs(20 - temp) - (umidade * 0.1)
            if pontos > pontuacao_corrida:
                pontuacao_corrida = pontos
                melhor_hora_corrida = f"{hora_str} (Temp: {temp:.1f}°C, Umidade: {umidade}%, Clima: {descricao})"

    return chovera, horas_chuva, melhor_hora_corrida

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def main():
    dados = buscar_clima()
    chovera, horas_chuva, melhor_hora_corrida = analisar_dados(dados)

    # Montando a mensagem
    msg = f"🌤 *Bom dia! Aqui está seu resumo diário para {CIDADE.split(',')[0]}*\n\n"
    
    if chovera:
        msg += f"☔ *Atenção, vai chover hoje!*\nHorários com risco: {', '.join(horas_chuva)}\n\n"
    else:
        msg += "☀️ *Sem previsão de chuva para hoje!*\n\n"

    if melhor_hora_corrida:
        msg += f"🏃‍♂️ *Melhor hora para correr:*\n{melhor_hora_corrida}\n"
    else:
        msg += "🏃‍♂️ *Corrida:*\nHoje não tem nenhuma janela de clima 100% ideal (sem chuva, temp amena), avalie antes de sair!\n"

    enviar_telegram(msg)

if __name__ == "__main__":
    main()
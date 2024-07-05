import requests
import pandas as pd
import sqlalchemy
from sqlalchemy.types import NVARCHAR
from urllib.parse import quote_plus

#Colocar seu access token e sua enterprise
access_token = '{seuaccesstoken}'
url = "https://api.github.com/enterprises/{suaenterprise}/copilot/billing/seats"
# Se tiver apenas organização utilizar orgs/{org}/copilot/billing
#https://docs.github.com/en/rest/copilot/copilot-user-management?apiVersion=2022-11-28#list-all-copilot-seat-assignments-for-an-organization
headers = {
    "Authorization": f"Bearer {access_token}"
}

dict_list = []
#Páginação para coletar todos os dados
page = 1
per_page = 100  

while True:
    params = {
        "page": page,
        "per_page": per_page
    }
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        seats_data = response.json()['seats']

        for seat in seats_data:
            assignee_logins = []
            assigning_team_names = []

            # Coleta todos os logins dos assignees
            if 'assignee' in seat and 'login' in seat['assignee']:
                assignee_logins.append(seat['assignee']['login'])
            elif 'assignee' in seat:
                assignee_logins.append(seat['assignee'])

            # Coleta todos os nomes das assigning teams
            if 'assigning_team' in seat and 'name' in seat['assigning_team']:
                assigning_team_names.append(seat['assigning_team']['name'])
            elif 'assigning_team' in seat:
                assigning_team_names.append(seat['assigning_team'])

            # Verifica se há valores antes de adicionar ao dicionário
            if assignee_logins:
                assignee_logins = assignee_logins[0]  # Se houver mais de um, pega o primeiro
            else:
                assignee_logins = None  # Define como None se estiver vazio

            # Verifica se há assigning teams e define como "SEM GRUPO" se estiver vazio
            if assigning_team_names:
                assigning_team_names = assigning_team_names[0]  # Se houver mais de um, pega o primeiro
            else:
                assigning_team_names = "SEM GRUPO"  # Define como "SEM GRUPO" se estiver vazio

            # Adiciona as novas informações
            created_at = seat.get('created_at', None)
            last_activity_at = seat.get('last_activity_at', None)
            last_activity_editor = seat.get('last_activity_editor', None)

            seat_dict = {
                'NICKNAMEGITHUB': assignee_logins,
                'GRUPO_GITHUB': assigning_team_names,
                'CREATED_AT': created_at,
                'LAST_ACTIVITY_AT': last_activity_at,
                'LAST_ACTIVITY_EDITOR': last_activity_editor
            }

            dict_list.append(seat_dict)

        # Verifica se há mais páginas
        if len(seats_data) < per_page:
            break
        else:
            page += 1

    else:
        print(f"Erro ao acessar a API do GitHub na página {page}: {response.status_code}")
        break

# Criar DataFrame com os dados coletados
df = pd.DataFrame(dict_list)
df.to_excel('LicencasCopilot.xlsx', index=False)

 
print("Fim do script.")

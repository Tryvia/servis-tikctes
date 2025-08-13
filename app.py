import os
import requests
import base64
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# Configuração CORS para permitir requisições de qualquer origem
CORS(app)

# Configuração das credenciais Freshdesk via variáveis de ambiente
FRESHDESK_API_KEY = os.environ.get('FRESHDESK_API_KEY', 'YbOYtaCLmhZuvC9hqWUo')
FRESHDESK_DOMAIN = os.environ.get('FRESHDESK_DOMAIN', 'suportetryvia')

def get_freshdesk_headers():
    """Gera os headers de autenticação para a API Freshdesk"""
    credentials = f"{FRESHDESK_API_KEY}:x"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/json'
    }

def fetch_tickets_by_empresa(cf_empresa):
    """Busca tickets do Freshdesk filtrados por cf_empresa"""
    headers = get_freshdesk_headers()
    all_tickets = []
    page = 1
    max_per_page = 100
    
    while True:
        url = f"https://{FRESHDESK_DOMAIN}.freshdesk.com/api/v2/tickets"
        params = {
            'page': page,
            'per_page': max_per_page
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            tickets = response.json()
            
            if not tickets:
                break
            
            # Filtrar tickets pelo campo customizado cf_empresa
            empresa_tickets = [
                ticket for ticket in tickets
                if ticket.get('custom_fields', {}).get('cf_empresa') == cf_empresa
            ]
            
            all_tickets.extend(empresa_tickets)
            
            # Se retornou menos que o máximo, chegou ao fim
            if len(tickets) < max_per_page:
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao buscar tickets da API Freshdesk: {str(e)}")
    
    return all_tickets

status_choices = {
    "10": ["Em análise", "Em análise"],
    "11": ["Interno", "Interno"],
    "2": ["Open", "Open"],
    "7": ["Aguardando Cliente", "Aguardando Cliente"],
    "4": ["Resolved", "Atribuído "],
    "6": [" Em Homologação", "Em Homologação"],
    "12": ["Aguardando publicar HML", "Aguardando publicar HML"],
    "13": ["Aguardando publicar em PROD", "Aguardando publicar em PROD"],
    "3": ["Pending", "Pendente"],
    "5": ["Closed", "Fechado"],
    "14": ["MVP", "MVP"],
    "15": ["Validação-Atendimento", "Abertos"],
    "16": ["Aguardando Parceiros", "Aguardando Parceiros"],
    "17": ["Pausado", "Pausado"],
    "18": ["Validação-CS", "Abertos"],
    "8": ["Em tratativa", "Em tratativa"],
}

def get_status_name(status_id):
    status_id_str = str(status_id)
    if status_id_str in status_choices:
        return status_choices[status_id_str][1] if len(status_choices[status_id_str]) > 1 else status_choices[status_id_str][0]
    return f"Desconhecido (ID: {status_id_str})"

@app.route('/', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da aplicação"""
    return jsonify({
        'status': 'healthy',
        'message': 'API Freshdesk funcionando',
        'version': '3.0',
        'features': ['tickets_by_empresa', 'direct_freshdesk_integration'],
        'endpoints': [
            '/health',
            '/api/tickets/status',
            '/api/tickets/client-by-empresa?cf_empresa=NOME'
        ]
    })

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de verificação de saúde da aplicação"""
    return jsonify({
        'status': 'healthy',
        'message': 'API Freshdesk funcionando',
        'version': '3.0'
    })

@app.route('/api/tickets/status', methods=['GET'])
def get_tickets_status():
    """Endpoint de status dos tickets"""
    return jsonify({
        'status': 'active',
        'message': 'Serviço de tickets funcionando',
        'freshdesk_domain': FRESHDESK_DOMAIN,
        'endpoints': [
            '/api/tickets/client-by-empresa?cf_empresa=NOME'
        ]
    })

@app.route('/api/tickets/client-by-empresa', methods=['GET'])
def get_tickets_by_cf_empresa():
    """Buscar tickets por cf_empresa diretamente da API Freshdesk"""
    try:
        # Obter cf_empresa dos parâmetros da query
        cf_empresa = request.args.get('cf_empresa')
        if not cf_empresa:
            return jsonify({'error': 'cf_empresa é obrigatório'}), 400
        
        # Buscar tickets diretamente da API Freshdesk
        tickets = fetch_tickets_by_empresa(cf_empresa)
        
        # Mapeia o status real para cada ticket
        for ticket in tickets:
            status_id = ticket.get('status')
            ticket['status_name'] = get_status_name(status_id)
        
        return jsonify(tickets)
        
    except Exception as e:
        return jsonify({
            'error': f'Erro interno: {str(e)}',
            'cf_empresa': cf_empresa
        }), 500

@app.route('/api/tickets/test', methods=['GET'])
def test_endpoint():
    """Endpoint de teste para verificar se a API está funcionando"""
    return jsonify({
        'message': 'API funcionando corretamente',
        'test': True,
        'freshdesk_domain': FRESHDESK_DOMAIN,
        'endpoints': [
            '/api/tickets/client-by-empresa?cf_empresa=NOME'
        ]
    })

if __name__ == '__main__':
    # Para desenvolvimento local
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# API Freshdesk para Render

Esta é uma API Flask que integra diretamente com a API do Freshdesk para buscar tickets por empresa, otimizada para implantação no Render.

## 🚀 Características

- **Integração direta com Freshdesk**: Sem dependências de PowerShell
- **Pronto para produção**: Configurado com Gunicorn e variáveis de ambiente
- **CORS habilitado**: Permite requisições de qualquer origem
- **Endpoints RESTful**: API limpa e bem documentada

## 📋 Endpoints Disponíveis

### GET `/`
Verificação de saúde da aplicação
```json
{
  "status": "healthy",
  "message": "API Freshdesk funcionando",
  "version": "3.0",
  "features": ["tickets_by_empresa", "direct_freshdesk_integration"]
}
```

### GET `/api/tickets/client-by-empresa?cf_empresa=NOME`
Busca tickets por empresa usando o campo customizado `cf_empresa`
```json
[
  {
    "id": 4552,
    "subject": "Suzantur sem grade",
    "status": 13,
    "priority": 1,
    "created_at": "2025-07-25T15:00:37Z",
    "custom_fields": {
      "cf_empresa": "Suzantur",
      "cf_analista": "Gustavo Martins"
    }
  }
]
```

## 🛠 Deploy no Render

### Passo 1: Preparar o Repositório

1. Crie um novo repositório no GitHub
2. Faça upload de todos os arquivos deste projeto
3. Certifique-se de que todos os arquivos estão na raiz do repositório:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `.env.example`

### Passo 2: Criar Serviço no Render

1. Acesse [render.com](https://render.com) e faça login
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub
4. Configure o serviço:
   - **Name**: `freshdesk-api` (ou nome de sua escolha)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### Passo 3: Configurar Variáveis de Ambiente

No painel do Render, vá em "Environment" e adicione:

```
FRESHDESK_API_KEY=YbOYtaCLmhZuvC9hqWUo
FRESHDESK_DOMAIN=suportetryvia
```

### Passo 4: Deploy

1. Clique em "Create Web Service"
2. Aguarde o build e deploy (geralmente 2-5 minutos)
3. Sua API estará disponível em: `https://seu-servico.onrender.com`

## 🧪 Testando a API

Após o deploy, teste os endpoints:

```bash
# Verificação de saúde
curl https://seu-servico.onrender.com/

# Buscar tickets da Suzantur
curl "https://seu-servico.onrender.com/api/tickets/client-by-empresa?cf_empresa=Suzantur"
```

## 🔧 Configuração Local

Para testar localmente:

1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure as variáveis de ambiente (copie `.env.example` para `.env`)
4. Execute: `python app.py`
5. Acesse: `http://localhost:5000`

## 📝 Notas Importantes

- A API usa autenticação básica com a chave da API Freshdesk
- Os tickets são filtrados pelo campo customizado `cf_empresa`
- A API faz paginação automática para buscar todos os tickets
- Timeout de 30 segundos por requisição à API Freshdesk

## 🔒 Segurança

- Nunca commite credenciais no código
- Use sempre variáveis de ambiente para dados sensíveis
- A chave da API Freshdesk deve ser mantida em segredo


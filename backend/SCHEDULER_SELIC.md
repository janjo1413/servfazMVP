# 🕐 Scheduler Automático de SELIC

## Funcionalidade

O sistema agora atualiza automaticamente o cache de SELIC **sem necessidade de intervenção manual**.

## Como Funciona

### 1. **Atualização Automática Diária**
- **Horário:** Todo dia às **06:00** (6h da manhã)
- **Ação:** Busca novas taxas SELIC da API do Banco Central
- **Validação:** Apenas meses completos (mês atual - 1)
- **Logs:** Console mostra detalhes da atualização

### 2. **Atualização ao Iniciar**
- Quando o backend inicia, verifica se o cache tem mais de **24 horas**
- Se tiver, atualiza automaticamente antes de aceitar requisições

### 3. **Meses Completos**
- Sistema sempre usa `mês_atual - 1` para evitar dados incompletos
- Exemplo: Em 08/11/2025, só usa dados até 01/10/2025
- Novembro não é usado até que Dezembro apareça na API

## Endpoints Disponíveis

### Status do Cache
```
GET /selic/status
```

Retorna informações completas:
- Total de meses no cache
- Primeiro e último mês disponível
- Última atualização
- Próxima atualização agendada
- Status do scheduler

**Exemplo de resposta:**
```json
{
  "cache": {
    "total_meses": 58,
    "primeiro_mes": "2020-01",
    "ultimo_mes": "2025-10",
    "ultima_atualizacao": "2025-11-08T06:00:00",
    "taxa_ultimo_mes": 1.28
  },
  "scheduler": {
    "ativo": true,
    "proxima_atualizacao": "2025-11-09T06:00:00",
    "horario_agendado": "06:00 (diariamente)"
  }
}
```

### Forçar Atualização
```
POST /selic/forcar-atualizacao
```

Atualiza o cache **imediatamente** sem esperar o agendamento.

**Exemplo de resposta:**
```json
{
  "status": "sucesso",
  "mensagem": "Cache SELIC atualizado com sucesso",
  "total_meses": 58,
  "ultimo_mes": "2025-10",
  "taxa_ultimo_mes": 1.28,
  "atualizado_em": "2025-11-08T14:35:22.123456"
}
```

### Health Check
```
GET /
```

Agora inclui informações do scheduler:
```json
{
  "status": "online",
  "service": "RcJgJp MVP",
  "scheduler": {
    "ativo": true,
    "proxima_atualizacao_selic": "2025-11-09T06:00:00"
  }
}
```

## Logs do Console

### Inicialização
```
[SCHEDULER] 🚀 Scheduler iniciado - Atualização automática de SELIC agendada para 06:00 diariamente
```

### Atualização Agendada (às 6h)
```
============================================================
[SCHEDULER] Executando atualização automática de SELIC - 2025-11-09 06:00:00.123456
============================================================
Ignorando mês incompleto: 2025-11 = 0.28%
Cache atualizado com 58 meses até 2025-10
[SCHEDULER] ✅ Cache SELIC atualizado com sucesso!
============================================================
```

### Erro (se houver)
```
[SCHEDULER] ❌ Erro ao atualizar SELIC: [detalhes do erro]
```

## Benefícios

### ✅ Automatização Total
- Não precisa reiniciar o servidor para pegar novas SELICs
- Sistema sempre tem dados atualizados

### ✅ Confiabilidade
- Dupla proteção: ao iniciar (24h) + diariamente (6h)
- Logs claros para acompanhamento

### ✅ Produção-Ready
- Adequado para servidor hospedado 24/7
- Não sobrecarrega a API do Banco Central (1 requisição/dia)

### ✅ Segurança de Dados
- Filtra meses incompletos automaticamente
- Evita problemas como o bug do outubro/2025 (0.72% vs 1.28%)

## Dependências

- **APScheduler 3.11.1** - Agendamento de tarefas em background
- **tzlocal 5.3.1** - Gerenciamento de timezone

## Configuração

### Alterar Horário (opcional)
Edite `backend/main.py`:

```python
# Mudar de 6h para 8h da manhã
scheduler.add_job(
    func=atualizar_selic_agendado,
    trigger=CronTrigger(hour=8, minute=0),  # <-- Altere aqui
    ...
)
```

### Alterar Frequência (opcional)
```python
# A cada 12 horas (6h e 18h)
scheduler.add_job(
    func=atualizar_selic_agendado,
    trigger=CronTrigger(hour='6,18', minute=0),
    ...
)
```

## Troubleshooting

### Scheduler não está rodando
Verifique o endpoint `/` - campo `scheduler.ativo` deve ser `true`

### Cache não atualiza
1. Verifique logs do console
2. Use `/selic/status` para ver última atualização
3. Force atualização manual com `/selic/forcar-atualizacao`

### Fuso horário errado
O scheduler usa o timezone local do servidor. Verifique configurações do sistema.

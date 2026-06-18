# 🔧 Troubleshooting - Sistema de E-mail (Brevo)

## Problema: E-mails de Recuperação de Senha Não Estão Sendo Enviados

### ✅ Checklist de Diagnóstico

#### 1. **Verificar Variáveis de Ambiente**
Certifique-se de que as seguintes variáveis estão configuradas no seu painel de hospedagem (Railway/Render):

- `EMAIL_HOST_USER`: O e-mail de login do Brevo.
- `EMAIL_HOST_PASSWORD`: A chave SMTP (xsmtpsib-...).
- `BREVO_API_KEY`: A chave API HTTP (xkeysib-...).

#### 2. **Por que usar a API HTTP (Porta 443)?**
O sistema foi atualizado para priorizar o envio via API HTTP da Brevo. Isso resolve problemas comuns de:
- Firewall bloqueando as portas 587 ou 465.
- Lentidão no protocolo SMTP.
- Bloqueios de segurança de provedores de hospedagem.

#### 3. **Como testar?**
No terminal do seu servidor:
```bash
python manage.py shell
```
```python
from django.core.mail import send_mail
send_mail('Teste', 'Mensagem de teste', 'seu-email-configurado@brevo.com', ['seu-email@pessoal.com'])
```

---

## 🚨 Erros Comuns

### Erro 401 (Unauthorized)
A `BREVO_API_KEY` está incorreta ou expirada. Gere uma nova chave em "SMTP & API" no painel do Brevo.

### Erro 400 (Bad Request)
Geralmente indica que o e-mail do remetente (`EMAIL_HOST_USER`) não foi validado no painel do Brevo em "Senders & IPs".

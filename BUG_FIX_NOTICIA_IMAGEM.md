# Correção: Bug ao Salvar Notícia com Imagem de Capa

## Problema Identificado

Ao criar uma nova notícia no painel (`/painel/noticias/nova/`), quando você:
1. Carrega uma imagem de capa → a prévia aparece corretamente
2. Tenta salvar a notícia → **o salvamento falha silenciosamente**
3. A prévia da imagem desaparece
4. Nenhuma mensagem de erro é exibida

**Causa raiz**: O template `painel/templates/painel/criar_noticia.html` não exibia os erros de validação do formulário. Quando o POST falhava, a página recarregava sem mostrar o motivo do erro.

## Solução Implementada

### Mudanças no Template (`criar_noticia.html`)

Foram adicionadas exibições de erros em todos os campos do formulário:

#### 1. **Erros Gerais (no topo do formulário)**
```django
{% if form.non_field_errors %}
    <div class="alert alert-danger alert-dismissible fade show" role="alert">
        <strong><i class="fas fa-exclamation-circle me-2"></i>Erro ao salvar a notícia:</strong>
        <ul class="mb-0 mt-2">
            {% for error in form.non_field_errors %}
                <li>{{ error }}</li>
            {% endfor %}
        </ul>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
{% endif %}
```

#### 2. **Erros Específicos do Campo de Imagem**
```django
{% if form.imagem.errors %}
    <div class="alert alert-danger mt-2" role="alert">
        <strong><i class="fas fa-exclamation-triangle me-2"></i>Erro ao fazer upload da imagem:</strong>
        <ul class="mb-0 mt-2">
            {% for error in form.imagem.errors %}
                <li>{{ error }}</li>
            {% endfor %}
        </ul>
    </div>
{% endif %}
```

#### 3. **Erros em Cada Campo**
Adicionados blocos de erro após cada campo do formulário (título, resumo, data, autor, conteúdo):
```django
{% if form.campo.errors %}
    <div class="invalid-feedback d-block">
        {% for error in form.campo.errors %}
            <i class="fas fa-times-circle me-1"></i>{{ error }}<br>
        {% endfor %}
    </div>
{% endif %}
```

## Como Diagnosticar o Erro Real

Agora que os erros são exibidos, você poderá ver mensagens como:

### Possíveis Erros e Soluções

| Erro | Causa | Solução |
|------|-------|--------|
| `"Envie um arquivo válido. Este arquivo não parece ser uma imagem."` | Arquivo não é uma imagem válida | Verifique se o arquivo é PNG, JPG, GIF ou WebP |
| `"O tamanho do arquivo excede o máximo permitido."` | Imagem muito grande | Comprima a imagem antes de fazer upload |
| `"Erro ao fazer upload para o Cloudinary"` | Credenciais do Cloudinary inválidas ou serviço indisponível | Verifique as variáveis de ambiente `CLOUDINARY_*` em `settings.py` |
| `"Este campo é obrigatório."` | Campo não foi preenchido | Preencha o campo obrigatório |
| `"Slug duplicado"` | Já existe uma notícia com o mesmo título/slug | Altere o título da notícia |

## Próximos Passos

1. **Teste a criação de notícia com imagem** e observe a mensagem de erro exibida
2. **Identifique o erro específico** usando a tabela acima
3. **Corrija o problema** conforme a solução indicada
4. Se o erro for relacionado ao Cloudinary, verifique:
   - Se as credenciais estão corretas em `fepi_site/settings.py` (linhas 218-222)
   - Se o serviço Cloudinary está funcionando
   - Se as variáveis de ambiente estão definidas no servidor

## Arquivos Modificados

- `painel/templates/painel/criar_noticia.html` - Adicionada exibição de erros em todos os campos

## Versão

- **Data**: 2026-06-23
- **Commit**: Adição de exibição de erros de validação no formulário de notícias

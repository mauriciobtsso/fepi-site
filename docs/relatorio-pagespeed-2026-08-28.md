# Relatório de performance e SEO — FEPI

**Data:** 28 de agosto de 2026  
**Página avaliada:** [https://fepiaui.org.br/](https://fepiaui.org.br/)  
**Dispositivo:** Mobile  
**Ferramenta:** [PageSpeed Insights](https://pagespeed.web.dev/)

## Resultado executivo

A medição inicial desta rodada apresentou Performance **76**, FCP de **2,6 s** e LCP de **5,2 s**. Após a publicação das correções, uma medição intermediária chegou a Performance **91** e LCP de **2,9 s**. A medição final concluída pelo PageSpeed no relatório `g0l6c02wi9` apresentou Performance **93**, FCP de **2,6 s** e LCP de **2,6 s**. Como o Lighthouse utiliza condições de rede e cache variáveis, os números devem ser acompanhados por tendência, não por uma única execução.

| Indicador | Medição inicial | Melhor medição pós-correção | Medição final confirmada |
|---|---:|---:|---:|
| Performance | 76 | 91 | **93** |
| FCP | 2,6 s | 2,7 s | **2,6 s** |
| LCP | 5,2 s | 2,9 s | **2,6 s** |
| Acessibilidade | 89 | 89 | 89 |
| Boas práticas | 96 | 96 | 96 |
| SEO | 92 | 92 | 92 |

## Correções publicadas

A imagem do primeiro slide do carrossel passou a ser descoberta antecipadamente por `preload`, `imagesrcset` e `fetchpriority=high`, mantendo variantes Cloudinary responsivas. A inicialização do carrossel deixou de remover e readicionar a classe do primeiro slide durante o primeiro paint.

O Analytics e o VLibras foram retirados da cadeia crítica e passaram a ser carregados após o `load`/idle. O vídeo do YouTube não cria mais iframe nem baixa miniatura no carregamento inicial; o iframe só é criado quando o visitante solicita o vídeo.

O Font Awesome passou a ser servido localmente, com arquivos versionados pelo manifest do WhiteNoise, fontes WOFF2 e `font-display: swap`. O CSS de ícones é carregado depois do `load`, com fallback em `noscript`, para não bloquear a renderização inicial.

As imagens do Instagram e da livraria passaram a usar variantes Cloudinary compatíveis com o espaço visual real. Também foi mantido cache longo apenas para arquivos estáticos versionados, sem aplicar essa política ao HTML dinâmico.

Foi criada a página pública [`/llms.txt`](https://fepiaui.org.br/llms.txt), com descrição da FEPI, links das áreas públicas, sitemap, robots.txt e orientação para que sistemas de IA usem o domínio oficial como fonte primária. Rotas administrativas, APIs internas e páginas autenticadas não foram incluídas.

## Validação técnica

Foram executados `python manage.py check`, a suíte de **29 testes automatizados**, `collectstatic` com **5.985 arquivos pós-processados** e um verificador de integração das rotas públicas. As rotas home, notícias, cursos, palestras e `/llms.txt` retornaram HTTP 200 no ambiente de teste; a resposta do `llms.txt` foi `text/plain`; e a home respondeu comprimida quando o cliente anunciou suporte a gzip.

O repositório está limpo e as alterações foram publicadas em `main` nos commits `010fb8f`, `f7b8aaf` e `2fabe62`.

## Pendências residuais

A medição final ainda lista forced reflow, cadeia de dependências, aproximadamente 4 KiB de cache potencial, aproximadamente 17 KiB de otimização de imagens, causas de layout shift, DOM grande, terceiros, aproximadamente 21 KiB de CSS não utilizado, aproximadamente 70 KiB de JavaScript não utilizado, quatro tarefas longas e animações não compostas. Esses itens são principalmente associados ao widget VLibras, Google Analytics, Google Fonts, imagens editoriais e ao pacote completo de ícones. Eles não impedem a boa pontuação final de Performance, mas podem ser tratados em uma próxima rodada com orçamento de regressão e testes visuais.

O `manage.py check` continua exibindo o aviso preexistente do CKEditor 4.22.1. Essa dependência não foi substituída nesta rodada porque a migração para CKEditor 5 pode alterar edição, upload e compatibilidade de conteúdo administrativo.

## Referências

[1]: https://pagespeed.web.dev/analysis/https-fepiaui-org-br/g0l6c02wi9?form_factor=mobile "Relatório final do PageSpeed Insights"
[2]: https://pagespeed.web.dev/analysis/https-fepiaui-org-br/m1cidaqbpg?form_factor=mobile "Medição intermediária do PageSpeed Insights"
[3]: https://developer.chrome.com/docs/lighthouse/performance/ "Documentação de performance do Lighthouse"
